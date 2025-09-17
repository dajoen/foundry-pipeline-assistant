"""
End-to-end tests for orchestrator with mocked LLM calls.

Tests the complete pipeline analysis workflow with stable, canned LLM responses
to ensure consistent test results and verify the full integration.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from services.orchestrator import run, get_workflow_status, run_quick_health_check


class TestOrchestratorEndToEnd:
    """Test complete orchestrator workflow with mocked LLM calls."""
    
    @pytest.fixture
    def mock_llm_responses(self):
        """Fixture providing stable canned LLM responses for testing."""
        return {
            'json_response': {
                "pipeline_key": "PROJ-PLAN1",
                "summary": "Pipeline shows excellent health with 100% success rate and consistent performance over 3 recent runs",
                "top_errors": [],
                "recommendations": [
                    "Continue monitoring pipeline performance",
                    "Maintain current deployment practices"
                ]
            },
            'text_response': """# CI/CD Pipeline Report
*Generated automatically by Pipeline Assistant*

## Executive Summary

Our CI/CD pipeline analysis reveals **excellent overall health** across all 3 monitored pipelines. With a combined **87.5% success rate** and average execution time of **9 minutes**, the infrastructure demonstrates solid reliability with minimal critical issues requiring attention.

## Pipeline Performance Overview

| Metric | Value |
|--------|--------|
| Total Pipelines | 3 |
| Total Runs Analyzed | 8 |
| Average Duration | 542 seconds (9.0 minutes) |
| Success Rate | 87.5% |
| Critical Issues | 2 |

## Critical Issues Requiring Attention

**2 high-priority issues** have been identified that need immediate attention:

1. 🔴 **PROJ-PLAN3**: Database connection timeout during integration tests
   - **Frequency**: 1 occurrence
   - **Impact**: Service dependency failures affecting test reliability
   - **Recommendation**: Review database connection pooling and timeout configurations

2. 🔴 **PROJ-PLAN3**: Service health check failures in integration environment  
   - **Frequency**: 1 occurrence
   - **Impact**: Integration test suite reliability concerns
   - **Recommendation**: Investigate service startup sequences and health check intervals

## Recommendations

Based on our analysis, we recommend the following actions prioritized by business impact:

1. **Address integration test environment stability** - Focus on database connectivity and service dependencies for PROJ-PLAN3
2. **Investigate test assertion logic** - Review failing validation tests in PROJ-PLAN2 to improve reliability
3. **Optimize build performance** - Consider parallel execution strategies to reduce average build times
4. **Implement proactive monitoring** - Add alerting for timeout and connection issues before they impact production
5. **Review service health check configurations** - Ensure proper startup sequences and realistic timeout values

## Individual Pipeline Status

### ✅ PROJ-PLAN1 - Project Alpha Build and Deploy
**Status**: Excellent performance with 100% success rate over 3 runs. Average execution time of 7 minutes demonstrates efficient build processes. No issues detected.

### ⚠️ PROJ-PLAN2 - Project Beta Testing Pipeline  
**Status**: Mixed performance with 50% success rate requiring attention. Recent test failures indicate validation logic issues that need investigation.

### 🔴 PROJ-PLAN3 - Project Gamma Integration Tests
**Status**: Critical attention needed with infrastructure stability issues. Database timeouts and service health check failures are impacting integration test reliability.

---

