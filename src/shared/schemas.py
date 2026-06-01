"""
Shared schema definitions for Business Consultant AI.

This module defines all structured data types used across the system,
following a schema-first approach for consistency and validation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import UTC, datetime


class BusinessStage(str, Enum):
    """Business maturity stages."""
    IDEA = "idea"
    PRE_LAUNCH = "pre_launch"
    LAUNCHED = "launched"
    EARLY_GROWTH = "early_growth"
    SCALING = "scaling"


class CaseStudyOutcome(str, Enum):
    """Normalized case study outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    ACQUISITION = "acquisition"
    SHUTDOWN = "shutdown"
    ONGOING = "ongoing"


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
class CaseStudySource:
    """Source material used to curate or extract a case study."""
    source_id: str
    title: str
    source_type: str
    url: Optional[str] = None
    locator: Optional[str] = None
    published_year: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class CaseStudyEvidence:
    """Traceable evidence supporting one extracted or curated field."""
    field_name: str
    source_id: str
    excerpt: str
    rationale: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    locator: Optional[str] = None


@dataclass
class CaseStudyExtractionMetadata:
    """Metadata about how a case study record was extracted."""
    extractor_agent: str
    prompt_version: str
    extraction_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    extraction_notes: List[str] = field(default_factory=list)
    manual_review_required: bool = True
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


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
    outcome: CaseStudyOutcome
    published_year: int
    source_type: str  # "blog", "case_study", "book", "interview", etc.
    
    # Optional fields
    major_pivots: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    source_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    relevance_to_saas: str = "medium"
    summary: Optional[str] = None
    source_materials: List[CaseStudySource] = field(default_factory=list)
    evidence: List[CaseStudyEvidence] = field(default_factory=list)
    uncertainty_notes: List[str] = field(default_factory=list)
    extraction_metadata: Optional[CaseStudyExtractionMetadata] = None


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


def validate_case_study(case_study: CaseStudy, require_traceability: bool = False) -> None:
    """Validate core case study requirements."""
    required_text_fields = [
        case_study.case_id,
        case_study.company_name,
        case_study.industry,
        case_study.business_model,
        case_study.customer_segment,
        case_study.go_to_market_approach,
        case_study.pricing_strategy,
        case_study.why_succeeded_or_failed,
        case_study.source_type,
    ]
    if any(not field for field in required_text_fields):
        raise ValueError("Case study is missing one or more required text fields.")

    if case_study.timeline_months <= 0:
        raise ValueError("Case study timeline_months must be greater than zero.")

    if case_study.published_year <= 0:
        raise ValueError("Case study published_year must be greater than zero.")

    if not case_study.what_worked and not case_study.what_failed:
        raise ValueError("Case study must document what worked or what failed.")

    valid_outcomes = {outcome.value for outcome in CaseStudyOutcome}
    if case_study.outcome not in valid_outcomes:
        raise ValueError("Case study outcome must be one of the normalized outcome values.")

    if require_traceability:
        if not case_study.source_materials:
            raise ValueError("Traceable case studies require source_materials.")
        if not case_study.evidence:
            raise ValueError("Traceable case studies require evidence entries.")
        if not case_study.uncertainty_notes:
            raise ValueError("Traceable case studies require uncertainty_notes.")
        if case_study.extraction_metadata is None:
            raise ValueError("Traceable case studies require extraction_metadata.")

        source_ids = {source.source_id for source in case_study.source_materials}
        for evidence in case_study.evidence:
            if evidence.source_id not in source_ids:
                raise ValueError(
                    f"Evidence for field '{evidence.field_name}' references unknown "
                    f"source_id '{evidence.source_id}'."
                )


def case_study_from_dict(
    data: Dict[str, Any],
    require_traceability: bool = False,
) -> CaseStudy:
    """Build a validated CaseStudy from a dictionary payload."""
    source_materials = [
        CaseStudySource(**item)
        for item in data.get("source_materials", [])
    ]
    evidence = [
        CaseStudyEvidence(
            field_name=item["field_name"],
            source_id=item["source_id"],
            excerpt=item["excerpt"],
            rationale=item["rationale"],
            confidence=ConfidenceLevel(item.get("confidence", ConfidenceLevel.MEDIUM.value)),
            locator=item.get("locator"),
        )
        for item in data.get("evidence", [])
    ]

    extraction_payload = data.get("extraction_metadata")
    extraction_metadata = None
    if extraction_payload:
        extraction_metadata = CaseStudyExtractionMetadata(
            extractor_agent=extraction_payload["extractor_agent"],
            prompt_version=extraction_payload["prompt_version"],
            extraction_confidence=ConfidenceLevel(
                extraction_payload.get(
                    "extraction_confidence",
                    ConfidenceLevel.MEDIUM.value,
                )
            ),
            extraction_notes=extraction_payload.get("extraction_notes", []),
            manual_review_required=extraction_payload.get("manual_review_required", True),
            extracted_at=datetime.fromisoformat(extraction_payload["extracted_at"])
            if extraction_payload.get("extracted_at")
            else datetime.now(UTC),
        )

    study = CaseStudy(
        case_id=data["case_id"],
        company_name=data["company_name"],
        industry=data["industry"],
        business_model=data["business_model"],
        customer_segment=data["customer_segment"],
        stage_at_event=BusinessStage(data["stage_at_event"]),
        founding_assumptions=data["founding_assumptions"],
        key_decisions=data["key_decisions"],
        go_to_market_approach=data["go_to_market_approach"],
        pricing_strategy=data["pricing_strategy"],
        what_worked=data["what_worked"],
        what_failed=data["what_failed"],
        why_succeeded_or_failed=data["why_succeeded_or_failed"],
        timeline_months=data["timeline_months"],
        outcome=CaseStudyOutcome(data["outcome"]),
        published_year=data["published_year"],
        source_type=data["source_type"],
        major_pivots=data.get("major_pivots", []),
        failure_modes=data.get("failure_modes", []),
        source_url=data.get("source_url"),
        tags=data.get("tags", []),
        relevance_to_saas=data.get("relevance_to_saas", "medium"),
        summary=data.get("summary"),
        source_materials=source_materials,
        evidence=evidence,
        uncertainty_notes=data.get("uncertainty_notes", []),
        extraction_metadata=extraction_metadata,
    )
    validate_case_study(study, require_traceability=require_traceability)
    return study
