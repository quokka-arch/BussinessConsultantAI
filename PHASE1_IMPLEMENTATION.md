# Phase 1 (Foundation) Implementation Guide

## Overview

Phase 1 establishes the foundational infrastructure for the Business Consultant AI system. This document covers the structure, components, and how to use them.

## Project Structure

```
src/
├── shared/                    # Shared utilities across all modules
│   ├── schemas.py            # All data type definitions
│   ├── evaluation.py         # Scoring and risk identification
│   ├── case_studies.py       # Case study knowledge base
│   └── config.py             # Configuration management
├── intake/                    # Business context intake
│   └── processor.py          # Form validation and processing
├── retrieval/                # (Placeholder for Phase 2)
├── reasoning/                # (Placeholder for Phase 2)
├── recommendation/           # (Placeholder for Phase 2)
├── memory/                   # (Placeholder for Phase 2)
└── feedback/                 # (Placeholder for Phase 2)

tests/
├── unit/                     # Unit tests
│   ├── test_intake.py       # Intake validation tests
│   ├── test_evaluation.py   # Scoring and risk tests
│   └── test_case_studies.py # Case study management tests
└── integration/
    └── test_phase1_foundation.py  # End-to-end workflow tests

data/
├── case_studies/             # Case study dataset
└── frameworks/               # Business framework definitions
```

## Key Components

### 1. Schemas (`src/shared/schemas.py`)

Defines all data structures using Python dataclasses:

- **IntakeForm**: Captures comprehensive business context
- **Risk**: Identified business risks with mitigation strategies
- **Assumption**: Key business assumptions to validate
- **Experiment**: Recommended validation experiments
- **ActionItem**: Items for 30-day execution plan
- **ConsultationReport**: Standard output format
- **CaseStudy**: Knowledge base entries for analog matching
- **Framework**: Business analysis frameworks

### 2. Intake Module (`src/intake/processor.py`)

**IntakeValidator**: Validates form submission

```python
from intake.processor import IntakeValidator, create_sample_intake

# Validate intake data
validator = IntakeValidator()
is_valid, errors, warnings = validator.validate(intake_data)
```

**IntakeProcessor**: Normalizes and processes intake

```python
from intake.processor import IntakeProcessor

processor = IntakeProcessor()
form, errors, warnings = processor.process_intake(intake_data)
```

### 3. Evaluation Module (`src/shared/evaluation.py`)

**IdeaScorer**: Scores business ideas on 1-5 scale

```python
from shared.evaluation import IdeaScorer

scorer = IdeaScorer()
overall_score, rationale, dimension_scores = scorer.score_idea(intake_form)
```

Scoring dimensions:
- Market need (25% weight)
- Unfair advantage (20%)
- Monetization clarity (15%)
- Execution capability (20%)
- Market size (15%)
- Traction evidence (5%)

**RiskIdentifier**: Identifies and prioritizes risks

```python
from shared.evaluation import RiskIdentifier

identifier = RiskIdentifier()
risks = identifier.identify_risks(intake_form)  # Returns sorted by severity
```

**AssumptionIdentifier**: Extracts key assumptions

```python
from shared.evaluation import AssumptionIdentifier

identifier = AssumptionIdentifier()
assumptions = identifier.identify_assumptions(intake_form)
```

### 4. Case Studies Module (`src/shared/case_studies.py`)

**CaseStudyLibrary**: Manages the knowledge base

```python
from shared.case_studies import CaseStudyLibrary, create_initial_case_studies

lib = CaseStudyLibrary()
for study in create_initial_case_studies():
    lib.add_study(study)

# Search and retrieve
success_cases = lib.search_by_outcome("success")
similar = lib.get_similar_studies(
    industry="SaaS",
    business_model="B2B SaaS",
    customer_segment="product teams"
)
```

Initial dataset includes 5 curated case studies:
1. **Slack** (SaaS, success) - Network effects and product-led growth
2. **Friendster** (Social, failure) - Technical infrastructure collapse
3. **Notion** (SaaS, success) - Community-driven adoption
4. **Yo** (Mobile, failure) - Viral without staying power
5. **GitHub** (SaaS, success) - Developer-first approach

## Usage Example

Complete workflow for a new consultation:

```python
from intake.processor import IntakeProcessor, create_sample_intake
from shared.evaluation import IdeaScorer, RiskIdentifier, AssumptionIdentifier
from shared.case_studies import CaseStudyLibrary, create_initial_case_studies
from shared.schemas import ConsultationReport, ConfidenceLevel

# 1. Get and validate intake
intake_data = create_sample_intake()  # or load from form
processor = IntakeProcessor()
intake_form, errors, warnings = processor.process_intake(intake_data)

if not intake_form:
    print("Validation errors:", errors)
    exit(1)

# 2. Evaluate the idea
scorer = IdeaScorer()
idea_score, rationale, dimensions = scorer.score_idea(intake_form)

# 3. Identify risks
risk_identifier = RiskIdentifier()
risks = risk_identifier.identify_risks(intake_form)

# 4. Identify assumptions
assumption_identifier = AssumptionIdentifier()
assumptions = assumption_identifier.identify_assumptions(intake_form)

# 5. Find relevant case studies
lib = CaseStudyLibrary()
for study in create_initial_case_studies():
    lib.add_study(study)

success_cases = lib.search_by_outcome("success")
failure_cases = lib.search_by_outcome("failure")

# 6. Build consultation report structure
report = ConsultationReport(
    report_id="report_001",
    consultation_id="consult_001",
    business_summary=f"{intake_form.business_name}: {intake_form.idea_description[:100]}",
    idea_strength_score=idea_score,
    idea_strength_rationale=rationale,
    overall_confidence=ConfidenceLevel.MEDIUM,
    confidence_rationale="Based on validation evidence and team composition.",
    top_risks=risks,
    key_assumptions=assumptions,
    success_cases=success_cases[:3],
    failure_cases=failure_cases[:2],
)
```

