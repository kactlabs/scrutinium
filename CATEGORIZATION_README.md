# Dynamic Question Categorization Feature

This document explains the dynamic automatic question categorization feature that has been added to Scrutinium.

## Overview

The system now automatically categorizes benchmark questions into **any appropriate category** determined by the LLM, such as:
- **artificial intelligence**, **programming**, **web development** (tech-related)
- **finance**, **marketing**, **entrepreneurship** (business-related)  
- **movies**, **music**, **sports** (entertainment-related)
- **medicine**, **science**, **history**, **cooking**, **travel**, etc. (any domain)

The categories are **completely dynamic** and determined by the AI based on the question content, not limited to predefined options.

## How It Works

1. **Dynamic Categorization**: When you submit a new benchmark evaluation, the system uses LangChain + Gemini to automatically determine the most appropriate category for the question.

2. **Open-ended Categories**: The AI can generate any category name that best describes the question (e.g., "artificial intelligence", "finance", "cooking", "history", etc.).

3. **Database Storage**: The category is stored in the MongoDB database along with other benchmark data.

4. **Dynamic Archive Filtering**: The `/archive` page automatically generates filter tabs based on the actual categories found in your data.

## Files Added/Modified

### New Files:
- `tag_filler.py` - One-time script to categorize existing database records
- `test_categorization.py` - Test script to verify categorization accuracy
- `CATEGORIZATION_README.md` - This documentation file

### Modified Files:
- `business.py` - Added `categorize_question()` method
- `app.py` - Updated evaluation endpoint to include categorization
- `db/benchmark_handler.py` - Added category field to database operations
- `templates/archive.html` - Updated to use database categories instead of JavaScript categorization

## Setup Requirements

Make sure you have the required environment variables:
```bash
# Required for categorization (choose one)
GEMINI_API_KEY=your_gemini_api_key
# OR
GOOGLE_API_KEY=your_google_api_key
```

## Usage

### 1. Test Categorization
First, test that categorization is working:
```bash
python test_categorization.py
```

### 2. Update Existing Records (One-time)
To categorize existing benchmark results in your database:
```bash
# Test mode (doesn't modify database)
python tag_filler.py --test

# Full update (modifies database)
python tag_filler.py
```

### 3. Normal Operation
- New benchmark evaluations will be automatically categorized with dynamic, AI-determined categories
- Visit `/archive` to see all results with their unique categories
- Filter tabs are automatically generated based on the categories in your data
- Each category gets a unique color for visual distinction

## API Changes

The evaluation endpoint now automatically includes dynamic categorization:
- No changes needed to existing API calls
- Category is automatically determined by AI and stored
- Categories can be any descriptive term (not limited to predefined options)
- Results include the category in the database

## Archive Page Features

- **Dynamic Category Filtering**: Filter tabs are automatically generated based on actual categories in your data
- **Visual Categories**: Each card shows its category with automatically assigned color-coded badges
- **Database-Driven**: Categories come from the database, determined by AI
- **Unlimited Categories**: No restriction on category types - can be anything from "cooking" to "quantum physics"

## Troubleshooting

### Common Issues:

1. **"Gemini API key not found" error**:
   - Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in your `.env` file
   - Make sure the API key is valid and has quota

2. **Categorization not working**:
   - Run `python test_categorization.py` to verify setup
   - Check that the API key has sufficient quota

3. **Archive page shows wrong categories**:
   - Run `python tag_filler.py` to update existing records
   - New evaluations should have correct categories automatically

### Performance Notes:

- Categorization adds ~1-2 seconds to evaluation time
- Uses the same Gemini API as evaluation (if using Gemini provider)
- Categories are cached in database, no re-categorization needed

## Future Enhancements

Potential improvements:
- Category analytics and insights (most popular categories, etc.)
- Allow manual category override in the UI
- Category-based search and recommendations
- Export results by category
- Category trending over time