"""
Pipeline logs mock service for testing and development.

This module provides static mock data that mimics pipeline execution logs
with deterministic content including run durations, error information, and
execution details for reliable testing.
"""

from typing import Dict, List, Any


def get_pipeline_logs(pipeline_key: str) -> Dict[str, Any]:
    """
    Get static pipeline logs for a specific pipeline key.
    
    Returns deterministic mock log data with multiple runs per pipeline,
    including duration information and error details where applicable.
    
    Args:
        pipeline_key: The pipeline key (e.g., 'PROJ-PLAN1')
        
    Returns:
        Dict containing pipeline log data with runs, durations, and errors
    """
    # Static log data based on pipeline key for deterministic testing
    logs_data = {
        "PROJ-PLAN1": {
            "pipeline_key": "PROJ-PLAN1",
            "pipeline_name": "Project Alpha - Build and Deploy",
            "total_runs": 3,
            "runs": [
                {
                    "run_id": "run-001",
                    "build_number": 123,
                    "status": "SUCCESS",
                    "started_at": "2025-09-17T10:15:30Z",
                    "completed_at": "2025-09-17T10:21:55Z",
                    "duration_seconds": 385,
                    "triggered_by": "admin",
                    "branch": "main",
                    "commit_hash": "abc123def456",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 15,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS", 
                            "duration_seconds": 240,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "test",
                            "status": "SUCCESS",
                            "duration_seconds": 85,
                            "output": "All 3 tests passed"
                        },
                        {
                            "step": "deploy",
                            "status": "SUCCESS",
                            "duration_seconds": 45,
                            "output": "Deployment to staging completed"
                        }
                    ]
                },
                {
                    "run_id": "run-002",
                    "build_number": 122,
                    "status": "SUCCESS",
                    "started_at": "2025-09-17T09:30:12Z",
                    "completed_at": "2025-09-17T09:37:48Z",
                    "duration_seconds": 456,
                    "triggered_by": "developer",
                    "branch": "main",
                    "commit_hash": "xyz789abc123",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 18,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 285,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "test",
                            "status": "SUCCESS",
                            "duration_seconds": 98,
                            "output": "All 3 tests passed"
                        },
                        {
                            "step": "deploy",
                            "status": "SUCCESS",
                            "duration_seconds": 55,
                            "output": "Deployment to staging completed"
                        }
                    ]
                },
                {
                    "run_id": "run-003",
                    "build_number": 121,
                    "status": "SUCCESS",
                    "started_at": "2025-09-16T16:45:20Z",
                    "completed_at": "2025-09-16T16:52:35Z",
                    "duration_seconds": 435,
                    "triggered_by": "scheduler",
                    "branch": "main",
                    "commit_hash": "def456ghi789",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 12,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 265,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "test",
                            "status": "SUCCESS",
                            "duration_seconds": 105,
                            "output": "All 3 tests passed"
                        },
                        {
                            "step": "deploy",
                            "status": "SUCCESS",
                            "duration_seconds": 53,
                            "output": "Deployment to staging completed"
                        }
                    ]
                }
            ]
        },
        "PROJ-PLAN2": {
            "pipeline_key": "PROJ-PLAN2",
            "pipeline_name": "Project Beta - Testing Pipeline",
            "total_runs": 2,
            "runs": [
                {
                    "run_id": "run-087",
                    "build_number": 87,
                    "status": "FAILED",
                    "started_at": "2025-09-16T14:20:15Z",
                    "completed_at": "2025-09-16T14:22:40Z",
                    "duration_seconds": 145,
                    "triggered_by": "developer",
                    "branch": "feature/new-tests",
                    "commit_hash": "def456ghi789",
                    "errors": [
                        {
                            "step": "test",
                            "message": "Test 'test_user_validation' failed: AssertionError: Expected 'valid' but got 'invalid'"
                        },
                        {
                            "step": "test",
                            "message": "1 out of 3 tests failed"
                        }
                    ],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 10,
                            "output": "Successfully checked out feature/new-tests branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 95,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "test",
                            "status": "FAILED",
                            "duration_seconds": 40,
                            "output": "Test execution failed: 2 passed, 1 failed"
                        }
                    ]
                },
                {
                    "run_id": "run-086",
                    "build_number": 86,
                    "status": "SUCCESS",
                    "started_at": "2025-09-16T13:15:45Z",
                    "completed_at": "2025-09-16T13:18:50Z",
                    "duration_seconds": 185,
                    "triggered_by": "developer",
                    "branch": "main",
                    "commit_hash": "ghi789jkl012",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 8,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 120,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "test",
                            "status": "SUCCESS",
                            "duration_seconds": 57,
                            "output": "All 3 tests passed"
                        }
                    ]
                }
            ]
        },
        "PROJ-PLAN3": {
            "pipeline_key": "PROJ-PLAN3",
            "pipeline_name": "Project Gamma - Integration Tests",
            "total_runs": 3,
            "runs": [
                {
                    "run_id": "run-201",
                    "build_number": 201,
                    "status": "IN_PROGRESS",
                    "started_at": "2025-09-17T11:45:30Z",
                    "completed_at": None,
                    "duration_seconds": 0,
                    "triggered_by": "scheduler",
                    "branch": "main",
                    "commit_hash": "ghi789jkl012",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 15,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "IN_PROGRESS",
                            "duration_seconds": 0,
                            "output": "Build in progress..."
                        }
                    ]
                },
                {
                    "run_id": "run-200",
                    "build_number": 200,
                    "status": "FAILED",
                    "started_at": "2025-09-17T08:30:20Z",
                    "completed_at": "2025-09-17T08:44:15Z",
                    "duration_seconds": 835,
                    "triggered_by": "developer",
                    "branch": "develop",
                    "commit_hash": "jkl012mno345",
                    "errors": [
                        {
                            "step": "integration-test",
                            "message": "Database connection timeout: Unable to connect to test database after 30 seconds"
                        },
                        {
                            "step": "integration-test",
                            "message": "Service 'user-service' failed health check: HTTP 503 Service Unavailable"
                        },
                        {
                            "step": "integration-test",
                            "message": "Integration test suite failed: 5 out of 12 tests failed due to service dependencies"
                        }
                    ],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 12,
                            "output": "Successfully checked out develop branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 320,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "unit-test",
                            "status": "SUCCESS",
                            "duration_seconds": 180,
                            "output": "All 25 unit tests passed"
                        },
                        {
                            "step": "integration-test",
                            "status": "FAILED",
                            "duration_seconds": 323,
                            "output": "Integration tests failed: 7 passed, 5 failed"
                        }
                    ]
                },
                {
                    "run_id": "run-199",
                    "build_number": 199,
                    "status": "SUCCESS",
                    "started_at": "2025-09-16T20:15:10Z",
                    "completed_at": "2025-09-16T20:29:25Z",
                    "duration_seconds": 855,
                    "triggered_by": "scheduler",
                    "branch": "main",
                    "commit_hash": "mno345pqr678",
                    "errors": [],
                    "steps": [
                        {
                            "step": "checkout",
                            "status": "SUCCESS",
                            "duration_seconds": 10,
                            "output": "Successfully checked out main branch"
                        },
                        {
                            "step": "build",
                            "status": "SUCCESS",
                            "duration_seconds": 345,
                            "output": "Build completed successfully"
                        },
                        {
                            "step": "unit-test",
                            "status": "SUCCESS",
                            "duration_seconds": 195,
                            "output": "All 25 unit tests passed"
                        },
                        {
                            "step": "integration-test",
                            "status": "SUCCESS",
                            "duration_seconds": 305,
                            "output": "All 12 integration tests passed"
                        }
                    ]
                }
            ]
        }
    }
    
    # Return empty structure if pipeline not found
    if pipeline_key not in logs_data:
        return {
            "pipeline_key": pipeline_key,
            "pipeline_name": f"Unknown Pipeline ({pipeline_key})",
            "total_runs": 0,
            "runs": []
        }
    
    return logs_data[pipeline_key]


