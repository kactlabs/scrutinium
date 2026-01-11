.. :changelog:

History
-------

1.1.0 (2025-01-10)
---------------------

**Enhanced Scoring System with 1000-Scale Precision**

* **NEW**: Implemented 1000-scale scoring system for maximum precision
  
  - LLM now provides scores from 0-1000 instead of 0-10
  - Automatic conversion to 10-scale for display (862/1000 → 8.620/10)
  - Enhanced prompting to request granular scoring with examples

* **IMPROVED**: Metric Display Formatting
  
  - All metrics now display with 3 decimal places (8.620/10 vs 8/10)
  - Updated Jinja2 templates with ``"%.3f"|format()`` formatting
  - Updated JavaScript with ``parseFloat().toFixed(3)`` formatting
  - Consistent formatting across web UI, shared pages, and CSV exports

* **FIXED**: Database Storage Precision
  
  - Scores now stored as floats with 3 decimal places in MongoDB
  - Updated ``save_evaluation_results()`` to convert 1000-scale to 10-scale
  - Fixed integer conversion issue in ``benchmark_handler.py``

* **ENHANCED**: CSV Export and Data Processing
  
  - Updated ``create_results_table()`` methods in both business modules
  - CSV exports now include decimal precision for all metrics
  - Proper float conversion throughout the data pipeline

* **UPDATED**: Test Data and Debug Tools
  
  - Updated test files to use 1000-scale format
  - Added comprehensive debug scripts for testing conversion logic
  - Enhanced error handling and type checking

* **TECHNICAL**: Prompt Engineering Improvements
  
  - Updated prompts in ``business.py`` and ``business_anthropic.py``
  - Clear instructions for 1000-scale scoring with examples
  - JSON schema updated to reflect new scoring format

1.0.0 (2025-01-10)
---------------------

**Initial Release - GenAI Benchmarking Platform**

* **CORE**: Cross-GenAI Tool Evaluation System
  
  - Support for multiple AI tools: ChatGPT, Claude, DeepSeek, Kimi, Qwen, Mistral, Grok
  - Multi-metric evaluation: Truthfulness, Creativity, Coherence, Utility
  - LangChain integration with Gemini and Anthropic Claude models

* **DATABASE**: MongoDB Integration
  
  - Async MongoDB operations with Motor
  - Auto-incrementing SCID system starting from configurable index
  - Comprehensive benchmark result storage with detailed explanations
  - UUID-based sharing system for public result access

* **WEB INTERFACE**: FastAPI + Jinja2 Templates
  
  - Interactive evaluation interface with real-time results
  - Shareable result pages with unique URLs
  - Responsive design with winner highlighting and ranking display
  - CSV export functionality for data analysis

* **API**: RESTful Endpoints
  
  - ``POST /evaluate`` - Run evaluations and get results
  - ``GET /share/{uuid}`` - Access shared evaluation results
  - ``GET /api/benchmark/*`` - CRUD operations for benchmark data
  - Comprehensive error handling and validation

* **ARCHITECTURE**: Modular Design
  
  - Separate business logic for different LLM providers
  - Database abstraction layer with async operations
  - Controller-based API organization
  - Environment-based configuration management

* **FEATURES**: Advanced Functionality
  
  - Detailed reasoning for each metric score
  - Winner determination with explanatory reasoning
  - Tool ranking system based on overall performance
  - Comprehensive logging and debug capabilities
