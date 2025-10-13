"""
PagerDuty incident management tools for the Incident Agent MCP server.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastmcp import Context

from ..client import get_pagerduty_client


async def get_latest_incidents(
    limit: int = 5, 
    status_filter: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get the latest PagerDuty incidents with optional filtering.
    
    Args:
        limit: Maximum number of incidents to return (default: 5)
        status_filter: Optional status filter ('open', 'resolved', or None for all)
        ctx: FastMCP context for logging
        
    Returns:
        Dictionary containing incident information and summary
    """
    if ctx:
        await ctx.info(f"Querying latest PagerDuty incidents (limit: {limit}, filter: {status_filter})")
    
    try:
        client = get_pagerduty_client()
        
        # Health check
        if not client.health_check():
            error_msg = "❌ Cannot connect to PagerDuty API"
            if ctx:
                await ctx.error(error_msg)
            return {"error": error_msg, "incidents": []}
        
        incidents = []
        summary = {}
        
        if status_filter == "open":
            # Get only open incidents
            raw_incidents = client.get_open_incidents()
            summary["type"] = "Currently Open Incidents"
            summary["total_count"] = len(raw_incidents)
            
        elif status_filter == "resolved":
            # Get only resolved incidents from this week
            raw_incidents = client.get_this_week_resolved_incidents()
            summary["type"] = "Recently Resolved Incidents (This Week)"
            summary["total_count"] = len(raw_incidents)
            
        else:
            # Get recent incidents (last 24 hours)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            raw_incidents = client.get_incidents(
                since=start_date.isoformat() + 'Z',
                until=end_date.isoformat() + 'Z',
                sort_by='created_at:desc'
            )
            summary["type"] = "Recent Incidents (Last 24 Hours)"
            summary["total_count"] = len(raw_incidents)
        
        # Format incidents for display
        for incident in raw_incidents[:limit]:
            formatted_incident = {
                "incident_number": incident["incident_number"],
                "title": incident["title"],
                "status": incident["status"],
                "urgency": incident["urgency"],
                "service": incident["service"]["summary"],
                "created_at": incident["created_at"],
                "html_url": incident["html_url"]
            }
            
            # Add resolution time if resolved
            if incident.get("resolved_at"):
                formatted_incident["resolved_at"] = incident["resolved_at"]
                
                # Calculate resolution time
                created = datetime.fromisoformat(incident["created_at"].replace('Z', '+00:00'))
                resolved = datetime.fromisoformat(incident["resolved_at"].replace('Z', '+00:00'))
                resolution_minutes = int((resolved - created).total_seconds() / 60)
                formatted_incident["resolution_time_minutes"] = resolution_minutes
            
            # Add assignees if any
            if incident.get('assignments'):
                assignees = [a['assignee']['summary'] for a in incident['assignments']]
                formatted_incident["assignees"] = assignees
            
            incidents.append(formatted_incident)
        
        # Add summary statistics
        if raw_incidents:
            status_counts = {}
            urgency_counts = {}
            
            for incident in raw_incidents:
                status = incident['status']
                urgency = incident['urgency']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            summary["status_breakdown"] = status_counts
            summary["urgency_breakdown"] = urgency_counts
        
        if ctx:
            await ctx.info(f"Successfully retrieved {len(incidents)} incidents")
        
        return {
            "success": True,
            "summary": summary,
            "incidents": incidents,
            "query_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Error querying PagerDuty incidents: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg, "incidents": []}


async def get_incident_summary(days: int = 7, ctx: Context = None) -> Dict[str, Any]:
    """
    Get a comprehensive summary of PagerDuty incidents over a specified period.
    
    Args:
        days: Number of days to look back (default: 7)
        ctx: FastMCP context for logging
        
    Returns:
        Dictionary containing incident summary and statistics
    """
    if ctx:
        await ctx.info(f"Generating PagerDuty incident summary for last {days} days")
    
    try:
        client = get_pagerduty_client()
        
        # Health check
        if not client.health_check():
            error_msg = "❌ Cannot connect to PagerDuty API"
            if ctx:
                await ctx.error(error_msg)
            return {"error": error_msg}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get incidents
        incidents = client.get_incidents(
            since=start_date.isoformat() + 'Z',
            until=end_date.isoformat() + 'Z',
            sort_by='created_at:desc'
        )
        
        # Calculate statistics
        total_incidents = len(incidents)
        
        # Group by various attributes
        status_stats = {}
        urgency_stats = {}
        service_stats = {}
        resolution_times = []
        
        for incident in incidents:
            # Status breakdown
            status = incident['status']
            status_stats[status] = status_stats.get(status, 0) + 1
            
            # Urgency breakdown
            urgency = incident['urgency']
            urgency_stats[urgency] = urgency_stats.get(urgency, 0) + 1
            
            # Service breakdown
            service = incident['service']['summary']
            service_stats[service] = service_stats.get(service, 0) + 1
            
            # Resolution time calculation
            if incident.get('resolved_at') and incident.get('created_at'):
                created = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))
                resolved = datetime.fromisoformat(incident['resolved_at'].replace('Z', '+00:00'))
                resolution_minutes = int((resolved - created).total_seconds() / 60)
                resolution_times.append(resolution_minutes)
        
        # Calculate resolution time statistics
        resolution_stats = {}
        if resolution_times:
            resolution_stats = {
                "average_minutes": sum(resolution_times) / len(resolution_times),
                "min_minutes": min(resolution_times),
                "max_minutes": max(resolution_times),
                "resolved_count": len(resolution_times)
            }
        
        # Get top services
        top_services = sorted(service_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        summary = {
            "success": True,
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_incidents": total_incidents,
            "status_breakdown": status_stats,
            "urgency_breakdown": urgency_stats,
            "top_services": dict(top_services),
            "resolution_statistics": resolution_stats,
            "query_time": datetime.now().isoformat()
        }
        
        if ctx:
            await ctx.info(f"Generated summary for {total_incidents} incidents over {days} days")
        
        return summary
        
    except Exception as e:
        error_msg = f"Error generating incident summary: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg}


async def search_incidents(
    query: str,
    limit: int = 10, 
    days: int = 30,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Search for PagerDuty incidents by title/description.
    
    Args:
        query: Search term to look for in incident titles
        limit: Maximum number of results to return (default: 10)
        days: Number of days to search back (default: 30)
        ctx: FastMCP context for logging
        
    Returns:
        Dictionary containing matching incidents
    """
    if ctx:
        await ctx.info(f"Searching PagerDuty incidents for: '{query}' (last {days} days)")
    
    try:
        client = get_pagerduty_client()
        
        # Health check
        if not client.health_check():
            error_msg = "❌ Cannot connect to PagerDuty API"
            if ctx:
                await ctx.error(error_msg)
            return {"error": error_msg, "incidents": []}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get recent incidents
        all_incidents = client.get_incidents(
            since=start_date.isoformat() + 'Z',
            until=end_date.isoformat() + 'Z',
            sort_by='created_at:desc'
        )
        
        # Filter incidents by search query
        query_lower = query.lower()
        matching_incidents = []
        
        for incident in all_incidents:
            title = incident.get("title", "").lower()
            if query_lower in title:
                formatted_incident = {
                    "incident_number": incident["incident_number"],
                    "title": incident["title"],
                    "status": incident["status"],
                    "urgency": incident["urgency"],
                    "service": incident["service"]["summary"],
                    "created_at": incident["created_at"],
                    "html_url": incident["html_url"]
                }
                
                if incident.get("resolved_at"):
                    formatted_incident["resolved_at"] = incident["resolved_at"]
                
                matching_incidents.append(formatted_incident)
                
                if len(matching_incidents) >= limit:
                    break
        
        if ctx:
            await ctx.info(f"Found {len(matching_incidents)} matching incidents")
        
        return {
            "success": True,
            "query": query,
            "search_period_days": days,
            "total_matches": len(matching_incidents),
            "incidents": matching_incidents,
            "query_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Error searching incidents: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg, "incidents": []}
