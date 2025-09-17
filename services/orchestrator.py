"""
Pipeline orchestrator service for coordinating complete pipeline analysis workflow.

This module provides the main entry point for running comprehensive pipeline
analysis, from data collection through AI-powered analysis to executive reporting.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from .bamboo_mock import get_bamboo_plans, get_plan_results
from .logs_mock import get_all_logs
from .analyzer_agent import analyze_multiple_pipelines
from .reporting_agent import aggregate_and_report

# Configure logging with ERROR as default level
# This can be overridden by the main application based on verbosity flags
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run(question: str) -> Dict[str, Any]:
    """
    Execute complete pipeline analysis workflow.
    
    Orchestrates the full pipeline from data collection through AI analysis
    to executive reporting. Provides comprehensive traceability of all
    inputs and outputs for debugging and auditing.
    
    Args:
        question: User question or context for the analysis (for future extension)
        
    Returns:
        Dict containing complete workflow results with traceability:
        - workflow_info: Metadata about the execution
        - inputs: All input data used in the analysis
        - processing: Intermediate results from each stage
        - outputs: Final results and reports
        - question: Original user question for context
        
    Example:
        >>> result = run("What's the current state of our CI/CD pipelines?")
        >>> print(result['outputs']['report']['stats']['pipelines_total'])
        3
    """
    start_time = datetime.now()
    logger.info(f"Starting pipeline analysis for question: '{question}'")
    
    try:
        # Step 1: Get Bamboo plans (mock data)
        logger.debug("Step 1: Fetching Bamboo plans...")
        raw_bamboo_data = get_bamboo_plans()
        normalized_plans = _normalize_bamboo_plans(raw_bamboo_data)
        logger.debug(f"Retrieved {len(normalized_plans)} pipelines")
        
        # Step 2: Fetch logs for each pipeline (mock data)
        logger.debug("Step 2: Fetching pipeline logs...")
        all_logs = get_all_logs(normalized_plans)
        total_runs = sum(len(logs.get('runs', [])) for logs in all_logs)
        logger.debug(f"Retrieved logs for {total_runs} total runs across all pipelines")
        
        # Step 3: Analyze each pipeline via analyzer_agent
        logger.debug("Step 3: Analyzing pipelines with AI agent...")
        analyses = analyze_multiple_pipelines(all_logs)
        logger.debug(f"Completed analysis for {len(analyses)} pipelines")
        
        # Step 4: Aggregate and generate report via reporting_agent
        logger.debug("Step 4: Generating executive report...")
        report = aggregate_and_report(analyses, all_logs)
        logger.info(f"Analysis complete: {report['stats']['errors_total']} errors found across {len(analyses)} pipelines")
        
        # Step 5: Compile complete workflow result
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        workflow_result = {
            "workflow_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "status": "success",
                "version": "1.0",
                "steps_completed": 4
            },
            "inputs": {
                "question": question,
                "raw_bamboo_data": raw_bamboo_data,
                "normalized_plans": normalized_plans,
                "logs_fetched": len(all_logs)
            },
            "processing": {
                "step1_plans": {
                    "pipelines_found": len(normalized_plans),
                    "pipeline_keys": [plan.get('key', 'UNKNOWN') for plan in normalized_plans]
                },
                "step2_logs": {
                    "logs_retrieved": len(all_logs),
                    "total_runs": total_runs,
                    "logs_summary": [
                        {
                            "pipeline_key": logs.get('pipeline_key'),
                            "runs_count": len(logs.get('runs', [])),
                            "has_errors": any(run.get('errors', []) for run in logs.get('runs', []))
                        }
                        for logs in all_logs
                    ]
                },
                "step3_analysis": {
                    "analyses_completed": len(analyses),
                    "analysis_summary": [
                        {
                            "pipeline_key": analysis.get('pipeline_key'),
                            "error_count": len(analysis.get('top_errors', [])),
                            "recommendation_count": len(analysis.get('recommendations', []))
                        }
                        for analysis in analyses
                    ]
                },
                "step4_reporting": {
                    "report_generated": True,
                    "stats_computed": bool(report.get('stats')),
                    "bugs_found": len(report.get('bugs_summary', [])),
                    "markdown_length": len(report.get('markdown', ''))
                }
            },
            "outputs": {
                "pipelines": normalized_plans,
                "logs": all_logs,
                "analyses": analyses,
                "report": report,
                "summary": _generate_execution_summary(analyses, report, execution_time)
            },
            "question": question
        }
        
        logger.info(f"Pipeline analysis completed successfully ({execution_time:.1f}s)")
        return workflow_result
        
    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.error(f"Workflow failed after {execution_time:.2f} seconds: {str(e)}")
        
        # Return error result with traceability
        return {
            "workflow_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "status": "error",
                "error_message": str(e),
                "version": "1.0",
                "steps_completed": 0
            },
            "inputs": {
                "question": question
            },
            "processing": {},
            "outputs": {},
            "question": question
        }


def _normalize_bamboo_plans(raw_bamboo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize Bamboo plans data into consistent format.
    
    Extracts and standardizes plan information from raw Bamboo API response
    into a simpler, consistent structure for downstream processing.
    
    Args:
        raw_bamboo_data: Raw response from get_bamboo_plans()
        
    Returns:
        List of normalized plan dictionaries
    """
    plans = raw_bamboo_data.get('plans', {}).get('plan', [])
    
    normalized = []
    for plan in plans:
        normalized_plan = {
            'key': plan.get('key', 'UNKNOWN'),
            'name': plan.get('name', 'Unknown Plan'),
            'enabled': plan.get('enabled', False),
            'shortName': plan.get('shortName', ''),
            'projectKey': plan.get('projectKey', ''),
            'projectName': plan.get('projectName', ''),
            'description': plan.get('description', ''),
            'isActive': plan.get('isActive', False),
            'isBuilding': plan.get('isBuilding', False),
            'averageBuildTimeInSeconds': plan.get('averageBuildTimeInSeconds', 0),
            'link': plan.get('link', {}).get('href', ''),
            # Preserve original for reference
            '_original': plan
        }
        normalized.append(normalized_plan)
    
    # Sort by key for deterministic ordering
    normalized.sort(key=lambda x: x['key'])
    
    logger.debug(f"Normalized {len(normalized)} plans")
    return normalized


