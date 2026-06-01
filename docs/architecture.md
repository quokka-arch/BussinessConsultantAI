# Architecture & Workflow Modules

## End-to-End Workflow

1. Intake
2. Retrieval & Research
3. Reasoning
4. Recommendation
5. Memory Update
6. Feedback & Learning

## Module Definitions

### 1) Intake Module

Purpose: collect structured business context.

Typical inputs:
- Business idea and target customer
- Problem statement and value proposition
- Business model and monetization plan
- Stage, geography, team profile, constraints

Output: normalized consultation context object.

### 2) Retrieval & Research Module

Purpose: gather relevant evidence and analogs.

Responsibilities:
- Retrieve comparable success/failure case studies
- Pull stage-relevant frameworks and benchmarks
- Gather references from internal knowledge base
- Run the side `case_study_extractor` agent to convert raw source material into traceable case-study records

Output: ranked evidence package with source metadata.

### 3) Reasoning Module

Purpose: diagnose situation and prioritize decision risks.

Responsibilities:
- Compare user case against known patterns
- Identify bottlenecks and high-risk assumptions
- Build hypotheses and tradeoff analysis

Output: structured diagnosis with confidence and uncertainty labels.

### 4) Recommendation Module

Purpose: produce founder-ready action guidance.

Responsibilities:
- Generate prioritized recommendations
- Propose validation experiments and milestones
- Explain rationale and expected impact

Output: standard consultation report.

### 5) Memory Module

Purpose: maintain longitudinal context per business.

Stores:
- Prior advice and decisions
- KPI snapshots and experiment outcomes
- Resolved/unresolved risks

Output: updated business memory profile for future consultations.

### 6) Feedback Module

Purpose: measure usefulness and improve quality over time.

Responsibilities:
- Capture founder feedback and adoption rate
- Track recommendation outcomes
- Flag vague, generic, or incorrect guidance

Output: evaluation signals for iteration and model improvement.

## Standard Consultation / Report Format

1. Business Summary
2. Comparable Cases (success + failure)
3. Key Assumptions
4. Top Risks
5. Recommended Experiments
6. 30-Day Action Plan
7. Confidence & Uncertainty Notes
8. Human Review Flags (if high-stakes)
