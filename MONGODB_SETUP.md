# MongoDB Integration Setup

This document explains how to set up and use the MongoDB integration for storing benchmarking results.

## Prerequisites

1. **MongoDB Atlas Account** (recommended) or local MongoDB installation
2. **Python dependencies** installed: `pip install -r requirements.txt`

## Configuration

1. **Copy environment file:**
   ```bash
   cp .env.sample .env
   ```

2. **Configure MongoDB connection in `.env`:**
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.kubu7.mongodb.net/
   DB_NAME=genai_benchmark
   ID_STARTING_INDEX=12001
   ```

3. **Set up your MongoDB Atlas cluster:**
   - Create a free MongoDB Atlas account at https://www.mongodb.com/atlas
   - Create a new cluster
   - Create a database user with read/write permissions
   - Get your connection string and update `MONGO_URI`

## Database Schema

The system creates a `benchmark_results` collection with the following structure:

```json
{
  "scid": 12001,                    // Auto-incremented ID starting from 12001
  "judge": "gemini",                // Evaluation provider (gemini, anthropic, groq)
  "question": "Your question here",
  "chatgpt_answer": "Response...",
  "kimi_answer": "Response...",
  "deepseek_answer": "Response...",
  "qwen_answer": "Response...",
  "mistral_answer": "Response...",
  "claude_answer": "Response...",
  "grok_answer": "Response...",
  "truthfulness": {                 // JSON object with scores per tool
    "chatgpt": 8,
    "deepseek": 9,
    "claude": 9
  },
  "creativity": {
    "chatgpt": 7,
    "deepseek": 8,
    "claude": 9
  },
  "coherence": {
    "chatgpt": 9,
    "deepseek": 8,
    "claude": 9
  },
  "utility": {
    "chatgpt": 8,
    "deepseek": 9,
    "claude": 8
  },
  "overall_score": {
    "chatgpt": 8.0,
    "deepseek": 8.5,
    "claude": 8.75
  },
  "created_at": "2026-01-10T...",
  "updated_at": "2026-01-10T..."
}
```

## Setup Instructions

1. **Initialize the database:**
   ```bash
   python db_setup/setup_collections.py
   ```

2. **Test the connection:**
   ```bash
   python test_mongodb.py
   ```

3. **Start the application:**
   ```bash
   python app.py
   ```

## API Endpoints

The system provides REST API endpoints for managing benchmark results:

### Get All Results
```http
GET /api/benchmark/
```

### Get Specific Result
```http
GET /api/benchmark/{scid}
```

### Create New Result
```http
POST /api/benchmark/
Content-Type: application/json

{
  "judge": "gemini",
  "question": "Your question",
  "chatgpt_answer": "Response...",
  // ... other fields
}
```

### Update Result
```http
PUT /api/benchmark/{scid}
Content-Type: application/json

{
  "judge": "updated_judge"
  // ... fields to update
}
```

### Delete Result
```http
DELETE /api/benchmark/{scid}
```

### Get Statistics
```http
GET /api/benchmark/stats
```

## Automatic Integration

When you use the `/evaluate` endpoint, results are automatically saved to MongoDB:

1. User submits evaluation request
2. System runs AI evaluation
3. Results are automatically saved to MongoDB with auto-incremented SCID
4. Response includes the assigned SCID

## File Structure

```
├── db/
│   ├── __init__.py
│   ├── db_common.py           # Database connection utilities
│   └── benchmark_handler.py   # MongoDB operations for benchmarks
├── controllers/
│   ├── __init__.py
│   └── benchmark_controller.py # REST API endpoints
├── db_setup/
│   ├── __init__.py
│   └── setup_collections.py   # Database initialization
├── test_mongodb.py            # Connection test script
└── MONGODB_SETUP.md          # This file
```

## Troubleshooting

1. **Connection Issues:**
   - Verify your MongoDB URI is correct
   - Check if your IP is whitelisted in MongoDB Atlas
   - Ensure database user has proper permissions

2. **Import Errors:**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Verify Python path includes the project directory

3. **Permission Errors:**
   - Ensure your MongoDB user has read/write permissions
   - Check if the database name matches your configuration

## Migration from Existing Data

If you have existing benchmark results in JSON/CSV format, you can create a migration script to import them into MongoDB using the `benchmark_handler.py` functions.