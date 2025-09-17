"""
Pipeline analyzer agent using Azure AI for intelligent log analysis.

This module provides AI-powered analysis of pipeline logs with automatic fallback
to heuristic analysis if the LLM service is unavailable.
"""

import json
import os
from typing import Dict, List, Any
from collections import Counter

from common.azure_ai import llm_json, get_client, AzureAIError


def analyze_pipeline_logs(pipeline_logs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze pipeline logs using Azure AI with fallback to heuristic analysis.
    
    Uses Azure OpenAI to provide intelligent insights about pipeline performance,
    error patterns, and actionable recommendations. Falls back to local analysis
    if the AI service is unavailable.
    
    Args:
        pipeline_logs: Pipeline log data from get_pipeline_logs()
        
    Returns:
        Dict containing analysis results with keys:
        - pipeline_key: The pipeline identifier
        - summary: High-level analysis summary
        - top_errors: List of {message: str, count: int} for most common errors
        - recommendations: List of actionable recommendation strings
        
    Example:
        >>> logs = get_pipeline_logs("PROJ-PLAN1")
        >>> analysis = analyze_pipeline_logs(logs)
        >>> print(analysis['summary'])
        "Pipeline shows consistent success with good performance"
    """
    pipeline_key = pipeline_logs.get('pipeline_key', 'UNKNOWN')
    pipeline_name = pipeline_logs.get('pipeline_name', 'Unknown Pipeline')
    
    # Prepare system prompt for senior CI engineer persona
    system_prompt = """You are a senior CI/CD engineer with 10+ years of experience analyzing Bamboo pipeline logs. 
Your expertise includes identifying failure patterns, performance bottlenecks, and providing actionable recommendations 
for improving pipeline reliability and efficiency.

Analyze the provided pipeline log data and provide insights that would help a development team optimize their CI/CD process."""
    
    # Create user prompt with pipeline data
    user_prompt = f"""Analyze the following Bamboo pipeline logs for {pipeline_name} ({pipeline_key}):

{json.dumps(pipeline_logs, indent=2)}

Please provide a comprehensive analysis focusing on:
1. Overall pipeline health and performance trends
2. Error patterns and their frequency
3. Specific actionable recommendations for improvement
4. Any performance or reliability concerns

Consider the success/failure rates, error types, duration patterns, and any recurring issues."""
    
    # Define explicit JSON schema for response
    response_schema_hint = """{
  "pipeline_key": "string - the pipeline identifier",
  "summary": "string - concise 2-3 sentence overview of pipeline health and key findings",
  "top_errors": [
    {
      "message": "string - clear description of the error or issue",
      "count": "integer - number of times this error occurred"
    }
  ],
  "recommendations": [
    "string - specific actionable recommendation for improvement"
  ]
}"""
    
    try:
        # Get the Azure AI client
        client = get_client()
        
        # Check if assistant is configured
        if client.assistant_id:
            # Use Azure AI Foundry assistant for analysis
            full_prompt = f"""Analyze the following Bamboo pipeline logs for {pipeline_name} ({pipeline_key}):

{json.dumps(pipeline_logs, indent=2)}

Please provide a comprehensive analysis focusing on:
1. Overall pipeline health and performance trends
2. Error patterns and their frequency  
3. Specific actionable recommendations for improvement
4. Any performance or reliability concerns

Consider the success/failure rates, error types, duration patterns, and any recurring issues.

Please respond with valid JSON in this exact format:
{response_schema_hint}"""
            
            response_text = client.llm_text_with_assistant(full_prompt, system_prompt)
            
            # Parse the JSON response
            import re
            # Extract JSON from response if it's wrapped in markdown
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text
            
            analysis = json.loads(json_text)
        else:
            # Use traditional chat completions
            analysis = llm_json(system_prompt, user_prompt, response_schema_hint)
        
        # Validate required keys are present
        required_keys = ['pipeline_key', 'summary', 'top_errors', 'recommendations']
        if not all(key in analysis for key in required_keys):
            raise ValueError(f"AI response missing required keys: {required_keys}")
        
        # Ensure pipeline_key matches
        analysis['pipeline_key'] = pipeline_key
        
        # Validate top_errors structure
        if not isinstance(analysis.get('top_errors'), list):
            analysis['top_errors'] = []
        
        for error in analysis['top_errors']:
            if not isinstance(error, dict) or 'message' not in error or 'count' not in error:
                # Fix malformed error entries
                if isinstance(error, str):
                    error = {'message': error, 'count': 1}
                elif isinstance(error, dict):
                    error.setdefault('message', 'Unknown error')
                    error.setdefault('count', 1)
        
        # Validate recommendations structure
        if not isinstance(analysis.get('recommendations'), list):
            analysis['recommendations'] = []
        
        return analysis
        
    except (AzureAIError, ValueError, KeyError, TypeError) as e:
        # Fallback to heuristic analysis
        print(f"AI analysis failed ({e}), falling back to heuristic analysis")
        return _heuristic_analysis(pipeline_logs)


def _heuristic_analysis(pipeline_logs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide heuristic analysis of pipeline logs when AI service is unavailable.
    
    Uses local algorithms to analyze error patterns, success rates, and
    performance metrics to generate basic insights.
    
    Args:
        pipeline_logs: Pipeline log data
        
    Returns:
        Dict with same structure as AI analysis
    """
    pipeline_key = pipeline_logs.get('pipeline_key', 'UNKNOWN')
    pipeline_name = pipeline_logs.get('pipeline_name', 'Unknown Pipeline')
    runs = pipeline_logs.get('runs', [])
    
    if not runs:
        return {
            'pipeline_key': pipeline_key,
            'summary': f"No execution data available for {pipeline_name}",
            'top_errors': [],
            'recommendations': ['Configure pipeline to capture execution logs']
        }
    
    # Calculate basic statistics
    total_runs = len(runs)
    successful_runs = sum(1 for run in runs if run.get('status') == 'SUCCESS')
    failed_runs = sum(1 for run in runs if run.get('status') == 'FAILED')
    in_progress_runs = sum(1 for run in runs if run.get('status') == 'IN_PROGRESS')
    
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
    
    # Collect and count errors
    all_errors = []
    total_duration = 0
    completed_runs = 0
    
    for run in runs:
        # Collect errors
        for error in run.get('errors', []):
            if isinstance(error, dict) and 'message' in error:
                all_errors.append(error['message'])
            elif isinstance(error, str):
                all_errors.append(error)
        
        # Calculate average duration for completed runs
        duration = run.get('duration_seconds', 0)
        if duration > 0:
            total_duration += duration
            completed_runs += 1
    
    # Count error frequency
    error_counter = Counter(all_errors)
    top_errors = [
        {'message': message, 'count': count}
        for message, count in error_counter.most_common(5)
    ]
    
    # Generate summary
    avg_duration = (total_duration / completed_runs) if completed_runs > 0 else 0
    avg_minutes = avg_duration // 60
    
    if success_rate >= 90:
        health_status = "excellent"
    elif success_rate >= 75:
        health_status = "good"
    elif success_rate >= 50:
        health_status = "concerning"
    else:
        health_status = "poor"
    
    summary_parts = [
        f"Pipeline shows {health_status} health with {success_rate:.1f}% success rate ({successful_runs}/{total_runs} runs)"
    ]
    
    if avg_duration > 0:
        summary_parts.append(f"Average execution time is {avg_minutes:.0f} minutes")
    
    if failed_runs > 0:
        summary_parts.append(f"{failed_runs} recent failures requiring attention")
    
    summary = ". ".join(summary_parts) + "."
    
    # Generate heuristic recommendations
    recommendations = []
    
    if success_rate < 75:
        recommendations.append("Investigate recurring failures to improve pipeline stability")
    
    if len(top_errors) > 0:
        recommendations.append("Address top error patterns to reduce failure rate")
    
    if avg_duration > 1800:  # > 30 minutes
        recommendations.append("Consider optimizing build steps to reduce execution time")
    
    if failed_runs > successful_runs:
        recommendations.append("Pipeline requires immediate attention due to high failure rate")
    
    if in_progress_runs > 0:
        recommendations.append("Monitor currently running builds for potential issues")
    
    # Check for specific error patterns
    error_messages = " ".join(all_errors).lower()
    if 'timeout' in error_messages:
        recommendations.append("Review timeout configurations and resource allocation")
    
    if 'test' in error_messages and 'failed' in error_messages:
        recommendations.append("Focus on test stability and test environment configuration")
    
    if 'connection' in error_messages or 'network' in error_messages:
        recommendations.append("Investigate network connectivity and service dependencies")
    
    if not recommendations:
        if success_rate >= 90:
            recommendations.append("Pipeline performing well, continue monitoring")
        else:
            recommendations.append("Monitor pipeline trends and investigate any performance degradation")
    
    return {
        'pipeline_key': pipeline_key,
        'summary': summary,
        'top_errors': top_errors,
        'recommendations': recommendations[:5]  # Limit to top 5 recommendations
    }


def analyze_multiple_pipelines(all_pipeline_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple pipelines and return aggregated insights.
    
    Args:
        all_pipeline_logs: List of pipeline log data from get_all_logs()
        
    Returns:
        List of analysis results for each pipeline
    """
    analyses = []
    
    for pipeline_logs in all_pipeline_logs:
        try:
            analysis = analyze_pipeline_logs(pipeline_logs)
            analyses.append(analysis)
        except Exception as e:
            # Ensure we always return something for each pipeline
            pipeline_key = pipeline_logs.get('pipeline_key', 'UNKNOWN')
            analyses.append({
                'pipeline_key': pipeline_key,
                'summary': f"Analysis failed for {pipeline_key}: {str(e)}",
                'top_errors': [],
                'recommendations': ['Manual investigation required due to analysis error']
            })
    
    return analyses


def get_fleet_summary(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate high-level summary across multiple pipeline analyses.
    
    Args:
        analyses: List of pipeline analysis results
        
    Returns:
        Dict containing fleet-wide insights and recommendations
    """
    if not analyses:
        return {
            'total_pipelines': 0,
            'overall_health': 'unknown',
            'common_issues': [],
            'fleet_recommendations': []
        }
    
    total_pipelines = len(analyses)
    
    # Extract all errors across pipelines
    all_errors = []
    all_recommendations = []
    
    for analysis in analyses:
        for error in analysis.get('top_errors', []):
            all_errors.append(error.get('message', ''))
        
        all_recommendations.extend(analysis.get('recommendations', []))
    
    # Find common error patterns
    error_counter = Counter(all_errors)
    common_issues = [
        {'issue': issue, 'affected_pipelines': count}
        for issue, count in error_counter.most_common(3)
        if count > 1  # Only include issues affecting multiple pipelines
    ]
    
    # Find common recommendations
    recommendation_counter = Counter(all_recommendations)
    fleet_recommendations = [
        rec for rec, count in recommendation_counter.most_common(5)
        if count > 1  # Recommendations that apply to multiple pipelines
    ]
    
    # Determine overall health (simplified heuristic)
    healthy_keywords = ['excellent', 'good', 'performing well', 'consistent success']
    unhealthy_keywords = ['poor', 'concerning', 'failures', 'requires attention']
    
    health_score = 0
    for analysis in analyses:
        summary = analysis.get('summary', '').lower()
        if any(keyword in summary for keyword in healthy_keywords):
            health_score += 1
        elif any(keyword in summary for keyword in unhealthy_keywords):
            health_score -= 1
    
    if health_score > len(analyses) * 0.5:
        overall_health = 'good'
    elif health_score < -len(analyses) * 0.3:
        overall_health = 'concerning'
    else:
        overall_health = 'mixed'
    
    return {
        'total_pipelines': total_pipelines,
        'overall_health': overall_health,
        'common_issues': common_issues,
        'fleet_recommendations': fleet_recommendations[:3]  # Top 3 fleet-wide recommendations
    }