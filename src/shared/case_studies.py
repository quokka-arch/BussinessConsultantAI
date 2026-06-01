"""
Case Study Knowledge Base: Curated success and failure patterns.

This module manages the case study database used for analog matching
and pattern recognition.
"""

import csv
import json
from typing import List, Optional, Dict
from pathlib import Path
from shared.schemas import CaseStudy, BusinessStage
import logging

logger = logging.getLogger(__name__)


class CaseStudyLibrary:
    """Manages the case study knowledge base."""
    
    def __init__(self, data_dir: str = "data/case_studies"):
        """Initialize case study library."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.studies: Dict[str, CaseStudy] = {}
        self._load_studies()
    
    def _load_studies(self) -> None:
        """Load case studies from data files."""
        # For now, this will be populated manually or via CSV import
        pass
    
    def add_study(self, study: CaseStudy) -> None:
        """Add a case study to the library."""
        self.studies[study.case_id] = study
        logger.info(f"Added case study: {study.company_name} ({study.case_id})")
    
    def get_study(self, case_id: str) -> Optional[CaseStudy]:
        """Get a single case study by ID."""
        return self.studies.get(case_id)
    
    def get_all_studies(self) -> List[CaseStudy]:
        """Get all case studies."""
        return list(self.studies.values())
    
    def search_by_industry(self, industry: str) -> List[CaseStudy]:
        """Search case studies by industry."""
        return [s for s in self.studies.values() if industry.lower() in s.industry.lower()]
    
    def search_by_outcome(self, outcome: str) -> List[CaseStudy]:
        """Search case studies by outcome (success/failure)."""
        return [s for s in self.studies.values() if s.outcome == outcome]
    
    def search_by_business_model(self, model: str) -> List[CaseStudy]:
        """Search case studies by business model."""
        return [s for s in self.studies.values() if model.lower() in s.business_model.lower()]
    
    def get_similar_studies(
        self,
        industry: str,
        business_model: str,
        customer_segment: str,
        limit: int = 5
    ) -> List[CaseStudy]:
        """
        Find similar case studies for analog matching.
        
        Args:
            industry: Target industry
            business_model: Target business model
            customer_segment: Target customer segment
            limit: Maximum number to return
            
        Returns:
            List of similar case studies
        """
        matches = []
        for study in self.studies.values():
            score = 0
            
            # Score relevance
            if industry.lower() in study.industry.lower():
                score += 3
            if business_model.lower() in study.business_model.lower():
                score += 3
            if customer_segment.lower() in study.customer_segment.lower():
                score += 2
            
            if score > 0:
                matches.append((study, score))
        
        # Sort by score and return top N
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:limit]]
    
    def save_to_json(self, filepath: str) -> None:
        """Save case studies to JSON file."""
        data = []
        for study in self.studies.values():
            data.append({
                "case_id": study.case_id,
                "company_name": study.company_name,
                "industry": study.industry,
                "business_model": study.business_model,
                "customer_segment": study.customer_segment,
                "stage_at_event": study.stage_at_event.value,
                "founding_assumptions": study.founding_assumptions,
                "key_decisions": study.key_decisions,
                "major_pivots": study.major_pivots,
                "go_to_market_approach": study.go_to_market_approach,
                "pricing_strategy": study.pricing_strategy,
                "what_worked": study.what_worked,
                "what_failed": study.what_failed,
                "failure_modes": study.failure_modes,
                "why_succeeded_or_failed": study.why_succeeded_or_failed,
                "timeline_months": study.timeline_months,
                "outcome": study.outcome,
                "published_year": study.published_year,
                "source_url": study.source_url,
                "source_type": study.source_type,
                "tags": study.tags,
                "relevance_to_saas": study.relevance_to_saas,
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} case studies to {filepath}")
    
    def load_from_json(self, filepath: str) -> None:
        """Load case studies from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for item in data:
            study = CaseStudy(
                case_id=item["case_id"],
                company_name=item["company_name"],
                industry=item["industry"],
                business_model=item["business_model"],
                customer_segment=item["customer_segment"],
                stage_at_event=BusinessStage(item["stage_at_event"]),
                founding_assumptions=item["founding_assumptions"],
                key_decisions=item["key_decisions"],
                major_pivots=item.get("major_pivots", []),
                go_to_market_approach=item["go_to_market_approach"],
                pricing_strategy=item["pricing_strategy"],
                what_worked=item["what_worked"],
                what_failed=item["what_failed"],
                failure_modes=item.get("failure_modes", []),
                why_succeeded_or_failed=item["why_succeeded_or_failed"],
                timeline_months=item["timeline_months"],
                outcome=item["outcome"],
                published_year=item["published_year"],
                source_url=item.get("source_url"),
                source_type=item["source_type"],
                tags=item.get("tags", []),
                relevance_to_saas=item.get("relevance_to_saas", "medium"),
            )
            self.add_study(study)
        
        logger.info(f"Loaded {len(data)} case studies from {filepath}")


