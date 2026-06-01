# Phase 1 Setup & Quick Start Guide

## Installation

```bash
# Clone and navigate to project
cd BussinessConsultantAI

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_intake.py -v

# Run with coverage report
python -m pytest tests/ --cov=src
```

### Use the System

```python
from src.intake.processor import IntakeProcessor, create_sample_intake
from src.shared.evaluation import IdeaScorer, RiskIdentifier, AssumptionIdentifier
from src.shared.case_studies import CaseStudyLibrary, create_initial_case_studies

# Process a sample intake form
processor = IntakeProcessor()
intake_data = create_sample_intake()
form, errors, warnings = processor.process_intake(intake_data)

# Score the idea
scorer = IdeaScorer()
score, rationale, dimensions = scorer.score_idea(form)
print(f"Idea Score: {score}/5.0")

# Identify risks
identifier = RiskIdentifier()
risks = identifier.identify_risks(form)
print(f"Identified {len(risks)} risks")

# Get case studies
lib = CaseStudyLibrary()
for study in create_initial_case_studies():
    lib.add_study(study)
similar = lib.get_similar_studies("SaaS", "B2B SaaS", "product teams")
print(f"Found {len(similar)} similar cases")
```

## Project Structure

```
src/
  shared/           # Core schemas and utilities
  intake/           # Intake form processing
  retrieval/        # (Phase 2) Evidence retrieval
  reasoning/        # (Phase 2) Analysis engines
  recommendation/   # (Phase 2) Report generation
  memory/           # (Phase 3) Business memory
  feedback/         # (Phase 3) Feedback loop

tests/
  unit/             # Unit tests (44 tests)
  integration/      # Integration tests (7 tests)

data/               # Knowledge base (to be populated)
config/             # Configuration files
docs/               # Architecture documentation
```

## What's Included in Phase 1

✅ **Completed**:
- Data schemas and types
- Intake form validation and processing
- Idea strength scoring (1-5 scale)
- Risk identification and prioritization
- Assumption identification
- Case study knowledge base with 5 curated examples
- Comprehensive test suite (51 tests)
- Configuration management
- Documentation

📋 **Schema Definitions**:
- IntakeForm - Business context capture
- Risk - Risk identification with mitigation
- Assumption - Key assumptions to validate
- Experiment - Validation experiment recommendations
- ActionItem - 30-day action plan
- ConsultationReport - Standard output format
- CaseStudy - Knowledge base entries

🎯 **Test Coverage**:
- 51 automated tests, all passing
- Unit tests for all components
- Integration tests for end-to-end workflows
- Data quality validation

## Configuration

Edit `src/shared/config.py` for:
- Scoring thresholds
- Risk severity settings
- Number of recommendations
- File paths and logging levels

## Next Steps

### For Phase 2 Implementation:
1. Implement retrieval module for evidence gathering
2. Build recommendation generation
3. Create standardized report templates
4. Add source attribution and traceability

### For Extending Case Studies:
1. Add more case studies to `create_initial_case_studies()`
2. Implement case study import from CSV/JSON
3. Add metadata tagging system
4. Build case study search indexing

### For Production Deployment:
1. Add database backend (PostgreSQL recommended)
2. Implement API layer (FastAPI recommended)
3. Add authentication and authorization
4. Build web interface
5. Add monitoring and logging

## Troubleshooting

### Tests fail with import errors
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m pytest tests/
```

### Module not found errors
```bash
# Run from project root
cd BussinessConsultantAI
python -m pytest tests/
```

## Documentation Files

- `README.md` - Project overview
- `docs/product-vision.md` - Product strategy
- `docs/architecture.md` - System architecture
- `docs/roadmap.md` - Implementation roadmap
- `PHASE1_IMPLEMENTATION.md` - Phase 1 details
- `SETUP.md` - This file

## Resources

- **Product Vision**: `docs/product-vision.md`
- **Architecture Details**: `docs/architecture.md`
- **Implementation Guide**: `PHASE1_IMPLEMENTATION.md`
- **Roadmap**: `docs/roadmap.md`
- **Test Code**: `tests/` directory

## Support

For issues or questions:
1. Check the documentation
2. Review test examples
3. Look at `create_sample_intake()` for usage patterns
4. Check config.py for customization options
