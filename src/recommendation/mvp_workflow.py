"""
Phase 2 MVP workflow: intake -> retrieval -> standardized report generation.
"""

from datetime import UTC, datetime
from typing import Dict, List, Optional, Tuple

from intake.processor import IntakeProcessor
from retrieval.evidence_retriever import EvidenceRetriever, RetrievedEvidence
from shared.case_studies import CaseStudyLibrary, create_initial_case_studies
from shared.evaluation import AssumptionIdentifier, IdeaScorer, RiskIdentifier
from shared.schemas import (
    ActionItem,
    Assumption,
    ConfidenceLevel,
    ConsultationReport,
    Experiment,
    ExperimentType,
    IntakeForm,
    Risk,
    RiskSeverity,
)


class Phase2MVPWorkflow:
    """Initial end-to-end orchestration for the Phase 2 MVP report flow."""

    def __init__(self, case_library: Optional[CaseStudyLibrary] = None) -> None:
        self.intake_processor = IntakeProcessor()
        self.idea_scorer = IdeaScorer()
        self.risk_identifier = RiskIdentifier()
        self.assumption_identifier = AssumptionIdentifier()

        self.case_library = case_library or CaseStudyLibrary()
        if not self.case_library.get_all_studies():
            for study in create_initial_case_studies():
                self.case_library.add_study(study)

        self.retriever = EvidenceRetriever(self.case_library)

    def run(
        self,
        intake_data: Dict,
        consultation_id: str = "consultation_mvp",
        report_id: Optional[str] = None,
    ) -> Tuple[Optional[ConsultationReport], List[str], List[str]]:
        """Generate a standardized consultation report from intake data."""
        intake_form, errors, warnings = self.intake_processor.process_intake(intake_data)
        if intake_form is None:
            return None, errors, warnings

        idea_score, rationale, _ = self.idea_scorer.score_idea(intake_form)
        risks = self.risk_identifier.identify_risks(intake_form)
        assumptions = self.assumption_identifier.identify_assumptions(intake_form)
        retrieved = self.retriever.retrieve(intake_form)

        generated_report_id = report_id or f"report_{consultation_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        report = self._build_report(
            report_id=generated_report_id,
            consultation_id=consultation_id,
            intake_form=intake_form,
            idea_score=idea_score,
            rationale=rationale,
            risks=risks,
            assumptions=assumptions,
            retrieved=retrieved,
        )
        return report, [], warnings

    def _build_report(
        self,
        report_id: str,
        consultation_id: str,
        intake_form: IntakeForm,
        idea_score: float,
        rationale: str,
        risks: List[Risk],
        assumptions: List[Assumption],
        retrieved: RetrievedEvidence,
    ) -> ConsultationReport:
        confidence = self._determine_confidence(idea_score, retrieved)
        requires_human_review = confidence == ConfidenceLevel.LOW or any(
            risk.severity == RiskSeverity.CRITICAL for risk in risks
        )

        recommended_experiments = self._build_experiments(assumptions, risks)
        thirty_day_plan = self._build_30_day_plan(recommended_experiments)
        uncertainty_notes = self._build_uncertainty_notes(retrieved, confidence)

        evidence_sources = dict(retrieved.evidence_sources)
        evidence_sources["risks"] = [risk.title for risk in risks[:3]]
        evidence_sources["assumptions"] = [assumption.statement for assumption in assumptions[:3]]

        return ConsultationReport(
            report_id=report_id,
            consultation_id=consultation_id,
            business_summary=(
                f"{intake_form.business_name} is a {intake_form.stage.value} stage business "
                f"targeting {intake_form.target_customer} with a {intake_form.monetization_model} model."
            ),
            idea_strength_score=idea_score,
            idea_strength_rationale=rationale,
            overall_confidence=confidence,
            confidence_rationale=(
                "Confidence is based on intake completeness, baseline scoring signals, and "
                "retrieved comparable-case coverage."
            ),
            success_cases=retrieved.success_cases,
            failure_cases=retrieved.failure_cases,
            key_assumptions=assumptions,
            top_risks=risks,
            recommended_experiments=recommended_experiments,
            thirty_day_plan=thirty_day_plan,
            uncertainty_notes=uncertainty_notes,
            requires_human_review=requires_human_review,
            review_reason=(
                "Low confidence signals detected; manual reviewer should verify assumptions."
                if requires_human_review
                else None
            ),
            frameworks_applied=["baseline_evaluation_rubric", "analog_case_matching"],
            evidence_sources=evidence_sources,
            disclaimers=[
                "This report provides strategic guidance, not legal, tax, or investment advice.",
                "Validate high-impact decisions with domain experts before execution.",
            ],
        )

    @staticmethod
    def _determine_confidence(idea_score: float, retrieved: RetrievedEvidence) -> ConfidenceLevel:
        if idea_score >= 4.0 and retrieved.success_cases and retrieved.failure_cases:
            return ConfidenceLevel.HIGH
        if idea_score >= 3.0:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    @staticmethod
    def _build_experiments(assumptions: List[Assumption], risks: List[Risk]) -> List[Experiment]:
        experiments: List[Experiment] = []
        for index, assumption in enumerate(assumptions[:3], start=1):
            experiments.append(
                Experiment(
                    title=f"Assumption validation sprint {index}",
                    type=ExperimentType.CUSTOMER_INTERVIEW,
                    description=f"Validate assumption: {assumption.statement}",
                    objectives=[
                        "Test assumption against target users",
                        "Collect evidence for go/no-go decisions",
                    ],
                    duration_days=7,
                    success_criteria=[
                        "At least 5 qualified interviews completed",
                        "Assumption confidence increases with clear evidence",
                    ],
                    key_metrics=["interview_completion_rate", "assumption_confidence_delta"],
                    estimated_effort="medium",
                    related_risks=[risk.title for risk in risks[:2]],
                    related_assumptions=[assumption.statement],
                    rationale=assumption.validation_approach,
                )
            )
        return experiments

    @staticmethod
    def _build_30_day_plan(experiments: List[Experiment]) -> List[ActionItem]:
        action_items: List[ActionItem] = []
        for week in range(1, 5):
            if week == 1:
                title = "Finalize validation backlog"
                description = "Align assumptions, interview scripts, and candidate list."
            elif week == 2:
                title = "Execute customer interviews"
                description = "Run interviews and synthesize insight themes."
            elif week == 3:
                title = "Run fast prototype checks"
                description = "Test revised positioning or prototype with target users."
            else:
                title = "Decide next execution focus"
                description = "Prioritize roadmap based on experiment outcomes."

            action_items.append(
                ActionItem(
                    priority=week,
                    week=week,
                    title=title,
                    description=description,
                    depends_on=[experiments[0].title] if week > 1 and experiments else [],
                    estimated_hours=8 if week == 1 else 12,
                    success_metric="Weekly milestone completed with documented findings",
                )
            )
        return action_items

    @staticmethod
    def _build_uncertainty_notes(
        retrieved: RetrievedEvidence, confidence: ConfidenceLevel
    ) -> List[str]:
        notes: List[str] = []
        if not retrieved.success_cases:
            notes.append("No close success analog retrieved; broaden case-study dataset coverage.")
        if not retrieved.failure_cases:
            notes.append("No close failure analog retrieved; risk pattern confidence is reduced.")
        if confidence == ConfidenceLevel.LOW:
            notes.append("Overall confidence is low; require human reviewer sign-off before execution.")
        if not notes:
            notes.append("Comparable-case coverage is baseline; continue expanding evidence depth per segment.")
        return notes
