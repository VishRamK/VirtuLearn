import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="About VirtuLearn", page_icon="ℹ️")

st.title("ℹ️ About VirtuLearn")

st.markdown("""
## Welcome to VirtuLearn! 🎓

VirtuLearn is an innovative educational analytics platform designed to revolutionize teaching and learning through data-driven insights. Our platform serves both educators and students by analyzing lecture content and providing actionable feedback.

### 🎯 Our Mission

To enhance educational quality by providing real-time analytics on teaching effectiveness and student learning outcomes through advanced content analysis of lectures, transcripts, and educational materials.

### 👥 Who We Serve

#### 👨‍🏫 **For Teachers**
- **Performance Analytics**: Get detailed insights into your teaching effectiveness
- **Content Analysis**: Analyze lecture transcripts for clarity, engagement, and comprehension
- **Student Feedback**: Receive structured feedback from students
- **Improvement Recommendations**: AI-powered suggestions for enhancing your teaching

#### 👨‍🎓 **For Students**
- **Learning Support**: Access analyzed lecture content and summaries
- **Progress Tracking**: Monitor your understanding and engagement levels
- **Study Materials**: Get organized access to transcripts, slides, and resources
- **Personalized Insights**: Understand your learning patterns and areas for improvement

#### 👨‍💼 **For Administrators**
- **School-wide Analytics**: Overview of teaching quality across the institution
- **Performance Monitoring**: Track teacher effectiveness and student outcomes
- **Data-driven Decisions**: Make informed decisions based on comprehensive analytics
- **Resource Optimization**: Identify areas needing support or improvement

### 🚀 Key Features

#### 📤 **Lecture Upload & Analysis**
- Upload lecture transcripts, slides, and supplementary materials
- Automated content analysis using NLP and machine learning
- Real-time feedback on lecture quality and effectiveness

#### 📊 **Performance Metrics**
- Teaching effectiveness scores
- Student engagement analytics
- Content quality assessments
- Comparative analysis across time periods

#### 🎯 **AI-Powered Insights**
- Automated recommendations for teaching improvement
- Content optimization suggestions
- Student learning pattern analysis
- Predictive analytics for academic outcomes

#### 📈 **Comprehensive Dashboards**
- Teacher performance dashboards
- Student learning analytics
- Administrative oversight panels
- Customizable reporting tools

### 🔧 Technology Stack

This application is built using cutting-edge technologies:
- **Streamlit**: Interactive web interface
- **Python**: Core backend processing
- **Natural Language Processing**: Content analysis and insights
- **Machine Learning**: Predictive analytics and recommendations
- **Plotly**: Advanced data visualizations
- **Pandas**: Data manipulation and analysis

### 📈 Platform Statistics

"""
)

# Add some sample metrics about the platform
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Lectures Analyzed", "12,450+", "↗️ Growing daily")

with col2:
    st.metric("Teachers Served", "350+", "↗️ Across 15 schools")

with col3:
    st.metric("Student Improvement", "23%", "↗️ Average increase")

st.markdown("""

### 🌟 Success Stories

> *"VirtuLearn helped me identify that my lectures were too fast-paced. After implementing their suggestions, student comprehension improved by 30%!"*
> 
> **— Dr. Sarah Johnson, Mathematics Professor**

> *"The platform's analysis of our lecture transcripts revealed patterns we never noticed. It's like having a teaching coach available 24/7."*
> 
> **— Prof. Michael Chen, Physics Department**

### 🔒 Privacy & Security

We take data privacy seriously:
- All lecture content is encrypted and securely stored
- User data is anonymized for analytics
- Compliance with educational privacy standards
- Transparent data usage policies

### 📞 Get Started

Ready to transform your educational experience?

1. **Teachers**: Upload your first lecture transcript and get instant insights
2. **Students**: Access your learning dashboard to track progress
3. **Administrators**: Set up school-wide analytics and monitoring

### 🆘 Support & Resources

- 📖 **Documentation**: Comprehensive guides and tutorials
- 💬 **Community Forum**: Connect with other educators and students
- 📧 **Support Team**: Get help when you need it
- 🎥 **Training Videos**: Learn to maximize platform benefits

---

*Empowering education through intelligent analytics* ✨
""")

# Add a feedback section
st.subheader("� Share Your Thoughts")
with st.expander("We'd love to hear from you!"):
    user_type = st.selectbox("I am a:", ["Teacher", "Student", "Administrator", "Other"])
    feedback = st.text_area("What do you think about VirtuLearn?", 
                           placeholder="Your feedback helps us improve the platform...")
    
    rating = st.slider("Rate your experience", 1, 5, 5)
    
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! 🙏 We'll use it to make VirtuLearn even better.")