"""
Phase 2 retrieval helper for comparable-case evidence packaging.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from shared.case_studies import CaseStudyLibrary
from shared.schemas import CaseStudy, ComparableCase, IntakeForm


@dataclass
class RetrievedEvidence:
    """Structured retrieval output used by recommendation/report generation."""

    success_cases: List[ComparableCase] = field(default_factory=list)
    failure_cases: List[ComparableCase] = field(default_factory=list)
    evidence_sources: Dict[str, List[str]] = field(default_factory=dict)


class EvidenceRetriever:
    """Retrieve comparable success/failure cases for an intake context."""

    def __init__(self, library: CaseStudyLibrary, cases_per_outcome: int = 2) -> None:
        self.library = library
        self.cases_per_outcome = cases_per_outcome

    def retrieve(self, intake: IntakeForm) -> RetrievedEvidence:
        """Build a retrieval package from similar studies and fallback samples."""
        similar = self.library.get_similar_studies(
            industry=intake.monetization_model,
            business_model=intake.monetization_model,
            customer_segment=intake.target_customer,
            limit=max(self.cases_per_outcome * 3, 6),
        )

        success_studies = [study for study in similar if study.outcome == "success"]
        failure_studies = [study for study in similar if study.outcome == "failure"]

        if len(success_studies) < self.cases_per_outcome:
            success_studies = self._fill_from_library(
                selected=success_studies,
                fallback=self.library.search_by_outcome("success"),
            )
        if len(failure_studies) < self.cases_per_outcome:
            failure_studies = self._fill_from_library(
                selected=failure_studies,
                fallback=self.library.search_by_outcome("failure"),
            )

        success_cases = [
            self._to_comparable_case(study, intake)
            for study in success_studies[: self.cases_per_outcome]
        ]
        failure_cases = [
            self._to_comparable_case(study, intake)
            for study in failure_studies[: self.cases_per_outcome]
        ]

        return RetrievedEvidence(
            success_cases=success_cases,
            failure_cases=failure_cases,
            evidence_sources={
                "success_cases": [case.case_id for case in success_cases],
                "failure_cases": [case.case_id for case in failure_cases],
            },
        )

    def _fill_from_library(self, selected: List[CaseStudy], fallback: List[CaseStudy]) -> List[CaseStudy]:
        """Fill with non-duplicate fallback studies up to the configured limit."""
        selected_ids = {study.case_id for study in selected}
        combined = list(selected)

        for study in fallback:
            if study.case_id in selected_ids:
                continue
            combined.append(study)
            selected_ids.add(study.case_id)
            if len(combined) >= self.cases_per_outcome:
                break
        return combined

    @staticmethod
    def _to_comparable_case(study: CaseStudy, intake: IntakeForm) -> ComparableCase:
        """Convert a full case study into compact comparable-case report format."""
        key_insight = ""
        if study.outcome == "success" and study.what_worked:
            key_insight = study.what_worked[0]
        elif study.outcome == "failure" and study.what_failed:
            key_insight = study.what_failed[0]
        else:
            key_insight = study.why_succeeded_or_failed

        relevance_reason = (
            f"{study.company_name} offers a {study.business_model} analog for "
            f"{intake.monetization_model} strategy decisions."
        )
        return ComparableCase(
            case_id=study.case_id,
            company_name=study.company_name,
            relevance_reason=relevance_reason,
            key_insight=key_insight,
            outcome=study.outcome,
            source=study.source_url or study.source_type,
        )
