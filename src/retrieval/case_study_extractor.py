"""
Case study extraction agent for converting raw source material into schema-aligned records.
"""

import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Callable, Dict, Optional, Union

from shared.schemas import (
    CaseStudy,
    CaseStudySource,
    ConfidenceLevel,
    case_study_from_dict,
)


DEFAULT_PROMPT_VERSION = "case-study-extractor-v1"


class CaseStudyExtractor:
    """LLM-facing helper that builds prompts and validates extracted case studies."""

    def __init__(
        self,
        agent_name: str = "case_study_extractor",
        prompt_version: str = DEFAULT_PROMPT_VERSION,
    ) -> None:
        self.agent_name = agent_name
        self.prompt_version = prompt_version

    def build_messages(
        self,
        source_text: str,
        source_metadata: Dict[str, Any],
    ) -> Dict[str, str]:
        """Build system and user prompts for the extraction agent."""
        system_prompt = (
            "You are case_study_extractor, a careful research assistant for "
            "Business Consultant AI. Read source material and return JSON only. "
            "Populate the normalized case-study schema, cite every important claim "
            "in the evidence array, preserve uncertainty in uncertainty_notes, and "
            "never invent metrics, dates, pivots, or outcomes that are not grounded "
            "in the source text."
        )
        user_prompt = (
            "Extract one structured business case study from the source below.\n\n"
            "Required JSON fields:\n"
            "- case_id\n"
            "- company_name\n"
            "- industry\n"
            "- business_model\n"
            "- customer_segment\n"
            "- stage_at_event\n"
            "- founding_assumptions\n"
            "- key_decisions\n"
            "- major_pivots\n"
            "- go_to_market_approach\n"
            "- pricing_strategy\n"
            "- what_worked\n"
            "- what_failed\n"
            "- failure_modes\n"
            "- why_succeeded_or_failed\n"
            "- timeline_months\n"
            "- outcome\n"
            "- published_year\n"
            "- source_type\n"
            "- summary\n"
            "- tags\n"
            "- relevance_to_saas\n"
            "- evidence (list of objects with field_name, source_id, excerpt, rationale, confidence, locator)\n"
            "- uncertainty_notes\n\n"
            "Traceability rules:\n"
            "- Use source_id "
            f"'{source_metadata['source_id']}' in every evidence item unless another source_id is provided.\n"
            "- Capture ambiguity and missing details in uncertainty_notes.\n"
            "- Keep what_worked and what_failed grounded in explicit facts or cautious synthesis.\n\n"
            f"Source metadata: {json.dumps(source_metadata, indent=2, sort_keys=True)}\n\n"
            f"Source text:\n{source_text}"
        )
        return {
            "system": system_prompt,
            "user": user_prompt,
        }

    def run(
        self,
        source_text: str,
        source_metadata: Dict[str, Any],
        llm_callable: Callable[[Dict[str, str]], Union[str, Dict[str, Any]]],
    ) -> CaseStudy:
        """Execute extraction with a supplied LLM callable."""
        messages = self.build_messages(source_text, source_metadata)
        llm_output = llm_callable(messages)
        return self.parse_response(
            llm_output=llm_output,
            source_metadata=source_metadata,
        )

    def parse_response(
        self,
        llm_output: Union[str, Dict[str, Any]],
        source_metadata: Dict[str, Any],
    ) -> CaseStudy:
        """Parse and validate an LLM response into a CaseStudy object."""
        payload = json.loads(llm_output) if isinstance(llm_output, str) else deepcopy(llm_output)
        payload = self._ensure_source_defaults(payload, source_metadata)
        payload = self._ensure_extraction_metadata(payload)
        return case_study_from_dict(payload, require_traceability=True)

    def _ensure_source_defaults(
        self,
        payload: Dict[str, Any],
        source_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Inject source attribution defaults from the workflow input."""
        payload.setdefault("source_url", source_metadata.get("url"))
        payload.setdefault("source_type", source_metadata.get("source_type", "article"))
        payload.setdefault("published_year", source_metadata.get("published_year", datetime.now(UTC).year))

        if "source_materials" not in payload or not payload["source_materials"]:
            payload["source_materials"] = [
                self._source_material_dict(source_metadata)
            ]

        source_ids = {
            source["source_id"]
            for source in payload["source_materials"]
        }
        expected_source_id = source_metadata["source_id"]
        if expected_source_id not in source_ids:
            payload["source_materials"].append(self._source_material_dict(source_metadata))

        return payload

    def _ensure_extraction_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inject extractor metadata so downstream review can trace provenance."""
        payload.setdefault(
            "extraction_metadata",
            {
                "extractor_agent": self.agent_name,
                "prompt_version": self.prompt_version,
                "extraction_confidence": ConfidenceLevel.MEDIUM.value,
                "extraction_notes": [
                    "Draft extracted by LLM agent; human review required before curation."
                ],
                "manual_review_required": True,
                "extracted_at": datetime.now(UTC).isoformat(),
            },
        )
        return payload

    @staticmethod
    def _source_material_dict(source_metadata: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Normalize workflow source metadata into a schema-aligned source entry."""
        source = CaseStudySource(
            source_id=source_metadata["source_id"],
            title=source_metadata["title"],
            source_type=source_metadata.get("source_type", "article"),
            url=source_metadata.get("url"),
            locator=source_metadata.get("locator"),
            published_year=source_metadata.get("published_year"),
            notes=source_metadata.get("notes"),
        )
        return {
            "source_id": source.source_id,
            "title": source.title,
            "source_type": source.source_type,
            "url": source.url,
            "locator": source.locator,
            "published_year": source.published_year,
            "notes": source.notes,
        }
