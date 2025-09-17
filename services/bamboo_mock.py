"""
Bamboo mock service for testing and development.

This module provides static mock data that mimics Bamboo CI/CD plan responses
for deterministic testing and development without requiring actual Bamboo server access.
"""

from typing import Dict, Any


def get_bamboo_plans() -> Dict[str, Any]:
    """
    Get static Bamboo-like JSON payload with 3 predefined plans.
    
    Returns deterministic mock data suitable for testing that mimics
    the structure of Bamboo's plan listing API response.
    
    Returns:
        Dict containing Bamboo-like plan data with exactly 3 plans:
        - PROJ-PLAN1: Enabled plan with successful build
        - PROJ-PLAN2: Disabled plan with failed build
        - PROJ-PLAN3: Enabled plan with in-progress build
    """
    return {
        "plans": {
            "size": 3,
            "start-index": 0,
            "max-result": 25,
            "plan": [
                {
                    "shortName": "PLAN1",
                    "shortKey": "PLAN1", 
                    "type": "chain",
                    "enabled": True,
                    "link": {
                        "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN1",
                        "rel": "self"
                    },
                    "key": "PROJ-PLAN1",
                    "name": "Project Alpha - Build and Deploy",
                    "planKey": {
                        "key": "PROJ-PLAN1"
                    },
                    "projectKey": "PROJ",
                    "projectName": "Project Alpha",
                    "description": "Main build and deployment pipeline for Project Alpha",
                    "isActive": True,
                    "isBuilding": False,
                    "averageBuildTimeInSeconds": 420,
                    "actions": {
                        "size": 2,
                        "start-index": 0,
                        "max-result": 2
                    },
                    "stages": {
                        "size": 3,
                        "start-index": 0,
                        "max-result": 3
                    },
                    "branches": {
                        "size": 1,
                        "start-index": 0,
                        "max-result": 25
                    },
                    "variableContext": {
                        "size": 5,
                        "start-index": 0,
                        "max-result": 25
                    }
                },
                {
                    "shortName": "PLAN2",
                    "shortKey": "PLAN2",
                    "type": "chain", 
                    "enabled": False,
                    "link": {
                        "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN2",
                        "rel": "self"
                    },
                    "key": "PROJ-PLAN2",
                    "name": "Project Beta - Testing Pipeline",
                    "planKey": {
                        "key": "PROJ-PLAN2"
                    },
                    "projectKey": "PROJ",
                    "projectName": "Project Beta",
                    "description": "Automated testing pipeline for Project Beta components",
                    "isActive": False,
                    "isBuilding": False,
                    "averageBuildTimeInSeconds": 180,
                    "actions": {
                        "size": 1,
                        "start-index": 0,
                        "max-result": 1
                    },
                    "stages": {
                        "size": 2,
                        "start-index": 0,
                        "max-result": 2
                    },
                    "branches": {
                        "size": 1,
                        "start-index": 0,
                        "max-result": 25
                    },
                    "variableContext": {
                        "size": 3,
                        "start-index": 0,
                        "max-result": 25
                    }
                },
                {
                    "shortName": "PLAN3",
                    "shortKey": "PLAN3",
                    "type": "chain",
                    "enabled": True,
                    "link": {
                        "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN3", 
                        "rel": "self"
                    },
                    "key": "PROJ-PLAN3",
                    "name": "Project Gamma - Integration Tests",
                    "planKey": {
                        "key": "PROJ-PLAN3"
                    },
                    "projectKey": "PROJ",
                    "projectName": "Project Gamma",
                    "description": "End-to-end integration testing for Project Gamma services",
                    "isActive": True,
                    "isBuilding": True,
                    "averageBuildTimeInSeconds": 840,
                    "actions": {
                        "size": 3,
                        "start-index": 0,
                        "max-result": 3
                    },
                    "stages": {
                        "size": 4,
                        "start-index": 0,
                        "max-result": 4
                    },
                    "branches": {
                        "size": 2,
                        "start-index": 0,
                        "max-result": 25
                    },
                    "variableContext": {
                        "size": 8,
                        "start-index": 0,
                        "max-result": 25
                    }
                }
            ]
        },
        "expand": "plans.plan",
        "link": {
            "href": "https://bamboo.company.com/rest/api/latest/plan",
            "rel": "self"
        }
    }


