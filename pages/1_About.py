import streamlit as st# About page placeholder


st.set_page_config(
    page_title="About VirtuLearn",
    page_icon="📚",
    layout="wide"
)

st.title("📚 About VirtuLearn")
st.markdown("---")

# Introduction
st.header("🎯 Purpose")
st.markdown("""
VirtuLearn is designed specifically for **school principals** to evaluate and monitor lecture quality 
across their institution. Our platform provides comprehensive analytics to help improve educational outcomes 
through data-driven insights.
""")

# Key Features
st.header("✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Lecture Evaluation")
    st.markdown("""
    - Upload teacher lecture transcripts
    - Automated quality scoring system
    - Detailed evaluation reports
    - Performance tracking over time
    """)
    
    st.subheader("📈 Analytics Dashboard")
    st.markdown("""
    - School-wide performance metrics
    - Teacher comparison analytics
    - Trend analysis and insights
    - Department-wise breakdowns
    """)

with col2:
    st.subheader("🎯 Scoring Criteria")
    st.markdown("""
    - **Content Correctness (40%)**: Accuracy and curriculum alignment
    - **Class Engagement (35%)**: Student interaction and participation
    - **Structure & Clarity (15%)**: Organization and delivery
    - **Topic Coverage (10%)**: Completeness of subject matter
    """)
    
    st.subheader("💾 Data Management")
    st.markdown("""
    - Secure MongoDB cloud storage
    - Historical data preservation
    - Export capabilities
    - Privacy protection
    """)

# How to Use
st.header("🚀 How to Use VirtuLearn")

st.markdown("""
### Getting Started

1. **📚 Upload Lectures**: Start by uploading teacher lecture transcripts
2. **⚡ Automatic Analysis**: Our system evaluates content and engagement
3. **📊 Review Scores**: Get detailed scoring across multiple criteria
4. **📈 Track Progress**: Monitor improvements over time
5. **🎯 Take Action**: Use insights to support teacher development

### Navigation

- **Home**: Upload lectures and view evaluation results
- **Teacher Analytics**: Compare individual teacher performance
- **Lecture Analytics**: Analyze specific lecture trends and patterns
""")

# Technical Details
st.header("🔧 Technical Information")

with st.expander("System Details"):
    st.markdown("""
    - **Framework**: Streamlit web application
    - **Database**: MongoDB Atlas cloud storage
    - **Security**: Encrypted data transmission and storage
    - **Analytics**: Real-time processing and trend analysis
    - **Compatibility**: Web-based, works on all modern browsers
    """)

# Contact and Support
st.header("📞 Support")
st.markdown("""
For technical support or feature requests, please contact your system administrator 
or IT department.
""")

st.markdown("---")
st.markdown("*VirtuLearn - Empowering Educational Excellence Through Data*")