def get_all_logs(pipelines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get logs for multiple pipelines by mapping each pipeline to its log data.
    
    Helper function that takes a list of pipeline objects and returns
    the corresponding log data for each pipeline.
    
    Args:
        pipelines: List of pipeline dictionaries, each containing at least a 'key' field
        
    Returns:
        List of pipeline log dictionaries in the same order as input pipelines
        
    Example:
        >>> plans = [{'key': 'PROJ-PLAN1'}, {'key': 'PROJ-PLAN2'}]
        >>> logs = get_all_logs(plans)
        >>> len(logs)
        2
    """
    logs = []
    
    for pipeline in pipelines:
        # Extract pipeline key from various possible field names
        pipeline_key = None
        for key_field in ['key', 'planKey', 'pipeline_key', 'id']:
            if key_field in pipeline:
                if isinstance(pipeline[key_field], dict):
                    # Handle nested key structures like planKey: {key: "PROJ-PLAN1"}
                    pipeline_key = pipeline[key_field].get('key')
                else:
                    pipeline_key = pipeline[key_field]
                break
        
        if pipeline_key:
            logs.append(get_pipeline_logs(pipeline_key))
        else:
            # If no valid key found, create empty log entry
            logs.append({
                "pipeline_key": "UNKNOWN",
                "pipeline_name": "Unknown Pipeline",
                "total_runs": 0,
                "runs": [],
                "error": "No valid pipeline key found in pipeline data"
            })
    
    return logs


def get_error_summary(pipeline_logs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract error summary from pipeline logs.
    
    Args:
        pipeline_logs: Pipeline log data from get_pipeline_logs()
        
    Returns:
        Dict containing error statistics and details
    """
    total_runs = len(pipeline_logs.get('runs', []))
    failed_runs = 0
    total_errors = 0
    error_details = []
    
    for run in pipeline_logs.get('runs', []):
        if run.get('status') == 'FAILED':
            failed_runs += 1
            run_errors = run.get('errors', [])
            total_errors += len(run_errors)
            
            for error in run_errors:
                error_details.append({
                    'run_id': run.get('run_id'),
                    'build_number': run.get('build_number'),
                    'step': error.get('step'),
                    'message': error.get('message'),
                    'timestamp': run.get('started_at')
                })
    
    return {
        'pipeline_key': pipeline_logs.get('pipeline_key'),
        'pipeline_name': pipeline_logs.get('pipeline_name'),
        'total_runs': total_runs,
        'failed_runs': failed_runs,
        'success_rate': round((total_runs - failed_runs) / total_runs * 100, 1) if total_runs > 0 else 0.0,
        'total_errors': total_errors,
        'error_details': error_details
    }