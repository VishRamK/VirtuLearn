"""
Reusable components for the VirtuLearn Streamlit app
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def render_course_card(course_data, key_suffix=""):
    """Render a course card component"""
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {course_data['name']}")
            st.write(f"**{course_data['category']} | {course_data['level']}**")
            st.write(f"Duration: {course_data['duration']} weeks")
            st.write(f"Rating: {'⭐' * int(course_data['rating'])} ({course_data['rating']})")
            st.write(f"Students: {course_data['students']:,}")
        
        with col2:
            st.markdown(f"<h3 style='color: #1f77b4;'>${course_data['price']}</h3>", 
                       unsafe_allow_html=True)
            
            if st.button("Enroll Now", key=f"enroll_{key_suffix}"):
                st.success(f"Enrolled in {course_data['name']}!")
            
            if st.button("Learn More", key=f"learn_{key_suffix}"):
                st.info(f"Viewing details for {course_data['name']}")
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_progress_chart(data, chart_type="line", title="Progress Chart"):
    """Render a progress chart component"""
    if chart_type == "line":
        fig = px.line(data, x='Date', y='Value', title=title)
    elif chart_type == "bar":
        fig = px.bar(data, x='Date', y='Value', title=title)
    elif chart_type == "area":
        fig = px.area(data, x='Date', y='Value', title=title)
    else:
        fig = px.line(data, x='Date', y='Value', title=title)
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_metric_grid(metrics, columns=4):
    """Render a grid of metrics"""
    cols = st.columns(columns)
    
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            st.metric(
                label=metric.get('label', 'Metric'),
                value=metric.get('value', '0'),
                delta=metric.get('delta', None)
            )


def render_learning_module(module_data, key_suffix=""):
    """Render a learning module component"""
    with st.expander(f"{module_data['name']} - {module_data['status']}"):
        # Progress bar
        progress = module_data.get('progress', 0)
        st.progress(progress / 100)
        st.write(f"Progress: {progress}%")
        
        # Description
        if 'description' in module_data:
            st.write(module_data['description'])
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if progress > 0:
                if st.button(f"Continue", key=f"continue_{key_suffix}"):
                    st.success(f"Continuing {module_data['name']}")
        
        with col2:
            if progress > 0:
                if st.button(f"Review", key=f"review_{key_suffix}"):
                    st.info(f"Reviewing {module_data['name']}")
        
        with col3:
            if progress == 100:
                st.success("✅ Completed")
            elif progress > 0:
                st.warning("🔄 In Progress")
            else:
                st.error("🔒 Locked")


def render_activity_feed(activities, max_items=5):
    """Render an activity feed component"""
    st.subheader("🕒 Recent Activities")
    
    for i, activity in enumerate(activities[:max_items]):
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.write(activity.get('time', 'Unknown'))
            
            with col2:
                st.write(activity.get('description', 'No description'))
            
            with col3:
                status = activity.get('status', 'unknown')
                if status == 'completed':
                    st.success("✅")
                elif status == 'pending':
                    st.warning("⏳")
                elif status == 'failed':
                    st.error("❌")
                else:
                    st.info("ℹ️")
            
            if i < len(activities[:max_items]) - 1:
                st.markdown("---")


def render_goal_tracker(current_value, target_value, label="Goal"):
    """Render a goal tracking component"""
    progress = min(current_value / target_value * 100, 100) if target_value > 0 else 0
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**{label}**")
        st.progress(progress / 100)
        st.write(f"{current_value} / {target_value} ({progress:.1f}%)")
    
    with col2:
        if progress >= 100:
            st.success("🎯 Goal Achieved!")
        elif progress >= 75:
            st.warning("🎯 Almost there!")
        else:
            st.info(f"🎯 Keep going!")


def render_study_streak(streak_days):
    """Render study streak component"""
    if streak_days > 0:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin: 1rem 0;
        ">
            <h3>🔥 Study Streak</h3>
            <h1>{streak_days} Days</h1>
            <p>Keep it up! You're on fire!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: #6c757d;
            margin: 1rem 0;
            border: 2px dashed #dee2e6;
        ">
            <h3>💪 Start Your Streak</h3>
            <p>Study today to begin your streak!</p>
        </div>
        """, unsafe_allow_html=True)


def render_performance_radar(scores, categories):
    """Render a radar chart for performance across categories"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Your Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Performance Across Categories"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_calendar_heatmap(data, date_col, value_col, title="Activity Calendar"):
    """Render a calendar heatmap"""
    # This is a simplified version - you might want to use a proper calendar library
    pivot_data = data.pivot_table(
        index=data[date_col].dt.day_name(),
        columns=data[date_col].dt.week,
        values=value_col,
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_data,
        title=title,
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        xaxis_title="Week of Year",
        yaxis_title="Day of Week"
    )
    
    st.plotly_chart(fig, use_container_width=True)