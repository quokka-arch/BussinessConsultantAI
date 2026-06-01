"""
Baseline Evaluation Rubric: Idea assessment and scoring.

This module defines the scoring framework for evaluating business ideas
and identifying key risks and opportunities.
"""

from typing import Dict, List, Tuple
from shared.schemas import (
    IntakeForm, Risk, Assumption, ConfidenceLevel, RiskSeverity,
    BusinessStage
)
import logging

logger = logging.getLogger(__name__)


class IdeaScorer:
    """Scores business ideas on multiple dimensions."""
    
    # Scoring dimensions
    DIMENSIONS = {
        "market_need": "Is there evidence of market need?",
        "unfair_advantage": "Does the team have unique advantage?",
        "monetization_clarity": "Is the monetization model clear?",
        "execution_capability": "Can the team execute?",
        "market_size": "Is the market large enough?",
        "traction_evidence": "Is there validation evidence?",
    }
    
    # Dimension weights (sum = 1.0)
    WEIGHTS = {
        "market_need": 0.25,
        "unfair_advantage": 0.20,
        "monetization_clarity": 0.15,
        "execution_capability": 0.20,
        "market_size": 0.15,
        "traction_evidence": 0.05,  # MVP phase
    }
    
    def __init__(self):
        """Initialize scorer."""
        self.dimension_scores: Dict[str, float] = {}
        self.justifications: Dict[str, str] = {}
    
    def score_idea(self, intake: IntakeForm) -> Tuple[float, str, Dict[str, float]]:
        """
        Score business idea on 1-5 scale.
        
        Args:
            intake: Intake form with business context
            
        Returns:
            Tuple of (overall_score, rationale, dimension_scores)
        """
        self.dimension_scores = {}
        self.justifications = {}
        
        # Score each dimension
        self._score_market_need(intake)
        self._score_unfair_advantage(intake)
        self._score_monetization_clarity(intake)
        self._score_execution_capability(intake)
        self._score_market_size(intake)
        self._score_traction_evidence(intake)
        
        # Calculate weighted overall score
        overall_score = sum(
            self.dimension_scores.get(dim, 2.5) * self.WEIGHTS[dim]
            for dim in self.DIMENSIONS
        )
        
        # Build rationale
        rationale = self._build_rationale()
        
        return round(overall_score, 2), rationale, self.dimension_scores
    
    def _score_market_need(self, intake: IntakeForm) -> None:
        """Score evidence of market need."""
        score = 2.5  # Default
        justification_parts = []
        
        # Check problem clarity
        if len(intake.problem_statement) > 100:
            score += 0.5
            justification_parts.append("Clear problem statement")
        
        # Check for validation
        if intake.existing_validation and len(intake.existing_validation) > 50:
            score += 0.75
            justification_parts.append("Customer interviews conducted")
            
            if "willing to pay" in intake.existing_validation.lower():
                score += 0.25
                justification_parts.append("Evidence of willingness to pay")
        
        # Check target customer clarity
        if len(intake.target_customer) > 50:
            score += 0.25
            justification_parts.append("Clear target customer segment")
        
        # Cap at 5
        score = min(score, 5.0)
        self.dimension_scores["market_need"] = score
        self.justifications["market_need"] = "; ".join(justification_parts) or "Limited market validation"
    
    def _score_unfair_advantage(self, intake: IntakeForm) -> None:
        """Score team's unfair advantage."""
        score = 2.5  # Default
        justification_parts = []
        
        if not intake.team_members:
            self.dimension_scores["unfair_advantage"] = score
            self.justifications["unfair_advantage"] = "No team identified"
            return
        
        # Count relevant experience
        avg_experience = sum(tm.experience_years for tm in intake.team_members) / len(intake.team_members)
        if avg_experience >= 5:
            score += 0.5
            justification_parts.append(f"Avg {avg_experience:.1f} years experience")
        
        # Check for domain expertise
        all_expertise = []
        for tm in intake.team_members:
            all_expertise.extend(tm.relevant_expertise)
        
        if all_expertise:
            score += 0.75
            justification_parts.append("Relevant domain expertise present")
        
        # Check for complementary skills (multiple team members)
        if len(intake.team_members) >= 2:
            roles = [tm.role for tm in intake.team_members]
            if len(set(roles)) > 1:
                score += 0.5
                justification_parts.append("Complementary team roles")
        
        score = min(score, 5.0)
        self.dimension_scores["unfair_advantage"] = score
        self.justifications["unfair_advantage"] = "; ".join(justification_parts) or "Team composition unclear"
    
    def _score_monetization_clarity(self, intake: IntakeForm) -> None:
        """Score clarity of monetization model."""
        score = 2.5
        justification_parts = []
        
        # Model clarity
        if intake.monetization_model and len(intake.monetization_model) > 5:
            score += 0.75
            justification_parts.append(f"Model: {intake.monetization_model}")
        
        # Revenue model
        if intake.revenue_model and len(intake.revenue_model) > 5:
            score += 0.75
            justification_parts.append(f"Revenue: {intake.revenue_model}")
        
        # Price point
        if intake.price_point:
            score += 0.5
            justification_parts.append("Price point defined")
        
        # Recurring vs one-time (recurring is better for SaaS)
        if intake.revenue_model and "subscription" in intake.revenue_model.lower():
            score += 0.25
            justification_parts.append("Recurring revenue model")
        
        score = min(score, 5.0)
        self.dimension_scores["monetization_clarity"] = score
        self.justifications["monetization_clarity"] = "; ".join(justification_parts) or "Monetization unclear"
    
    def _score_execution_capability(self, intake: IntakeForm) -> None:
        """Score team's execution capability."""
        score = 2.5
        justification_parts = []
        
        # Timeline commitment
        if intake.months_since_inception == 0 and intake.planned_launch_date:
            score += 0.5
            justification_parts.append("Clear launch timeline")
        
        # Constraints management
        num_constraints = len(intake.constraints)
        if num_constraints == 0:
            score += 0.5
            justification_parts.append("No critical constraints")
        elif num_constraints <= 2:
            score += 0.25
            justification_parts.append("Reasonable constraints")
        else:
            score -= 0.25
            justification_parts.append("Multiple constraints to navigate")
        
        # Team readiness
        if intake.team_members and len(intake.team_members) >= 2:
            score += 0.5
            justification_parts.append("Founding team in place")
        elif intake.team_members:
            score += 0.25
            justification_parts.append("Solo founder - hiring needed")
        
        score = min(score, 5.0)
        self.dimension_scores["execution_capability"] = score
        self.justifications["execution_capability"] = "; ".join(justification_parts) or "Execution readiness unclear"
    
    def _score_market_size(self, intake: IntakeForm) -> None:
        """Score addressable market size."""
        score = 2.5
        justification_parts = []
        
        # Geographic reach
        if intake.geographic_focus.lower() in ["global", "us", "eu"]:
            score += 0.75
            justification_parts.append(f"Market: {intake.geographic_focus}")
        
        # Target segment clarity
        if intake.target_customer and len(intake.target_customer) > 50:
            score += 0.5
            justification_parts.append("Clear customer segment")
        
        # B2B SaaS typically has good unit economics
        if intake.monetization_model and "saas" in intake.monetization_model.lower():
            score += 0.5
            justification_parts.append("SaaS model (scalable)")
        
        score = min(score, 5.0)
        self.dimension_scores["market_size"] = score
        self.justifications["market_size"] = "; ".join(justification_parts) or "Market size unclear"
    
    def _score_traction_evidence(self, intake: IntakeForm) -> None:
        """Score existing traction and validation."""
        score = 2.5
        
        if intake.existing_validation and len(intake.existing_validation) > 100:
            score += 1.0
            self.justifications["traction_evidence"] = "Documented customer validation"
        elif intake.existing_validation and len(intake.existing_validation) > 30:
            score += 0.5
            self.justifications["traction_evidence"] = "Some validation started"
        else:
            self.justifications["traction_evidence"] = "No validation conducted yet"
        
        self.dimension_scores["traction_evidence"] = score
    
    def _build_rationale(self) -> str:
        """Build text rationale for overall score."""
        parts = []
        for dim in self.DIMENSIONS:
            parts.append(
                f"- {self.DIMENSIONS[dim]} {self.justifications.get(dim, 'Unknown')}"
            )
        return "\n".join(parts)