def create_initial_case_studies() -> List[CaseStudy]:
    """Create initial set of curated case studies for MVP."""
    studies = [
        CaseStudy(
            case_id="cs001",
            company_name="Slack",
            industry="SaaS - Team Communication",
            business_model="B2B SaaS",
            customer_segment="Engineering teams, enterprises",
            stage_at_event=BusinessStage.LAUNCHED,
            founding_assumptions=[
                "Teams need better internal communication than email",
                "Teams would pay premium for organized conversations",
                "Integration with dev tools would drive adoption"
            ],
            key_decisions=[
                "Started as internal tool at Tiny Speck",
                "Focused on engineering teams first",
                "Free tier with paid upgrades",
            ],
            major_pivots=[
                "Pivoted from gaming platform to internal tool",
                "Eventually became standalone product"
            ],
            go_to_market_approach="Product-led growth, free tier, engineering-first",
            pricing_strategy="Freemium model with per-user paid tiers",
            what_worked=[
                "Network effects within organizations",
                "Viral adoption through free tier",
                "Strong integrations ecosystem",
                "Premium features justified higher pricing"
            ],
            what_failed=[
                "Competing with established enterprise tools initially underestimated"
            ],
            failure_modes=[],
            why_succeeded_or_failed="Found product-market fit by targeting high-collaboration teams with product-led growth. Integration ecosystem and network effects locked in adoption.",
            timeline_months=48,
            outcome="success",
            published_year=2013,
            source_url="https://slack.com",
            source_type="company",
            tags=["saas", "communication", "network-effects", "product-led-growth"],
            relevance_to_saas="high"
        ),
        CaseStudy(
            case_id="cs002",
            company_name="Friendster",
            industry="Social Network",
            business_model="B2C Social Network",
            customer_segment="General users",
            stage_at_event=BusinessStage.LAUNCHED,
            founding_assumptions=[
                "Users want to connect with people they know online",
                "Can monetize through ads and premium features",
                "Can scale globally from day one"
            ],
            key_decisions=[
                "Focused on real identity (vs. pseudonymous)",
                "Launched in US first",
                "Advertisement-heavy model early"
            ],
            major_pivots=[
                "Later tried pivoting to gaming platform"
            ],
            go_to_market_approach="Viral, word-of-mouth among friends",
            pricing_strategy="Freemium with ads",
            what_worked=[
                "Early viral adoption in US",
                "Strong initial network effects"
            ],
            what_failed=[
                "Poor engineering infrastructure - site frequently unavailable",
                "Late response to Facebook competition",
                "Failed to build gaming platform pivot",
                "Users migrated to Facebook over performance and features"
            ],
            failure_modes=[
                "Technical infrastructure failure during growth",
                "Inability to compete with better-funded competitor",
                "Delayed international expansion"
            ],
            why_succeeded_or_failed="Had early traction but failed due to poor engineering (site downtime) and inability to respond to Facebook competition. Shows importance of infrastructure.",
            timeline_months=60,
            outcome="failure",
            published_year=2003,
            source_url="https://en.wikipedia.org/wiki/Friendster",
            source_type="historical",
            tags=["social-network", "viral", "technical-failure", "competition"],
            relevance_to_saas="medium"
        ),
        CaseStudy(
            case_id="cs003",
            company_name="Notion",
            industry="SaaS - Productivity",
            business_model="B2B SaaS",
            customer_segment="Knowledge workers, teams, creators",
            stage_at_event=BusinessStage.EARLY_GROWTH,
            founding_assumptions=[
                "Teams need flexible, customizable workspace",
                "Database + documents + wiki in one product",
                "Community-driven growth could work"
            ],
            key_decisions=[
                "Kept product free while iterating",
                "Built for power users first",
                "Invested heavily in documentation and templates"
            ],
            major_pivots=[
                "From project management to flexible workspace platform"
            ],
            go_to_market_approach="Product-led growth, creator community, templates",
            pricing_strategy="Freemium with team/business tiers",
            what_worked=[
                "Powerful, flexible product attracted power users",
                "Community contributions (templates, tutorials)",
                "Creator and educator adoption drove B2B sales",
                "Low initial infrastructure costs (indie-friendly)"
            ],
            what_failed=[],
            failure_modes=[],
            why_succeeded_or_failed="Built powerful product and cultivated engaged community before monetization. Users became advocates, driving bottom-up adoption.",
            timeline_months=48,
            outcome="success",
            published_year=2016,
            source_url="https://notion.so",
            source_type="company",
            tags=["saas", "productivity", "community", "product-led-growth"],
            relevance_to_saas="high"
        ),
        CaseStudy(
            case_id="cs004",
            company_name="Yo",
            industry="Mobile App - Messaging",
            business_model="B2C Mobile",
            customer_segment="General mobile users",
            stage_at_event=BusinessStage.LAUNCHED,
            founding_assumptions=[
                "Users want ultra-simple one-click notifications",
                "Can monetize through premium features",
                "Simplicity is a feature"
            ],
            key_decisions=[
                "App does only one thing: send 'Yo' messages",
                "No backend infrastructure optimization"
            ],
            major_pivots=[],
            go_to_market_approach="Viral marketing, novelty factor",
            pricing_strategy="Free app with premium features",
            what_worked=[
                "Viral attention due to novelty",
                "Raised significant funding"
            ],
            what_failed=[
                "No real use case beyond novelty",
                "Users quickly stopped using after initial install",
                "Limited monetization despite funding",
                "No sustainable business model"
            ],
            failure_modes=[
                "One-trick pony problem",
                "Viral hype without sustainable engagement",
                "Unclear value prop beyond novelty"
            ],
            why_succeeded_or_failed="Got viral attention but couldn't convert to engagement or revenue. Novelty ≠ sustainable business.",
            timeline_months=24,
            outcome="failure",
            published_year=2014,
            source_url="https://en.wikipedia.org/wiki/Yo_(app)",
            source_type="historical",
            tags=["mobile", "viral-failure", "novelty", "no-moat"],
            relevance_to_saas="low"
        ),
        CaseStudy(
            case_id="cs005",
            company_name="GitHub",
            industry="SaaS - Developer Tools",
            business_model="B2B SaaS",
            customer_segment="Software developers, teams, enterprises",
            stage_at_event=BusinessStage.EARLY_GROWTH,
            founding_assumptions=[
                "Developers would prefer hosted Git over self-hosted",
                "Collaborative development tools would have strong demand",
                "Network effects around code would drive growth"
            ],
            key_decisions=[
                "Focused on developer experience (not enterprise sales)",
                "Built around Git (existing standard)",
                "Free tier for open-source projects",
                "Built community features (stars, follows)"
            ],
            major_pivots=[],
            go_to_market_approach="Product-led growth, open-source focus, developer community",
            pricing_strategy="Freemium with private repo tiers",
            what_worked=[
                "Solved real pain point for developers",
                "Strong developer advocacy and community",
                "Open-source projects drove adoption",
                "Network effects and visibility",
                "Enterprise tier added later"
            ],
            what_failed=[],
            failure_modes=[],
            why_succeeded_or_failed="Hit product-market fit by solving developer pain points and building strong community. Network effects of code visibility drove growth.",
            timeline_months=72,
            outcome="success",
            published_year=2008,
            source_url="https://github.com",
            source_type="company",
            tags=["saas", "developer-tools", "network-effects", "open-source"],
            relevance_to_saas="high"
        ),
    ]
    
    return studies
