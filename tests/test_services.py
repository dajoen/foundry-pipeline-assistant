"""
Tests for bamboo_mock normalization and logs_mock services.

Tests the deterministic mock data generation and normalization functions
to ensure consistent test data and proper data structure transformations.
"""

import pytest
from typing import Dict, List, Any

from services.bamboo_mock import get_bamboo_plans, get_plan_results
from services.logs_mock import get_pipeline_logs, get_all_logs, get_error_summary
from services.orchestrator import _normalize_bamboo_plans


class TestBambooMockNormalization:
    """Test bamboo mock data and normalization functions."""
    
    def test_get_bamboo_plans_structure(self):
        """Test that bamboo plans have expected structure."""
        plans = get_bamboo_plans()
        
        # Check top-level structure
        assert 'plans' in plans
        assert 'plan' in plans['plans']
        assert plans['plans']['size'] == 3
        assert len(plans['plans']['plan']) == 3
        
        # Check individual plan structure
        for plan in plans['plans']['plan']:
            assert 'key' in plan
            assert 'name' in plan
            assert 'enabled' in plan
            assert 'link' in plan
            assert isinstance(plan['enabled'], bool)
    
    def test_normalize_bamboo_plans_deterministic_ordering(self):
        """Test that normalization produces consistent ordering."""
        raw_data = get_bamboo_plans()
        normalized1 = _normalize_bamboo_plans(raw_data)
        normalized2 = _normalize_bamboo_plans(raw_data)
        
        # Should have same order both times
        keys1 = [plan['key'] for plan in normalized1]
        keys2 = [plan['key'] for plan in normalized2]
        assert keys1 == keys2
        
        # Should be sorted by key
        assert keys1 == sorted(keys1)
        
        # Should have exactly the expected keys
        expected_keys = ['PROJ-PLAN1', 'PROJ-PLAN2', 'PROJ-PLAN3']
        assert keys1 == expected_keys
    
    def test_normalize_bamboo_plans_structure(self):
        """Test that normalized plans have expected structure."""
        raw_data = get_bamboo_plans()
        normalized = _normalize_bamboo_plans(raw_data)
        
        assert len(normalized) == 3
        
        for plan in normalized:
            # Check required fields
            required_fields = ['key', 'name', 'enabled', 'shortName', 'projectKey']
            for field in required_fields:
                assert field in plan, f"Missing field {field} in normalized plan"
            
            # Check data types
            assert isinstance(plan['enabled'], bool)
            assert isinstance(plan['isActive'], bool)
            assert isinstance(plan['isBuilding'], bool)
            assert isinstance(plan['averageBuildTimeInSeconds'], int)
            
            # Check original data is preserved
            assert '_original' in plan
            assert isinstance(plan['_original'], dict)
    
    def test_normalize_bamboo_plans_specific_content(self):
        """Test specific content of normalized plans."""
        raw_data = get_bamboo_plans()
        normalized = _normalize_bamboo_plans(raw_data)
        
        # Find specific plans
        plan1 = next(p for p in normalized if p['key'] == 'PROJ-PLAN1')
        plan2 = next(p for p in normalized if p['key'] == 'PROJ-PLAN2')
        plan3 = next(p for p in normalized if p['key'] == 'PROJ-PLAN3')
        
        # Check specific attributes
        assert plan1['enabled'] is True
        assert plan1['name'] == "Project Alpha - Build and Deploy"
        
        assert plan2['enabled'] is False
        assert plan2['name'] == "Project Beta - Testing Pipeline"
        
        assert plan3['enabled'] is True
        assert plan3['name'] == "Project Gamma - Integration Tests"
        assert plan3['isBuilding'] is True


