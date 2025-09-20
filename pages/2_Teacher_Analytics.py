import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Teacher Analytics", page_icon="�‍🏫")

st.title("�‍🏫 Teacher Analytics & Performance")

# Sample teacher data
np.random.seed(42)
teachers_data = {
    "Teacher": ["Dr. Sarah Johnson", "Prof. Michael Chen", "Ms. Emily Davis", "Mr. Robert Wilson", 
                "Dr. Lisa Brown", "Prof. James Miller", "Ms. Anna Taylor", "Dr. David Garcia"],
    "Subject": ["Mathematics", "Physics", "Chemistry", "Biology", "Literature", "History", "Art", "Computer Science"],
    "Teaching_Score": [8.7, 8.5, 9.1, 8.2, 8.8, 7.9, 8.6, 9.0],
    "Student_Engagement": [89, 85, 92, 78, 91, 82, 88, 94],
    "Content_Quality": [8.9, 8.3, 9.0, 8.1, 8.7, 8.0, 8.5, 9.2],
    "Lectures_Analyzed": [24, 18, 31, 15, 27, 22, 19, 25],
    "Students_Count": [156, 142, 178, 134, 165, 128, 98, 187],
    "Improvement_Rate": [12, 8, 15, 5, 11, 7, 9, 16]
}

teachers_df = pd.DataFrame(teachers_data)

# Sidebar filters
st.sidebar.subheader("🔍 Filter Teachers")

subjects = st.sidebar.multiselect(
    "Select Subjects:",
    options=teachers_df["Subject"].unique(),
    default=teachers_df["Subject"].unique()
)

score_range = st.sidebar.slider(
    "Teaching Score Range:",
    min_value=7.0,
    max_value=10.0,
    value=(7.0, 10.0),
    step=0.1
)

engagement_threshold = st.sidebar.slider(
    "Minimum Engagement %:",
    min_value=70,
    max_value=100,
    value=80
)

# Filter data
filtered_df = teachers_df[
    (teachers_df["Subject"].isin(subjects)) &
    (teachers_df["Teaching_Score"] >= score_range[0]) &
    (teachers_df["Teaching_Score"] <= score_range[1]) &
    (teachers_df["Student_Engagement"] >= engagement_threshold)
]

