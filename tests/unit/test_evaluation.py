"""
Unit tests for evaluation module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from shared.evaluation import IdeaScorer, RiskIdentifier, AssumptionIdentifier
from shared.schemas import (
    BusinessStage, ConfidenceLevel, RiskSeverity, IntakeForm,
    TeamMember, Constraint
)
from intake.processor import create_sample_intake, IntakeProcessor


class TestIdeaScorer:
    """Test idea scoring."""
    
    def test_scores_are_in_range(self):
        """Test that scores are within 1-5 range."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        scorer = IdeaScorer()
        overall_score, rationale, dimension_scores = scorer.score_idea(form)
        
        assert 1.0 <= overall_score <= 5.0
        assert len(rationale) > 0
        assert len(dimension_scores) == len(scorer.DIMENSIONS)
    
    def test_all_dimensions_scored(self):
        """Test that all dimensions are scored."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        scorer = IdeaScorer()
        overall_score, rationale, dimension_scores = scorer.score_idea(form)
        
        for dim in scorer.DIMENSIONS:
            assert dim in dimension_scores
            assert 1.0 <= dimension_scores[dim] <= 5.0
    
    def test_better_validation_improves_score(self):
        """Test that more validation increases market need score."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form1, _, _ = processor.process_intake(data)
        
        scorer1 = IdeaScorer()
        _, _, scores1 = scorer1.score_idea(form1)
        
        # Now with more validation
        data["existing_validation"] = "Conducted 50 customer interviews with strong validation that customers are willing to pay $500-1000/month."
        form2, _, _ = processor.process_intake(data)
        
        scorer2 = IdeaScorer()
        _, _, scores2 = scorer2.score_idea(form2)
        
        # Market need should improve with validation
        assert scores2["market_need"] >= scores1["market_need"]
    
    def test_rationale_includes_justifications(self):
        """Test that rationale includes dimension justifications."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        scorer = IdeaScorer()
        overall_score, rationale, dimension_scores = scorer.score_idea(form)
        
        # Rationale should mention key dimensions
        assert "market_need" in scorer.justifications or "Problem" in rationale


class TestRiskIdentifier:
    """Test risk identification."""
    
    def test_identifies_market_risks(self):
        """Test that market risks are identified."""
        data = create_sample_intake()
        data["existing_validation"] = ""  # No validation
        
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = RiskIdentifier()
        risks = identifier.identify_risks(form)
        
        assert len(risks) > 0
        assert any("validation" in risk.title.lower() for risk in risks)
    
    def test_identifies_team_risks(self):
        """Test that team risks are identified."""
        data = create_sample_intake()
        data["team_members"] = []  # No team
        
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = RiskIdentifier()
        risks = identifier.identify_risks(form)
        
        assert len(risks) > 0
        assert any("team" in risk.title.lower() for risk in risks)
    
    def test_identifies_monetization_risks(self):
        """Test that monetization risks are identified."""
        data = create_sample_intake()
        data["monetization_model"] = ""
        data["price_point"] = None
        
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = RiskIdentifier()
        risks = identifier.identify_risks(form)
        
        assert len(risks) > 0
        assert any("monetization" in risk.title.lower() for risk in risks)
    
    def test_risks_have_mitigation_strategies(self):
        """Test that identified risks have mitigation strategies."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = RiskIdentifier()
        risks = identifier.identify_risks(form)
        
        for risk in risks:
            assert risk.mitigation_strategy is not None
            assert len(risk.mitigation_strategy) > 0
    
    def test_risks_sorted_by_severity(self):
        """Test that risks are sorted by severity."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = RiskIdentifier()
        risks = identifier.identify_risks(form)
        
        severity_order = {
            RiskSeverity.CRITICAL: 0,
            RiskSeverity.HIGH: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.LOW: 3,
        }
        
        for i in range(len(risks) - 1):
            assert severity_order[risks[i].severity] <= severity_order[risks[i+1].severity]


class TestAssumptionIdentifier:
    """Test assumption identification."""
    
    def test_identifies_key_assumptions(self):
        """Test that key assumptions are identified."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = AssumptionIdentifier()
        assumptions = identifier.identify_assumptions(form)
        
        assert len(assumptions) > 0
        assert any("market" in ass.category.lower() for ass in assumptions)
        assert any("product" in ass.category.lower() for ass in assumptions)
    
    def test_assumptions_have_validation_approaches(self):
        """Test that assumptions have validation approaches."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = AssumptionIdentifier()
        assumptions = identifier.identify_assumptions(form)
        
        for assumption in assumptions:
            assert assumption.validation_approach is not None
            assert len(assumption.validation_approach) > 0
    
    def test_includes_user_provided_assumptions(self):
        """Test that user-provided assumptions are included."""
        data = create_sample_intake()
        user_assumption = "Our international expansion will be rapid"
        data["key_assumptions"] = [user_assumption]
        
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = AssumptionIdentifier()
        assumptions = identifier.identify_assumptions(form)
        
        assumption_statements = [a.statement for a in assumptions]
        assert any(user_assumption in stmt for stmt in assumption_statements)
    
    def test_assumptions_categorized(self):
        """Test that assumptions are properly categorized."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, _, _ = processor.process_intake(data)
        
        identifier = AssumptionIdentifier()
        assumptions = identifier.identify_assumptions(form)
        
        categories = set(a.category for a in assumptions)
        assert len(categories) > 1  # Should have multiple categories


class TestEvaluationIntegration:
    """Integration tests for evaluation module."""
    
    def test_complete_evaluation_workflow(self):
        """Test complete evaluation workflow with sample intake."""
        data = create_sample_intake()
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        
        # Score idea
        scorer = IdeaScorer()
        overall_score, rationale, dimensions = scorer.score_idea(form)
        assert 1.0 <= overall_score <= 5.0
        
        # Identify risks
        risk_identifier = RiskIdentifier()
        risks = risk_identifier.identify_risks(form)
        assert len(risks) > 0
        
        # Identify assumptions
        assumption_identifier = AssumptionIdentifier()
        assumptions = assumption_identifier.identify_assumptions(form)
        assert len(assumptions) > 0
    
    def test_weak_idea_scores_lower(self):
        """Test that weak ideas score lower."""
        # Create weak idea data (but still valid)
        weak_data = {
            "business_name": "Generic Company",
            "idea_description": "A generic app idea that solves something generic and unspecific.",
            "problem_statement": "Generic problem that people face.",
            "proposed_solution": "A generic solution to the problem.",
            "target_customer": "General consumers",
            "monetization_model": "Subscription",
            "revenue_model": "One-time fee",
            "stage": "idea",
            "months_since_inception": 0,
            "geographic_focus": "Global",
            "team_members": [],
            "existing_validation": "No validation done yet",
        }
        
        processor = IntakeProcessor()
        weak_form, _, _ = processor.process_intake(weak_data)
        
        assert weak_form is not None, "Weak form should still be valid for comparison"
        
        # Score weak idea
        scorer = IdeaScorer()
        weak_score, _, _ = scorer.score_idea(weak_form)
        
        # Compare with sample strong idea
        strong_data = create_sample_intake()
        strong_form, _, _ = processor.process_intake(strong_data)
        strong_score, _, _ = scorer.score_idea(strong_form)
        
        # Strong idea should score better
        assert strong_score > weak_score