def get_plan_results(plan_key: str) -> Dict[str, Any]:
    """
    Get static Bamboo-like JSON payload for plan build results.
    
    Args:
        plan_key: The plan key (e.g., 'PROJ-PLAN1')
        
    Returns:
        Dict containing mock build results for the specified plan
    """
    # Static results based on plan key for deterministic testing
    results_data = {
        "PROJ-PLAN1": {
            "results": {
                "size": 1,
                "start-index": 0,
                "max-result": 25,
                "result": [
                    {
                        "expand": "changes,metadata,plan,vcs,artifacts,comments,labels,jiraIssues,stages",
                        "link": {
                            "href": "https://bamboo.company.com/rest/api/latest/result/PROJ-PLAN1-123",
                            "rel": "self"
                        },
                        "plan": {
                            "shortName": "PLAN1",
                            "shortKey": "PLAN1",
                            "type": "chain",
                            "enabled": True,
                            "link": {
                                "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN1",
                                "rel": "self"
                            },
                            "key": "PROJ-PLAN1",
                            "name": "Project Alpha - Build and Deploy"
                        },
                        "planName": "Project Alpha - Build and Deploy",
                        "projectName": "Project Alpha",
                        "buildResultKey": "PROJ-PLAN1-123",
                        "lifeCycleState": "Finished",
                        "id": 123,
                        "buildNumber": 123,
                        "state": "Successful",
                        "buildState": "Successful",
                        "number": 123,
                        "buildRelativeTime": "2 hours ago",
                        "buildTestSummary": "3 passed",
                        "successfulTestCount": 3,
                        "failedTestCount": 0,
                        "quarantinedTestCount": 0,
                        "skippedTestCount": 0,
                        "continuable": False,
                        "onceOff": False,
                        "restartable": False,
                        "notRunYet": False,
                        "finished": True,
                        "successful": True,
                        "buildReason": "Manual run by admin",
                        "reasonSummary": "Manual run by admin",
                        "buildDurationInSeconds": 385,
                        "buildDuration": 385000,
                        "buildDurationDescription": "6 minutes",
                        "buildRelativeTime": "2 hours ago",
                        "vcsRevisionKey": "abc123def456",
                        "buildTestSummary": "3 passed",
                        "key": "PROJ-PLAN1-123"
                    }
                ]
            }
        },
        "PROJ-PLAN2": {
            "results": {
                "size": 1, 
                "start-index": 0,
                "max-result": 25,
                "result": [
                    {
                        "expand": "changes,metadata,plan,vcs,artifacts,comments,labels,jiraIssues,stages",
                        "link": {
                            "href": "https://bamboo.company.com/rest/api/latest/result/PROJ-PLAN2-87",
                            "rel": "self"
                        },
                        "plan": {
                            "shortName": "PLAN2",
                            "shortKey": "PLAN2", 
                            "type": "chain",
                            "enabled": False,
                            "link": {
                                "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN2",
                                "rel": "self"
                            },
                            "key": "PROJ-PLAN2",
                            "name": "Project Beta - Testing Pipeline"
                        },
                        "planName": "Project Beta - Testing Pipeline",
                        "projectName": "Project Beta", 
                        "buildResultKey": "PROJ-PLAN2-87",
                        "lifeCycleState": "Finished",
                        "id": 87,
                        "buildNumber": 87,
                        "state": "Failed",
                        "buildState": "Failed",
                        "number": 87,
                        "buildRelativeTime": "1 day ago",
                        "buildTestSummary": "2 passed, 1 failed",
                        "successfulTestCount": 2,
                        "failedTestCount": 1,
                        "quarantinedTestCount": 0,
                        "skippedTestCount": 0,
                        "continuable": False,
                        "onceOff": False,
                        "restartable": True,
                        "notRunYet": False,
                        "finished": True,
                        "successful": False,
                        "buildReason": "Code has been updated by developer",
                        "reasonSummary": "Code has been updated by developer",
                        "buildDurationInSeconds": 145,
                        "buildDuration": 145000,
                        "buildDurationDescription": "2 minutes",
                        "buildRelativeTime": "1 day ago",
                        "vcsRevisionKey": "def456ghi789",
                        "buildTestSummary": "2 passed, 1 failed",
                        "key": "PROJ-PLAN2-87"
                    }
                ]
            }
        },
        "PROJ-PLAN3": {
            "results": {
                "size": 1,
                "start-index": 0,
                "max-result": 25,
                "result": [
                    {
                        "expand": "changes,metadata,plan,vcs,artifacts,comments,labels,jiraIssues,stages",
                        "link": {
                            "href": "https://bamboo.company.com/rest/api/latest/result/PROJ-PLAN3-201",
                            "rel": "self"
                        },
                        "plan": {
                            "shortName": "PLAN3",
                            "shortKey": "PLAN3",
                            "type": "chain", 
                            "enabled": True,
                            "link": {
                                "href": "https://bamboo.company.com/rest/api/latest/plan/PROJ-PLAN3",
                                "rel": "self"
                            },
                            "key": "PROJ-PLAN3",
                            "name": "Project Gamma - Integration Tests"
                        },
                        "planName": "Project Gamma - Integration Tests",
                        "projectName": "Project Gamma",
                        "buildResultKey": "PROJ-PLAN3-201",
                        "lifeCycleState": "InProgress",
                        "id": 201,
                        "buildNumber": 201,
                        "state": "Unknown",
                        "buildState": "Unknown",
                        "number": 201,
                        "buildRelativeTime": "5 minutes ago",
                        "buildTestSummary": "Running...",
                        "successfulTestCount": 0,
                        "failedTestCount": 0,
                        "quarantinedTestCount": 0,
                        "skippedTestCount": 0,
                        "continuable": False,
                        "onceOff": False,
                        "restartable": False,
                        "notRunYet": False,
                        "finished": False,
                        "successful": False,
                        "buildReason": "Scheduled trigger",
                        "reasonSummary": "Scheduled trigger",
                        "buildDurationInSeconds": 0,
                        "buildDuration": 0,
                        "buildDurationDescription": "Currently running",
                        "buildRelativeTime": "5 minutes ago",
                        "vcsRevisionKey": "ghi789jkl012",
                        "buildTestSummary": "Running...",
                        "key": "PROJ-PLAN3-201"
                    }
                ]
            }
        }
    }
    
    return results_data.get(plan_key, {"results": {"size": 0, "result": []}})