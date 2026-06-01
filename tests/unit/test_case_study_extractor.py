"""
Unit tests for case study schema validation and extractor behavior.
"""

import json
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from retrieval.case_study_extractor import CaseStudyExtractor
from shared.case_studies import CaseStudyLibrary
from shared.schemas import case_study_from_dict


def _case_study_dataset_dir() -> Path:
    return Path(__file__).parent.parent.parent / "data" / "case_studies"


def _company_dataset_paths():
    return sorted(_case_study_dataset_dir().glob("*.json"))


def _normalize_company_filename(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


class TestCaseStudySchemaValidation:
    """Validate structured case-study records with traceability fields."""

    def test_seed_dataset_examples_validate(self):
        """Seed examples should validate as traceable case studies."""
        dataset_paths = _company_dataset_paths()

        studies = []
        for dataset_path in dataset_paths:
            payload = json.loads(dataset_path.read_text())
            assert payload
            assert {
                _normalize_company_filename(item["company_name"])
                for item in payload
            } == {dataset_path.stem}
            studies.extend(
                case_study_from_dict(item, require_traceability=True)
                for item in payload
            )

        assert len(dataset_paths) == 2
        assert len(studies) == 2
        assert all(study.source_materials for study in studies)
        assert all(study.evidence for study in studies)
        assert all(study.uncertainty_notes for study in studies)

    def test_case_study_requires_traceability_for_extracted_records(self):
        """Traceable validation should reject records without evidence."""
        payload = {
            "case_id": "missing_traceability",
            "company_name": "ExampleCo",
            "industry": "SaaS",
            "business_model": "B2B SaaS",
            "customer_segment": "Operations teams",
            "stage_at_event": "launched",
            "founding_assumptions": ["Teams need a better dashboard."],
            "key_decisions": ["Shipped a self-serve launch."],
            "go_to_market_approach": "Outbound plus content.",
            "pricing_strategy": "Subscription.",
            "what_worked": ["Initial interest from pilot users."],
            "what_failed": [],
            "why_succeeded_or_failed": "Still too early to know the final outcome.",
            "timeline_months": 12,
            "outcome": "ongoing",
            "published_year": 2025,
            "source_type": "interview",
            "uncertainty_notes": [],
        }

        with pytest.raises(ValueError, match="source_materials"):
            case_study_from_dict(payload, require_traceability=True)

    def test_library_json_round_trip_preserves_traceability(self, tmp_path):
        """JSON save/load should preserve nested traceability data."""
        library = CaseStudyLibrary(data_dir=str(tmp_path / "case_studies"))
        for dataset_path in _company_dataset_paths():
            payload = json.loads(dataset_path.read_text())
            for item in payload:
                library.add_study(case_study_from_dict(item, require_traceability=True))

        output_path = tmp_path / "round_trip.json"
        library.save_to_json(str(output_path))

        reloaded = CaseStudyLibrary(data_dir=str(tmp_path / "empty"))
        reloaded.load_from_json(str(output_path))

        slack = reloaded.get_study("seed_slack_success")
        assert slack is not None
        assert slack.source_materials[0].source_id == "slack_case_primary"
        assert slack.evidence[0].field_name == "major_pivots"


class TestCaseStudyExtractor:
    """Validate prompt construction and response parsing for extractor agent."""

    @staticmethod
    def _sample_source_metadata():
        return {
            "source_id": "figma_source",
            "title": "Figma growth article",
            "source_type": "article",
            "url": "https://example.com/figma",
            "published_year": 2024,
            "locator": "Paragraphs 2-5",
        }

    @classmethod
    def _sample_llm_output(cls):
        return {
            "case_id": "figma_growth_case",
            "company_name": "Figma",
            "industry": "SaaS - Design Tools",
            "business_model": "B2B SaaS",
            "customer_segment": "Designers and product teams",
            "stage_at_event": "early_growth",
            "founding_assumptions": [
                "Cloud collaboration would beat desktop workflows."
            ],
            "key_decisions": [
                "Prioritized browser-based collaboration."
            ],
            "major_pivots": [],
            "go_to_market_approach": "Product-led adoption inside design teams.",
            "pricing_strategy": "Freemium with paid team tiers.",
            "what_worked": [
                "Collaboration differentiated the product."
            ],
            "what_failed": [],
            "failure_modes": [],
            "why_succeeded_or_failed": "A collaborative design workflow created strong team-level pull.",
            "timeline_months": 36,
            "outcome": "success",
            "summary": "Collaborative browser design expanded bottom-up.",
            "tags": ["saas", "design"],
            "relevance_to_saas": "high",
            "evidence": [
                {
                    "field_name": "go_to_market_approach",
                    "source_id": "figma_source",
                    "excerpt": "Teams adopted Figma because multiple people could work together in the browser.",
                    "rationale": "Supports the collaborative PLG positioning.",
                    "confidence": "high",
                }
            ],
            "uncertainty_notes": [
                "Pricing details are summarized from public positioning."
            ],
        }

    def test_prompt_includes_traceability_requirements(self):
        """Prompt should explicitly request evidence and uncertainty fields."""
        extractor = CaseStudyExtractor()
        messages = extractor.build_messages(
            source_text="Sample article text",
            source_metadata={
                "source_id": "source_001",
                "title": "Sample article",
                "source_type": "article",
            },
        )

        assert "return JSON only" in messages["system"]
        assert "evidence" in messages["user"]
        assert "uncertainty_notes" in messages["user"]
        assert "source_001" in messages["user"]

    def test_parse_response_injects_source_metadata(self):
        """Extractor should attach workflow source metadata before validation."""
        extractor = CaseStudyExtractor()
        study = extractor.parse_response(
            llm_output=self._sample_llm_output(),
            source_metadata=self._sample_source_metadata(),
        )

        assert study.source_materials[0].source_id == "figma_source"
        assert study.extraction_metadata is not None
        assert study.extraction_metadata.extractor_agent == "case_study_extractor"
        assert study.source_url == "https://example.com/figma"

    def test_run_passes_selected_model_to_model_aware_callable(self):
        """Extractor should support model-aware callables without hardcoding a provider."""
        called = {}
        extractor = CaseStudyExtractor(default_model="gpt-4.1-mini")

        def model_caller(model, messages):
            called["model"] = model
            called["messages"] = messages
            return self._sample_llm_output()

        study = extractor.run(
            source_text="Sample article text",
            source_metadata=self._sample_source_metadata(),
            llm_callable=model_caller,
            model="claude-sonnet-4.5",
        )

        assert called["model"] == "claude-sonnet-4.5"
        assert "Sample article text" in called["messages"]["user"]
        assert study.company_name == "Figma"

    def test_run_supports_legacy_prompt_only_callable(self):
        """Extractor should remain compatible with prompt-only callables."""
        called = {}
        extractor = CaseStudyExtractor()

        def legacy_caller(messages):
            called["messages"] = messages
            return self._sample_llm_output()

        study = extractor.run(
            source_text="Sample article text",
            source_metadata=self._sample_source_metadata(),
            llm_callable=legacy_caller,
        )

        assert "Sample article text" in called["messages"]["user"]
        assert study.company_name == "Figma"

    def test_parse_response_requires_uncertainty_notes(self):
        """Extractor should reject outputs that omit uncertainty handling."""
        extractor = CaseStudyExtractor()

        with pytest.raises(ValueError, match="uncertainty_notes"):
            extractor.parse_response(
                llm_output={
                    "case_id": "bad_case",
                    "company_name": "BadCo",
                    "industry": "SaaS",
                    "business_model": "B2B SaaS",
                    "customer_segment": "Finance teams",
                    "stage_at_event": "launched",
                    "founding_assumptions": ["Finance teams want automation."],
                    "key_decisions": ["Launched quickly."],
                    "major_pivots": [],
                    "go_to_market_approach": "Outbound sales.",
                    "pricing_strategy": "Subscription.",
                    "what_worked": ["Some early interest."],
                    "what_failed": [],
                    "failure_modes": [],
                    "why_succeeded_or_failed": "Outcome remains uncertain.",
                    "timeline_months": 10,
                    "outcome": "ongoing",
                    "summary": "An incomplete extraction example.",
                    "tags": ["saas"],
                    "relevance_to_saas": "high",
                    "evidence": [
                        {
                            "field_name": "what_worked",
                            "source_id": "bad_source",
                            "excerpt": "A handful of teams expressed interest.",
                            "rationale": "Supports early traction.",
                            "confidence": "medium",
                        }
                    ],
                },
                source_metadata={
                    "source_id": "bad_source",
                    "title": "Bad source",
                    "source_type": "article",
                },
            )
