"""
Configuration management for Business Consultant AI.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration container."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CASE_STUDIES_DIR: Path = DATA_DIR / "case_studies"
    FRAMEWORKS_DIR: Path = DATA_DIR / "frameworks"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Evaluation settings
    IDEA_SCORE_MIN: float = 1.0
    IDEA_SCORE_MAX: float = 5.0
    CONFIDENCE_THRESHOLD_HIGH: float = 0.85
    CONFIDENCE_THRESHOLD_MEDIUM: float = 0.65
    
    # Risk thresholds
    AUTO_HUMAN_REVIEW_CRITICAL_RISKS: int = 1  # Critical risks trigger review
    AUTO_HUMAN_REVIEW_LOW_CONFIDENCE: float = 0.50
    
    # Case study settings
    MIN_CASE_STUDIES_FOR_CONSULTATION: int = 3
    NUM_COMPARABLE_CASES_TO_SHOW: int = 3
    
    # Experiment settings
    MIN_EXPERIMENTS_TO_RECOMMEND: int = 3
    MAX_EXPERIMENTS_TO_RECOMMEND: int = 7
    
    # 30-day plan settings
    WEEKS_IN_PLAN: int = 4
    MIN_ACTION_ITEMS_PER_WEEK: int = 2
    MAX_ACTION_ITEMS_PER_WEEK: int = 5
    
    def __post_init__(self):
        """Ensure all directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CASE_STUDIES_DIR.mkdir(parents=True, exist_ok=True)
        self.FRAMEWORKS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """Set global config (mainly for testing)."""
    global _config
    _config = config
