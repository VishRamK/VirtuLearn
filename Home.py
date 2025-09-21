import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dotenv import load_dotenv
import os
import json
import hashlib
import openai
import io

# Try to import optional file parsing libraries
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

# Import data manager
from utils.data_manager import LectureDataManager

# Load environment variables
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return LectureDataManager(use_mongodb=True)

# File parsing utility functions
def parse_text_file(file):
    """Parse text file content"""
    try:
        content = str(file.read(), "utf-8")
        return content
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return ""

def parse_pdf_file(file):
    """Parse PDF file content using PyMuPDF"""
    if not PDF_AVAILABLE:
        st.warning("PDF parsing not available. Please install PyMuPDF: pip install PyMuPDF")
        return ""
    
    try:
        # Read the file content
        file_bytes = file.read()
        
        # Open PDF document from bytes
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text() + "\n"
        
        pdf_document.close()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {str(e)}")
        return ""

def parse_docx_file(file):
    """Parse DOCX file content"""
    if not DOCX_AVAILABLE:
        st.warning("DOCX parsing not available. Please install python-docx: pip install python-docx")
        return ""
    
    try:
        doc = Document(io.BytesIO(file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX file: {str(e)}")
        return ""

def parse_pptx_file(file):
    """Parse PPTX file content"""
    if not PPTX_AVAILABLE:
        st.warning("PPTX parsing not available. Please install python-pptx: pip install python-pptx")
        return ""
    
    try:
        prs = Presentation(io.BytesIO(file.read()))
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PPTX file: {str(e)}")
        return ""

def parse_uploaded_file(uploaded_file):
    """Parse uploaded file based on file type"""
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.type
    
    if file_type == "text/plain":
        return parse_text_file(uploaded_file)
    elif file_type == "application/pdf":
        return parse_pdf_file(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return parse_docx_file(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return parse_pptx_file(uploaded_file)
    elif file_type == "application/vnd.ms-powerpoint":
        st.warning("Please convert .ppt files to .pptx format for parsing")
        return ""
    else:
        st.warning(f"Unsupported file type: {file_type}")
        return ""

# Page configuration
st.set_page_config(
    page_title="VirtuLearn - Principal Lecture Evaluation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/community',
        'Report a bug': "https://github.com/yourusername/virtulearn/issues",
        'About': "# VirtuLearn Principal Dashboard\nLecture Quality Evaluation & Analytics Platform"
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
    .evaluation-card {
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
    .principal-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .score-excellent {
        background: linear-gradient(135deg, #00c851 0%, #00695c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .score-good {
        background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .score-needs-improvement {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def calculate_lecture_score(transcript_text, topics_covered, learning_objectives, duration, source_materials="", slides_content=""):
    """Calculate lecture quality score based on multiple factors including source materials and slides"""
    score_components = {}
    
    # Combine all content for comprehensive analysis
    combined_content = transcript_text
    if source_materials:
        combined_content += "\n\n" + source_materials
    if slides_content:
        combined_content += "\n\n" + slides_content
    
    # 1. Content Correctness (40% of total score)
    word_count = len(transcript_text.split())
    total_word_count = len(combined_content.split())
    
    # Base content density on transcript
    content_density = min(word_count / (duration * 10), 1.0) if duration else 0.5  # Target: 10 words per minute
    
    # Bonus for having source materials and slides (up to 10% bonus)
    material_bonus = 0
    if source_materials:
        material_bonus += min(len(source_materials.split()) / 100, 5)  # Up to 5% for source materials
    if slides_content:
        material_bonus += min(len(slides_content.split()) / 100, 5)  # Up to 5% for slides
    
    correctness_score = min((content_density * 40) + material_bonus, 40)
    score_components['Content Correctness'] = correctness_score
    
    # 2. Class Engagement Indicators (35% of total score) - analyzed from transcript
    question_keywords = ['question', 'ask', 'think', 'discuss', 'what do you', 'anyone', 'raise your hand']
    engagement_count = sum(transcript_text.lower().count(keyword) for keyword in question_keywords)
    
    # Check if slides contain interactive elements
    interactive_keywords = ['exercise', 'activity', 'group work', 'discussion', 'poll', 'quiz']
    if slides_content:
        engagement_count += sum(slides_content.lower().count(keyword) for keyword in interactive_keywords)
    
    engagement_score = min(engagement_count * 3, 35)  # Max 35 points for engagement
    score_components['Class Engagement'] = engagement_score
    
    # 3. Structure and Organization (15% of total score) - check all materials
    structure_keywords = ['first', 'second', 'third', 'next', 'finally', 'in conclusion', 'to summarize']
    structure_count = sum(combined_content.lower().count(keyword) for keyword in structure_keywords)
    
    # Bonus for having organized slides
    if slides_content and any(keyword in slides_content.lower() for keyword in ['outline', 'agenda', 'objectives']):
        structure_count += 2
    
    structure_score = min(structure_count * 2, 15)  # Max 15 points for structure
    score_components['Structure & Organization'] = structure_score
    
    # 4. Topic Coverage (10% of total score) - check all materials
    topics_list = [topic.strip() for topic in topics_covered.split(",")] if topics_covered else []
    topic_coverage_count = 0
    
    for topic in topics_list:
        if topic.lower() in combined_content.lower():
            topic_coverage_count += 1
    
    topic_coverage_score = min(topic_coverage_count * 2, 10)  # Max 10 points for topic coverage
    score_components['Topic Coverage'] = topic_coverage_score
    
    total_score = sum(score_components.values())
    
    return total_score, score_components

def generate_evaluation_report(score, score_components, transcript_text, topics_covered):
    """Generate detailed evaluation report"""
    report = {
        'overall_score': score,
        'grade': 'A' if score >= 85 else 'B' if score >= 75 else 'C' if score >= 65 else 'D' if score >= 55 else 'F',
        'score_breakdown': score_components,
        'word_count': len(transcript_text.split()),
        'topics_covered': [topic.strip() for topic in topics_covered.split(",")] if topics_covered else [],
        'timestamp': datetime.now().isoformat(),
    }
    
    # Generate recommendations based on score
    recommendations = []
    if score_components['Content Correctness'] < 30:
        recommendations.append("⚠️ Increase content density - aim for more comprehensive coverage")
    if score_components['Class Engagement'] < 25:
        recommendations.append("⚠️ Incorporate more interactive elements and student questions")
    if score_components['Structure & Organization'] < 10:
        recommendations.append("⚠️ Improve lecture structure with clear transitions and summaries")
    if score_components['Topic Coverage'] < 8:
        recommendations.append("⚠️ Cover more diverse topics to enhance learning breadth")
    
    if score >= 85:
        recommendations.append("🌟 Excellent lecture quality! Maintain this high standard")
    elif score >= 75:
        recommendations.append("👍 Good lecture quality with room for minor improvements")
    else:
        recommendations.append("📈 Focus on improving engagement and content structure")
    
    report['recommendations'] = recommendations
    return report

def show_lecture_upload():
    """Display lecture upload and evaluation interface for principal"""
    st.header("📚 Lecture Evaluation System")
    
    st.markdown("""
    <div class="upload-section">
        <h3>🎯 Upload Lecture Materials for Quality Assessment</h3>
        <p>Upload teacher lecture transcripts and materials to evaluate teaching quality and engagement</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Lecture Information")
        teacher_name = st.text_input("Teacher Name:", placeholder="e.g., Dr. Smith")
        lecture_title = st.text_input("Lecture Title:", placeholder="e.g., Introduction to Calculus")
        lecture_date = st.date_input("Lecture Date:", value=datetime.now().date())
        course_code = st.text_input("Course Code:", placeholder="e.g., MATH101")
        duration = st.number_input("Duration (minutes):", min_value=1, max_value=180, value=50)
        class_size = st.number_input("Class Size:", min_value=1, max_value=200, value=25)
        
        st.subheader("Expected Content")
        topics_covered = st.text_area("Topics to be Covered:", placeholder="List expected topics separated by commas")
        learning_objectives = st.text_area("Learning Objectives:", placeholder="What should students learn?")
    
    with col2:
        st.subheader("Upload Materials")
        
        # Transcript upload (required)
        transcript_file = st.file_uploader(
            "📝 Upload Lecture Transcript (Required)",
            type=['txt', 'docx', 'pdf'],
            help="Upload the lecture transcript for evaluation"
        )
        
        # Slides upload (optional)
        slides_file = st.file_uploader(
            "🖼️ Upload Lecture Slides (Optional)",
            type=['pptx', 'pdf', 'ppt'],
            help="Upload lecture slides for additional context"
        )
        
        # Source materials (required)
        materials_files = st.file_uploader(
            "📎 Upload Source Materials (Required)",
            type=['pdf', 'docx', 'xlsx', 'txt'],
            accept_multiple_files=True,
            help="Upload handouts or reference materials"
        )
    
    if st.button("🔍 Evaluate Lecture Quality", type="primary"):
        if transcript_file and teacher_name and lecture_title:
            with st.spinner("Evaluating lecture quality..."):
                try:
                    # Get data manager
                    data_manager = get_data_manager()
                    
                    # Process transcript file
                    transcript_text = parse_uploaded_file(transcript_file)
                    if not transcript_text:
                        st.error("Failed to parse transcript file. Please try a different format.")
                        return
                    
                    # Process slides file if uploaded
                    slides_content = ""
                    if slides_file:
                        slides_content = parse_uploaded_file(slides_file)
                        if not slides_content:
                            st.warning("Could not parse slides file, continuing without slides content.")
                    
                    # Process source materials if uploaded
                    source_materials_content = ""
                    if materials_files:
                        for material_file in materials_files:
                            material_content = parse_uploaded_file(material_file)
                            if material_content:
                                source_materials_content += f"\n\n--- {material_file.name} ---\n"
                                source_materials_content += material_content
                            else:
                                st.warning(f"Could not parse {material_file.name}, skipping this file.")
                    
                    # Calculate lecture quality score with all parsed content
                    score, score_components = calculate_lecture_score(
                        transcript_text, 
                        topics_covered, 
                        learning_objectives, 
                        duration,
                        source_materials_content,
                        slides_content
                    )
                    
                    # Generate evaluation report
                    evaluation_report = generate_evaluation_report(
                        score, score_components, transcript_text, topics_covered
                    )
                    
                    # Create lecture entry in database
                    lecture_entry_data = {
                        'title': lecture_title,
                        'teacher_id': teacher_name,
                        'course_code': course_code,
                        'date': lecture_date,
                        'transcript_text': transcript_text,
                        'duration': int(duration) if duration else None,
                        'topics': [topic.strip() for topic in topics_covered.split(",")] if topics_covered else [],
                        'objectives': [obj.strip() for obj in learning_objectives.split(",")] if learning_objectives else []
                    }
                    
                    # Add parsed content if available
                    if source_materials_content:
                        lecture_entry_data['source_materials'] = source_materials_content
                    if slides_content:
                        lecture_entry_data['slides_content'] = slides_content
                    
                    lecture_id = data_manager.create_lecture_entry(**lecture_entry_data)
                    
                    # Store evaluation results in database
                    evaluation_data = {
                        'lecture_id': lecture_id,
                        'teacher_name': teacher_name,
                        'course_code': course_code,
                        'lecture_title': lecture_title,
                        'evaluation_score': score,
                        'score_breakdown': score_components,
                        'evaluation_report': evaluation_report,
                        'class_size': class_size,
                        'evaluation_timestamp': datetime.now(),
                        'evaluated_by': 'Principal'
                    }
                    
                    # Store evaluation in database
                    if hasattr(data_manager, 'store_evaluation'):
                        eval_id = data_manager.store_evaluation(evaluation_data)
                    else:
                        # Store as metadata if store_evaluation doesn't exist
                        eval_id = data_manager.save_lecture_data(lecture_id, evaluation_data, 'evaluation')
                    
                    # Store additional files if uploaded (need to re-read since we already parsed them)
                    if slides_file:
                        # Reset file pointer and read again for storage
                        slides_file.seek(0)
                        file_id = data_manager.store_uploaded_file(
                            lecture_id=lecture_id,
                            file_content=slides_file.read(),
                            filename=slides_file.name,
                            file_type="slides"
                        )
                    
                    if materials_files:
                        for material_file in materials_files:
                            # Reset file pointer and read again for storage
                            material_file.seek(0)
                            file_id = data_manager.store_uploaded_file(
                                lecture_id=lecture_id,
                                file_content=material_file.read(),
                                filename=material_file.name,
                                file_type="material"
                            )
                    
                    # Display evaluation results
                    st.success(f"✅ Lecture evaluation completed! Evaluation ID: {eval_id}")
                    
                    # Show evaluation score with color coding
                    st.subheader("🎯 Lecture Quality Evaluation")
                    
                    score_col1, score_col2, score_col3 = st.columns([2, 1, 1])
                    
                    with score_col1:
                        if score >= 85:
                            st.markdown(f"""
                            <div class="score-excellent">
                                <h2>Overall Score: {score:.1f}/100</h2>
                                <h3>Grade: {evaluation_report['grade']} - Excellent!</h3>
                                <p>🌟 Outstanding lecture quality</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif score >= 70:
                            st.markdown(f"""
                            <div class="score-good">
                                <h2>Overall Score: {score:.1f}/100</h2>
                                <h3>Grade: {evaluation_report['grade']} - Good</h3>
                                <p>👍 Solid lecture with room for improvement</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="score-needs-improvement">
                                <h2>Overall Score: {score:.1f}/100</h2>
                                <h3>Grade: {evaluation_report['grade']} - Needs Improvement</h3>
                                <p>⚠️ Requires significant enhancement</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with score_col2:
                        st.metric("Teacher", teacher_name, f"Class Size: {class_size}")
                        st.metric("Duration", f"{duration} min", f"Words: {evaluation_report['word_count']:,}")
                    
                    with score_col3:
                        st.metric("Course", course_code, f"Date: {lecture_date}")
                        st.metric("Topics", f"{len(evaluation_report['topics_covered'])}", "Covered")
                    
                    # Score breakdown
                    st.subheader("📊 Detailed Score Breakdown")
                    total_score = sum(score_components.values())
                    breakdown_df = pd.DataFrame({
                        'Component': list(score_components.keys()),
                        'Score': list(score_components.values()),
                        'Percentage': [f"{(comp_score/total_score)*100:.1f}%" if total_score > 0 else "0%" for comp_score in score_components.values()]
                    })
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(breakdown_df, x='Component', y='Score', 
                                   title="Score Distribution by Component",
                                   color='Score', color_continuous_scale='RdYlGn')
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendations
                    st.subheader("💡 Evaluation Recommendations")
                    for i, recommendation in enumerate(evaluation_report['recommendations'], 1):
                        st.write(f"{i}. {recommendation}")
                    
                    # Database storage confirmation
                    if data_manager.use_mongodb:
                        st.success("💾 Evaluation results stored in MongoDB database for analytics tracking")
                    else:
                        st.warning("💾 Evaluation stored locally (MongoDB connection failed)")
                    
                except Exception as e:
                    st.error(f"❌ Error evaluating lecture: {str(e)}")
                    st.exception(e)
        else:
            st.error("Please provide teacher name, lecture title, and transcript file.")

def show_analytics_dashboard():
    """Display analytics dashboard with evolving insights"""
    st.header("📈 School-wide Lecture Analytics")
    
    # Key performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="principal-metric">
            <h4>📊 Average Lecture Score</h4>
            <h2>78.4/100</h2>
            <p>↗️ +2.3 this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="principal-metric">
            <h4>🎯 Lectures Evaluated</h4>
            <h2>127</h2>
            <p>📅 This semester</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="principal-metric">
            <h4>👨‍🏫 Teachers Assessed</h4>
            <h2>24</h2>
            <p>🏫 School-wide</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="principal-metric">
            <h4>📚 Courses Covered</h4>
            <h2>18</h2>
            <p>🎓 All departments</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Analytics trends
    st.subheader("📈 Lecture Quality Trends Over Time")
    
    # Generate sample trend data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='W')
    trend_data = pd.DataFrame({
        'Date': dates,
        'Average_Score': np.random.normal(76, 5, len(dates)) + np.linspace(0, 6, len(dates)),  # Improving trend
        'Lectures_Count': np.random.poisson(8, len(dates)),
        'Teacher_Participation': np.random.normal(85, 8, len(dates))
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_data['Date'], y=trend_data['Average_Score'],
                                mode='lines+markers', name='Average Lecture Score',
                                line=dict(color='#1f77b4', width=3)))
        fig.update_layout(title="Average Lecture Quality Over Time", 
                         yaxis_title="Score (0-100)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(trend_data.tail(10), x='Date', y='Lectures_Count',
                     title="Weekly Lecture Evaluations",
                     color='Lectures_Count', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    # Department-wise analysis
    st.subheader("🏫 Department Performance Analysis")
    
    dept_data = pd.DataFrame({
        'Department': ['Mathematics', 'Science', 'English', 'History', 'Computer Science', 'Arts'],
        'Average_Score': [82.3, 79.1, 85.2, 77.8, 88.5, 74.9],
        'Lectures_Evaluated': [25, 22, 18, 15, 12, 8],
        'Top_Teacher': ['Dr. Smith', 'Prof. Johnson', 'Ms. Davis', 'Mr. Wilson', 'Dr. Brown', 'Ms. Garcia']
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(dept_data, x='Department', y='Average_Score',
                     title="Average Lecture Scores by Department",
                     color='Average_Score', color_continuous_scale='RdYlGn')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(dept_data, hide_index=True, use_container_width=True)

def show_teacher_performance():
    """Display individual teacher performance metrics"""
    st.header("👨‍🏫 Teacher Performance Overview")
    
    # Teacher selection
    teachers = ['Dr. Smith', 'Prof. Johnson', 'Ms. Davis', 'Mr. Wilson', 'Dr. Brown', 'Ms. Garcia']
    selected_teacher = st.selectbox("Select Teacher for Detailed Analysis:", teachers)
    
    if selected_teacher:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Score", "84.2/100", "↗️ +3.1 vs last month")
            st.metric("Lectures Evaluated", "12", "This semester")
        
        with col2:
            st.metric("Best Score", "92.5/100", "Recent improvement")
            st.metric("Consistency", "High", "Low variance")
        
        with col3:
            st.metric("Improvement Rate", "+15%", "Since first evaluation")
            st.metric("Ranking", "3rd", "Out of 24 teachers")
        
        # Individual lecture scores
        st.subheader(f"📊 {selected_teacher}'s Lecture Quality Timeline")
        
        # Generate sample data for selected teacher
        lecture_dates = pd.date_range(start='2024-08-01', periods=12, freq='W')
        teacher_scores = np.random.normal(82, 6, len(lecture_dates))
        teacher_scores = np.clip(teacher_scores, 60, 95)  # Keep scores realistic
        
        teacher_data = pd.DataFrame({
            'Date': lecture_dates,
            'Score': teacher_scores,
            'Lecture_Title': [f"Lecture {i+1}" for i in range(len(lecture_dates))]
        })
        
        fig = px.line(teacher_data, x='Date', y='Score', markers=True,
                      title=f"{selected_teacher} - Lecture Quality Progress",
                      hover_data=['Lecture_Title'])
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                      annotation_text="School Average")
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function for Principal Dashboard"""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 VirtuLearn - Principal Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Lecture Quality Evaluation & Analytics System</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🏫 Principal Navigation")
        
        # Principal identification
        principal_name = st.text_input("Principal Name:", value="Dr. Patricia Williams")
        school_name = st.text_input("School Name:", value="Lincoln High School")
        st.write(f"Welcome, {principal_name}! 👋")
        st.write(f"🏫 {school_name}")
        
        # Date range for analysis
        st.subheader("📅 Analysis Period")
        date_range = st.date_input(
            "Select Date Range:",
            value=(datetime.now().date() - pd.Timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date()
        )
        
        # Mode selection for principal
        mode = st.selectbox(
            "Choose Function:",
            ["📚 Evaluate Lectures", "📈 Analytics Dashboard", "👨‍🏫 Teacher Performance", "⚙️ System Settings"]
        )
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        st.metric("Total Evaluations", "127", "↗️ +12 this week")
        st.metric("Average Score", "78.4", "↗️ +2.3 this month")
        st.metric("Active Teachers", "24", "🏫 School-wide")
    
    # Main content area
    if mode == "📚 Evaluate Lectures":
        show_lecture_upload()
    elif mode == "📈 Analytics Dashboard":
        show_analytics_dashboard()
    elif mode == "👨‍🏫 Teacher Performance":
        show_teacher_performance()
    else:  # System Settings
        st.header("⚙️ System Settings")
        st.subheader("📊 System Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Evaluations", "127", "This semester")
        
        with col2:
            st.metric("Storage Used", "1.2 GB", "45% of capacity")
        
        with col3:
            st.metric("System Uptime", "99.9%", "Last 30 days")
        
        st.subheader("🔧 Configuration")
        st.checkbox("Enable automatic evaluation reminders", value=True)
        st.checkbox("Send weekly analytics reports", value=True)
        st.selectbox("Evaluation frequency:", ["Weekly", "Bi-weekly", "Monthly"])

if __name__ == "__main__":
    main()

