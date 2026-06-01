"""
Integration tests for initial Phase 2 MVP workflow.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from intake.processor import create_sample_intake
from recommendation.mvp_workflow import Phase2MVPWorkflow
from shared.schemas import ConfidenceLevel


class TestPhase2MVPWorkflow:
    """Validate intake -> retrieval -> report orchestration for Phase 2 kickoff."""

    def test_generates_standardized_report(self):
        workflow = Phase2MVPWorkflow()
        report, errors, warnings = workflow.run(
            create_sample_intake(),
            consultation_id="consult_phase2",
            report_id="report_phase2_001",
        )

        assert report is not None
        assert errors == []
        assert isinstance(warnings, list)

        assert report.report_id == "report_phase2_001"
        assert report.consultation_id == "consult_phase2"
        assert report.idea_strength_score >= 1.0
        assert report.overall_confidence in {
            ConfidenceLevel.LOW,
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.HIGH,
        }

        assert len(report.success_cases) > 0
        assert len(report.failure_cases) > 0
        assert "success_cases" in report.evidence_sources
        assert "failure_cases" in report.evidence_sources
        assert len(report.recommended_experiments) > 0
        assert len(report.thirty_day_plan) == 4
        assert len(report.disclaimers) >= 1

    def test_returns_validation_errors_for_invalid_intake(self):
        workflow = Phase2MVPWorkflow()
        report, errors, _ = workflow.run(
            {"business_name": "Incomplete Startup"},
            consultation_id="consult_invalid",
        )

        assert report is None
        assert len(errors) > 0