## Testing

Run the complete test suite:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/unit/test_intake.py -v
```

**Test Coverage**: 51 tests across:
- Unit tests: 44 tests
  - Intake validation and processing (6 tests)
  - Idea scoring (4 tests)
  - Risk identification (5 tests)
  - Assumption identification (4 tests)
  - Case studies (17 tests)
- Integration tests: 7 tests
  - Complete workflows
  - Data quality verification

## Configuration

Edit `src/shared/config.py` to customize:

```python
# Scoring thresholds
IDEA_SCORE_MIN: float = 1.0
IDEA_SCORE_MAX: float = 5.0

# Risk thresholds
AUTO_HUMAN_REVIEW_CRITICAL_RISKS: int = 1
AUTO_HUMAN_REVIEW_LOW_CONFIDENCE: float = 0.50

# Experiment recommendations
MIN_EXPERIMENTS_TO_RECOMMEND: int = 3
MAX_EXPERIMENTS_TO_RECOMMEND: int = 7
```

## Data Quality Standards

### Intake Form Requirements

Required fields:
- business_name, idea_description, problem_statement, proposed_solution
- target_customer, monetization_model, revenue_model
- stage, months_since_inception, geographic_focus, existing_validation

Validation rules:
- Idea description: 50-5000 characters
- Problem statement: 30+ characters
- Business stage: must be one of (idea, pre_launch, launched, early_growth, scaling)
- Months since inception: 0-240 (20 years)

### Case Study Standards

Every case study must include:
- Company name, industry, business model, customer segment
- Founding assumptions and key decisions
- What worked and what failed with detailed explanation
- Go-to-market approach and pricing strategy
- Timeline and outcome
- Source attribution with year and type

### Risk Documentation

Every identified risk must have:
- Clear title and description
- Severity level (critical, high, medium, low)
- Risk type (market, product, team, execution, business_model, financial)
- Specific mitigation strategy
- Confidence level

## Future Phases

### Phase 2 (Weeks 3-4): MVP Build
- Implement retrieval module for evidence gathering
- Add recommendation generation with standardized reports
- Create traceability system for source attribution
- Deploy pilot with real founders

### Phase 3 (Weeks 5-6): Quality Loop
- Add human reviewer workflow
- Integrate feedback capture
- Improve weak sections (generic advice detection)
- Add follow-up chat for experiment tracking

### Phase 4: Operator Assistant
- Weekly check-in format
- KPI-aware bottleneck detection
- Expanded playbooks for pricing, GTM, hiring

### Phase 5: Strategic Advisor
- Multi-quarter memory and scenario planning
- Strategy memo generation
- Trend and risk alerts

## API Documentation

### IntakeValidator.validate()

```python
is_valid: bool
errors: List[str]        # Validation errors
warnings: List[str]      # Warnings (e.g., missing optional fields)
```

### IntakeProcessor.process_intake()

```python
form: Optional[IntakeForm]
errors: List[str]
warnings: List[str]
```

### IdeaScorer.score_idea()

```python
overall_score: float                    # 1-5 scale
rationale: str                          # Detailed explanation
dimension_scores: Dict[str, float]      # Per-dimension scores
```

### RiskIdentifier.identify_risks()

```python
List[Risk]:  # Sorted by severity (critical → low)
```

### AssumptionIdentifier.identify_assumptions()

```python
List[Assumption]:  # Includes user-provided and system-identified
```

### CaseStudyLibrary methods

- `add_study(study: CaseStudy)` → None
- `get_study(case_id: str)` → Optional[CaseStudy]
- `get_all_studies()` → List[CaseStudy]
- `search_by_industry(industry: str)` → List[CaseStudy]
- `search_by_outcome(outcome: str)` → List[CaseStudy]
- `search_by_business_model(model: str)` → List[CaseStudy]
- `get_similar_studies(industry, business_model, customer_segment, limit)` → List[CaseStudy]

## Traceability

All reports should include:
- `report_id`: Unique identifier
- `consultation_id`: Links to source consultation
- `generated_at`: Timestamp
- `frameworks_applied`: List of analysis frameworks used
- `evidence_sources`: Mapping of findings to source case studies
- `disclaimers`: Professional disclaimers and limitations

## Guardrails

1. **Confidence Levels**: Always include confidence and uncertainty
2. **Citations**: Recommend linking to evidence sources
3. **Human Review**: Flag high-stakes recommendations
4. **Professional Disclaimers**: Always include legal/tax/financial disclaimers
5. **Stage-Appropriate**: Adjust guidance based on business maturity

## Contributing

When adding new components:

1. Update schemas.py with new data types
2. Add validation/processing logic
3. Write unit tests (aim for 90%+ coverage)
4. Add integration tests for workflows
5. Document in this guide
6. Update roadmap.md if scope changes
