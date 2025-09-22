import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Lecture Analytics", page_icon="�")

st.title("� Lecture Analytics & Insights")

st.markdown("""
This page provides comprehensive analytics for individual lectures, helping teachers understand 
the effectiveness of their content and identify areas for improvement.
""")

# Sample lecture data
lecture_data = {
    "Lecture Title": [
        "Introduction to Derivatives",
        "Limits and Continuity", 
        "Function Graphs",
        "Polynomial Functions",
        "Trigonometric Functions",
        "Integration Basics",
        "Applications of Calculus",
        "Differential Equations"
    ],
    "Date": [
        "2024-09-18", "2024-09-15", "2024-09-13", "2024-09-11",
        "2024-09-09", "2024-09-06", "2024-09-04", "2024-09-02"
    ],
    "Duration": [52, 48, 55, 50, 53, 49, 58, 56],
    "Word_Count": [2847, 2650, 3120, 2890, 2750, 2980, 3200, 3050],
    "Engagement_Score": [92, 88, 85, 90, 87, 91, 89, 86],
    "Clarity_Score": [8.7, 8.5, 8.2, 8.9, 8.6, 8.8, 8.4, 8.3],
    "Student_Questions": [15, 12, 8, 18, 14, 16, 11, 13],
    "Comprehension_Rate": [78, 75, 72, 82, 76, 80, 74, 73]
}

lectures_df = pd.DataFrame(lecture_data)
lectures_df['Date'] = pd.to_datetime(lectures_df['Date'])

# Sidebar for lecture selection and filters
st.sidebar.subheader("🎯 Select Analysis Focus")

selected_lecture = st.sidebar.selectbox(
    "Choose Lecture to Analyze:",
    lectures_df['Lecture Title'].tolist()
)

analysis_type = st.sidebar.selectbox(
    "Analysis Type:",
    ["Detailed Analysis", "Comparative Analysis", "Trend Analysis", "Content Analysis"]
)

# Date range for trend analysis
if analysis_type == "Trend Analysis":
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
        max_value=datetime.now().date()
    )

