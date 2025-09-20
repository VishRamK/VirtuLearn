"""
Data management utilities for VirtuLearn - Enhanced for lecture analysis with MongoDB integration
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import hashlib
from .mongodb_manager import MongoDBDataManager


class LectureDataManager:
    """Class to handle lecture data operations for the VirtuLearn app with MongoDB backend"""
    
    def __init__(self, use_mongodb=True, data_dir="data"):
        self.data_dir = data_dir
        self.use_mongodb = use_mongodb
        
        if use_mongodb:
            try:
                self.db_manager = MongoDBDataManager()
                print("✅ Connected to MongoDB successfully")
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                print("🔄 Falling back to local file storage")
                self.use_mongodb = False
                self.db_manager = None
                self.ensure_data_dir()
        else:
            self.db_manager = None
            self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Ensure the data directory exists (for fallback mode)"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Create subdirectories for different data types
        subdirs = ['lectures', 'transcripts', 'slides', 'analytics', 'teachers', 'students']
        for subdir in subdirs:
            subdir_path = os.path.join(self.data_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
    
    def save_lecture_data(self, lecture_id, data, data_type="metadata"):
        """Save lecture-specific data (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                # Store in MongoDB
                if data_type == "metadata":
                    # Update lecture document
                    self.db_manager.db.lectures.update_one(
                        {'lecture_id': lecture_id},
                        {'$set': data},
                        upsert=True
                    )
                else:
                    # Store as analytics or materials
                    self.db_manager.store_analytics(lecture_id, data_type, data)
                return True
            except Exception as e:
                print(f"MongoDB save failed: {e}, falling back to local storage")
        
        # Fallback to local file storage
        filepath = os.path.join(self.data_dir, 'lectures', f"{lecture_id}_{data_type}.json")
        
        if isinstance(data, dict):
            # Add timestamp
            data['last_updated'] = datetime.now().isoformat()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError("Data must be a dictionary")
    
    def load_lecture_data(self, lecture_id, data_type="metadata"):
        """Load lecture-specific data (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                if data_type == "metadata":
                    # Get from lectures collection
                    lecture = self.db_manager.get_lecture_by_id(lecture_id)
                    return lecture
                else:
                    # Get from analytics collection
                    analytics = self.db_manager.get_analytics(lecture_id, data_type)
                    return analytics[0] if analytics else None
            except Exception as e:
                print(f"MongoDB load failed: {e}, falling back to local storage")
        
        # Fallback to local file storage
        filepath = os.path.join(self.data_dir, 'lectures', f"{lecture_id}_{data_type}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading lecture data: {e}")
            return None
    
    def create_lecture_entry(self, title, teacher_id, course_code, date, transcript_text=None, 
                           slides_content=None, duration=None, topics=None, objectives=None):
        """Create a new lecture entry (with MongoDB integration)"""
        
        if self.use_mongodb and self.db_manager:
            try:
                # Use MongoDB manager
                lecture_id = self.db_manager.create_lecture_entry(
                    title=title,
                    teacher_id=teacher_id,
                    course_code=course_code,
                    date=date,
                    transcript_text=transcript_text,
                    slides_content=slides_content,
                    duration=duration,
                    topics=topics,
                    objectives=objectives
                )
                return lecture_id
            except Exception as e:
                print(f"MongoDB create failed: {e}, falling back to local storage")
        
        # Fallback to local storage
        
        # Generate unique lecture ID
        lecture_id = hashlib.md5(f"{teacher_id}_{title}_{date}".encode()).hexdigest()[:12]
        
        # Basic lecture metadata
        lecture_data = {
            'lecture_id': lecture_id,
            'title': title,
            'teacher_id': teacher_id,
            'course_code': course_code,
            'date': date.isoformat() if isinstance(date, datetime) else str(date),
            'duration': duration,
            'topics_covered': topics or [],
            'learning_objectives': objectives or [],
            'created_at': datetime.now().isoformat(),
            'status': 'uploaded'
        }
        
        # Save basic metadata
        self.save_lecture_data(lecture_id, lecture_data, 'metadata')
        
        # Process and save transcript if provided
        if transcript_text:
            transcript_analysis = self.analyze_transcript(transcript_text)
            self.save_lecture_data(lecture_id, {
                'raw_text': transcript_text,
                'analysis': transcript_analysis
            }, 'transcript')
            
            # Update lecture metadata with analysis results
            lecture_data.update({
                'word_count': transcript_analysis.get('word_count', 0),
                'readability_score': transcript_analysis.get('readability_score', 0),
                'estimated_engagement': transcript_analysis.get('engagement_score', 0),
                'status': 'analyzed'
            })
            self.save_lecture_data(lecture_id, lecture_data, 'metadata')
        
        return lecture_id
    
    def get_teacher_performance_metrics(self, teacher_id):
        """Get teacher performance metrics (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                return self.db_manager.get_teacher_performance_metrics(teacher_id)
            except Exception as e:
                print(f"MongoDB metrics failed: {e}, falling back to local calculation")
        
        # Fallback to local calculation
        return self._calculate_local_teacher_metrics(teacher_id)
    
    def _calculate_local_teacher_metrics(self, teacher_id):
        """Calculate teacher metrics from local files"""
    
    def analyze_transcript(self, transcript_text):
        """Analyze transcript text and return metrics"""
        if not transcript_text:
            return {}
        
        # Basic text analysis
        words = transcript_text.split()
        sentences = transcript_text.split('.')
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Simulate readability analysis (Flesch Reading Ease approximation)
        avg_words_per_sentence = avg_sentence_length
        syllable_estimate = sum([len(word) * 0.5 for word in words])  # Rough estimate
        avg_syllables_per_word = syllable_estimate / word_count if word_count > 0 else 0
        
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        # Engagement indicators
        question_count = transcript_text.count('?')
        exclamation_count = transcript_text.count('!')
        interactive_words = ['think', 'consider', 'imagine', 'what if', 'let\'s', 'together']
        interactive_count = sum([transcript_text.lower().count(word) for word in interactive_words])
        
        engagement_score = min(100, 60 + (question_count * 3) + (interactive_count * 2) + (exclamation_count * 1))
        
        # Content analysis
        math_terms = ['equation', 'formula', 'calculate', 'solve', 'derivative', 'integral', 'function']
        science_terms = ['experiment', 'hypothesis', 'theory', 'molecule', 'energy', 'force']
        general_terms = ['example', 'important', 'remember', 'understand', 'concept']
        
        math_score = sum([transcript_text.lower().count(term) for term in math_terms])
        science_score = sum([transcript_text.lower().count(term) for term in science_terms])
        general_score = sum([transcript_text.lower().count(term) for term in general_terms])
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'readability_score': round(flesch_score, 1),
            'engagement_score': round(engagement_score, 1),
            'question_count': question_count,
            'interactive_elements': interactive_count,
            'content_indicators': {
                'math_focus': math_score,
                'science_focus': science_score,
                'general_teaching': general_score
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_local_teacher_metrics(self, teacher_id):
        """Calculate teacher metrics from local files"""
        lectures = self.get_teacher_lectures(teacher_id)
        
        if not lectures:
            return {
                'total_lectures': 0,
                'avg_teaching_score': 0,
                'avg_engagement': 0,
                'avg_readability': 0,
                'improvement_trend': 0
            }
        
        # Calculate averages
        engagement_scores = [l.get('estimated_engagement', 70) for l in lectures if l.get('estimated_engagement')]
        readability_scores = [l.get('readability_score', 70) for l in lectures if l.get('readability_score')]
        word_counts = [l.get('word_count', 0) for l in lectures if l.get('word_count')]
        
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 70
        avg_readability = np.mean(readability_scores) if readability_scores else 70
        avg_word_count = np.mean(word_counts) if word_counts else 0
        
        # Calculate teaching score (composite metric)
        teaching_score = (avg_engagement * 0.4 + avg_readability * 0.3 + 
                         min(100, avg_word_count / 30) * 0.3) / 10
        
        # Calculate improvement trend (compare recent vs older lectures)
        if len(lectures) >= 4:
            recent_engagement = np.mean([l.get('estimated_engagement', 70) for l in lectures[:2]])
            older_engagement = np.mean([l.get('estimated_engagement', 70) for l in lectures[-2:]])
            improvement_trend = ((recent_engagement - older_engagement) / older_engagement) * 100
        else:
            improvement_trend = 0
        
        return {
            'total_lectures': len(lectures),
            'avg_teaching_score': round(teaching_score, 1),
            'avg_engagement': round(avg_engagement, 1),
            'avg_readability': round(avg_readability, 1),
            'avg_word_count': round(avg_word_count, 0),
            'improvement_trend': round(improvement_trend, 1),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_all_lectures(self, limit=None):
        """Get all lectures (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                return self.db_manager.get_all_lectures(limit)
            except Exception as e:
                print(f"MongoDB get_all_lectures failed: {e}, falling back to local storage")
        
        # Fallback to local storage
        lectures = []
        lectures_dir = os.path.join(self.data_dir, 'lectures')
        
        if not os.path.exists(lectures_dir):
            return lectures
        
        for filename in os.listdir(lectures_dir):
            if filename.endswith('_metadata.json'):
                lecture_data = self.load_lecture_data(filename.replace('_metadata.json', ''), 'metadata')
                if lecture_data:
                    lectures.append(lecture_data)
        
        # Sort by date (most recent first)
        lectures.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if limit:
            lectures = lectures[:limit]
        
        return lectures
    
    def store_uploaded_file(self, lecture_id, file_content, filename, file_type):
        """Store uploaded files (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                return self.db_manager.store_uploaded_file(lecture_id, file_content, filename, file_type)
            except Exception as e:
                print(f"MongoDB file storage failed: {e}, falling back to local storage")
        
        # Fallback to local storage
        file_dir = os.path.join(self.data_dir, 'uploads', lecture_id)
        os.makedirs(file_dir, exist_ok=True)
        
        file_path = os.path.join(file_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    def get_teacher_lectures(self, teacher_id, limit=None):
        """Get all lectures for a specific teacher (with MongoDB integration)"""
        if self.use_mongodb and self.db_manager:
            try:
                return self.db_manager.get_teacher_lectures(teacher_id, limit)
            except Exception as e:
                print(f"MongoDB get_teacher_lectures failed: {e}, falling back to local storage")
        
        # Fallback to local storage
        lectures = []
        lectures_dir = os.path.join(self.data_dir, 'lectures')
        
        if not os.path.exists(lectures_dir):
            return lectures
        
        for filename in os.listdir(lectures_dir):
            if filename.endswith('_metadata.json'):
                lecture_data = self.load_lecture_data(filename.replace('_metadata.json', ''), 'metadata')
                if lecture_data and lecture_data.get('teacher_id') == teacher_id:
                    lectures.append(lecture_data)
        
        # Sort by date (most recent first)
        lectures.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if limit:
            lectures = lectures[:limit]
        
        return lectures
    
    def get_teacher_performance_metrics(self, teacher_id):
        """Calculate performance metrics for a teacher"""
        lectures = self.get_teacher_lectures(teacher_id)
        
        if not lectures:
            return {
                'total_lectures': 0,
                'avg_teaching_score': 0,
                'avg_engagement': 0,
                'avg_readability': 0,
                'improvement_trend': 0
            }
        
        # Calculate averages
        engagement_scores = [l.get('estimated_engagement', 70) for l in lectures if l.get('estimated_engagement')]
        readability_scores = [l.get('readability_score', 70) for l in lectures if l.get('readability_score')]
        word_counts = [l.get('word_count', 0) for l in lectures if l.get('word_count')]
        
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 70
        avg_readability = np.mean(readability_scores) if readability_scores else 70
        avg_word_count = np.mean(word_counts) if word_counts else 0
        
        # Calculate teaching score (composite metric)
        teaching_score = (avg_engagement * 0.4 + avg_readability * 0.3 + 
                         min(100, avg_word_count / 30) * 0.3) / 10
        
        # Calculate improvement trend (compare recent vs older lectures)
        if len(lectures) >= 4:
            recent_engagement = np.mean([l.get('estimated_engagement', 70) for l in lectures[:2]])
            older_engagement = np.mean([l.get('estimated_engagement', 70) for l in lectures[-2:]])
            improvement_trend = ((recent_engagement - older_engagement) / older_engagement) * 100
        else:
            improvement_trend = 0
        
        return {
            'total_lectures': len(lectures),
            'avg_teaching_score': round(teaching_score, 1),
            'avg_engagement': round(avg_engagement, 1),
            'avg_readability': round(avg_readability, 1),
            'avg_word_count': round(avg_word_count, 0),
            'improvement_trend': round(improvement_trend, 1),
            'last_updated': datetime.now().isoformat()
        }
    
    def save_teacher_profile(self, teacher_id, profile_data):
        """Save teacher profile information"""
        filepath = os.path.join(self.data_dir, 'teachers', f"{teacher_id}_profile.json")
        
        profile_data['teacher_id'] = teacher_id
        profile_data['last_updated'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(profile_data, f, indent=2, default=str)
    
    def load_teacher_profile(self, teacher_id):
        """Load teacher profile information"""
        filepath = os.path.join(self.data_dir, 'teachers', f"{teacher_id}_profile.json")
        
        if not os.path.exists(filepath):
            return {
                'teacher_id': teacher_id,
                'name': f"Teacher {teacher_id}",
                'subject': 'General',
                'email': f"{teacher_id}@school.edu",
                'created_at': datetime.now().isoformat()
            }
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading teacher profile: {e}")
            return None
    
    def get_student_lecture_access(self, student_id, course_codes=None):
        """Get lectures accessible to a student"""
        accessible_lectures = []
        lectures_dir = os.path.join(self.data_dir, 'lectures')
        
        if not os.path.exists(lectures_dir):
            return accessible_lectures
        
        for filename in os.listdir(lectures_dir):
            if filename.endswith('_metadata.json'):
                lecture_data = self.load_lecture_data(filename.replace('_metadata.json', ''), 'metadata')
                if lecture_data:
                    # If course codes specified, filter by them
                    if course_codes and lecture_data.get('course_code') not in course_codes:
                        continue
                    
                    # Create student-friendly view (remove sensitive teacher data)
                    student_view = {
                        'lecture_id': lecture_data.get('lecture_id'),
                        'title': lecture_data.get('title'),
                        'course_code': lecture_data.get('course_code'),
                        'date': lecture_data.get('date'),
                        'duration': lecture_data.get('duration'),
                        'topics_covered': lecture_data.get('topics_covered', []),
                        'learning_objectives': lecture_data.get('learning_objectives', []),
                        'has_transcript': self.load_lecture_data(lecture_data.get('lecture_id'), 'transcript') is not None
                    }
                    accessible_lectures.append(student_view)
        
        # Sort by date (most recent first)
        accessible_lectures.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return accessible_lectures
    
    def generate_sample_lecture_data(self, teacher_id, num_lectures=5):
        """Generate sample lecture data for demonstration"""
        sample_titles = [
            "Introduction to Derivatives",
            "Limits and Continuity", 
            "Function Graphs and Analysis",
            "Polynomial Functions",
            "Trigonometric Functions",
            "Integration Basics",
            "Applications of Calculus",
            "Differential Equations"
        ]
        
        sample_transcripts = [
            "Today we'll explore derivatives, which are fundamental to calculus. Think of a derivative as the rate of change. For example, if you're driving, your speedometer shows the derivative of distance with respect to time. Let's work through some examples together.",
            "Limits help us understand what happens to a function as we approach a particular point. This concept is crucial for understanding continuity. Can you think of real-world examples where we approach but never quite reach a limit?",
            "Graphing functions visually represents mathematical relationships. When we plot a function, we can see its behavior clearly. What patterns do you notice in these graphs?",
            "Polynomial functions form the building blocks of many mathematical models. These functions appear everywhere in science and engineering. Let's solve some problems step by step.",
            "Trigonometric functions describe periodic phenomena. From sound waves to seasonal temperature changes, these functions model repeating patterns. Remember the key relationships we discussed."
        ]
        
        for i in range(min(num_lectures, len(sample_titles))):
            lecture_date = datetime.now() - timedelta(days=i*3)
            
            self.create_lecture_entry(
                title=sample_titles[i],
                teacher_id=teacher_id,
                course_code="MATH101",
                date=lecture_date,
                transcript_text=sample_transcripts[i % len(sample_transcripts)],
                duration=np.random.randint(45, 60),
                topics=[f"Topic {j+1}" for j in range(np.random.randint(2, 5))],
                objectives=[f"Objective {j+1}" for j in range(np.random.randint(2, 4))]
            )
    
    def export_teacher_data(self, teacher_id):
        """Export all data for a teacher"""
        teacher_data = {
            'profile': self.load_teacher_profile(teacher_id),
            'lectures': self.get_teacher_lectures(teacher_id),
            'performance_metrics': self.get_teacher_performance_metrics(teacher_id),
            'export_timestamp': datetime.now().isoformat()
        }
        
        return teacher_data
    
    def get_school_analytics(self):
        """Get school-wide analytics"""
        teachers_dir = os.path.join(self.data_dir, 'teachers')
        lectures_dir = os.path.join(self.data_dir, 'lectures')
        
        total_teachers = 0
        total_lectures = 0
        avg_scores = []
        
        # Count teachers
        if os.path.exists(teachers_dir):
            total_teachers = len([f for f in os.listdir(teachers_dir) if f.endswith('_profile.json')])
        
        # Count lectures and calculate averages
        if os.path.exists(lectures_dir):
            lecture_files = [f for f in os.listdir(lectures_dir) if f.endswith('_metadata.json')]
            total_lectures = len(lecture_files)
            
            for filename in lecture_files:
                lecture_data = self.load_lecture_data(filename.replace('_metadata.json', ''), 'metadata')
                if lecture_data and lecture_data.get('estimated_engagement'):
                    avg_scores.append(lecture_data.get('estimated_engagement'))
        
        school_avg = np.mean(avg_scores) if avg_scores else 0
        
        return {
            'total_teachers': total_teachers,
            'total_lectures': total_lectures,
            'school_avg_engagement': round(school_avg, 1),
            'active_courses': len(set([l.get('course_code', '') for l in [
                self.load_lecture_data(f.replace('_metadata.json', ''), 'metadata') 
                for f in os.listdir(lectures_dir) if f.endswith('_metadata.json')
            ] if l and l.get('course_code')])),
            'last_calculated': datetime.now().isoformat()
        }


# Global instance
lecture_data_manager = LectureDataManager()