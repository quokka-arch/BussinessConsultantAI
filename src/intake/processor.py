"""
Intake Module: Structured data collection and validation.

This module handles collection and validation of business context
needed for idea validation consultation.
"""

from typing import List, Tuple, Optional
from shared.schemas import (
    IntakeForm, TeamMember, Constraint, BusinessStage, 
    to_dict
)
import logging

logger = logging.getLogger(__name__)


class IntakeValidator:
    """Validates intake form data."""
    
    # Required fields for consultation
    REQUIRED_FIELDS = {
        "business_name",
        "idea_description",
        "problem_statement",
        "proposed_solution",
        "target_customer",
        "monetization_model",
        "revenue_model",
        "stage",
        "months_since_inception",
        "geographic_focus",
        "existing_validation",
    }
    
    # Validation rules
    MIN_IDEA_DESCRIPTION_LENGTH = 50
    MAX_IDEA_DESCRIPTION_LENGTH = 5000
    MIN_PROBLEM_STATEMENT_LENGTH = 30
    
    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, intake_data: dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate intake form data.
        
        Args:
            intake_data: Dictionary with form data
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check required fields
        self._validate_required_fields(intake_data)
        
        # Validate text fields
        if "idea_description" in intake_data:
            self._validate_text_field(
                intake_data["idea_description"],
                "idea_description",
                self.MIN_IDEA_DESCRIPTION_LENGTH,
                self.MAX_IDEA_DESCRIPTION_LENGTH
            )
        
        if "problem_statement" in intake_data:
            self._validate_text_field(
                intake_data["problem_statement"],
                "problem_statement",
                self.MIN_PROBLEM_STATEMENT_LENGTH,
                5000
            )
        
        # Validate business stage
        if "stage" in intake_data:
            self._validate_enum(intake_data["stage"], "stage", BusinessStage)
        
        # Validate numeric fields
        if "months_since_inception" in intake_data:
            self._validate_numeric(
                intake_data["months_since_inception"],
                "months_since_inception",
                min_val=0,
                max_val=240  # 20 years
            )
        
        # Check for team
        if not intake_data.get("team_members"):
            self.warnings.append(
                "No team members provided. Highly experienced teams are key success factor."
            )
        
        # Check for constraints
        if intake_data.get("constraints") and len(intake_data["constraints"]) > 5:
            self.warnings.append(
                "Multiple constraints may limit execution speed. Prioritize top 3."
            )
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_required_fields(self, data: dict) -> None:
        """Check that all required fields are present."""
        missing = self.REQUIRED_FIELDS - set(data.keys())
        if missing:
            for field in sorted(missing):
                self.errors.append(f"Missing required field: {field}")
    
    def _validate_text_field(
        self,
        value: str,
        field_name: str,
        min_len: int,
        max_len: int
    ) -> None:
        """Validate text field length."""
        if not isinstance(value, str):
            self.errors.append(f"{field_name} must be a string")
            return
        
        if len(value.strip()) < min_len:
            self.errors.append(
                f"{field_name} too short (min {min_len} chars)"
            )
        elif len(value) > max_len:
            self.errors.append(
                f"{field_name} too long (max {max_len} chars)"
            )
    
    def _validate_numeric(
        self,
        value: int,
        field_name: str,
        min_val: int,
        max_val: int
    ) -> None:
        """Validate numeric field range."""
        if not isinstance(value, int):
            self.errors.append(f"{field_name} must be an integer")
            return
        
        if value < min_val or value > max_val:
            self.errors.append(
                f"{field_name} must be between {min_val} and {max_val}"
            )
    
    def _validate_enum(self, value: str, field_name: str, enum_class) -> None:
        """Validate enum field."""
        valid_values = [e.value for e in enum_class]
        if value not in valid_values:
            self.errors.append(
                f"{field_name} must be one of: {', '.join(valid_values)}"
            )


