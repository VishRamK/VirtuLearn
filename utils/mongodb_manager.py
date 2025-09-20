"""
MongoDB Data Manager for VirtuLearn - Enhanced Database Integration
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import base64

import pymongo
from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
import openai
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBDataManager:
    """Enhanced MongoDB data manager for VirtuLearn lecture analysis platform"""
    
    def __init__(self):
        # Database configuration
        self.database_url = os.getenv('DATABASE_URL')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Initialize MongoDB connection
        self.client = None
        self.db = None
        self.fs = None
        self.connect_to_database()
        
        # Configure OpenAI if available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def connect_to_database(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.database_url)
            self.db = self.client.virtulearn
            self.fs = GridFS(self.db)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes for better performance
            self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Lectures collection indexes
            self.db.lectures.create_index([("lecture_id", 1)], unique=True)
            self.db.lectures.create_index([("teacher_id", 1)])
            self.db.lectures.create_index([("course_code", 1)])
            self.db.lectures.create_index([("date", -1)])
            self.db.lectures.create_index([("status", 1)])
            
            # Teachers collection indexes
            self.db.teachers.create_index([("teacher_id", 1)], unique=True)
            self.db.teachers.create_index([("email", 1)], unique=True)
            
            # Students collection indexes
            self.db.students.create_index([("student_id", 1)], unique=True)
            self.db.students.create_index([("email", 1)], unique=True)
            
            # Analytics collection indexes
            self.db.analytics.create_index([("lecture_id", 1)])
            self.db.analytics.create_index([("analysis_type", 1)])
            self.db.analytics.create_index([("created_at", -1)])
            
            # Materials collection indexes
            self.db.materials.create_index([("lecture_id", 1)])
            self.db.materials.create_index([("material_type", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    # Lecture Management
    def create_lecture_entry(self, title: str, teacher_id: str, course_code: str, 
                           date: datetime, transcript_text: Optional[str] = None,
                           slides_content: Optional[str] = None, duration: Optional[int] = None,
                           topics: Optional[List[str]] = None, objectives: Optional[List[str]] = None) -> str:
        """Create a new lecture entry in MongoDB"""
        
        # Generate unique lecture ID
        lecture_id = hashlib.md5(f"{teacher_id}_{title}_{date}".encode()).hexdigest()[:12]
        
        # Basic lecture document
        lecture_doc = {
            'lecture_id': lecture_id,
            'title': title,
            'teacher_id': teacher_id,
            'course_code': course_code,
            'date': date,
            'duration': duration,
            'topics_covered': topics or [],
            'learning_objectives': objectives or [],
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'status': 'uploaded',
            'analytics_generated': False,
            'metadata': {
                'word_count': 0,
                'readability_score': 0,
                'engagement_score': 0,
                'ai_analysis_completed': False
            }
        }
        
        try:
            # Insert lecture document
            self.db.lectures.insert_one(lecture_doc)
            logger.info(f"Created lecture entry: {lecture_id}")
            
            # Process transcript if provided
            if transcript_text:
                self.store_transcript(lecture_id, transcript_text)
                
            # Process slides if provided
            if slides_content:
                self.store_slides(lecture_id, slides_content)
                
            return lecture_id
            
        except Exception as e:
            logger.error(f"Error creating lecture entry: {e}")
            raise
    
    def store_transcript(self, lecture_id: str, transcript_text: str) -> Dict[str, Any]:
        """Store and analyze transcript text"""
        try:
            # Analyze transcript
            analysis = self.analyze_transcript(transcript_text)
            
            # Store transcript and analysis
            transcript_doc = {
                'lecture_id': lecture_id,
                'material_type': 'transcript',
                'content': transcript_text,
                'analysis': analysis,
                'created_at': datetime.now(),
                'file_size': len(transcript_text.encode('utf-8'))
            }
            
            self.db.materials.insert_one(transcript_doc)
            
            # Update lecture metadata
            self.db.lectures.update_one(
                {'lecture_id': lecture_id},
                {
                    '$set': {
                        'metadata.word_count': analysis.get('word_count', 0),
                        'metadata.readability_score': analysis.get('readability_score', 0),
                        'metadata.engagement_score': analysis.get('engagement_score', 0),
                        'status': 'analyzed',
                        'last_updated': datetime.now()
                    }
                }
            )
            
            logger.info(f"Stored transcript for lecture: {lecture_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error storing transcript: {e}")
            raise
    
    def store_slides(self, lecture_id: str, slides_content: str) -> bool:
        """Store lecture slides content"""
        try:
            slides_doc = {
                'lecture_id': lecture_id,
                'material_type': 'slides',
                'content': slides_content,
                'created_at': datetime.now(),
                'file_size': len(slides_content.encode('utf-8'))
            }
            
            self.db.materials.insert_one(slides_doc)
            logger.info(f"Stored slides for lecture: {lecture_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing slides: {e}")
            return False
    
    def store_uploaded_file(self, lecture_id: str, file_content: bytes, 
                          filename: str, file_type: str) -> str:
        """Store uploaded files using GridFS for large files"""
        try:
            # Store file in GridFS
            file_id = self.fs.put(
                file_content,
                filename=filename,
                lecture_id=lecture_id,
                file_type=file_type,
                upload_date=datetime.now()
            )
            
            # Create reference document
            file_doc = {
                'lecture_id': lecture_id,
                'material_type': 'uploaded_file',
                'file_id': file_id,
                'filename': filename,
                'file_type': file_type,
                'file_size': len(file_content),
                'created_at': datetime.now()
            }
            
            self.db.materials.insert_one(file_doc)
            logger.info(f"Stored uploaded file: {filename} for lecture: {lecture_id}")
            
            return str(file_id)
            
        except Exception as e:
            logger.error(f"Error storing uploaded file: {e}")
            raise
    
    def get_uploaded_file(self, file_id: str) -> bytes:
        """Retrieve uploaded file from GridFS"""
        try:
            file_obj = self.fs.get(file_id)
            return file_obj.read()
        except Exception as e:
            logger.error(f"Error retrieving file: {e}")
            raise
    
    # Analytics and Insights
    def store_analytics(self, lecture_id: str, analysis_type: str, 
                       insights: Dict[str, Any]) -> bool:
        """Store generated analytics and insights"""
        try:
            analytics_doc = {
                'lecture_id': lecture_id,
                'analysis_type': analysis_type,
                'insights': insights,
                'created_at': datetime.now(),
                'ai_generated': True if 'ai_' in analysis_type else False
            }
            
            # Store or update analytics
            self.db.analytics.replace_one(
                {'lecture_id': lecture_id, 'analysis_type': analysis_type},
                analytics_doc,
                upsert=True
            )
            
            # Update lecture analytics flag
            self.db.lectures.update_one(
                {'lecture_id': lecture_id},
                {
                    '$set': {
                        'analytics_generated': True,
                        'last_updated': datetime.now()
                    }
                }
            )
            
            logger.info(f"Stored {analysis_type} analytics for lecture: {lecture_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analytics: {e}")
            return False
    
    def get_analytics(self, lecture_id: str, analysis_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve analytics for a lecture"""
        try:
            query = {'lecture_id': lecture_id}
            if analysis_type:
                query['analysis_type'] = analysis_type
                
            analytics = list(self.db.analytics.find(query, {'_id': 0}))
            return analytics
            
        except Exception as e:
            logger.error(f"Error retrieving analytics: {e}")
            return []
    
    def analyze_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Enhanced transcript analysis with AI insights"""
        if not transcript_text:
            return {}
        
        # Basic text analysis
        words = transcript_text.split()
        sentences = transcript_text.split('.')
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability analysis (Flesch Reading Ease)
        syllable_estimate = sum([len(word) * 0.5 for word in words])
        avg_syllables_per_word = syllable_estimate / word_count if word_count > 0 else 0
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))
        
        # Engagement indicators
        question_count = transcript_text.count('?')
        exclamation_count = transcript_text.count('!')
        interactive_words = ['think', 'consider', 'imagine', 'what if', 'let\'s', 'together', 'discuss']
        interactive_count = sum([transcript_text.lower().count(word) for word in interactive_words])
        
        engagement_score = min(100, 60 + (question_count * 3) + (interactive_count * 2) + (exclamation_count * 1))
        
        # Content analysis
        subject_keywords = {
            'math': ['equation', 'formula', 'calculate', 'solve', 'derivative', 'integral', 'function', 'theorem'],
            'science': ['experiment', 'hypothesis', 'theory', 'molecule', 'energy', 'force', 'reaction'],
            'history': ['century', 'war', 'revolution', 'empire', 'civilization', 'ancient', 'medieval'],
            'language': ['grammar', 'vocabulary', 'syntax', 'literature', 'poetry', 'prose', 'metaphor'],
            'general': ['example', 'important', 'remember', 'understand', 'concept', 'principle']
        }
        
        subject_scores = {}
        for subject, keywords in subject_keywords.items():
            subject_scores[subject] = sum([transcript_text.lower().count(term) for term in keywords])
        
        # AI-enhanced analysis (if OpenAI available)
        ai_insights = {}
        if self.openai_api_key and word_count > 50:
            try:
                ai_insights = self.generate_ai_insights(transcript_text)
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
        
        analysis_result = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'readability_score': round(flesch_score, 1),
            'engagement_score': round(engagement_score, 1),
            'question_count': question_count,
            'interactive_elements': interactive_count,
            'subject_focus': subject_scores,
            'analysis_timestamp': datetime.now().isoformat(),
            'ai_insights': ai_insights
        }
        
        return analysis_result
    
    def generate_ai_insights(self, transcript_text: str) -> Dict[str, Any]:
        """Generate AI-powered insights using OpenAI"""
        try:
            # Truncate text if too long for API
            max_tokens = 3000
            if len(transcript_text) > max_tokens:
                transcript_text = transcript_text[:max_tokens] + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational expert analyzing lecture transcripts. Provide insights on teaching effectiveness, clarity, engagement, and areas for improvement."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this lecture transcript and provide insights:\n\n{transcript_text}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'summary': ai_analysis,
                'generated_at': datetime.now().isoformat(),
                'model_used': 'gpt-3.5-turbo'
            }
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return {'error': str(e)}
    
    # Teacher and Student Management
    def get_teacher_lectures(self, teacher_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all lectures for a specific teacher"""
        try:
            query = {'teacher_id': teacher_id}
            cursor = self.db.lectures.find(query, {'_id': 0}).sort('date', -1)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Error retrieving teacher lectures: {e}")
            return []
    
    def get_teacher_performance_metrics(self, teacher_id: str) -> Dict[str, Any]:
        """Calculate comprehensive teacher performance metrics"""
        try:
            lectures = self.get_teacher_lectures(teacher_id)
            
            if not lectures:
                return {'error': 'No lectures found for teacher'}
            
            # Calculate metrics
            total_lectures = len(lectures)
            avg_readability = sum([l.get('metadata', {}).get('readability_score', 0) for l in lectures]) / total_lectures
            avg_engagement = sum([l.get('metadata', {}).get('engagement_score', 0) for l in lectures]) / total_lectures
            total_word_count = sum([l.get('metadata', {}).get('word_count', 0) for l in lectures])
            
            # Recent performance (last 30 days)
            recent_date = datetime.now() - timedelta(days=30)
            recent_lectures = [l for l in lectures if l.get('date', datetime.min) > recent_date]
            
            metrics = {
                'teacher_id': teacher_id,
                'total_lectures': total_lectures,
                'recent_lectures': len(recent_lectures),
                'avg_readability_score': round(avg_readability, 1),
                'avg_engagement_score': round(avg_engagement, 1),
                'total_content_delivered': total_word_count,
                'performance_trend': 'improving' if len(recent_lectures) > total_lectures * 0.3 else 'stable',
                'calculated_at': datetime.now(),
                'courses_taught': list(set([l.get('course_code') for l in lectures]))
            }
            
            # Store metrics
            self.store_analytics(f"teacher_{teacher_id}", 'performance_metrics', metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating teacher metrics: {e}")
            return {'error': str(e)}
    
    def get_all_lectures(self, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        """Get all lectures with optional limit"""
        try:
            cursor = self.db.lectures.find({}, {'_id': 0}).sort('date', -1)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving lectures: {e}")
            return []
    
    def get_lecture_by_id(self, lecture_id: str) -> Optional[Dict[str, Any]]:
        """Get specific lecture by ID"""
        try:
            lecture = self.db.lectures.find_one({'lecture_id': lecture_id}, {'_id': 0})
            return lecture
        except Exception as e:
            logger.error(f"Error retrieving lecture: {e}")
            return None
    
    def get_lecture_materials(self, lecture_id: str) -> List[Dict[str, Any]]:
        """Get all materials for a specific lecture"""
        try:
            materials = list(self.db.materials.find(
                {'lecture_id': lecture_id}, 
                {'_id': 0, 'content': 0}  # Exclude large content field
            ))
            return materials
        except Exception as e:
            logger.error(f"Error retrieving lecture materials: {e}")
            return []