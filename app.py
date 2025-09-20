import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from dotenv import load_dotenv
import io
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="VirtuLearn - Teacher & Student Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/community',
        'Report a bug': "https://github.com/yourusername/virtulearn/issues",
        'About': "# VirtuLearn App\nTeacher Performance & Student Learning Analytics"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .lecture-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #1f77b4;
        text-align: center;
        margin: 1rem 0;
    }
    .teacher-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .student-metric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 VirtuLearn - Educational Analytics Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        # User role selection
        user_role = st.selectbox(
            "Select Your Role:",
            ["👨‍🏫 Teacher", "👨‍🎓 Student", "👨‍💼 Administrator"]
        )
        
        # User identification
        if user_role == "👨‍🏫 Teacher":
            teacher_name = st.text_input("Teacher Name:", value="Dr. Smith")
            subject = st.selectbox("Subject:", ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Literature", "History"])
            st.write(f"Welcome, {teacher_name}! 👋")
        elif user_role == "👨‍🎓 Student":
            student_name = st.text_input("Student Name:", value="Alex Johnson")
            grade_level = st.selectbox("Grade Level:", ["9th Grade", "10th Grade", "11th Grade", "12th Grade", "Undergraduate", "Graduate"])
            st.write(f"Welcome, {student_name}! 👋")
        else:
            admin_name = st.text_input("Administrator Name:", value="Principal Davis")
            st.write(f"Welcome, {admin_name}! 👋")
        
        # Date range for analysis
        st.subheader("📅 Analysis Period")
        date_range = st.date_input(
            "Select Date Range:",
            value=(datetime.now().date() - pd.Timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date()
        )
        
        # Mode selection based on user role
        if user_role == "👨‍🏫 Teacher":
            mode = st.selectbox(
                "Choose Mode:",
                ["Upload Lecture", "Performance Dashboard", "Lecture Analysis", "Student Feedback"]
            )
        elif user_role == "👨‍🎓 Student":
            mode = st.selectbox(
                "Choose Mode:",
                ["Learning Dashboard", "Lecture Review", "Study Materials", "Progress Tracking"]
            )
        else:
            mode = st.selectbox(
                "Choose Mode:",
                ["School Overview", "Teacher Analytics", "Student Performance", "System Management"]
            )
    
    # Main content area based on user role and mode
    if user_role == "👨‍🏫 Teacher":
        if mode == "Upload Lecture":
            show_lecture_upload()
        elif mode == "Performance Dashboard":
            show_teacher_dashboard()
        elif mode == "Lecture Analysis":
            show_lecture_analysis()
        else:
            show_student_feedback()
    elif user_role == "👨‍🎓 Student":
        if mode == "Learning Dashboard":
            show_student_dashboard()
        elif mode == "Lecture Review":
            show_lecture_review()
        elif mode == "Study Materials":
            show_study_materials()
        else:
            show_progress_tracking()
    else:  # Administrator
        if mode == "School Overview":
            show_school_overview()
        elif mode == "Teacher Analytics":
            show_teacher_analytics()
        elif mode == "Student Performance":
            show_student_performance()
        else:
            show_system_management()

def show_lecture_upload():
    """Display lecture upload interface for teachers"""
    st.header("� Upload Lecture Materials")
    
    st.markdown("""
    <div class="upload-section">
        <h3>📚 Upload Your Lecture Content</h3>
        <p>Upload transcript, slides, and supplementary materials for analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Lecture Information")
        lecture_title = st.text_input("Lecture Title:", placeholder="e.g., Introduction to Calculus")
        lecture_date = st.date_input("Lecture Date:", value=datetime.now().date())
        course_code = st.text_input("Course Code:", placeholder="e.g., MATH101")
        duration = st.number_input("Duration (minutes):", min_value=1, max_value=180, value=50)
        
        st.subheader("Content Classification")
        difficulty_level = st.selectbox("Difficulty Level:", ["Beginner", "Intermediate", "Advanced"])
        topics_covered = st.text_area("Topics Covered:", placeholder="List main topics separated by commas")
        learning_objectives = st.text_area("Learning Objectives:", placeholder="What should students learn?")
    
    with col2:
        st.subheader("File Uploads")
        
        # Transcript upload
        transcript_file = st.file_uploader(
            "📝 Upload Lecture Transcript",
            type=['txt', 'docx', 'pdf'],
            help="Upload the lecture transcript in text, Word, or PDF format"
        )
        
        # Slides upload
        slides_file = st.file_uploader(
            "🖼️ Upload Lecture Slides",
            type=['pptx', 'pdf', 'ppt'],
            help="Upload your presentation slides"
        )
        
        # Additional materials
        materials_files = st.file_uploader(
            "📎 Upload Additional Materials",
            type=['pdf', 'docx', 'xlsx', 'txt', 'jpg', 'png'],
            accept_multiple_files=True,
            help="Upload handouts, assignments, or reference materials"
        )
        
        # Audio/Video (optional)
        media_file = st.file_uploader(
            "🎥 Upload Audio/Video (Optional)",
            type=['mp4', 'mp3', 'wav', 'avi'],
            help="Upload lecture recording if available"
        )
    
    if st.button("🚀 Analyze Lecture Content", type="primary"):
        if transcript_file and lecture_title:
            with st.spinner("Analyzing lecture content..."):
                # Simulate analysis
                st.success("✅ Lecture uploaded and analyzed successfully!")
                
                # Show analysis preview
                st.subheader("📊 Quick Analysis Preview")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Word Count", "2,847", "↗️ Above average")
                
                with col2:
                    st.metric("Readability Score", "7.2/10", "✅ Appropriate")
                
                with col3:
                    st.metric("Engagement Level", "85%", "↗️ High")
                
                with col4:
                    st.metric("Concept Density", "12 concepts", "📚 Rich content")
                
                st.info("📈 Full analysis available in Performance Dashboard")
        else:
            st.error("Please provide at least a lecture title and transcript file.")

def show_teacher_dashboard():
    """Display teacher performance dashboard"""
    st.header("�‍🏫 Teacher Performance Dashboard")
    
    # Key performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="teacher-metric">
            <h4>📊 Teaching Score</h4>
            <h2>8.7/10</h2>
            <p>↗️ +0.3 this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="teacher-metric">
            <h4>🎯 Student Engagement</h4>
            <h2>89%</h2>
            <p>↗️ +5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="teacher-metric">
            <h4>📝 Lectures Analyzed</h4>
            <h2>24</h2>
            <p>📅 This semester</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="teacher-metric">
            <h4>� Students Helped</h4>
            <h2>156</h2>
            <p>🎓 Across all courses</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Teaching Performance Trends")
        
        # Generate sample data
        dates = pd.date_range(start='2024-01-01', periods=20, freq='W')
        performance_data = pd.DataFrame({
            'Date': dates,
            'Teaching_Score': np.random.normal(8.5, 0.5, len(dates)),
            'Engagement_Rate': np.random.normal(85, 5, len(dates)),
            'Content_Quality': np.random.normal(8.2, 0.3, len(dates))
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=performance_data['Date'], y=performance_data['Teaching_Score'],
                                mode='lines+markers', name='Teaching Score'))
        fig.add_trace(go.Scatter(x=performance_data['Date'], y=performance_data['Engagement_Rate']/10,
                                mode='lines+markers', name='Engagement Rate'))
        
        fig.update_layout(title="Performance Over Time", yaxis_title="Score (1-10)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Areas for Improvement")
        
        improvement_areas = pd.DataFrame({
            'Area': ['Lecture Clarity', 'Student Interaction', 'Content Depth', 'Time Management', 'Technology Use'],
            'Current Score': [8.5, 7.8, 9.2, 8.1, 7.3],
            'Target Score': [9.0, 8.5, 9.5, 8.8, 8.0]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=improvement_areas['Area'], y=improvement_areas['Current Score'],
                            name='Current', marker_color='lightblue'))
        fig.add_trace(go.Bar(x=improvement_areas['Area'], y=improvement_areas['Target Score'],
                            name='Target', marker_color='darkblue'))
        
        fig.update_layout(title="Improvement Targets", yaxis_title="Score", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent lectures
    st.subheader("📚 Recent Lectures")
    recent_lectures = pd.DataFrame({
        'Date': ['2024-09-18', '2024-09-15', '2024-09-13', '2024-09-11'],
        'Lecture Title': ['Introduction to Derivatives', 'Limits and Continuity', 'Function Graphs', 'Polynomial Functions'],
        'Engagement Score': ['92%', '88%', '85%', '90%'],
        'Student Questions': [15, 12, 8, 18],
        'Analysis Status': ['✅ Complete', '✅ Complete', '✅ Complete', '⏳ Processing']
    })
    st.dataframe(recent_lectures, use_container_width=True, hide_index=True)

def show_lecture_analysis():
    """Display detailed lecture analysis"""
    st.header("🔍 Lecture Analysis")
    
    # Lecture selector
    lecture_options = [
        "Introduction to Derivatives - Sept 18",
        "Limits and Continuity - Sept 15", 
        "Function Graphs - Sept 13",
        "Polynomial Functions - Sept 11"
    ]
    selected_lecture = st.selectbox("Select Lecture to Analyze:", lecture_options)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📝 Content Analysis", "👥 Student Impact", "🎯 Recommendations"])
    
    with tab1:
        st.subheader("Lecture Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Duration", "52 minutes", "2 min over planned")
            st.metric("Word Count", "2,847 words", "12% above average")
        
        with col2:
            st.metric("Speaking Pace", "142 WPM", "✅ Optimal range")
            st.metric("Pauses/Breaks", "23", "🎯 Good distribution")
        
        with col3:
            st.metric("Questions Asked", "15", "↗️ +3 vs average")
            st.metric("Student Responses", "12", "80% response rate")
        
        # Content breakdown
        st.subheader("📚 Content Breakdown")
        content_data = pd.DataFrame({
            'Content Type': ['Explanation', 'Examples', 'Q&A', 'Review', 'Practice'],
            'Time (minutes)': [25, 12, 8, 4, 3],
            'Percentage': [48, 23, 15, 8, 6]
        })
        
        fig = px.pie(content_data, values='Time (minutes)', names='Content Type', 
                     title="Time Distribution by Content Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📝 Content Quality Analysis")
        
        # Readability and complexity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Readability Metrics")
            readability_data = {
                'Metric': ['Flesch Reading Ease', 'Grade Level', 'Avg Sentence Length', 'Complex Words %'],
                'Score': [72.3, '9th Grade', '18 words', '15%'],
                'Status': ['✅ Good', '✅ Appropriate', '⚠️ Slightly High', '✅ Good']
            }
            st.dataframe(pd.DataFrame(readability_data), hide_index=True)
        
        with col2:
            st.subheader("Concept Coverage")
            concepts = ['Derivatives', 'Chain Rule', 'Product Rule', 'Applications', 'Practice Problems']
            coverage = [95, 85, 78, 90, 70]
            
            fig = px.bar(x=concepts, y=coverage, title="Concept Coverage %")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("👥 Student Learning Impact")
        
        # Engagement metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Pre-lecture Understanding", "45%", "Based on quiz")
            st.metric("Post-lecture Understanding", "78%", "↗️ +33% improvement")
            st.metric("Student Satisfaction", "4.3/5", "↗️ Above average")
        
        with col2:
            # Engagement timeline
            time_points = list(range(0, 55, 5))
            engagement = [85, 88, 82, 75, 80, 85, 90, 88, 85, 82, 78]
            
            fig = px.line(x=time_points, y=engagement, title="Student Engagement Throughout Lecture",
                         labels={'x': 'Time (minutes)', 'y': 'Engagement %'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🎯 AI-Generated Recommendations")
        
        st.success("🌟 **Strengths Identified:**")
        st.write("• Excellent use of real-world examples to explain derivatives")
        st.write("• Good pacing with appropriate pauses for note-taking")
        st.write("• Effective use of visual aids and board work")
        
        st.warning("⚠️ **Areas for Improvement:**")
        st.write("• Consider breaking down complex sentences (avg 18 words)")
        st.write("• Add more interactive elements during the middle section")
        st.write("• Provide more practice problems for chain rule concept")
        
        st.info("💡 **Specific Suggestions:**")
        st.write("• Implement a 2-minute group discussion at the 25-minute mark")
        st.write("• Add 3-4 quick practice problems for immediate application")
        st.write("• Use more analogies to explain abstract concepts")

def show_student_feedback():
    """Display student feedback and Q&A"""
    st.header("💬 Student Feedback & Questions")
    
    # Feedback summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Rating", "4.3/5", "↗️ +0.2")
    
    with col2:
        st.metric("Response Rate", "87%", "↗️ +5%")
    
    with col3:
        st.metric("Questions Submitted", "23", "This week")
    
    with col4:
        st.metric("Clarity Score", "8.7/10", "↗️ +0.4")
    
    # Recent feedback
    st.subheader("� Recent Student Feedback")
    
    feedback_data = pd.DataFrame({
        'Date': ['2024-09-18', '2024-09-18', '2024-09-15', '2024-09-15'],
        'Student': ['Anonymous', 'Sarah M.', 'Anonymous', 'Mike T.'],
        'Lecture': ['Introduction to Derivatives', 'Introduction to Derivatives', 'Limits and Continuity', 'Limits and Continuity'],
        'Rating': [5, 4, 5, 4],
        'Comment': [
            'Great examples! Really helped me understand the concept.',
            'Could use more practice problems.',
            'Excellent explanation of limits!',
            'A bit fast-paced but overall good.'
        ]
    })
    
    for _, row in feedback_data.iterrows():
        with st.expander(f"{row['Lecture']} - {row['Student']} ({'⭐' * row['Rating']})"):
            st.write(row['Comment'])
            st.caption(f"Submitted on {row['Date']}")

def show_student_dashboard():
    """Display student learning dashboard"""
    st.header("👨‍🎓 Student Learning Dashboard")
    
    # Student metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="student-metric">
            <h4>📚 Lectures Attended</h4>
            <h2>18/20</h2>
            <p>90% attendance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="student-metric">
            <h4>🎯 Understanding Level</h4>
            <h2>82%</h2>
            <p>↗️ +7% this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="student-metric">
            <h4>❓ Questions Asked</h4>
            <h2>12</h2>
            <p>This semester</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="student-metric">
            <h4>📈 Progress Score</h4>
            <h2>B+</h2>
            <p>Current grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Learning progress
    st.subheader("📈 Your Learning Progress")
    
    # Progress by topic
    topics = ['Basic Functions', 'Limits', 'Derivatives', 'Chain Rule', 'Applications']
    understanding = [95, 88, 78, 65, 45]
    
    fig = px.bar(x=topics, y=understanding, title="Understanding by Topic (%)",
                 color=understanding, color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

def show_lecture_review():
    """Display lecture review and materials"""
    st.header("📖 Lecture Review")
    
    lecture_list = [
        "Introduction to Derivatives - Sept 18",
        "Limits and Continuity - Sept 15",
        "Function Graphs - Sept 13",
        "Polynomial Functions - Sept 11"
    ]
    
    selected = st.selectbox("Select a lecture to review:", lecture_list)
    
    if selected:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Lecture Summary")
            st.write("**Key Concepts Covered:**")
            st.write("• Definition of derivatives")
            st.write("• Geometric interpretation")
            st.write("• Basic derivative rules")
            st.write("• Real-world applications")
            
            st.subheader("🎯 Learning Objectives")
            st.write("By the end of this lecture, you should be able to:")
            st.write("1. Define what a derivative represents")
            st.write("2. Calculate basic derivatives using rules")
            st.write("3. Apply derivatives to solve real problems")
            
        with col2:
            st.subheader("📊 Your Performance")
            st.metric("Comprehension Score", "78%", "↗️ +5%")
            st.metric("Engagement Level", "High", "🎯")
            st.metric("Questions Asked", "2", "💭")
            
            if st.button("📝 Take Quick Quiz"):
                st.info("Quiz feature coming soon!")

def show_study_materials():
    """Display study materials and resources"""
    st.header("📚 Study Materials")
    
    tab1, tab2, tab3 = st.tabs(["📄 Transcripts", "🖼️ Slides", "📎 Resources"])
    
    with tab1:
        st.subheader("Lecture Transcripts")
        for lecture in ["Introduction to Derivatives", "Limits and Continuity", "Function Graphs"]:
            with st.expander(f"📄 {lecture}"):
                st.write("Transcript preview...")
                st.download_button(f"Download {lecture} transcript", "transcript_content", f"{lecture}.txt")
    
    with tab2:
        st.subheader("Lecture Slides")
        for lecture in ["Introduction to Derivatives", "Limits and Continuity", "Function Graphs"]:
            with st.expander(f"🖼️ {lecture}"):
                st.write("Slide preview...")
                st.download_button(f"Download {lecture} slides", "slides_content", f"{lecture}.pdf")
    
    with tab3:
        st.subheader("Additional Resources")
        st.write("📖 Recommended readings")
        st.write("🎥 Video tutorials")
        st.write("💻 Practice problems")

def show_progress_tracking():
    """Display student progress tracking"""
    st.header("📈 Progress Tracking")
    
    # Weekly progress
    weeks = list(range(1, 11))
    scores = [65, 70, 68, 75, 78, 82, 85, 83, 88, 85]
    
    fig = px.line(x=weeks, y=scores, title="Weekly Progress Scores",
                  markers=True, labels={'x': 'Week', 'y': 'Score (%)'})
    st.plotly_chart(fig, use_container_width=True)

def show_school_overview():
    """Display school-wide overview for administrators"""
    st.header("🏫 School Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Teachers", "45", "↗️ +3 this year")
    
    with col2:
        st.metric("Total Students", "1,250", "↗️ +50 this year")
    
    with col3:
        st.metric("Average Teaching Score", "8.4/10", "↗️ +0.2")
    
    with col4:
        st.metric("Student Satisfaction", "87%", "↗️ +3%")

def show_teacher_analytics():
    """Display teacher analytics for administrators"""
    st.header("👨‍🏫 Teacher Analytics")
    
    # Sample teacher performance data
    teachers = ['Dr. Smith', 'Prof. Johnson', 'Ms. Davis', 'Mr. Wilson', 'Dr. Brown']
    scores = [8.7, 8.5, 9.1, 8.2, 8.8]
    
    fig = px.bar(x=teachers, y=scores, title="Teacher Performance Scores")
    st.plotly_chart(fig, use_container_width=True)

def show_student_performance():
    """Display student performance analytics"""
    st.header("📊 Student Performance Analytics")
    
    # Grade distribution
    grades = ['A', 'B', 'C', 'D', 'F']
    counts = [45, 78, 65, 23, 8]
    
    fig = px.pie(values=counts, names=grades, title="Grade Distribution")
    st.plotly_chart(fig, use_container_width=True)

def show_system_management():
    """Display system management interface"""
    st.header("⚙️ System Management")
    
    st.subheader("📊 System Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Lectures Processed", "1,247", "This semester")
    
    with col2:
        st.metric("Storage Used", "2.3 TB", "67% of capacity")
    
    with col3:
        st.metric("System Uptime", "99.8%", "Last 30 days")

if __name__ == "__main__":
    main()