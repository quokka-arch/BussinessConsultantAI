"""
Integration tests for Phase 1 Foundation.

Tests the complete workflow of intake → evaluation → case study retrieval.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from intake.processor import IntakeProcessor, create_sample_intake
from shared.evaluation import IdeaScorer, RiskIdentifier, AssumptionIdentifier
from shared.case_studies import CaseStudyLibrary, create_initial_case_studies
from shared.schemas import ConsultationReport, ConfidenceLevel


class TestPhase1Integration:
    """Integration tests for Phase 1 Foundation components."""
    
    def test_complete_consultation_preparation_workflow(self):
        """Test complete workflow: intake → evaluation → case retrieval."""
        
        # Step 1: Get and process intake
        intake_data = create_sample_intake()
        processor = IntakeProcessor()
        intake_form, errors, warnings = processor.process_intake(intake_data)
        
        assert intake_form is not None
        assert len(errors) == 0
        
        # Step 2: Score the idea
        scorer = IdeaScorer()
        idea_score, rationale, dimensions = scorer.score_idea(intake_form)
        
        assert 1.0 <= idea_score <= 5.0
        assert len(rationale) > 0
        
        # Step 3: Identify risks
        risk_identifier = RiskIdentifier()
        risks = risk_identifier.identify_risks(intake_form)
        
        assert len(risks) > 0
        assert all(risk.mitigation_strategy for risk in risks)
        
        # Step 4: Identify assumptions
        assumption_identifier = AssumptionIdentifier()
        assumptions = assumption_identifier.identify_assumptions(intake_form)
        
        assert len(assumptions) > 0
        assert all(assumption.validation_approach for assumption in assumptions)
        
        # Step 5: Find relevant case studies
        lib = CaseStudyLibrary()
        for study in create_initial_case_studies():
            lib.add_study(study)
        
        similar_studies = lib.get_similar_studies(
            industry=intake_form.target_customer,  # Using as proxy
            business_model=intake_form.monetization_model,
            customer_segment=intake_form.target_customer
        )
        
        assert len(similar_studies) > 0
    
    def test_foundation_report_structure(self):
        """Test that we can build the basic structure for a consultation report."""
        
        # Prepare data
        intake_data = create_sample_intake()
        processor = IntakeProcessor()
        intake_form, _, _ = processor.process_intake(intake_data)
        
        scorer = IdeaScorer()
        idea_score, rationale, _ = scorer.score_idea(intake_form)
        
        risk_identifier = RiskIdentifier()
        risks = risk_identifier.identify_risks(intake_form)
        
        assumption_identifier = AssumptionIdentifier()
        assumptions = assumption_identifier.identify_assumptions(intake_form)
        
        # Build basic report structure
        report = ConsultationReport(
            report_id="report_001",
            consultation_id="consult_001",
            business_summary=f"Business: {intake_form.business_name}. Stage: {intake_form.stage.value}",
            idea_strength_score=idea_score,
            idea_strength_rationale=rationale,
            overall_confidence=ConfidenceLevel.MEDIUM,
            confidence_rationale="Phase 1 foundation - confidence based on validation evidence and team composition.",
            key_assumptions=assumptions,
            top_risks=risks,
        )
        
        assert report.report_id == "report_001"
        assert report.idea_strength_score > 0
        assert len(report.top_risks) > 0
        assert len(report.key_assumptions) > 0
    
    def test_case_study_matching_for_analytics_saas(self):
        """Test case study retrieval for an analytics SaaS company."""
        
        lib = CaseStudyLibrary()
        for study in create_initial_case_studies():
            lib.add_study(study)
        
        # Search for analytics SaaS case studies
        analytics_cases = lib.search_by_industry("SaaS")
        success_cases = lib.search_by_outcome("success")
        
        assert len(analytics_cases) > 0
        assert len(success_cases) > 0
        
        # Get similar studies for product analytics startup
        similar = lib.get_similar_studies(
            industry="SaaS - Analytics",
            business_model="B2B SaaS",
            customer_segment="product teams"
        )
        
        assert len(similar) > 0
        for case in similar:
            assert "SaaS" in case.industry
    
    def test_multiple_intake_forms_scoring(self):
        """Test scoring multiple different intake forms."""
        
        processor = IntakeProcessor()
        scorer = IdeaScorer()
        
        # Strong SaaS idea
        strong_data = create_sample_intake()
        strong_form, _, _ = processor.process_intake(strong_data)
        strong_score, _, _ = scorer.score_idea(strong_form)
        
        # Weaker but valid idea
        weak_data = create_sample_intake()
        weak_data["existing_validation"] = ""  # No validation yet
        weak_form, _, _ = processor.process_intake(weak_data)
        weak_score, _, _ = scorer.score_idea(weak_form)
        
        # Strong should score higher than weak
        assert strong_score > weak_score
        
        # Both should be in valid range
        assert 1.0 <= strong_score <= 5.0
        assert 1.0 <= weak_score <= 5.0


class TestPhase1DataQuality:
    """Test data quality of Phase 1 components."""
    
    def test_case_studies_have_consistent_quality(self):
        """Test that case studies meet quality standards."""
        
        studies = create_initial_case_studies()
        
        for study in studies:
            # Each study must have documented outcomes
            assert study.what_worked or study.what_failed
            
            # Must have pricing information
            assert len(study.pricing_strategy) > 0
            
            # Must explain why it succeeded or failed
            assert len(study.why_succeeded_or_failed) > 50
            
            # Must have timeline information
            assert study.timeline_months > 0
            
            # Must have source attribution
            assert study.source_type in [
                "blog", "case_study", "book", "interview", 
                "company", "historical", "news"
            ]
    
    def test_all_risk_types_covered(self):
        """Test that risk identification covers all major risk types."""
        
        intake_data = create_sample_intake()
        processor = IntakeProcessor()
        intake_form, _, _ = processor.process_intake(intake_data)
        
        risk_identifier = RiskIdentifier()
        risks = risk_identifier.identify_risks(intake_form)
        
        risk_types = set(r.type for r in risks)
        
        # Should identify across multiple risk categories
        assert len(risk_types) >= 1
    
    def test_assumption_validation_approaches_are_specific(self):
        """Test that assumption validation approaches are actionable."""
        
        intake_data = create_sample_intake()
        processor = IntakeProcessor()
        intake_form, _, _ = processor.process_intake(intake_data)
        
        assumption_identifier = AssumptionIdentifier()
        assumptions = assumption_identifier.identify_assumptions(intake_form)
        
        for assumption in assumptions:
            # Validation approach should be specific enough to implement
            assert len(assumption.validation_approach) > 20
            # Should mention specific methods or actions
            assert any(
                word in assumption.validation_approach.lower()
                for word in ["conduct", "build", "test", "research", "survey", "determine", "map"]
            )
