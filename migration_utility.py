"""
Migration and Error Handling Utilities for VirtuLearn MongoDB Integration
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('virtulearn_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VirtuLearnMigrationManager:
    """Handles data migration and error recovery for VirtuLearn"""
    
    def __init__(self):
        self.local_data_dir = "data"
        self.backup_dir = "data_backup"
        self.mongo_manager = None
        
        # Initialize MongoDB connection with error handling
        try:
            from utils.simple_mongo import SimpleMongoManager
            self.mongo_manager = SimpleMongoManager()
            logger.info("✅ MongoDB connection established for migration")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.mongo_manager = None
    
    def create_backup(self) -> bool:
        """Create backup of local data before migration"""
        try:
            import shutil
            
            if os.path.exists(self.local_data_dir):
                # Create backup directory
                os.makedirs(self.backup_dir, exist_ok=True)
                
                # Copy all data files
                backup_path = os.path.join(self.backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copytree(self.local_data_dir, backup_path)
                
                logger.info(f"✅ Backup created at: {backup_path}")
                return True
            else:
                logger.info("📂 No local data directory found - skipping backup")
                return True
                
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return False
    
    def migrate_local_to_mongodb(self) -> Dict[str, Any]:
        """Migrate existing local data to MongoDB"""
        migration_results = {
            'lectures_migrated': 0,
            'materials_migrated': 0,
            'errors': [],
            'success': False
        }
        
        if not self.mongo_manager:
            migration_results['errors'].append("MongoDB connection not available")
            return migration_results
        
        try:
            # Create backup first
            if not self.create_backup():
                migration_results['errors'].append("Backup creation failed")
                return migration_results
            
            # Migrate lecture data
            lectures_dir = os.path.join(self.local_data_dir, 'lectures')
            if os.path.exists(lectures_dir):
                for filename in os.listdir(lectures_dir):
                    if filename.endswith('_metadata.json'):
                        try:
                            self._migrate_lecture_file(filename, lectures_dir)
                            migration_results['lectures_migrated'] += 1
                        except Exception as e:
                            error_msg = f"Failed to migrate {filename}: {str(e)}"
                            migration_results['errors'].append(error_msg)
                            logger.error(error_msg)
            
            # Migrate material files
            materials_dirs = ['transcripts', 'slides', 'analytics']
            for materials_dir in materials_dirs:
                dir_path = os.path.join(self.local_data_dir, materials_dir)
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        try:
                            self._migrate_material_file(filename, dir_path, materials_dir)
                            migration_results['materials_migrated'] += 1
                        except Exception as e:
                            error_msg = f"Failed to migrate material {filename}: {str(e)}"
                            migration_results['errors'].append(error_msg)
                            logger.error(error_msg)
            
            migration_results['success'] = True
            logger.info(f"✅ Migration completed: {migration_results}")
            
        except Exception as e:
            error_msg = f"Migration process failed: {str(e)}"
            migration_results['errors'].append(error_msg)
            logger.error(error_msg)
            logger.error(traceback.format_exc())
        
        return migration_results
    
    def _migrate_lecture_file(self, filename: str, lectures_dir: str):
        """Migrate a single lecture metadata file"""
        filepath = os.path.join(lectures_dir, filename)
        lecture_id = filename.replace('_metadata.json', '')
        
        with open(filepath, 'r') as f:
            lecture_data = json.load(f)
        
        # Check if lecture already exists in MongoDB
        existing = self.mongo_manager.get_lecture(lecture_id)
        if existing:
            logger.info(f"📝 Lecture {lecture_id} already exists in MongoDB, skipping")
            return
        
        # Insert lecture into MongoDB
        self.mongo_manager.store_lecture(
            title=lecture_data.get('title', 'Migrated Lecture'),
            teacher_id=lecture_data.get('teacher_id', 'unknown'),
            course_code=lecture_data.get('course_code', 'UNKNOWN'),
            transcript_text=None,  # Will be handled separately
            duration=lecture_data.get('duration'),
            topics=lecture_data.get('topics_covered', []),
            objectives=lecture_data.get('learning_objectives', [])
        )
        
        logger.info(f"✅ Migrated lecture: {lecture_id}")
    
    def _migrate_material_file(self, filename: str, dir_path: str, material_type: str):
        """Migrate a single material file"""
        filepath = os.path.join(dir_path, filename)
        
        # Extract lecture_id from filename (assuming format: lectureId_type.json)
        if '_' in filename:
            lecture_id = filename.split('_')[0]
        else:
            lecture_id = filename.replace('.json', '')
        
        with open(filepath, 'r') as f:
            material_data = json.load(f)
        
        # Store material in MongoDB
        material_doc = {
            'lecture_id': lecture_id,
            'material_type': material_type,
            'content': material_data,
            'migrated_from': filepath,
            'created_at': datetime.now()
        }
        
        self.mongo_manager.db.materials.insert_one(material_doc)
        logger.info(f"✅ Migrated material: {filename}")
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful"""
        verification_results = {
            'mongodb_lectures': 0,
            'mongodb_materials': 0,
            'local_lectures': 0,
            'local_materials': 0,
            'verification_passed': False
        }
        
        try:
            if self.mongo_manager:
                # Count MongoDB documents
                verification_results['mongodb_lectures'] = self.mongo_manager.db.lectures.count_documents({})
                verification_results['mongodb_materials'] = self.mongo_manager.db.materials.count_documents({})
            
            # Count local files
            lectures_dir = os.path.join(self.local_data_dir, 'lectures')
            if os.path.exists(lectures_dir):
                verification_results['local_lectures'] = len([f for f in os.listdir(lectures_dir) if f.endswith('_metadata.json')])
            
            materials_dirs = ['transcripts', 'slides', 'analytics']
            for materials_dir in materials_dirs:
                dir_path = os.path.join(self.local_data_dir, materials_dir)
                if os.path.exists(dir_path):
                    verification_results['local_materials'] += len([f for f in os.listdir(dir_path) if f.endswith('.json')])
            
            # Simple verification: MongoDB should have at least as many items as local
            verification_results['verification_passed'] = (
                verification_results['mongodb_lectures'] >= verification_results['local_lectures'] and
                verification_results['mongodb_materials'] >= verification_results['local_materials']
            )
            
            logger.info(f"📊 Verification results: {verification_results}")
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
        
        return verification_results
    
    def handle_database_error(self, error: Exception, operation: str, **context) -> Dict[str, Any]:
        """Centralized error handling for database operations"""
        error_info = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'recovery_suggestions': []
        }
        
        # Specific error handling based on error type
        if 'connection' in str(error).lower():
            error_info['recovery_suggestions'] = [
                "Check MongoDB connection string",
                "Verify network connectivity",
                "Ensure MongoDB Atlas cluster is running",
                "Check firewall settings"
            ]
        elif 'auth' in str(error).lower():
            error_info['recovery_suggestions'] = [
                "Verify MongoDB credentials",
                "Check database user permissions",
                "Ensure correct database name"
            ]
        elif 'timeout' in str(error).lower():
            error_info['recovery_suggestions'] = [
                "Retry the operation",
                "Check network stability",
                "Increase timeout settings"
            ]
        else:
            error_info['recovery_suggestions'] = [
                "Check the error message for specific details",
                "Verify data format and types",
                "Review MongoDB indexes and constraints"
            ]
        
        # Log the error
        logger.error(f"❌ Database error in {operation}: {error}")
        logger.error(f"📋 Recovery suggestions: {', '.join(error_info['recovery_suggestions'])}")
        
        return error_info
    
    def export_configuration_guide(self) -> str:
        """Export a configuration guide for users"""
        guide = """
# VirtuLearn MongoDB Configuration Guide

## Environment Setup
1. Create a .env file in your project root with:
   ```
   DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=YourApp
   OPENAI_API_KEY=your_openai_api_key_here (optional)
   ```

## MongoDB Atlas Setup
1. Create a MongoDB Atlas account at https://cloud.mongodb.com/
2. Create a new cluster
3. Add a database user with read/write permissions
4. Add your IP address to the IP whitelist
5. Get your connection string and update DATABASE_URL

## Required Python Packages
```bash
pip install pymongo python-dotenv streamlit pandas numpy plotly
```

## Running the Application
```bash
# Test MongoDB connection
python test_mongo.py

# Run the main app
python -m streamlit run app_mongo_demo.py
```

## Database Collections
- lectures: Main lecture metadata
- materials: Transcripts, slides, and other materials
- analytics: Performance metrics and insights

## Troubleshooting
- Connection issues: Check network and credentials
- Import errors: Ensure all packages are installed
- Performance issues: Consider indexing and query optimization

For more help, check the migration logs in virtulearn_migration.log
"""
        
        # Write guide to file
        with open('MongoDB_Setup_Guide.md', 'w') as f:
            f.write(guide)
        
        logger.info("📖 Configuration guide exported to MongoDB_Setup_Guide.md")
        return guide


