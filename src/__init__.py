"""Business Consultant AI - Multi-agent system for founder guidance."""

__version__ = "0.1.0"
__author__ = "Business Consultant AI Team"

# Import key modules
from shared.schemas import (
    IntakeForm,
    ConsultationReport,
    CaseStudy,
    Risk,
    Assumption,
    Experiment,
    ActionItem,
)
from intake.processor import IntakeProcessor, IntakeValidator
from shared.evaluation import IdeaScorer, RiskIdentifier, AssumptionIdentifier
from shared.case_studies import CaseStudyLibrary

__all__ = [
    "IntakeForm",
    "ConsultationReport",
    "CaseStudy",
    "IntakeProcessor",
    "IntakeValidator",
    "IdeaScorer",
    "RiskIdentifier",
    "AssumptionIdentifier",
    "CaseStudyLibrary",
]
