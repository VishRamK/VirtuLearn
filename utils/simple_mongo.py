"""
Simple MongoDB Manager for VirtuLearn App Integration
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMongoManager:
    """Simplified MongoDB manager for VirtuLearn"""
    
    def __init__(self):
        # Database configuration
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Initialize MongoDB connection
        self.client = None
        self.db = None
        self.connect_to_database()
    
    def connect_to_database(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.database_url)
            self.db = self.client.virtulearn
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create basic indexes
            self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """Create basic database indexes"""
        try:
            # Lectures collection indexes
            self.db.lectures.create_index([("lecture_id", 1)], unique=True)
            self.db.lectures.create_index([("teacher_id", 1)])
            self.db.lectures.create_index([("date", -1)])
            
            # Materials collection indexes
            self.db.materials.create_index([("lecture_id", 1)])
            self.db.materials.create_index([("material_type", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def store_lecture(self, title: str, teacher_id: str, course_code: str, 
                     transcript_text: str = None, **kwargs) -> str:
        """Store a lecture and return its ID"""
        try:
            # Generate unique lecture ID
            lecture_id = hashlib.md5(f"{teacher_id}_{title}_{datetime.now()}".encode()).hexdigest()[:12]
            
            # Create lecture document
            lecture_doc = {
                'lecture_id': lecture_id,
                'title': title,
                'teacher_id': teacher_id,
                'course_code': course_code,
                'date': datetime.now(),
                'created_at': datetime.now(),
                'status': 'uploaded',
                'transcript_analyzed': False,
                **kwargs  # Additional fields
            }
            
            # Insert lecture document
            self.db.lectures.insert_one(lecture_doc)
            logger.info(f"Stored lecture: {lecture_id}")
            
            # Process transcript if provided
            if transcript_text:
                self.store_transcript(lecture_id, transcript_text)
            
            return lecture_id
            
        except Exception as e:
            logger.error(f"Error storing lecture: {e}")
            raise
    
    def store_transcript(self, lecture_id: str, transcript_text: str):
        """Store and analyze transcript"""
        try:
            # Simple analysis
            words = transcript_text.split()
            word_count = len(words)
            
            # Store transcript
            transcript_doc = {
                'lecture_id': lecture_id,
                'material_type': 'transcript',
                'content': transcript_text,
                'word_count': word_count,
                'analysis': {
                    'word_count': word_count,
                    'readability_score': min(100, max(0, 80 - (word_count / 100))),
                    'engagement_score': min(100, 70 + (transcript_text.count('?') * 5)),
                },
                'created_at': datetime.now()
            }
            
            self.db.materials.insert_one(transcript_doc)
            
            # Update lecture with analysis
            self.db.lectures.update_one(
                {'lecture_id': lecture_id},
                {
                    '$set': {
                        'word_count': word_count,
                        'transcript_analyzed': True,
                        'status': 'analyzed'
                    }
                }
            )
            
            logger.info(f"Stored transcript for lecture: {lecture_id}")
            
        except Exception as e:
            logger.error(f"Error storing transcript: {e}")
    
    def store_file(self, lecture_id: str, file_content: bytes, 
                   filename: str, file_type: str) -> str:
        """Store uploaded file"""
        try:
            # For now, store file metadata (you could use GridFS for actual files)
            file_doc = {
                'lecture_id': lecture_id,
                'material_type': 'uploaded_file',
                'filename': filename,
                'file_type': file_type,
                'file_size': len(file_content),
                'created_at': datetime.now(),
                # For demo, we'll just store that we received the file
                'stored': True
            }
            
            result = self.db.materials.insert_one(file_doc)
            logger.info(f"Stored file metadata: {filename} for lecture: {lecture_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing file: {e}")
            raise
    
    def get_lecture(self, lecture_id: str) -> Optional[Dict[str, Any]]:
        """Get lecture by ID"""
        try:
            lecture = self.db.lectures.find_one({'lecture_id': lecture_id}, {'_id': 0})
            return lecture
        except Exception as e:
            logger.error(f"Error retrieving lecture: {e}")
            return None
    
    def get_teacher_lectures(self, teacher_id: str) -> List[Dict[str, Any]]:
        """Get all lectures for a teacher"""
        try:
            lectures = list(self.db.lectures.find(
                {'teacher_id': teacher_id}, 
                {'_id': 0}
            ).sort('date', -1))
            return lectures
        except Exception as e:
            logger.error(f"Error retrieving teacher lectures: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()


# Global instance for easy import
mongo_manager = SimpleMongoManager()