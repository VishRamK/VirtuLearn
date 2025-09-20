# VirtuLearn Utils Package

from .helpers import *
from .data_manager import lecture_data_manager, LectureDataManager

__all__ = [
    'generate_sample_data',
    'format_number', 
    'calculate_streak',
    'get_performance_insight',
    'create_progress_summary',
    'load_css',
    'display_metric_card',
    'load_sample_courses',
    'validate_email',
    'get_greeting',
    'lecture_data_manager',
    'LectureDataManager'
]