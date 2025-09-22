# Model package for VirtuLearn evaluation system

from .lecture_evaluator import (
    run_evaluation_sync,
    generate_comprehensive_evaluation_report
)

from .correctness_evaluator import calculate_correctness_score
from .engagement_evaluator import calculate_engagement_score
from .topic_evaluator import calculate_topic_coverage_score

__all__ = [
    'run_evaluation_sync',
    'generate_comprehensive_evaluation_report',
    'calculate_correctness_score',
    'calculate_engagement_score', 
    'calculate_topic_coverage_score'
]