def main():
    """Main migration function"""
    print("🚀 VirtuLearn MongoDB Migration Utility")
    print("=" * 50)
    
    migrator = VirtuLearnMigrationManager()
    
    # Export configuration guide
    migrator.export_configuration_guide()
    
    # Run migration if MongoDB is available
    if migrator.mongo_manager:
        print("📦 Starting data migration...")
        results = migrator.migrate_local_to_mongodb()
        
        print(f"\n📊 Migration Results:")
        print(f"✅ Lectures migrated: {results['lectures_migrated']}")
        print(f"✅ Materials migrated: {results['materials_migrated']}")
        
        if results['errors']:
            print(f"❌ Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")
        
        # Verify migration
        verification = migrator.verify_migration()
        print(f"\n🔍 Verification Results:")
        print(f"📊 MongoDB - Lectures: {verification['mongodb_lectures']}, Materials: {verification['mongodb_materials']}")
        print(f"📁 Local - Lectures: {verification['local_lectures']}, Materials: {verification['local_materials']}")
        print(f"✅ Verification: {'PASSED' if verification['verification_passed'] else 'FAILED'}")
        
    else:
        print("❌ MongoDB connection failed. Please check your configuration.")
        print("📖 See MongoDB_Setup_Guide.md for setup instructions.")


if __name__ == "__main__":
    main()