class RiskIdentifier:
    """Identifies and prioritizes key risks."""
    
    RISK_PATTERNS = {
        "market": {
            "no_validation": {
                "title": "Lack of market validation",
                "description": "No customer interviews or validation completed yet",
                "severity": RiskSeverity.HIGH,
            },
            "undefined_tam": {
                "title": "Unclear total addressable market",
                "description": "Market size and growth potential not clearly defined",
                "severity": RiskSeverity.MEDIUM,
            },
        },
        "product": {
            "feature_incomplete": {
                "title": "Unclear product scope",
                "description": "MVP feature set and differentiation not clearly defined",
                "severity": RiskSeverity.MEDIUM,
            },
        },
        "team": {
            "solo_founder": {
                "title": "Solo founder risk",
                "description": "Single founder creates dependency risk and limited skill coverage",
                "severity": RiskSeverity.MEDIUM,
            },
            "no_relevant_experience": {
                "title": "Limited relevant experience",
                "description": "Team lacks domain expertise in the target market",
                "severity": RiskSeverity.MEDIUM,
            },
        },
        "execution": {
            "multiple_constraints": {
                "title": "Multiple execution constraints",
                "description": "Budget, timeline, and resource constraints may slow progress",
                "severity": RiskSeverity.MEDIUM,
            },
            "short_runway": {
                "title": "Limited runway",
                "description": "Less than 3 months of funding remaining",
                "severity": RiskSeverity.HIGH,
            },
        },
        "business_model": {
            "unclear_monetization": {
                "title": "Unclear monetization path",
                "description": "Revenue model and pricing strategy not well defined",
                "severity": RiskSeverity.HIGH,
            },
            "unproven_pricing": {
                "title": "Unproven pricing model",
                "description": "Price point not validated with customers",
                "severity": RiskSeverity.MEDIUM,
            },
        },
    }
    
    def identify_risks(self, intake: IntakeForm) -> List[Risk]:
        """
        Identify key risks from intake form.
        
        Args:
            intake: Intake form with business context
            
        Returns:
            List of identified risks, sorted by severity
        """
        risks = []
        
        # Market risks
        if not intake.existing_validation or len(intake.existing_validation) < 30:
            risks.append(Risk(
                title="No customer validation yet",
                description="No documented customer interviews or market research",
                severity=RiskSeverity.HIGH,
                type="market",
                mitigation_strategy="Conduct 20+ customer interviews before MVP launch",
                confidence=ConfidenceLevel.HIGH
            ))
        
        # Team risks
        if not intake.team_members:
            risks.append(Risk(
                title="No founding team identified",
                description="Unclear who will execute the business plan",
                severity=RiskSeverity.CRITICAL,
                type="team",
                mitigation_strategy="Identify co-founders or key hires before launch",
                confidence=ConfidenceLevel.HIGH
            ))
        elif len(intake.team_members) == 1:
            risks.append(Risk(
                title="Solo founder risk",
                description="Single founder creates dependency and skill gaps",
                severity=RiskSeverity.MEDIUM,
                type="team",
                mitigation_strategy="Hire or partner with complementary co-founder",
                confidence=ConfidenceLevel.MEDIUM
            ))
        
        # Monetization risks
        if not intake.monetization_model or len(intake.monetization_model) < 5:
            risks.append(Risk(
                title="Monetization model not defined",
                description="Unclear how business will generate revenue",
                severity=RiskSeverity.HIGH,
                type="business_model",
                mitigation_strategy="Define and test 2-3 pricing models with customers",
                confidence=ConfidenceLevel.HIGH
            ))
        elif not intake.price_point:
            risks.append(Risk(
                title="Price point not validated",
                description="Pricing strategy exists but not tested with real customers",
                severity=RiskSeverity.MEDIUM,
                type="business_model",
                mitigation_strategy="Conduct pricing survey with 20+ potential customers",
                confidence=ConfidenceLevel.MEDIUM
            ))
        
        # Execution risks
        high_constraint_count = sum(1 for c in intake.constraints if c.impact == "high")
        if high_constraint_count >= 2:
            risks.append(Risk(
                title="Multiple execution constraints",
                description=f"{high_constraint_count} high-impact constraints identified",
                severity=RiskSeverity.MEDIUM,
                type="execution",
                mitigation_strategy="Prioritize top 3 constraints; create contingency plans",
                confidence=ConfidenceLevel.MEDIUM
            ))
        
        # Sort by severity
        severity_order = {
            RiskSeverity.CRITICAL: 0,
            RiskSeverity.HIGH: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.LOW: 3,
        }
        risks.sort(key=lambda r: severity_order[r.severity])
        
        return risks


