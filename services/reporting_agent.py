"""
Pipeline reporting agent for generating executive summaries and reports.

This module aggregates pipeline statistics and uses Azure AI to generate
human-readable Markdown reports for stakeholders and management.
"""

import os
from typing import Dict, List, Any
from statistics import mean

from common.azure_ai import llm_text, get_client, AzureAIError


def aggregate_and_report(analyses: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate pipeline statistics and generate human-readable Markdown report.
    
    Computes comprehensive statistics from pipeline analyses and logs, then uses
    Azure AI to generate an executive summary in Markdown format suitable for
    stakeholders and management reporting.
    
    Args:
        analyses: List of pipeline analysis results from analyze_pipeline_logs()
        all_logs: List of pipeline log data from get_all_logs()
        
    Returns:
        Dict containing:
        - stats: Aggregated statistics (pipelines_total, runs_total, etc.)
        - bugs_summary: List of critical issues across all pipelines
        - markdown: Human-readable Markdown report
        
    Example:
        >>> analyses = [analyze_pipeline_logs(logs) for logs in all_logs]
        >>> report = aggregate_and_report(analyses, all_logs)
        >>> print(report['stats']['pipelines_total'])
        3
    """
    # Ensure deterministic ordering by pipeline_key
    analyses_sorted = sorted(analyses, key=lambda x: x.get('pipeline_key', ''))
    all_logs_sorted = sorted(all_logs, key=lambda x: x.get('pipeline_key', ''))
    
    # Compute aggregate statistics
    stats = _compute_statistics(analyses_sorted, all_logs_sorted)
    
    # Extract bugs summary
    bugs_summary = _extract_bugs_summary(analyses_sorted, all_logs_sorted)
    
    # Generate Markdown report using Azure AI
    try:
        markdown = _generate_markdown_report(stats, bugs_summary, analyses_sorted)
    except (AzureAIError, Exception) as e:
        print(f"AI report generation failed ({e}), using fallback template")
        markdown = _generate_fallback_report(stats, bugs_summary, analyses_sorted)
    
    return {
        "stats": stats,
        "bugs_summary": bugs_summary,
        "markdown": markdown
    }


def _compute_statistics(analyses: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute aggregate statistics from analyses and logs.
    
    Args:
        analyses: Sorted list of pipeline analyses
        all_logs: Sorted list of pipeline logs
        
    Returns:
        Dict with computed statistics
    """
    pipelines_total = len(analyses)
    runs_total = 0
    total_duration = 0
    completed_runs = 0
    errors_total = 0
    
    # Aggregate data from logs (more detailed than analyses)
    for logs in all_logs:
        runs = logs.get('runs', [])
        runs_total += len(runs)
        
        for run in runs:
            # Count errors
            errors_total += len(run.get('errors', []))
            
            # Sum durations for completed runs only
            duration = run.get('duration_seconds', 0)
            if duration > 0:  # Only count completed runs
                total_duration += duration
                completed_runs += 1
    
    # Calculate average duration (rounded integer)
    avg_duration_seconds = round(total_duration / completed_runs) if completed_runs > 0 else 0
    
    return {
        "pipelines_total": pipelines_total,
        "runs_total": runs_total,
        "avg_duration_seconds": avg_duration_seconds,
        "errors_total": errors_total,
        "completed_runs": completed_runs
    }


def _extract_bugs_summary(analyses: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract critical bugs and issues from analyses and logs.
    
    Args:
        analyses: Sorted list of pipeline analyses
        all_logs: Sorted list of pipeline logs
        
    Returns:
        List of bug summaries with pipeline context
    """
    bugs_summary = []
    
    # Create lookup for logs by pipeline key
    logs_by_key = {logs.get('pipeline_key'): logs for logs in all_logs}
    
    for analysis in analyses:
        pipeline_key = analysis.get('pipeline_key', 'UNKNOWN')
        pipeline_logs = logs_by_key.get(pipeline_key, {})
        
        # Extract top errors from analysis
        top_errors = analysis.get('top_errors', [])
        
        for error in top_errors:
            error_message = error.get('message', 'Unknown error')
            error_count = error.get('count', 1)
            
            # Determine severity based on error patterns and frequency
            severity = _determine_error_severity(error_message, error_count)
            
            # Find recent run with this error for context
            recent_run = _find_recent_error_run(pipeline_logs, error_message)
            
            bug_entry = {
                "pipeline_key": pipeline_key,
                "pipeline_name": pipeline_logs.get('pipeline_name', 'Unknown Pipeline'),
                "error_message": error_message,
                "frequency": error_count,
                "severity": severity,
                "last_seen": recent_run.get('started_at', 'Unknown') if recent_run else 'Unknown',
                "affected_step": recent_run.get('failed_step', 'Unknown') if recent_run else 'Unknown'
            }
            
            bugs_summary.append(bug_entry)
    
    # Sort by severity (high first) then by frequency (high first)
    severity_order = {'high': 3, 'medium': 2, 'low': 1}
    bugs_summary.sort(
        key=lambda x: (severity_order.get(x['severity'], 0), x['frequency']),
        reverse=True
    )
    
    return bugs_summary


def _determine_error_severity(error_message: str, frequency: int) -> str:
    """
    Determine error severity based on message content and frequency.
    
    Args:
        error_message: The error message text
        frequency: How often this error occurs
        
    Returns:
        Severity level: 'high', 'medium', or 'low'
    """
    error_lower = error_message.lower()
    
    # High severity indicators
    high_severity_keywords = [
        'timeout', 'connection', 'database', 'service unavailable',
        'out of memory', 'disk space', 'network', 'authentication failed'
    ]
    
    # Medium severity indicators
    medium_severity_keywords = [
        'test failed', 'assertion', 'compilation error', 'build failed',
        'dependency', 'configuration'
    ]
    
    if frequency >= 3 or any(keyword in error_lower for keyword in high_severity_keywords):
        return 'high'
    elif frequency >= 2 or any(keyword in error_lower for keyword in medium_severity_keywords):
        return 'medium'
    else:
        return 'low'


def _find_recent_error_run(pipeline_logs: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    """
    Find the most recent run that contains the specified error.
    
    Args:
        pipeline_logs: Pipeline log data
        error_message: Error message to search for
        
    Returns:
        Most recent run dict containing the error, or empty dict
    """
    runs = pipeline_logs.get('runs', [])
    
    for run in runs:  # Runs are typically ordered newest first
        for error in run.get('errors', []):
            if isinstance(error, dict):
                if error.get('message') == error_message:
                    # Add failed step info if available
                    failed_step = error.get('step', 'Unknown')
                    run_copy = run.copy()
                    run_copy['failed_step'] = failed_step
                    return run_copy
            elif isinstance(error, str) and error == error_message:
                return run
    
    return {}


def _generate_markdown_report(
    stats: Dict[str, Any], 
    bugs_summary: List[Dict[str, Any]], 
    analyses: List[Dict[str, Any]]
) -> str:
    """
    Generate human-readable Markdown report using Azure AI.
    
    Args:
        stats: Aggregated statistics
        bugs_summary: Critical bugs and issues
        analyses: Pipeline analysis results
        
    Returns:
        Markdown formatted report string
    """
    system_prompt = """You are an experienced DevOps manager creating executive reports for engineering leadership. 
Your reports are clear, actionable, and focus on business impact. You highlight both successes and areas needing attention.

Create professional Markdown reports that executives and engineering managers can quickly understand and act upon."""
    
    # Prepare data summary for the AI
    data_summary = f"""
PIPELINE STATISTICS:
- Total Pipelines: {stats['pipelines_total']}
- Total Runs Analyzed: {stats['runs_total']}
- Average Run Duration: {stats['avg_duration_seconds']} seconds ({stats['avg_duration_seconds']//60} minutes)
- Total Errors Found: {stats['errors_total']}
- Completed Runs: {stats['completed_runs']}

CRITICAL ISSUES ({len(bugs_summary)} total):
"""
    
    for bug in bugs_summary[:5]:  # Top 5 issues
        data_summary += f"- {bug['severity'].upper()}: {bug['error_message']} (Pipeline: {bug['pipeline_key']}, Frequency: {bug['frequency']})\n"
    
    data_summary += "\nPIPELINE ANALYSIS SUMMARIES:\n"
    for analysis in analyses:
        pipeline_key = analysis.get('pipeline_key', 'UNKNOWN')
        summary = analysis.get('summary', 'No summary available')
        recommendations = analysis.get('recommendations', [])
        
        data_summary += f"\n{pipeline_key}:\n"
        data_summary += f"  Summary: {summary}\n"
        if recommendations:
            data_summary += f"  Key Recommendations: {'; '.join(recommendations[:2])}\n"
    
    user_prompt = f"""Create a comprehensive CI/CD Pipeline Report based on this data:

{data_summary}

Structure the report with these sections:
1. **Executive Summary** - High-level health and key findings
2. **Pipeline Performance Overview** - Statistics and trends
3. **Critical Issues** - Top bugs and failures requiring attention
4. **Recommendations** - Actionable next steps prioritized by impact
5. **Individual Pipeline Status** - Brief status for each pipeline

Use professional tone suitable for engineering leadership. Include specific metrics and make recommendations actionable with clear priorities."""
    
    # Try to use the reporting assistant if available
    try:
        reporting_assistant_id = os.getenv("AZURE_REPORTING_ASSISTANT_ID")
        if reporting_assistant_id:
            # Use specific reporting assistant
            client = get_client()
            markdown_report = client.llm_text_with_specific_assistant(
                user_prompt, 
                reporting_assistant_id, 
                system_prompt
            )
        else:
            # Fallback to regular text generation
            markdown_report = llm_text(system_prompt, user_prompt)
    except Exception as e:
        # Double fallback to regular text generation
        print(f"Reporting assistant failed ({e}), trying regular AI")
        markdown_report = llm_text(system_prompt, user_prompt)
    
    # Ensure the report ends properly
    if not markdown_report.strip().endswith('\n'):
        markdown_report += '\n'
    
    return markdown_report    # Ensure the report ends properly
    if not markdown_report.strip().endswith('\n'):
        markdown_report += '\n'
    
    return markdown_report


def _generate_fallback_report(
    stats: Dict[str, Any], 
    bugs_summary: List[Dict[str, Any]], 
    analyses: List[Dict[str, Any]]
) -> str:
    """
    Generate fallback Markdown report when AI service is unavailable.
    
    Args:
        stats: Aggregated statistics
        bugs_summary: Critical bugs and issues
        analyses: Pipeline analysis results
        
    Returns:
        Basic Markdown formatted report
    """
    avg_minutes = stats['avg_duration_seconds'] // 60
    
    report = f"""# CI/CD Pipeline Report
*Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

Analysis of **{stats['pipelines_total']} pipelines** with **{stats['runs_total']} total runs** shows:
- Average execution time: **{avg_minutes} minutes**
- Total errors detected: **{stats['errors_total']}**
- Success rate: **{((stats['completed_runs'] - stats['errors_total']) / max(stats['completed_runs'], 1) * 100):.1f}%**

## Pipeline Performance Overview

| Metric | Value |
|--------|--------|
| Total Pipelines | {stats['pipelines_total']} |
| Total Runs | {stats['runs_total']} |
| Average Duration | {stats['avg_duration_seconds']}s ({avg_minutes}m) |
| Total Errors | {stats['errors_total']} |
| Completed Runs | {stats['completed_runs']} |

## Critical Issues

"""
    
    if bugs_summary:
        report += f"Found **{len(bugs_summary)} critical issues** requiring attention:\n\n"
        
        for i, bug in enumerate(bugs_summary[:5], 1):
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(bug['severity'], "⚪")
            report += f"{i}. {severity_icon} **{bug['pipeline_key']}**: {bug['error_message']}\n"
            report += f"   - Frequency: {bug['frequency']} occurrences\n"
            report += f"   - Severity: {bug['severity'].title()}\n\n"
    else:
        report += "No critical issues detected. ✅\n\n"
    
    report += "## Recommendations\n\n"
    
    # Extract unique recommendations
    all_recommendations = []
    for analysis in analyses:
        all_recommendations.extend(analysis.get('recommendations', []))
    
    unique_recommendations = list(dict.fromkeys(all_recommendations))  # Preserve order, remove duplicates
    
    if unique_recommendations:
        for i, rec in enumerate(unique_recommendations[:5], 1):
            report += f"{i}. {rec}\n"
    else:
        report += "Continue monitoring pipeline performance and maintain current practices.\n"
    
    report += "\n## Individual Pipeline Status\n\n"
    
    for analysis in analyses:
        pipeline_key = analysis.get('pipeline_key', 'UNKNOWN')
        summary = analysis.get('summary', 'No summary available')
        
        # Determine status icon based on summary keywords
        summary_lower = summary.lower()
        if 'excellent' in summary_lower or 'good' in summary_lower:
            status_icon = "✅"
        elif 'concerning' in summary_lower or 'poor' in summary_lower:
            status_icon = "⚠️"
        else:
            status_icon = "ℹ️"
        
        report += f"### {status_icon} {pipeline_key}\n{summary}\n\n"
    
    report += "---\n*Report generated automatically by Pipeline Assistant*\n"
    
    return report


def generate_daily_summary(analyses: List[Dict[str, Any]], all_logs: List[Dict[str, Any]]) -> str:
    """
    Generate a brief daily summary suitable for team standup or Slack.
    
    Args:
        analyses: List of pipeline analysis results
        all_logs: List of pipeline log data
        
    Returns:
        Short summary string
    """
    stats = _compute_statistics(analyses, all_logs)
    bugs_summary = _extract_bugs_summary(analyses, all_logs)
    
    success_rate = ((stats['completed_runs'] - stats['errors_total']) / max(stats['completed_runs'], 1) * 100)
    high_severity_issues = sum(1 for bug in bugs_summary if bug['severity'] == 'high')
    
    if success_rate >= 90 and high_severity_issues == 0:
        status = "🟢 All systems healthy"
    elif success_rate >= 75 and high_severity_issues <= 1:
        status = "🟡 Minor issues detected"
    else:
        status = "🔴 Issues require attention"
    
    return f"{status} | {stats['pipelines_total']} pipelines, {stats['runs_total']} runs, {success_rate:.0f}% success rate, {high_severity_issues} critical issues"