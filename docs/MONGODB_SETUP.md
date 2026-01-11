# MongoDB Integration Setup

This document explains how to set up and use the MongoDB integration for storing benchmarking results.

## Prerequisites

1. **MongoDB Atlas Account** (recommended) or local MongoDB installation
2. **Python dewpendencies** installed: `pip install -r requirements.txt`

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
  "share_uuid": "ddcf90dd-609a-4969-9759-f9cccbc3c569", // UUID for sharing
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
  "truthfulness_details": {         // Detailed explanations for each metric
    "chatgpt": "Good factual accuracy with minor inconsistencies",
    "deepseek": "Excellent accuracy and well-researched information",
    "claude": "Highly accurate with comprehensive fact-checking"
  },
  "creativity_details": {
    "chatgpt": "Standard approach with some creative elements",
    "deepseek": "Creative problem-solving and unique perspectives",
    "claude": "Very creative with innovative examples and analogies"
  },
  "coherence_details": {
    "chatgpt": "Well-structured with clear logical flow",
    "deepseek": "Good organization with minor structural issues",
    "claude": "Excellent coherence and seamless reasoning"
  },
  "utility_details": {
    "chatgpt": "Practical advice with actionable insights",
    "deepseek": "Highly useful with real-world applications",
    "claude": "Useful information with clear implementation guidance"
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
3. **Test sharing functionality:**

   ```bash
   python test_sharing.py
   ```
4. **Start the application:**

   ```bash
   python app.py
   ```

## Sharing Functionality

The system includes a comprehensive sharing feature that allows users to share evaluation results via unique URLs:

### How Sharing Works

1. **Automatic UUID Generation**: Each evaluation automatically gets a unique UUID for sharing
2. **Share URL Format**: `/share/{uuid}` (e.g., `/share/ddcf90dd-609a-4969-9759-f9cccbc3c569`)
3. **Comprehensive Display**: Shared pages show:
   - Original question
   - All AI tool responses
   - Complete results table with rankings
   - Detailed metrics and explanations for each category

### Share Page Features

- **Question Display**: Shows the original question asked to all AI tools
- **AI Responses**: Complete responses from each tool that provided an answer
- **Results Table**: Ranked comparison table with scores for all metrics
- **Detailed Metrics**: Breakdown of each evaluation category with explanations:
  - **Truthfulness**: Factual correctness, internal consistency, resistance to hallucination
  - **Creativity**: Novel framing, non-obvious insights, original examples
  - **Coherence & Reasoning**: Logical flow, step-by-step reasoning, absence of contradictions
  - **Utility & Actionability**: Practical usefulness, clarity for decision-making, real-world applicability
- **Copy Link Feature**: Easy one-click copying of the share URL
- **Responsive Design**: Works perfectly on desktop and mobile devices

### Using the Share Feature

1. **Generate Results**: Run an evaluation through the main interface
2. **Get Share Link**: The system automatically generates a shareable URL
3. **Copy & Share**: Use the "Copy Link" button to share with others
4. **View Shared Page**: Click "View Shared Page" to see how others will see your result

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