# Main content based on analysis type
if analysis_type == "Detailed Analysis":
    st.subheader(f"📝 Detailed Analysis: {selected_lecture}")
    
    # Get selected lecture data
    lecture_info = lectures_df[lectures_df['Lecture Title'] == selected_lecture].iloc[0]
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{lecture_info['Duration']} min", 
                 "2 min over planned" if lecture_info['Duration'] > 50 else "✅ On time")
    
    with col2:
        st.metric("Engagement Score", f"{lecture_info['Engagement_Score']}%", 
                 f"↗️ +{lecture_info['Engagement_Score'] - 85}%" if lecture_info['Engagement_Score'] > 85 else "→ Average")
    
    with col3:
        st.metric("Word Count", f"{lecture_info['Word_Count']:,}", 
                 "12% above average" if lecture_info['Word_Count'] > 2800 else "✅ Appropriate")
    
    with col4:
        st.metric("Student Questions", f"{lecture_info['Student_Questions']}", 
                 f"↗️ +{lecture_info['Student_Questions'] - 12}" if lecture_info['Student_Questions'] > 12 else "→ Average")
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Content Metrics", "🎯 Engagement Analysis", "📝 Content Quality", "🔍 AI Insights"])
    
    with tab1:
        st.subheader("Content Distribution")
        
        # Simulate content breakdown
        content_types = ['Explanation', 'Examples', 'Q&A', 'Review', 'Practice']
        time_spent = [25, 12, 8, 4, 3]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(values=time_spent, names=content_types, 
                        title="Time Distribution by Content Type")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Speaking pace analysis
            speaking_data = pd.DataFrame({
                'Metric': ['Words per Minute', 'Pauses per Minute', 'Question Frequency'],
                'Value': [142, 4.2, 0.3],
                'Optimal Range': ['120-160', '3-5', '0.2-0.5'],
                'Status': ['✅ Optimal', '✅ Good', '✅ Good']
            })
            st.dataframe(speaking_data, hide_index=True)
    
    with tab2:
        st.subheader("Student Engagement Timeline")
        
        # Simulate engagement over time
        time_points = list(range(0, lecture_info['Duration'], 5))
        engagement_timeline = np.random.normal(lecture_info['Engagement_Score'], 5, len(time_points))
        engagement_timeline = np.clip(engagement_timeline, 70, 100)
        
        fig = px.line(x=time_points, y=engagement_timeline, 
                     title="Engagement Throughout Lecture",
                     labels={'x': 'Time (minutes)', 'y': 'Engagement %'})
        fig.add_hline(y=85, line_dash="dash", line_color="red", 
                     annotation_text="Target Engagement")
        st.plotly_chart(fig, use_container_width=True)
        
        # Engagement factors
        st.subheader("Engagement Factors")
        factors = ['Visual Aids', 'Interactive Elements', 'Real Examples', 'Student Participation', 'Clear Explanations']
        scores = [8.5, 7.8, 9.2, 8.1, 8.9]
        
        fig = px.bar(x=factors, y=scores, title="Engagement Factor Scores",
                    color=scores, color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Content Quality Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Readability Analysis")
            readability = {
                'Metric': ['Flesch Reading Ease', 'Grade Level', 'Avg Sentence Length', 'Complex Words %'],
                'Score': [72.3, '9th Grade', '18 words', '15%'],
                'Status': ['✅ Good', '✅ Appropriate', '⚠️ High', '✅ Good']
            }
            st.dataframe(pd.DataFrame(readability), hide_index=True)
        
        with col2:
            st.subheader("Concept Coverage")
            concepts = ['Main Topic', 'Supporting Concepts', 'Examples', 'Practice', 'Summary']
            coverage = [95, 88, 85, 70, 92]
            
            fig = px.bar(x=concepts, y=coverage, title="Concept Coverage %",
                        color=coverage, color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🤖 AI-Generated Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("🌟 **Strengths Identified:**")
            st.write("• Excellent use of real-world examples")
            st.write("• Good pacing with natural pauses")
            st.write("• Clear mathematical explanations")
            st.write("• Strong student engagement")
            
            st.info("💡 **Specific Recommendations:**")
            st.write("• Add 2-minute group discussion at 25min mark")
            st.write("• Include 3 more practice problems")
            st.write("• Use more visual diagrams for complex concepts")
        
        with col2:
            st.warning("⚠️ **Areas for Improvement:**")
            st.write("• Reduce average sentence length (currently 18 words)")
            st.write("• Add more interactive elements in middle section")
            st.write("• Provide more immediate feedback opportunities")
            
            # Improvement priority
            st.subheader("🎯 Improvement Priority")
            improvements = ['Sentence Clarity', 'Interactive Elements', 'Practice Time', 'Visual Aids']
            priority_scores = [9, 7, 6, 5]
            
            fig = px.bar(x=improvements, y=priority_scores, title="Improvement Priority",
                        color=priority_scores, color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Comparative Analysis":
    st.subheader("📊 Comparative Lecture Analysis")
    
    # Select lectures to compare
    compare_lectures = st.multiselect(
        "Select lectures to compare:",
        lectures_df['Lecture Title'].tolist(),
        default=lectures_df['Lecture Title'].tolist()[:3]
    )
    
    if compare_lectures:
        compare_data = lectures_df[lectures_df['Lecture Title'].isin(compare_lectures)]
        
        # Comparison metrics
        metrics = ['Engagement_Score', 'Clarity_Score', 'Student_Questions', 'Comprehension_Rate']
        
        fig = go.Figure()
        
        for metric in metrics:
            fig.add_trace(go.Bar(
                name=metric.replace('_', ' ').title(),
                x=compare_data['Lecture Title'],
                y=compare_data[metric]
            ))
        
        fig.update_layout(
            title="Lecture Performance Comparison",
            xaxis_title="Lectures",
            yaxis_title="Score",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Best/worst performers
        col1, col2 = st.columns(2)
        
        with col1:
            best_engagement = compare_data.loc[compare_data['Engagement_Score'].idxmax()]
            st.success(f"🏆 **Highest Engagement:** {best_engagement['Lecture Title']} ({best_engagement['Engagement_Score']}%)")
            
            best_clarity = compare_data.loc[compare_data['Clarity_Score'].idxmax()]
            st.success(f"⭐ **Clearest Content:** {best_clarity['Lecture Title']} ({best_clarity['Clarity_Score']}/10)")
        
        with col2:
            most_questions = compare_data.loc[compare_data['Student_Questions'].idxmax()]
            st.info(f"❓ **Most Interactive:** {most_questions['Lecture Title']} ({most_questions['Student_Questions']} questions)")
            
            best_comprehension = compare_data.loc[compare_data['Comprehension_Rate'].idxmax()]
            st.info(f"🎯 **Best Comprehension:** {best_comprehension['Lecture Title']} ({best_comprehension['Comprehension_Rate']}%)")

elif analysis_type == "Trend Analysis":
    st.subheader("📈 Performance Trends Over Time")
    
    # Time series analysis
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(lectures_df, x='Date', y='Engagement_Score', 
                     title="Engagement Score Trend", markers=True)
        fig.add_hline(y=85, line_dash="dash", line_color="red", 
                     annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(lectures_df, x='Date', y='Clarity_Score', 
                     title="Clarity Score Trend", markers=True)
        fig.add_hline(y=8.5, line_dash="dash", line_color="green", 
                     annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("� Performance Correlations")
    
    correlation_data = lectures_df[['Duration', 'Word_Count', 'Engagement_Score', 
                                   'Clarity_Score', 'Student_Questions', 'Comprehension_Rate']]
    
    fig = px.imshow(correlation_data.corr(), 
                   title="Correlation Matrix of Lecture Metrics",
                   color_continuous_scale='RdBu')
    st.plotly_chart(fig, use_container_width=True)

else:  # Content Analysis
    st.subheader("📚 Content Analysis Deep Dive")
    
    selected_data = lectures_df[lectures_df['Lecture Title'] == selected_lecture].iloc[0]
    
    # Simulated content analysis
    st.subheader("🔍 Natural Language Processing Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Topics Identified")
        topics = ['Derivatives', 'Chain Rule', 'Product Rule', 'Applications', 'Examples']
        frequencies = [45, 23, 18, 28, 35]
        
        fig = px.bar(x=topics, y=frequencies, title="Topic Frequency in Lecture")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sentiment Analysis")
        sentiments = ['Positive', 'Neutral', 'Negative']
        sentiment_scores = [75, 22, 3]
        
        fig = px.pie(values=sentiment_scores, names=sentiments, 
                    title="Lecture Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Word cloud simulation
    st.subheader("📝 Content Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vocabulary Complexity", "7.2/10", "✅ Appropriate")
        st.metric("Technical Terms", "45", "📚 Rich content")
    
    with col2:
        st.metric("Explanation Ratio", "65%", "📖 Well explained")
        st.metric("Example Density", "1 per 3 min", "💡 Good examples")
    
    with col3:
        st.metric("Question Prompts", "12", "❓ Interactive")
        st.metric("Summary Points", "8", "📋 Well structured")

# Export functionality
st.subheader("📥 Export Analysis")

export_format = st.selectbox("Choose export format:", ["PDF Report", "CSV Data", "JSON Analysis"], key="export_format_selectbox")

if st.button("📊 Generate Report"):
    st.success(f"✅ {export_format} report generated successfully!")
    st.info("📧 Report has been sent to your email and saved to your dashboard.")