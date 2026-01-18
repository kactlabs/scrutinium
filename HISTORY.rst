.. :changelog:

History
-------

1.3.1 (2025-01-17)
---------------------

**Archive Page Improvements**

* **ENHANCED**: Archive Page Sorting and Display
  
  - Implemented two-tier classification system for archive results
  - Results with scores > 0 displayed at top, sorted by date (newest first)
  - Results with all scores = 0 moved to bottom, sorted by date (newest first)
  - Better browsing experience by prioritizing meaningful benchmark results

* **IMPROVED**: Winner Display Format
  
  - Added overall score display next to winner name in archive cards
  - Format: ``🏆Winner (score)`` (e.g., ``🏆Grok (9.830)``)
  - Scores displayed with 3 decimal places for precision
  - More informative at-a-glance view of benchmark quality

1.3.0 (2025-01-11)
---------------------

**Judge Answer Generation and Display Control**

* **NEW**: Judge Answer Generation Feature
  
  - AI judge now generates its own comprehensive answer to questions
  - Judge's answer displayed for reference and comparison purposes
  - Enhanced evaluation prompt includes judge's response generation
  - Judge answer excluded from scoring to maintain evaluation objectivity

* **NEW**: Environment-Based Display Control
  
  - Added ``SHOW_JUDGE_ANSWER`` environment variable (0=hide, 1=show)
  - Configurable judge answer display in both main results and share pages
  - Performance optimization: skip judge answer generation when disabled
  - Backward compatibility with default setting (disabled)

* **ENHANCED**: Database Schema Updates
  
  - Added ``judge_answer`` field to MongoDB document structure
  - Updated ``save_evaluation_results()`` to store judge's comprehensive answers
  - Enhanced share page data retrieval to include judge responses
  - Graceful handling of legacy records without judge answers

* **IMPROVED**: Markdown Rendering and Content Processing
  
  - Added Python ``markdown`` library with safe extensions (nl2br, fenced_code, tables)
  - Server-side markdown rendering for share pages with ``|markdown|safe`` filter
  - Client-side JavaScript markdown converter for real-time results
  - Automatic image reference removal from ChatGPT responses (``![Image](url)`` patterns)

* **ENHANCED**: User Experience Improvements
  
  - Judge's answer displayed in dedicated section with proper styling
  - Conditional display based on environment configuration
  - Informative messages for legacy evaluations without judge answers
  - Responsive design for judge answer sections

* **TECHNICAL**: Robust Environment Variable Handling
  
  - Multiple format support: ``1``, ``true``, ``yes`` for enabling feature
  - Fallback parsing with string trimming and case-insensitive matching
  - Debug endpoints for environment variable verification
  - Comprehensive logging for troubleshooting

* **FIXED**: Session Middleware Dependencies
  
  - Added ``itsdangerous>=2.0.0`` dependency for Vercel deployment
  - Resolved ModuleNotFoundError in production environments
  - Proper session management for user API key storage

* **UPDATED**: Configuration Documentation
  
  - Updated ``.env.sample`` with ``SHOW_JUDGE_ANSWER`` setting
  - Clear documentation of judge answer control mechanism
  - Environment variable setup instructions for deployment platforms

1.2.0 (2025-01-11)
---------------------

**Enhanced Error Handling and Local AI Support**

* **NEW**: Ollama Local AI Integration
  
  - Added support for local Ollama models (mistral:latest by default)
  - No API keys required for local processing
  - Configurable model and base URL via environment variables
  - Added ``langchain_ollama`` dependency for local AI support

* **NEW**: Gemini API Error Handling & User Key Support
  
  - Intelligent error handling for Gemini quota limits (429) and leaked keys (403)
  - User-friendly error messages: "Gemini model limit reached, visit us back next time"
  - Modal dialog for users to provide their own Gemini API keys
  - Session-based API key storage (cleared when tab/window closes)
  - Automatic retry functionality with user-provided keys

* **NEW**: Default Provider Configuration
  
  - Added ``DEFAULT_PROVIDER`` environment variable support
  - Ollama set as default provider for local-first approach
  - Fallback to Gemini if no provider specified and no default set
  - Provider selection now respects environment configuration

* **ENHANCED**: Session Management
  
  - Added FastAPI SessionMiddleware for secure key storage
  - Session-based user API key management for Gemini
  - ``POST /clear-api-key`` endpoint for manual key clearing
  - Automatic session cleanup on browser close

* **IMPROVED**: User Interface
  
  - Added Ollama option to provider dropdown (🟠 Ollama Local)
  - Conditional API key input (only shown for providers that need it)
  - Enhanced modal design for API key input with help links
  - Better error messaging and user guidance

* **ENHANCED**: Error Handling Architecture
  
  - Provider-specific error handling in business logic
  - Structured error responses with error types
  - Graceful fallbacks for categorization failures
  - Improved debugging and logging for different providers

* **TECHNICAL**: Environment Configuration
  
  - Added ``OLLAMA_MODEL`` and ``OLLAMA_BASE_URL`` configuration
  - Added ``SESSION_SECRET_KEY`` for secure session management
  - Updated ``.env.sample`` with all new configuration options
  - Better documentation of environment variables

* **FIXED**: Chain Initialization Bug
  
  - Fixed missing ``self.chain`` attribute initialization
  - Proper prompt template and chain setup for all providers
  - Consistent LLM chain creation across all provider types

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
