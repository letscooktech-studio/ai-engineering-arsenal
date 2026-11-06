"""OutcomeLab: versioned, synthetic production-risk demonstrations."""
from .runner import CONTRACTS, ScenarioResult, run_all, run_scenario

__all__ = ["CONTRACTS", "ScenarioResult", "run_all", "run_scenario"]

__version__ = "0.2.0rc1"
