# Architecture

## System Overview
This product should be built as a workflow system, not a single free-form chatbot.

## Core Modules

1. **Intake Module**
   - Captures company profile, goals, stage, constraints
2. **Research Module**
   - Retrieves relevant business cases, benchmarks, frameworks
3. **Reasoning Module**
   - Diagnoses risks, bottlenecks, and missing assumptions
4. **Recommendation Module**
   - Produces ranked actions, tradeoffs, and expected impact
5. **Memory Module**
   - Stores historical decisions, KPIs, experiments, and outcomes
6. **Feedback Module**
   - Captures usefulness and learning signal from user outcomes

## Recommendation Pipeline

1. Retrieval (cases + frameworks + benchmarks)
2. Diagnosis (risk categories + likely bottlenecks)
3. Recommendation (prioritized actions + tradeoffs)
4. Explainability (why this advice + assumptions + confidence)

## Suggested Starter Stack
- Frontend: Next.js
- Backend: Python or Node.js
- LLM API: GPT-class model
- Data: SQL + vector index
- Analytics: feedback + outcome tracking

## Guardrails
- Distinguish facts vs. inference
- Cite supporting evidence when possible
- Show confidence
- Recommend professional review for legal/tax/financial decisions