def _generate_execution_summary(
    analyses: List[Dict[str, Any]], 
    report: Dict[str, Any], 
    execution_time: float
) -> Dict[str, Any]:
    """
    Generate high-level summary of workflow execution.
    
    Args:
        analyses: Pipeline analysis results
        report: Aggregated report data
        execution_time: Total execution time in seconds
        
    Returns:
        Dict containing execution summary
    """
    stats = report.get('stats', {})
    bugs = report.get('bugs_summary', [])
    
    # Categorize pipelines by health
    healthy_pipelines = []
    warning_pipelines = []
    critical_pipelines = []
    
    for analysis in analyses:
        pipeline_key = analysis.get('pipeline_key', 'UNKNOWN')
        summary = analysis.get('summary', '').lower()
        top_errors = analysis.get('top_errors', [])
        
        if 'excellent' in summary or 'good' in summary or len(top_errors) == 0:
            healthy_pipelines.append(pipeline_key)
        elif 'concerning' in summary or len(top_errors) <= 2:
            warning_pipelines.append(pipeline_key)
        else:
            critical_pipelines.append(pipeline_key)
    
    # Determine overall health
    total_pipelines = len(analyses)
    if len(critical_pipelines) == 0 and len(warning_pipelines) <= 1:
        overall_health = "excellent"
        health_emoji = "🟢"
    elif len(critical_pipelines) == 0:
        overall_health = "good"
        health_emoji = "🟡"
    elif len(critical_pipelines) <= 1:
        overall_health = "concerning"
        health_emoji = "🟠"
    else:
        overall_health = "critical"
        health_emoji = "🔴"
    
    return {
        "overall_health": overall_health,
        "health_emoji": health_emoji,
        "execution_time_seconds": round(execution_time, 2),
        "pipelines_analyzed": total_pipelines,
        "total_runs_analyzed": stats.get('runs_total', 0),
        "total_errors_found": stats.get('errors_total', 0),
        "critical_issues": len([bug for bug in bugs if bug.get('severity') == 'high']),
        "pipeline_health_breakdown": {
            "healthy": len(healthy_pipelines),
            "warning": len(warning_pipelines),
            "critical": len(critical_pipelines)
        },
        "pipeline_categories": {
            "healthy_pipelines": healthy_pipelines,
            "warning_pipelines": warning_pipelines,
            "critical_pipelines": critical_pipelines
        },
        "performance_metrics": {
            "avg_pipeline_duration_minutes": round(stats.get('avg_duration_seconds', 0) / 60, 1),
            "success_rate_percent": round(
                ((stats.get('completed_runs', 0) - stats.get('errors_total', 0)) / 
                 max(stats.get('completed_runs', 1), 1) * 100), 1
            )
        },
        "quick_summary": f"{health_emoji} {overall_health.title()} - {total_pipelines} pipelines, "
                        f"{stats.get('errors_total', 0)} errors, "
                        f"{len([bug for bug in bugs if bug.get('severity') == 'high'])} critical issues"
    }


def get_workflow_status() -> Dict[str, Any]:
    """
    Get current workflow system status and health check.
    
    Returns:
        Dict containing system status information
    """
    try:
        # Test each component quickly
        test_plans = get_bamboo_plans()
        test_logs = get_all_logs([{'key': 'PROJ-PLAN1'}])
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "bamboo_mock": "available" if test_plans else "unavailable",
                "logs_mock": "available" if test_logs else "unavailable",
                "analyzer_agent": "available",
                "reporting_agent": "available",
                "orchestrator": "available"
            },
            "version": "1.0",
            "ready": True
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0",
            "ready": False
        }


def run_quick_health_check() -> str:
    """
    Run a quick health check and return a simple status message.
    
    Returns:
        String status message suitable for monitoring
    """
    try:
        # Quick test of the workflow with minimal data
        result = run("Health check test")
        
        if result.get('workflow_info', {}).get('status') == 'success':
            stats = result.get('outputs', {}).get('report', {}).get('stats', {})
            return f"✅ Healthy - {stats.get('pipelines_total', 0)} pipelines analyzed successfully"
        else:
            return f"⚠️ Issues detected - {result.get('workflow_info', {}).get('error_message', 'Unknown error')}"
            
    except Exception as e:
        return f"🔴 System error - {str(e)}"