class IntakeProcessor:
    """Process and normalize intake form data."""
    
    def __init__(self):
        """Initialize processor."""
        self.validator = IntakeValidator()
    
    def process_intake(self, intake_data: dict) -> Tuple[Optional[IntakeForm], List[str], List[str]]:
        """
        Process raw intake data into normalized IntakeForm.
        
        Args:
            intake_data: Raw dictionary from form submission
            
        Returns:
            Tuple of (intake_form, errors, warnings)
        """
        # Validate first
        is_valid, errors, warnings = self.validator.validate(intake_data)
        
        if not is_valid:
            logger.error(f"Intake validation failed: {errors}")
            return None, errors, warnings
        
        try:
            # Build team members
            team_members = []
            if intake_data.get("team_members"):
                for tm in intake_data["team_members"]:
                    team_members.append(TeamMember(
                        name=tm.get("name", ""),
                        role=tm.get("role", ""),
                        experience_years=tm.get("experience_years", 0),
                        relevant_expertise=tm.get("relevant_expertise", [])
                    ))
            
            # Build constraints
            constraints = []
            if intake_data.get("constraints"):
                for c in intake_data["constraints"]:
                    constraints.append(Constraint(
                        type=c.get("type", ""),
                        description=c.get("description", ""),
                        impact=c.get("impact", "medium")
                    ))
            
            # Create IntakeForm
            form = IntakeForm(
                business_name=intake_data.get("business_name", ""),
                idea_description=intake_data.get("idea_description", ""),
                problem_statement=intake_data.get("problem_statement", ""),
                proposed_solution=intake_data.get("proposed_solution", ""),
                target_customer=intake_data.get("target_customer", ""),
                monetization_model=intake_data.get("monetization_model", ""),
                revenue_model=intake_data.get("revenue_model", ""),
                price_point=intake_data.get("price_point"),
                stage=BusinessStage(intake_data.get("stage", "idea")),
                months_since_inception=intake_data.get("months_since_inception", 0),
                planned_launch_date=intake_data.get("planned_launch_date"),
                geographic_focus=intake_data.get("geographic_focus", ""),
                team_members=team_members,
                existing_validation=intake_data.get("existing_validation", ""),
                current_users_or_revenue=intake_data.get("current_users_or_revenue"),
                constraints=constraints,
                key_assumptions=intake_data.get("key_assumptions", []),
                open_questions=intake_data.get("open_questions", []),
                submitter_email=intake_data.get("submitter_email"),
            )
            
            logger.info(f"Intake processed successfully for: {form.business_name}")
            return form, [], warnings
            
        except Exception as e:
            error_msg = f"Error processing intake: {str(e)}"
            logger.error(error_msg)
            return None, [error_msg], warnings


def create_sample_intake() -> dict:
    """Create a sample intake form for testing."""
    return {
        "business_name": "TechFlow Analytics",
        "idea_description": "A real-time analytics platform designed specifically for SaaS companies to track product usage patterns and user journey insights without extensive data engineering. We provide pre-built dashboards and automated insights for product-led growth metrics.",
        "problem_statement": "SaaS product teams lack real-time visibility into how users interact with their products, leading to delayed product decisions and missed growth opportunities. Current solutions require significant data engineering setup or are too generic.",
        "proposed_solution": "A plug-and-play analytics SDK that integrates in minutes and automatically tracks user behavior. Includes pre-built dashboards optimized for product-led growth KPIs.",
        "target_customer": "Early-stage SaaS companies (Series A-B) with product-led growth strategies",
        "monetization_model": "SaaS",
        "revenue_model": "subscription",
        "price_point": "$299-$999/month based on usage",
        "stage": "idea",
        "months_since_inception": 2,
        "planned_launch_date": "2024-09-01",
        "geographic_focus": "US",
        "team_members": [
            {
                "name": "Alice Chen",
                "role": "CEO/Co-founder",
                "experience_years": 8,
                "relevant_expertise": ["SaaS product", "Analytics", "Go-to-market"]
            },
            {
                "name": "Bob Johnson",
                "role": "CTO/Co-founder",
                "experience_years": 6,
                "relevant_expertise": ["Backend engineering", "Data infrastructure"]
            }
        ],
        "existing_validation": "Conducted 15 customer interviews with product managers at Series A companies. 12 expressed strong interest and willingness to pay.",
        "current_users_or_revenue": "None yet",
        "constraints": [
            {
                "type": "budget",
                "description": "Current runway: 6 months. No external funding raised yet.",
                "impact": "high"
            },
            {
                "type": "timeline",
                "description": "Founders committed to 6 months before considering other projects.",
                "impact": "high"
            }
        ],
        "key_assumptions": [
            "Product-led growth SaaS companies are willing to adopt new analytics tools",
            "Our integration process is faster than existing solutions",
            "Current pricing model aligns with customer value perception"
        ],
        "open_questions": [
            "What is the optimal time to market vs. feature completeness?",
            "Should we focus on one vertical (e.g., developer tools) first?",
            "What are the go-to-market channels with highest CAC efficiency?"
        ],
        "submitter_email": "alice@techflow.ai"
    }