class AssumptionIdentifier:
    """Identifies key assumptions to validate."""
    
    def identify_assumptions(self, intake: IntakeForm) -> List[Assumption]:
        """
        Identify key business assumptions.
        
        Args:
            intake: Intake form with business context
            
        Returns:
            List of identified assumptions
        """
        assumptions = []
        
        # Market assumptions
        assumptions.append(Assumption(
            statement=f"Target customers ({intake.target_customer}) have the problem described",
            category="customer",
            criticality="must_validate",
            evidence=intake.existing_validation or "Not yet validated",
            validation_approach="Conduct customer interviews with at least 20 target customers"
        ))
        
        # Product assumptions
        assumptions.append(Assumption(
            statement="Proposed solution adequately solves the identified problem",
            category="product",
            criticality="must_validate",
            evidence="Concept testing needed",
            validation_approach="Build prototype and test with customers (5+ users)"
        ))
        
        # Monetization assumptions
        assumptions.append(Assumption(
            statement=f"Customers are willing to pay {intake.price_point or 'proposed price'} for this solution",
            category="business_model",
            criticality="must_validate",
            evidence="No pricing validation yet" if not intake.price_point else "Pricing defined but not tested",
            validation_approach="Conduct pricing study with target customers"
        ))
        
        # Market size assumptions
        assumptions.append(Assumption(
            statement=f"The {intake.geographic_focus} market for this solution is large enough to build a sustainable business",
            category="market",
            criticality="should_validate",
            evidence="Market research recommended",
            validation_approach="Research TAM/SAM using market reports and customer research"
        ))
        
        # Team assumptions
        if intake.team_members:
            avg_exp = sum(tm.experience_years for tm in intake.team_members) / len(intake.team_members)
            assumptions.append(Assumption(
                statement=f"Current team with {avg_exp:.0f} years avg experience can execute this plan",
                category="team",
                criticality="should_validate",
                evidence="Team identified and experienced" if avg_exp >= 5 else "Team may need skill development",
                validation_approach="Map required skills against current team; identify hiring needs"
            ))
        
        # Include user-provided assumptions
        for user_assumption in intake.key_assumptions:
            assumptions.append(Assumption(
                statement=user_assumption,
                category="custom",
                criticality="should_validate",
                evidence="User-identified assumption",
                validation_approach="Determine best validation approach for this specific assumption"
            ))
        
        return assumptions
