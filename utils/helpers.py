"""
Utility functions for the VirtuLearn Streamlit app
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


def generate_sample_data(days=90):
    """Generate sample data for demonstration purposes"""
    np.random.seed(42)
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         end=datetime.now(), freq='D')
    
    data = pd.DataFrame({
        'Date': dates,
        'Study_Hours': np.random.exponential(2, len(dates)),
        'Quiz_Score': np.random.normal(85, 10, len(dates)),
        'Assignments_Completed': np.random.poisson(1, len(dates)),
        'Videos_Watched': np.random.poisson(2, len(dates))
    })
    
    # Clean the data
    data['Quiz_Score'] = np.clip(data['Quiz_Score'], 0, 100)
    data['Study_Hours'] = np.clip(data['Study_Hours'], 0, 8)
    
    return data


def format_number(num, suffix=''):
    """Format numbers with appropriate suffixes (K, M, B)"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B{suffix}"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M{suffix}"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K{suffix}"
    else:
        return f"{num:.0f}{suffix}"


def calculate_streak(data, column, threshold=0):
    """Calculate the current streak for a given column"""
    if len(data) == 0:
        return 0
    
    # Sort by date descending
    data_sorted = data.sort_values('Date', ascending=False)
    
    streak = 0
    for value in data_sorted[column]:
        if value > threshold:
            streak += 1
        else:
            break
    
    return streak


def get_performance_insight(current_score, previous_score):
    """Generate performance insights based on score comparison"""
    if current_score > previous_score:
        return "📈 Great improvement! Keep up the good work!"
    elif current_score == previous_score:
        return "➡️ Steady performance. Try to push for improvement!"
    else:
        return "📉 Performance dipped. Review your study strategy."


def create_progress_summary(data):
    """Create a summary of learning progress"""
    if len(data) == 0:
        return {}
    
    total_hours = data['Study_Hours'].sum()
    avg_score = data['Quiz_Score'].mean()
    total_assignments = data['Assignments_Completed'].sum()
    total_videos = data['Videos_Watched'].sum()
    
    # Calculate trends (last 7 days vs previous 7 days)
    recent_data = data.tail(7)
    previous_data = data.iloc[-14:-7] if len(data) >= 14 else data.head(7)
    
    recent_avg_hours = recent_data['Study_Hours'].mean()
    previous_avg_hours = previous_data['Study_Hours'].mean()
    hours_trend = recent_avg_hours - previous_avg_hours
    
    recent_avg_score = recent_data['Quiz_Score'].mean()
    previous_avg_score = previous_data['Quiz_Score'].mean()
    score_trend = recent_avg_score - previous_avg_score
    
    return {
        'total_hours': total_hours,
        'avg_score': avg_score,
        'total_assignments': total_assignments,
        'total_videos': total_videos,
        'hours_trend': hours_trend,
        'score_trend': score_trend,
        'study_streak': calculate_streak(data, 'Study_Hours', 0.5)
    }


def load_css():
    """Load custom CSS for styling"""
    css = """
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .course-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        background-color: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        background-color: #1f77b4;
        height: 20px;
        transition: width 0.3s ease;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def display_metric_card(title, value, delta=None, delta_color="normal"):
    """Display a custom metric card"""
    delta_html = ""
    if delta is not None:
        color = "green" if delta_color == "normal" and "↗" in str(delta) else "red" if "↘" in str(delta) else "gray"
        delta_html = f'<div style="color: {color}; font-size: 14px;">{delta}</div>'
    
    card_html = f"""
    <div class="metric-container">
        <div style="font-size: 14px; color: #666;">{title}</div>
        <div style="font-size: 24px; font-weight: bold; margin: 5px 0;">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


@st.cache_data
def load_sample_courses():
    """Load sample course data (cached for performance)"""
    courses = {
        "Course Name": [
            "Python Fundamentals", "Data Science with Python", "Web Development with React",
            "Machine Learning Basics", "Statistics and Probability", "Advanced Python Programming",
            "Full Stack Development", "Database Management", "Linear Algebra for ML", "Calculus for Engineers"
        ],
        "Category": [
            "Programming", "Data Science", "Web Development",
            "AI/ML", "Mathematics", "Programming",
            "Web Development", "Database", "Mathematics", "Mathematics"
        ],
        "Level": [
            "Beginner", "Intermediate", "Beginner",
            "Advanced", "Beginner", "Advanced",
            "Intermediate", "Intermediate", "Intermediate", "Beginner"
        ],
        "Duration": [4, 8, 6, 12, 5, 6, 8, 4, 10, 12],
        "Rating": [4.8, 4.6, 4.5, 4.9, 4.3, 4.7, 4.4, 4.2, 4.1, 4.0],
        "Students": [1250, 890, 1100, 560, 780, 340, 620, 450, 290, 380],
        "Price": [49, 99, 79, 149, 59, 89, 119, 69, 89, 99]
    }
    return pd.DataFrame(courses)


def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_greeting():
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! 🌅"
    elif hour < 17:
        return "Good afternoon! ☀️"
    else:
        return "Good evening! 🌙"