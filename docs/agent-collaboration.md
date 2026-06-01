# Agent Collaboration Guide

## Goal
Enable multiple AI agents (and humans) to collaborate safely on consulting outputs.

## Suggested Agent Roles

1. **Intake Agent**
   - Structures founder inputs and highlights missing information
2. **Research Agent**
   - Retrieves relevant cases, benchmarks, and frameworks
3. **Diagnosis Agent**
   - Identifies top risks, assumptions, and bottlenecks
4. **Recommendation Agent**
   - Produces prioritized actions with tradeoffs
5. **Reviewer Agent / Human Reviewer**
   - Checks factual grounding, hallucination risk, and actionability

## Shared Output Contract
All agents should use a common response shape:
1. Business summary
2. Comparable patterns
3. Assumptions
4. Risks
5. Recommended experiments/actions
6. Confidence and rationale

## Collaboration Rules
- Pass structured artifacts between agents, not only plain text
- Preserve source references and confidence metadata
- Separate observations from recommendations
- Escalate high-stakes legal/tax/finance decisions to professionals
- Keep a decision log so advice quality can be evaluated over time
