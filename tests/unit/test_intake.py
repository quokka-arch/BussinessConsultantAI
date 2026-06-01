"""
Unit tests for intake module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from intake.processor import IntakeValidator, IntakeProcessor, create_sample_intake
from shared.schemas import BusinessStage, IntakeForm


class TestIntakeValidator:
    """Test intake form validation."""
    
    def test_required_fields_validation(self):
        """Test that missing required fields are caught."""
        incomplete_data = {
            "business_name": "Test Company",
            "idea_description": "Test idea description that is long enough"
        }
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(incomplete_data)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("required" in error.lower() for error in errors)
    
    def test_valid_intake_data(self):
        """Test that valid intake data passes validation."""
        data = create_sample_intake()
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(data)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_text_field_length_validation(self):
        """Test text field length constraints."""
        data = create_sample_intake()
        data["idea_description"] = "Too short"  # Less than MIN_IDEA_DESCRIPTION_LENGTH
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(data)
        
        assert not is_valid
        assert any("too short" in error.lower() for error in errors)
    
    def test_numeric_field_validation(self):
        """Test numeric field range validation."""
        data = create_sample_intake()
        data["months_since_inception"] = 500  # Way beyond max
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(data)
        
        assert not is_valid
        assert any("between" in error.lower() for error in errors)
    
    def test_enum_field_validation(self):
        """Test enum field validation."""
        data = create_sample_intake()
        data["stage"] = "invalid_stage"
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(data)
        
        assert not is_valid
        assert any("stage" in error.lower() for error in errors)
    
    def test_warnings_for_missing_team(self):
        """Test warning when no team members provided."""
        data = create_sample_intake()
        data["team_members"] = []
        
        validator = IntakeValidator()
        is_valid, errors, warnings = validator.validate(data)
        
        assert is_valid
        assert len(warnings) > 0
        assert any("team" in warning.lower() for warning in warnings)


class TestIntakeProcessor:
    """Test intake form processing."""
    
    def test_process_valid_intake(self):
        """Test processing valid intake data."""
        data = create_sample_intake()
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        assert len(errors) == 0
        assert isinstance(form, IntakeForm)
        assert form.business_name == "TechFlow Analytics"
    
    def test_process_invalid_intake_returns_errors(self):
        """Test that invalid data returns errors."""
        data = {"business_name": "Test"}  # Incomplete
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is None
        assert len(errors) > 0
    
    def test_team_members_converted_properly(self):
        """Test that team members are properly converted."""
        data = create_sample_intake()
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        assert len(form.team_members) == 2
        assert form.team_members[0].name == "Alice Chen"
        assert form.team_members[0].role == "CEO/Co-founder"
    
    def test_constraints_converted_properly(self):
        """Test that constraints are properly converted."""
        data = create_sample_intake()
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        assert len(form.constraints) >= 2
        assert form.constraints[0].type == "budget"
    
    def test_business_stage_enum_conversion(self):
        """Test that business stage is converted to enum."""
        data = create_sample_intake()
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        assert form.stage == BusinessStage.IDEA
        assert isinstance(form.stage, BusinessStage)


class TestIntakeForms:
    """Integration tests for intake forms."""
    
    def test_sample_intake_valid(self):
        """Test that sample intake is valid."""
        data = create_sample_intake()
        
        processor = IntakeProcessor()
        form, errors, warnings = processor.process_intake(data)
        
        assert form is not None
        assert len(errors) == 0
        assert form.business_name == "TechFlow Analytics"
        assert form.target_customer == "Early-stage SaaS companies (Series A-B) with product-led growth strategies"
        assert form.stage == BusinessStage.IDEA
