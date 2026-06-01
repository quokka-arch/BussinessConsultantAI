"""
Unit tests for case study module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from shared.case_studies import CaseStudyLibrary, create_initial_case_studies
from shared.schemas import BusinessStage


class TestCaseStudyLibrary:
    """Test case study library operations."""
    
    def test_create_library(self):
        """Test creating a case study library."""
        lib = CaseStudyLibrary()
        assert lib is not None
    
    def test_add_and_retrieve_study(self):
        """Test adding and retrieving case studies."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        lib.add_study(studies[0])
        retrieved = lib.get_study(studies[0].case_id)
        
        assert retrieved is not None
        assert retrieved.company_name == studies[0].company_name
    
    def test_get_all_studies(self):
        """Test retrieving all studies."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        for study in studies:
            lib.add_study(study)
        
        all_studies = lib.get_all_studies()
        assert len(all_studies) == len(studies)
    
    def test_search_by_industry(self):
        """Test searching studies by industry."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        for study in studies:
            lib.add_study(study)
        
        saas_studies = lib.search_by_industry("SaaS")
        assert len(saas_studies) > 0
        assert all("SaaS" in s.industry for s in saas_studies)
    
    def test_search_by_outcome(self):
        """Test searching studies by outcome."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        for study in studies:
            lib.add_study(study)
        
        success_studies = lib.search_by_outcome("success")
        failure_studies = lib.search_by_outcome("failure")
        
        assert len(success_studies) > 0
        assert len(failure_studies) > 0
        assert all(s.outcome == "success" for s in success_studies)
        assert all(s.outcome == "failure" for s in failure_studies)
    
    def test_search_by_business_model(self):
        """Test searching studies by business model."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        for study in studies:
            lib.add_study(study)
        
        saas_studies = lib.search_by_business_model("SaaS")
        assert len(saas_studies) > 0
        assert all("SaaS" in s.business_model for s in saas_studies)
    
    def test_get_similar_studies(self):
        """Test finding similar studies for analog matching."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        
        for study in studies:
            lib.add_study(study)
        
        # Find similar to Slack (SaaS, team communication)
        similar = lib.get_similar_studies(
            industry="SaaS",
            business_model="B2B SaaS",
            customer_segment="teams",
            limit=3
        )
        
        assert len(similar) > 0
        assert len(similar) <= 3


class TestInitialCaseStudies:
    """Test initial case study dataset."""
    
    def test_creates_initial_studies(self):
        """Test that initial case studies are created."""
        studies = create_initial_case_studies()
        
        assert len(studies) >= 5
        assert all(s.case_id for s in studies)
        assert all(s.company_name for s in studies)
    
    def test_studies_have_required_fields(self):
        """Test that studies have all required fields."""
        studies = create_initial_case_studies()
        
        for study in studies:
            assert study.case_id
            assert study.company_name
            assert study.industry
            assert study.business_model
            assert study.customer_segment
            assert study.outcome in ["success", "failure", "acquisition", "shutdown", "ongoing"]
            assert study.why_succeeded_or_failed
    
    def test_studies_have_actionable_insights(self):
        """Test that studies contain actionable insights."""
        studies = create_initial_case_studies()
        
        for study in studies:
            assert len(study.what_worked) > 0 or len(study.what_failed) > 0
            assert study.go_to_market_approach
            assert study.pricing_strategy
    
    def test_failure_studies_have_failure_modes(self):
        """Test that failure studies document failure modes."""
        studies = create_initial_case_studies()
        failure_studies = [s for s in studies if s.outcome == "failure"]
        
        assert len(failure_studies) > 0
        for study in failure_studies:
            # Should have detailed failure explanation
            assert len(study.why_succeeded_or_failed) > 30
    
    def test_success_studies_have_working_insights(self):
        """Test that success studies document what worked."""
        studies = create_initial_case_studies()
        success_studies = [s for s in studies if s.outcome == "success"]
        
        assert len(success_studies) > 0
        for study in success_studies:
            assert len(study.what_worked) > 0
    
    def test_studies_cover_different_industries(self):
        """Test that studies span multiple industries."""
        studies = create_initial_case_studies()
        industries = set(s.industry for s in studies)
        
        assert len(industries) > 2  # Should have multiple industries
    
    def test_studies_have_source_attribution(self):
        """Test that studies include source attribution."""
        studies = create_initial_case_studies()
        
        for study in studies:
            assert study.source_type in [
                "blog", "case_study", "book", "interview", 
                "company", "historical", "news"
            ]
            assert study.published_year > 0


class TestCaseStudyCuration:
    """Test case study curation and relevance."""
    
    def test_relevant_cases_marked_for_saas(self):
        """Test that SaaS-relevant cases are properly marked."""
        studies = create_initial_case_studies()
        
        for study in studies:
            if "SaaS" in study.industry or "SaaS" in study.business_model:
                assert study.relevance_to_saas in ["high", "medium"]
    
    def test_studies_tagged_appropriately(self):
        """Test that studies are properly tagged."""
        studies = create_initial_case_studies()
        
        for study in studies:
            assert len(study.tags) > 0
            # Tags should be lowercase and hyphenated
            for tag in study.tags:
                assert tag.islower() or "-" in tag
    
    def test_analog_matching_for_new_business(self):
        """Test analog matching for a new business scenario."""
        lib = CaseStudyLibrary()
        studies = create_initial_case_studies()
        for study in studies:
            lib.add_study(study)
        
        # New SaaS analytics startup
        similar = lib.get_similar_studies(
            industry="SaaS - Analytics",
            business_model="B2B SaaS",
            customer_segment="product teams",
            limit=5
        )
        
        # Should find some relevant studies
        assert len(similar) > 0
        # Should be SaaS studies
        assert any("SaaS" in s.industry for s in similar)
