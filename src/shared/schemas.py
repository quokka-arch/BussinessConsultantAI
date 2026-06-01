"""
Shared schema definitions for Business Consultant AI.

This module defines all structured data types used across the system,
following a schema-first approach for consistency and validation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class BusinessStage(str, Enum):
    """Business maturity stages."""
    IDEA = "idea"
    PRE_LAUNCH = "pre_launch"
    LAUNCHED = "launched"
    EARLY_GROWTH = "early_growth"
    SCALING = "scaling"


class ConfidenceLevel(str, Enum):
    """Confidence levels for assessments."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskSeverity(str, Enum):
    """Severity levels for identified risks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExperimentType(str, Enum):
    """Types of validation experiments."""
    CUSTOMER_INTERVIEW = "customer_interview"
    MARKET_RESEARCH = "market_research"
    PROTOTYPE_TEST = "prototype_test"
    PRICING_TEST = "pricing_test"
    LANDING_PAGE = "landing_page"
    MVP_BUILD = "mvp_build"
    PARTNERSHIP_TEST = "partnership_test"
    OTHER = "other"


@dataclass
class TeamMember:
    """Represents a team member."""
    name: str
    role: str
    experience_years: int
    relevant_expertise: List[str] = field(default_factory=list)


@dataclass
class Constraint:
    """Business constraint."""
    type: str  # e.g., "budget", "timeline", "geography", "regulations"
    description: str
    impact: str  # "high", "medium", "low"


@dataclass
class IntakeForm:
    """
    Structured intake form for consultation.
    
    Captures comprehensive business context needed for idea validation.
    """
    # Basic business info (required, no defaults)
    business_name: str
    idea_description: str
    problem_statement: str
    proposed_solution: str
    target_customer: str
    monetization_model: str  # e.g., "SaaS", "Marketplace", "E-commerce"
    revenue_model: str  # e.g., "subscription", "one-time", "freemium"
    stage: BusinessStage
    months_since_inception: int
    geographic_focus: str  # e.g., "US", "Global", "EU"
    existing_validation: str  # Description of validation already done
    
    # Optional fields
    price_point: Optional[str] = None
    planned_launch_date: Optional[str] = None
    current_users_or_revenue: Optional[str] = None
    
    # Team
    team_members: List[TeamMember] = field(default_factory=list)
    
    # Constraints
    constraints: List[Constraint] = field(default_factory=list)
    
    # Additional context
    key_assumptions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    
    # Metadata
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    submitter_email: Optional[str] = None


@dataclass
class Risk:
    """Identified risk for the business."""
    title: str
    description: str
    severity: RiskSeverity
    type: str  # e.g., "market", "product", "team", "execution", "financial"
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    mitigation_strategy: Optional[str] = None


@dataclass
class Assumption:
    """Key business assumption to validate."""
    statement: str
    category: str  # e.g., "customer", "market", "product", "business_model"
    criticality: str  # "must_validate", "should_validate", "nice_to_validate"
    evidence: str  # What we know about this assumption
    validation_approach: str  # How to test this assumption


@dataclass
class Experiment:
    """Recommended validation experiment."""
    title: str
    type: ExperimentType
    description: str
    objectives: List[str]
    duration_days: int
    success_criteria: List[str]
    key_metrics: List[str]
    estimated_effort: str  # e.g., "low", "medium", "high"
    estimated_cost: Optional[str] = None
    related_risks: List[str] = field(default_factory=list)
    related_assumptions: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class ActionItem:
    """Action item in execution plan."""
    priority: int  # 1 = highest
    title: str
    description: str
    week: int  # Week number in 30-day plan (1-4)
    depends_on: List[str] = field(default_factory=list)
    estimated_hours: Optional[int] = None
    success_metric: Optional[str] = None


@dataclass
class ComparableCase:
    """Reference to a comparable success or failure case study."""
    case_id: str
    company_name: str
    relevance_reason: str
    key_insight: str
    outcome: str  # "success" or "failure"
    source: str


@dataclass
class ConsultationReport:
    """
    Standard consultation report output.
    
    This is the main deliverable of the idea validation consultation.
    """
    # Identifiers & required fields
    report_id: str
    consultation_id: str
    business_summary: str
    idea_strength_score: float  # 1-5 scale
    idea_strength_rationale: str
    overall_confidence: ConfidenceLevel
    confidence_rationale: str
    
    # Optional/default fields
    generated_at: datetime = field(default_factory=datetime.utcnow)
    success_cases: List[ComparableCase] = field(default_factory=list)
    failure_cases: List[ComparableCase] = field(default_factory=list)
    key_assumptions: List[Assumption] = field(default_factory=list)
    top_risks: List[Risk] = field(default_factory=list)
    recommended_experiments: List[Experiment] = field(default_factory=list)
    thirty_day_plan: List[ActionItem] = field(default_factory=list)
    uncertainty_notes: List[str] = field(default_factory=list)
    requires_human_review: bool = False
    review_reason: Optional[str] = None
    frameworks_applied: List[str] = field(default_factory=list)
    evidence_sources: Dict[str, List[str]] = field(default_factory=dict)
    disclaimers: List[str] = field(default_factory=list)


@dataclass
class CaseStudy:
    """
    Structured case study for the knowledge base.
    
    Used for analog matching and pattern recognition.
    """
    # Required fields
    case_id: str
    company_name: str
    industry: str
    business_model: str
    customer_segment: str
    stage_at_event: BusinessStage
    founding_assumptions: List[str]
    key_decisions: List[str]
    go_to_market_approach: str
    pricing_strategy: str
    what_worked: List[str]
    what_failed: List[str]
    why_succeeded_or_failed: str
    timeline_months: int
    outcome: str  # "success", "failure", "acquisition", "shutdown", "ongoing"
    published_year: int
    source_type: str  # "blog", "case_study", "book", "interview", etc.
    
    # Optional fields
    major_pivots: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    source_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    relevance_to_saas: str = "medium"


@dataclass
class Framework:
    """Business framework definition."""
    framework_id: str
    name: str
    description: str
    use_cases: List[str]
    components: Dict[str, str]  # e.g., {"lean_canvas": "Problem, Solution, ..."}
    helpful_for_stage: List[BusinessStage]
    reference: Optional[str] = None


def to_dict(obj: Any) -> Dict:
    """Convert dataclass to dictionary recursively."""
    if hasattr(obj, '__dataclass_fields__'):
        return {
            k: to_dict(getattr(obj, k))
            for k in obj.__dataclass_fields__
        }
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj
