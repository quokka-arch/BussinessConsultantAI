# Knowledge Foundation

## Objective

Create a trustworthy, structured knowledge base that grounds recommendations in real business outcomes.

## Core Knowledge Layers

### 1) Success/Failure Case Studies

Track structured fields:
- Company, industry, customer segment, business model
- Stage context and founding assumptions
- Key decisions, pivots, GTM and pricing approach
- What worked, what failed, and why
- Outcome and timeline
- Traceability via `source_materials`, `evidence`, and `uncertainty_notes`
- Extraction metadata for prompt version, agent identity, and review status

Primary use:
- Analog matching
- Failure mode prediction
- Recommendation explainability

### 2) Business Framework Library

Initial framework set:
- Lean Canvas
- SWOT
- Porter’s Five Forces
- Jobs-To-Be-Done (JTBD)
- TAM/SAM/SOM
- Unit economics and pricing checks
- AARRR funnel diagnostics

Primary use:
- Consistent analysis lens
- Stage-appropriate diagnostic checklists

### 3) Expert Playbooks

Codify reusable operating guidance from:
- Startup operators
- Consultants
- Product/GTM leaders
- Finance operators

Primary use:
- Decision templates
- Prioritized action sequences
- Contextual tradeoff rules

## MVP Knowledge Target

For the first release, curate:
- 50–100 high-signal case studies
- 10 common failure patterns
- 10 common success patterns
- A compact framework pack for early-stage SaaS

## Data Quality Rules

- Keep source references for every case.
- Separate facts from interpretation.
- Mark stale or uncertain entries.
- Avoid invented companies, metrics, or outcomes.

## Normalized Case Study Schema

Curated or extracted case studies should follow the normalized schema implemented in `src/shared/schemas.py`.

Required business fields:
- `case_id`, `company_name`, `industry`, `business_model`, `customer_segment`
- `stage_at_event`, `founding_assumptions`, `key_decisions`, `major_pivots`
- `go_to_market_approach`, `pricing_strategy`
- `what_worked`, `what_failed`, `failure_modes`
- `why_succeeded_or_failed`, `timeline_months`, `outcome`, `published_year`, `source_type`

Traceability fields required for extracted records:
- `source_materials`: normalized source references with IDs and locators
- `evidence`: field-level excerpts and rationale linked back to `source_id`
- `uncertainty_notes`: open questions, ambiguity, or assumptions made during curation
- `extraction_metadata`: extractor name, prompt version, confidence, timestamp, and review flag

## Seed Dataset Structure

Seed examples live in `/tmp/workspace/quokka-arch/BussinessConsultantAI/data/case_studies/seed_case_studies.json`.

Use that file as the canonical example for how curated records should be stored:
- one JSON array entry per case study
- include both successful and failed businesses
- keep evidence excerpts short and field-specific
- preserve uncertainty instead of forcing false precision

## Extraction Workflow

1. Collect source text and source metadata for a case-study candidate.
2. Run the `case_study_extractor` agent in `src/retrieval/case_study_extractor.py`.
3. Review the draft JSON for evidence quality, missing details, and unsupported claims.
4. Save approved records into `data/case_studies/` as curated JSON entries.
5. Only promote records to the main knowledge base after human review clears `manual_review_required`.