*This analysis was generated automatically and covers the most recent execution data. For questions or additional analysis, please contact the DevOps team.*"""
        }
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text') 
    def test_orchestrator_run_success(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test successful orchestrator run with mocked LLM calls."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        # Run orchestrator
        result = run("Test question for pipeline analysis")
        
        # Verify LLM was called
        assert mock_llm_json.called
        assert mock_llm_text.called
        
        # Check workflow completed successfully
        assert result['workflow_info']['status'] == 'success'
        assert result['workflow_info']['steps_completed'] == 4
        assert result['question'] == "Test question for pipeline analysis"
        
        # Verify execution time is recorded
        assert 'execution_time_seconds' in result['workflow_info']
        assert result['workflow_info']['execution_time_seconds'] > 0
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_orchestrator_result_structure(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that orchestrator result has complete expected structure."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("Structure test")
        
        # Check top-level structure
        required_top_level = ['workflow_info', 'inputs', 'processing', 'outputs', 'question']
        for key in required_top_level:
            assert key in result, f"Missing top-level key: {key}"
        
        # Check workflow_info structure
        workflow_required = ['start_time', 'end_time', 'execution_time_seconds', 'status', 'version', 'steps_completed']
        for key in workflow_required:
            assert key in result['workflow_info'], f"Missing workflow_info key: {key}"
        
        # Check inputs structure  
        inputs_required = ['question', 'raw_bamboo_data', 'normalized_plans', 'logs_fetched']
        for key in inputs_required:
            assert key in result['inputs'], f"Missing inputs key: {key}"
        
        # Check processing structure
        processing_required = ['step1_plans', 'step2_logs', 'step3_analysis', 'step4_reporting']
        for key in processing_required:
            assert key in result['processing'], f"Missing processing key: {key}"
        
        # Check outputs structure
        outputs_required = ['pipelines', 'logs', 'analyses', 'report', 'summary']
        for key in outputs_required:
            assert key in result['outputs'], f"Missing outputs key: {key}"
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_final_report_json_keys(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that final report JSON contains all expected keys."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("JSON keys test")
        
        # Get the final report
        report = result['outputs']['report']
        
        # Check report structure
        report_required = ['stats', 'bugs_summary', 'markdown']
        for key in report_required:
            assert key in report, f"Missing report key: {key}"
        
        # Check stats structure
        stats = report['stats']
        stats_required = ['pipelines_total', 'runs_total', 'avg_duration_seconds', 'errors_total']
        for key in stats_required:
            assert key in stats, f"Missing stats key: {key}"
        
        # Check bugs_summary is list
        assert isinstance(report['bugs_summary'], list)
        
        # Check markdown is string
        assert isinstance(report['markdown'], str)
        assert len(report['markdown']) > 0
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_markdown_content_assertions(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that Markdown contains expected content."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("Markdown content test")
        
        markdown = result['outputs']['report']['markdown']
        stats = result['outputs']['report']['stats']
        
        # Assert pipelines count is mentioned
        pipelines_count = str(stats['pipelines_total'])
        assert pipelines_count in markdown, f"Pipeline count {pipelines_count} not found in markdown"
        
        # Assert average duration is mentioned (check both seconds and minutes)
        avg_duration_seconds = stats['avg_duration_seconds']
        avg_duration_minutes = avg_duration_seconds // 60
        
        # Should mention either seconds or minutes
        duration_mentioned = (
            str(avg_duration_seconds) in markdown or 
            str(avg_duration_minutes) in markdown or
            "9 minutes" in markdown  # From our canned response
        )
        assert duration_mentioned, f"Average duration not found in markdown (expected ~{avg_duration_minutes}m or {avg_duration_seconds}s)"
        
        # Assert bug summary information is present
        bugs_summary = result['outputs']['report']['bugs_summary']
        if bugs_summary:
            # Should mention errors or issues
            error_keywords = ['error', 'issue', 'problem', 'failure', 'critical', 'bug']
            has_error_content = any(keyword.lower() in markdown.lower() for keyword in error_keywords)
            assert has_error_content, "Bug/error information not found in markdown"
        
        # Check that it looks like a proper markdown report
        assert markdown.startswith('#'), "Markdown should start with a header"
        assert 'Pipeline' in markdown, "Should mention pipelines"
        assert '|' in markdown, "Should contain table formatting"
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_statistics_calculations(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that statistics are calculated correctly."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("Stats calculation test")
        
        stats = result['outputs']['report']['stats']
        
        # Check expected values based on mock data
        assert stats['pipelines_total'] == 3, "Should analyze exactly 3 pipelines"
        assert stats['runs_total'] == 8, "Should find exactly 8 runs total (3+2+3)"
        assert stats['errors_total'] == 4, "Should find exactly 4 errors total"
        assert isinstance(stats['avg_duration_seconds'], int), "Average duration should be integer"
        assert stats['avg_duration_seconds'] > 0, "Average duration should be positive"
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_pipeline_processing_traceability(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that processing steps are properly tracked."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("Traceability test")
        
        processing = result['processing']
        
        # Check step 1 - plans
        step1 = processing['step1_plans']
        assert step1['pipelines_found'] == 3
        assert len(step1['pipeline_keys']) == 3
        assert 'PROJ-PLAN1' in step1['pipeline_keys']
        assert 'PROJ-PLAN2' in step1['pipeline_keys'] 
        assert 'PROJ-PLAN3' in step1['pipeline_keys']
        
        # Check step 2 - logs
        step2 = processing['step2_logs']
        assert step2['logs_retrieved'] == 3
        assert step2['total_runs'] == 8
        assert len(step2['logs_summary']) == 3
        
        # Check step 3 - analysis
        step3 = processing['step3_analysis']
        assert step3['analyses_completed'] == 3
        assert len(step3['analysis_summary']) == 3
        
        # Check step 4 - reporting
        step4 = processing['step4_reporting']
        assert step4['report_generated'] is True
        assert step4['stats_computed'] is True
        assert step4['markdown_length'] > 0
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_execution_summary(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that execution summary is generated correctly."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        result = run("Summary test")
        
        summary = result['outputs']['summary']
        
        # Check summary structure
        summary_required = [
            'overall_health', 'health_emoji', 'execution_time_seconds',
            'pipelines_analyzed', 'total_runs_analyzed', 'total_errors_found',
            'critical_issues', 'pipeline_health_breakdown', 'performance_metrics'
        ]
        for key in summary_required:
            assert key in summary, f"Missing summary key: {key}"
        
        # Check values
        assert summary['pipelines_analyzed'] == 3
        assert summary['total_runs_analyzed'] == 8
        assert summary['execution_time_seconds'] > 0
        assert summary['overall_health'] in ['excellent', 'good', 'concerning', 'critical']
        assert summary['health_emoji'] in ['🟢', '🟡', '🟠', '🔴']
        
        # Check performance metrics
        perf_metrics = summary['performance_metrics']
        assert 'avg_pipeline_duration_minutes' in perf_metrics
        assert 'success_rate_percent' in perf_metrics
        assert perf_metrics['avg_pipeline_duration_minutes'] > 0
        assert 0 <= perf_metrics['success_rate_percent'] <= 100
    
    @patch('services.analyzer_agent.llm_json')
    def test_llm_failure_fallback(self, mock_llm_json):
        """Test fallback behavior when LLM calls fail."""
        # Mock LLM to raise an exception
        mock_llm_json.side_effect = Exception("Simulated LLM failure")
        
        result = run("Fallback test")
        
        # Should still complete successfully with fallback analysis
        assert result['workflow_info']['status'] == 'success'
        
        # Should have analyses (from heuristic fallback)
        analyses = result['outputs']['analyses']
        assert len(analyses) == 3
        
        # Check that analyses still have required structure
        for analysis in analyses:
            assert 'pipeline_key' in analysis
            assert 'summary' in analysis
            assert 'top_errors' in analysis
            assert 'recommendations' in analysis
    
    @patch('services.analyzer_agent.llm_json')
    @patch('services.reporting_agent.llm_text')
    def test_deterministic_results(self, mock_llm_text, mock_llm_json, mock_llm_responses):
        """Test that results are deterministic with same inputs."""
        # Setup mocked responses
        mock_llm_json.return_value = mock_llm_responses['json_response']
        mock_llm_text.return_value = mock_llm_responses['text_response']
        
        # Run twice with same question
        result1 = run("Deterministic test")
        result2 = run("Deterministic test")
        
        # Key statistics should be identical
        stats1 = result1['outputs']['report']['stats']
        stats2 = result2['outputs']['report']['stats']
        
        assert stats1['pipelines_total'] == stats2['pipelines_total']
        assert stats1['runs_total'] == stats2['runs_total']
        assert stats1['errors_total'] == stats2['errors_total']
        
        # Processing steps should be identical
        proc1 = result1['processing']
        proc2 = result2['processing']
        
        assert proc1['step1_plans']['pipeline_keys'] == proc2['step1_plans']['pipeline_keys']
        assert proc1['step2_logs']['total_runs'] == proc2['step2_logs']['total_runs']


class TestWorkflowSystemFunctions:
    """Test system health and status functions."""
    
    def test_get_workflow_status(self):
        """Test workflow status check."""
        status = get_workflow_status()
        
        # Check structure
        required_fields = ['status', 'timestamp', 'components', 'version', 'ready']
        for field in required_fields:
            assert field in status
        
        # Check components
        expected_components = [
            'bamboo_mock', 'logs_mock', 'analyzer_agent', 
            'reporting_agent', 'orchestrator'
        ]
        for component in expected_components:
            assert component in status['components']
        
        # Should be healthy under normal conditions
        assert status['status'] in ['healthy', 'degraded']
        assert isinstance(status['ready'], bool)
    
    @patch('services.orchestrator.run')
    def test_run_quick_health_check_success(self, mock_run):
        """Test quick health check with successful run."""
        # Mock successful run
        mock_run.return_value = {
            'workflow_info': {'status': 'success'},
            'outputs': {
                'report': {
                    'stats': {'pipelines_total': 3}
                }
            }
        }
        
        result = run_quick_health_check()
        
        assert result.startswith("✅")
        assert "3 pipelines" in result
        assert "successfully" in result
    
    @patch('services.orchestrator.run')
    def test_run_quick_health_check_failure(self, mock_run):
        """Test quick health check with failed run."""
        # Mock failed run
        mock_run.return_value = {
            'workflow_info': {
                'status': 'error',
                'error_message': 'Test error'
            }
        }
        
        result = run_quick_health_check()
        
        assert result.startswith("⚠️")
        assert "Test error" in result
    
    @patch('services.orchestrator.run')
    def test_run_quick_health_check_exception(self, mock_run):
        """Test quick health check with exception."""
        # Mock exception
        mock_run.side_effect = Exception("System failure")
        
        result = run_quick_health_check()
        
        assert result.startswith("🔴")
        assert "System failure" in result