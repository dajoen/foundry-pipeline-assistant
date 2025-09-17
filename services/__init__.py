"""
Services module for the foundry-pipeline-assistant project.

Contains mock services and external API integrations.
"""

from .bamboo_mock import get_bamboo_plans, get_plan_results
from .logs_mock import get_pipeline_logs, get_all_logs, get_error_summary
from .analyzer_agent import analyze_pipeline_logs, analyze_multiple_pipelines, get_fleet_summary
from .reporting_agent import aggregate_and_report, generate_daily_summary
from .orchestrator import run, get_workflow_status, run_quick_health_check

__all__ = [
    "get_bamboo_plans",
    "get_plan_results",
    "get_pipeline_logs",
    "get_all_logs", 
    "get_error_summary",
    "analyze_pipeline_logs",
    "analyze_multiple_pipelines",
    "get_fleet_summary",
    "aggregate_and_report",
    "generate_daily_summary",
    "run",
    "get_workflow_status",
    "run_quick_health_check",
]