class TestLogsMockService:
    """Test logs mock service functions."""
    
    def test_get_pipeline_logs_deterministic(self):
        """Test that pipeline logs are deterministic."""
        logs1 = get_pipeline_logs("PROJ-PLAN1")
        logs2 = get_pipeline_logs("PROJ-PLAN1")
        
        # Should be identical
        assert logs1 == logs2
        assert logs1['pipeline_key'] == "PROJ-PLAN1"
        assert logs1['total_runs'] == 3
    
    def test_get_pipeline_logs_structure(self):
        """Test pipeline logs have expected structure."""
        logs = get_pipeline_logs("PROJ-PLAN1")
        
        # Check top-level structure
        required_fields = ['pipeline_key', 'pipeline_name', 'total_runs', 'runs']
        for field in required_fields:
            assert field in logs
        
        # Check runs structure
        assert isinstance(logs['runs'], list)
        assert len(logs['runs']) == logs['total_runs']
        
        for run in logs['runs']:
            run_fields = ['run_id', 'build_number', 'status', 'duration_seconds', 'errors']
            for field in run_fields:
                assert field in run
            
            # Check data types
            assert isinstance(run['duration_seconds'], int)
            assert isinstance(run['errors'], list)
            assert run['status'] in ['SUCCESS', 'FAILED', 'IN_PROGRESS']
    
    def test_get_pipeline_logs_errors_structure(self):
        """Test that error structures are correct."""
        # Get logs with errors
        logs = get_pipeline_logs("PROJ-PLAN2")
        
        # Find run with errors
        failed_run = next(run for run in logs['runs'] if run['status'] == 'FAILED')
        assert len(failed_run['errors']) > 0
        
        for error in failed_run['errors']:
            assert isinstance(error, dict)
            assert 'step' in error
            assert 'message' in error
            assert isinstance(error['step'], str)
            assert isinstance(error['message'], str)
    
    def test_get_all_logs_with_plans(self):
        """Test getting logs for multiple plans."""
        # Create test plans
        plans = [
            {'key': 'PROJ-PLAN1'},
            {'key': 'PROJ-PLAN2'},
            {'key': 'PROJ-PLAN3'}
        ]
        
        all_logs = get_all_logs(plans)
        
        # Should get logs for all plans
        assert len(all_logs) == 3
        
        # Check ordering matches input
        expected_keys = ['PROJ-PLAN1', 'PROJ-PLAN2', 'PROJ-PLAN3']
        actual_keys = [logs['pipeline_key'] for logs in all_logs]
        assert actual_keys == expected_keys
        
        # Each should have proper structure
        for logs in all_logs:
            assert 'pipeline_key' in logs
            assert 'runs' in logs
            assert isinstance(logs['runs'], list)
    
    def test_get_all_logs_key_variants(self):
        """Test that get_all_logs handles different key field names."""
        test_cases = [
            [{'key': 'PROJ-PLAN1'}],
            [{'planKey': {'key': 'PROJ-PLAN1'}}],
            [{'pipeline_key': 'PROJ-PLAN1'}],
            [{'id': 'PROJ-PLAN1'}]
        ]
        
        for plans in test_cases:
            all_logs = get_all_logs(plans)
            assert len(all_logs) == 1
            assert all_logs[0]['pipeline_key'] == 'PROJ-PLAN1'
    
    def test_get_error_summary_statistics(self):
        """Test error summary calculation."""
        # Get logs with known errors
        logs = get_pipeline_logs("PROJ-PLAN2")
        error_summary = get_error_summary(logs)
        
        # Check structure
        required_fields = [
            'pipeline_key', 'total_runs', 'failed_runs', 
            'success_rate', 'total_errors', 'error_details'
        ]
        for field in required_fields:
            assert field in error_summary
        
        # Check calculations
        assert error_summary['pipeline_key'] == 'PROJ-PLAN2'
        assert error_summary['total_runs'] == 2
        assert error_summary['failed_runs'] == 1  # One failed run in PROJ-PLAN2
        assert error_summary['success_rate'] == 50.0  # 1 success out of 2 runs
        assert error_summary['total_errors'] > 0
        assert isinstance(error_summary['error_details'], list)
    
    def test_get_error_summary_no_errors(self):
        """Test error summary for pipeline with no errors."""
        # PROJ-PLAN1 should have no errors
        logs = get_pipeline_logs("PROJ-PLAN1")
        error_summary = get_error_summary(logs)
        
        assert error_summary['failed_runs'] == 0
        assert error_summary['success_rate'] == 100.0
        assert error_summary['total_errors'] == 0
        assert error_summary['error_details'] == []
    
    def test_pipeline_specific_content(self):
        """Test specific content for each pipeline."""
        # PROJ-PLAN1 should be all success
        logs1 = get_pipeline_logs("PROJ-PLAN1")
        assert all(run['status'] == 'SUCCESS' for run in logs1['runs'])
        assert all(len(run['errors']) == 0 for run in logs1['runs'])
        
        # PROJ-PLAN2 should have at least one failure
        logs2 = get_pipeline_logs("PROJ-PLAN2")
        assert any(run['status'] == 'FAILED' for run in logs2['runs'])
        assert any(len(run['errors']) > 0 for run in logs2['runs'])
        
        # PROJ-PLAN3 should have mixed states including in-progress
        logs3 = get_pipeline_logs("PROJ-PLAN3")
        statuses = [run['status'] for run in logs3['runs']]
        assert 'IN_PROGRESS' in statuses
        assert any(len(run['errors']) > 0 for run in logs3['runs'])
    
    def test_unknown_pipeline_handling(self):
        """Test handling of unknown pipeline keys."""
        logs = get_pipeline_logs("UNKNOWN-PLAN")
        
        assert logs['pipeline_key'] == "UNKNOWN-PLAN"
        assert logs['total_runs'] == 0
        assert logs['runs'] == []
        assert "Unknown Pipeline" in logs['pipeline_name']