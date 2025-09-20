
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