# Overview metrics
st.subheader("📊 Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_score = filtered_df['Teaching_Score'].mean()
    st.metric("Average Teaching Score", f"{avg_score:.1f}/10", f"Target: 8.5")

with col2:
    avg_engagement = filtered_df['Student_Engagement'].mean()
    st.metric("Average Engagement", f"{avg_engagement:.0f}%", f"↗️ +3% vs last month")

with col3:
    total_lectures = filtered_df['Lectures_Analyzed'].sum()
    st.metric("Total Lectures Analyzed", f"{total_lectures}", f"This semester")

with col4:
    total_students = filtered_df['Students_Count'].sum()
    st.metric("Students Impacted", f"{total_students:,}", f"Across all teachers")

# Teacher performance comparison
st.subheader("📈 Teacher Performance Comparison")

tab1, tab2, tab3 = st.tabs(["Teaching Scores", "Student Engagement", "Content Quality"])

with tab1:
    fig = px.bar(filtered_df, x='Teacher', y='Teaching_Score', 
                 color='Teaching_Score', color_continuous_scale='RdYlGn',
                 title="Teaching Effectiveness Scores")
    fig.update_xaxes(tickangle=45)
    fig.add_hline(y=8.5, line_dash="dash", line_color="red", 
                  annotation_text="Target Score (8.5)")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.scatter(filtered_df, x='Lectures_Analyzed', y='Student_Engagement',
                     size='Students_Count', color='Subject', hover_name='Teacher',
                     title="Student Engagement vs Lectures Analyzed")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Teaching Score', x=filtered_df['Teacher'], y=filtered_df['Teaching_Score']))
    fig.add_trace(go.Bar(name='Content Quality', x=filtered_df['Teacher'], y=filtered_df['Content_Quality']))
    
    fig.update_layout(title='Teaching Score vs Content Quality Comparison',
                      xaxis_title='Teacher', yaxis_title='Score',
                      barmode='group')
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# Detailed teacher profiles
st.subheader("👥 Teacher Profiles")

search_teacher = st.text_input("🔍 Search for a specific teacher:", 
                              placeholder="Enter teacher name...")

if search_teacher:
    search_results = filtered_df[
        filtered_df['Teacher'].str.contains(search_teacher, case=False)
    ]
    filtered_df = search_results

# Display teacher cards
for i in range(0, len(filtered_df), 2):
    cols = st.columns(2)
    
    for j, col in enumerate(cols):
        if i + j < len(filtered_df):
            teacher = filtered_df.iloc[i + j]
            
            with col:
                with st.container():
                    # Teacher card styling
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                        <h4>👨‍🏫 {teacher['Teacher']}</h4>
                        <p><strong>Subject:</strong> {teacher['Subject']}</p>
                        <p><strong>Teaching Score:</strong> {teacher['Teaching_Score']}/10</p>
                        <p><strong>Student Engagement:</strong> {teacher['Student_Engagement']}%</p>
                        <p><strong>Students:</strong> {teacher['Students_Count']}</p>
                        <p><strong>Lectures Analyzed:</strong> {teacher['Lectures_Analyzed']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Performance indicators
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if teacher['Teaching_Score'] >= 8.5:
                            st.success("✅ Excellent Performance")
                        elif teacher['Teaching_Score'] >= 8.0:
                            st.info("👍 Good Performance")
                        else:
                            st.warning("⚠️ Needs Improvement")
                    
                    with col_b:
                        improvement_color = "green" if teacher['Improvement_Rate'] > 10 else "orange" if teacher['Improvement_Rate'] > 5 else "red"
                        st.markdown(f"<p style='color: {improvement_color}'>📈 {teacher['Improvement_Rate']}% improvement</p>", 
                                   unsafe_allow_html=True)
                    
                    # Action buttons
                    button_col1, button_col2 = st.columns(2)
                    with button_col1:
                        if st.button(f"View Details", key=f"details_{i+j}"):
                            st.info(f"Detailed analytics for {teacher['Teacher']} coming soon!")
                    with button_col2:
                        if st.button(f"Send Feedback", key=f"feedback_{i+j}"):
                            st.success(f"Feedback form for {teacher['Teacher']} opened!")

# Performance trends
st.subheader("📊 Performance Trends")

# Generate sample trend data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
avg_scores = [8.2, 8.3, 8.1, 8.4, 8.5, 8.3, 8.6, 8.4, 8.5]
engagement_scores = [82, 84, 81, 86, 87, 85, 89, 87, 88]

col1, col2 = st.columns(2)

with col1:
    fig = px.line(x=months, y=avg_scores, title="Monthly Average Teaching Scores",
                  markers=True, labels={'x': 'Month', 'y': 'Average Score'})
    fig.add_hline(y=8.5, line_dash="dash", line_color="green", 
                  annotation_text="Target")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(x=months, y=engagement_scores, title="Monthly Average Student Engagement",
                  markers=True, labels={'x': 'Month', 'y': 'Engagement %'},
                  line_shape="spline")
    st.plotly_chart(fig, use_container_width=True)

# Improvement recommendations
st.subheader("🎯 Improvement Recommendations")

low_performers = filtered_df[filtered_df['Teaching_Score'] < 8.5]

if len(low_performers) > 0:
    st.warning(f"⚠️ {len(low_performers)} teacher(s) below target performance:")
    
    for _, teacher in low_performers.iterrows():
        with st.expander(f"📋 Recommendations for {teacher['Teacher']}"):
            st.write(f"**Current Score:** {teacher['Teaching_Score']}/10")
            st.write("**Suggested Improvements:**")
            
            if teacher['Student_Engagement'] < 85:
                st.write("• 🎯 Focus on increasing student interaction and engagement")
                st.write("• 💡 Consider adding more interactive elements to lectures")
            
            if teacher['Content_Quality'] < 8.5:
                st.write("• 📚 Review lecture content for clarity and structure")
                st.write("• 🎨 Enhance visual aids and presentation materials")
            
            if teacher['Lectures_Analyzed'] < 20:
                st.write("• 📊 Upload more lectures for comprehensive analysis")
                st.write("• 🔄 Regular content analysis helps identify patterns")
            
            st.write("• 👥 Peer mentoring with high-performing teachers")
            st.write("• 📈 Set specific improvement targets for next month")
else:
    st.success("🎉 All teachers are meeting or exceeding performance targets!")

# Export functionality
st.subheader("📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Performance Report"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name="teacher_performance_report.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 Generate Summary"):
        st.info("Summary report generation feature coming soon!")