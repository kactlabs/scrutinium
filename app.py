from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import os
import markdown
from dotenv import load_dotenv
from datetime import datetime
from business import GenAIBenchmarkJudge
from db import benchmark_handler
from starlette.middleware.sessions import SessionMiddleware

# Load environment variables
load_dotenv()

# Import the new controller
from controllers.benchmark_controller import router as benchmark_router

app = FastAPI(title="Scrutinium: Cross-GenAI Benchmarking", description="Compare and evaluate responses from various GenAI tools")

# Add session middleware for handling user API keys
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "your-secret-key-here"))

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add markdown filter to Jinja2 environment
def markdown_filter(text):
    """Convert markdown text to HTML, removing image references"""
    if not text:
        return ""
    
    # Remove image references like ![Image](url) or ![alt text](url)
    import re
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    
    # Configure markdown with safe extensions
    md = markdown.Markdown(extensions=['nl2br', 'fenced_code', 'tables'])
    return md.convert(str(text))

templates.env.filters['markdown'] = markdown_filter

# Include routers
app.include_router(benchmark_router)

class EvaluationRequest(BaseModel):
    question: str
    responses: Dict[str, str]
    provider: Optional[str] = None  # Will use DEFAULT_PROVIDER from env if not specified
    user_api_key: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page for Scrutinium benchmarking"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Scrutinium - Cross-GenAI Benchmarking",
        "subtitle": "Scrutinium - The first best Cross-GenAI benchmarking tool in the GenAI Era"
    })

@app.post("/evaluate")
async def evaluate_responses(request: EvaluationRequest, http_request: Request):
    """Evaluate GenAI tool responses and return results"""
    try:
        # Handle user-provided API key for session storage
        api_key_to_use = None
        provider_to_use = request.provider or os.getenv("DEFAULT_PROVIDER", "gemini")
        
        if request.user_api_key:
            # Store the API key in session (will be cleared when session ends)
            http_request.session["user_gemini_key"] = request.user_api_key
            api_key_to_use = request.user_api_key
        elif provider_to_use == "gemini" and "user_gemini_key" in http_request.session:
            # Use stored session key
            api_key_to_use = http_request.session["user_gemini_key"]
        
        # Initialize the judge with the specified provider and API key
        judge = GenAIBenchmarkJudge(provider=provider_to_use, api_key=api_key_to_use)
        
        # Run evaluation - with or without judge's answer based on environment setting
        show_judge_answer_env = os.getenv("SHOW_JUDGE_ANSWER", "0").strip()
        show_judge_answer = (
            show_judge_answer_env == '1' or 
            show_judge_answer_env.lower() == 'true' or 
            show_judge_answer_env.lower() == 'yes'
        )
        
        if show_judge_answer:
            evaluation_results = judge.evaluate_with_judge_answer(request.question, request.responses)
        else:
            evaluation_results = judge.evaluate(request.question, request.responses)
        
        # Check for Gemini-specific errors
        if "error" in evaluation_results:
            if evaluation_results.get("provider") == "gemini" and evaluation_results.get("error_type") in ["quota_exceeded", "api_key_leaked"]:
                # Return special response for Gemini quota/key issues
                return JSONResponse(
                    status_code=200,  # Don't return error status, handle in frontend
                    content={
                        "success": False,
                        "gemini_limit_reached": True,
                        "error": evaluation_results["error"],
                        "error_type": evaluation_results["error_type"]
                    }
                )
            else:
                raise HTTPException(status_code=500, detail=evaluation_results["error"])
        
        # Categorize the question using the same judge
        try:
            category = judge.categorize_question(request.question)
            print(f"DEBUG: Question categorized as: {category}")
        except Exception as e:
            print(f"Warning: Failed to categorize question: {e}")
            category = "general"  # Default fallback
        
        # Save results to MongoDB
        try:
            # Use the judge's get_judge_name method to get the appropriate name for DB storage
            judge_name = judge.get_judge_name()
            
            scid, share_uuid = await benchmark_handler.save_evaluation_results(
                judge=judge_name,
                question=request.question,
                responses=request.responses,
                evaluation_data=evaluation_results,
                category=category  # Pass the category to the save function
            )
            evaluation_results["scid"] = scid
            evaluation_results["share_uuid"] = share_uuid
            
            # Use DOMAIN_NAME from environment or fallback to relative URL
            domain_name = os.getenv("DOMAIN_NAME", "").rstrip('/')  # Remove trailing slash if present
            if domain_name:
                evaluation_results["share_url"] = f"{domain_name}/share/{share_uuid}"
                print(f"DEBUG: Generated share URL: {evaluation_results['share_url']}")
            else:
                evaluation_results["share_url"] = f"/share/{share_uuid}"
                print(f"DEBUG: Generated relative share URL: {evaluation_results['share_url']}")
                
        except Exception as db_error:
            print(f"Warning: Failed to save to MongoDB: {db_error}")
            # Continue without failing the evaluation
        
        # Create results table data
        df = judge.create_results_table(evaluation_results)
        table_data = df.to_dict('records') if df is not None else []
        
        return {
            "success": True,
            "evaluation_results": evaluation_results,
            "table_data": table_data,
            "show_judge_answer": show_judge_answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "SHOW_JUDGE_ANSWER": os.getenv("SHOW_JUDGE_ANSWER", "NOT_SET"),
        "SHOW_JUDGE_ANSWER_parsed": int(os.getenv("SHOW_JUDGE_ANSWER", "0")) == 1,
        "DEFAULT_PROVIDER": os.getenv("DEFAULT_PROVIDER", "NOT_SET"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "NOT_SET")
    }

@app.post("/clear-api-key")
async def clear_api_key(request: Request):
    """Clear user API key from session"""
    if "user_gemini_key" in request.session:
        del request.session["user_gemini_key"]
    return {"success": True, "message": "API key cleared from session"}

@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    """Results page to display evaluation results"""
    return templates.TemplateResponse("results.html", {
        "request": request,
        "title": "Evaluation Results",
        "subtitle": "GenAI Tool Comparison Results"
    })

@app.get("/archive", response_class=HTMLResponse)
async def archive_page(request: Request):
    """Archive page to display all collected benchmark results"""
    try:
        # Get all benchmark results from database
        results = await benchmark_handler.get_all_benchmark_results()
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        # Process results for display
        processed_results = []
        for result in results:
            # Get the question (truncated for display)
            question = result.get("question", "")
            question_preview = question[:100] + "..." if len(question) > 100 else question
            
            # Get the winner (tool with highest overall score)
            overall_scores = result.get("overall_score", {})
            winner = ""
            if overall_scores:
                winner = max(overall_scores.items(), key=lambda x: float(x[1]) if x[1] else 0)[0]
                winner = winner.title()  # Capitalize first letter
            
            # Count participating tools
            answers = {
                "ChatGPT": result.get("chatgpt_answer", ""),
                "Kimi": result.get("kimi_answer", ""),
                "DeepSeek": result.get("deepseek_answer", ""),
                "Qwen": result.get("qwen_answer", ""),
                "Mistral": result.get("mistral_answer", ""),
                "Claude": result.get("claude_answer", ""),
                "Grok": result.get("grok_answer", "")
            }
            tool_count = len([v for v in answers.values() if v.strip()])
            
            # Format creation date
            created_at = result.get("created_at")
            date_str = ""
            if created_at:
                if isinstance(created_at, str):
                    date_str = created_at[:10]  # Just the date part
                else:
                    date_str = created_at.strftime("%Y-%m-%d")
            
            processed_results.append({
                "scid": result.get("scid", ""),
                "share_uuid": result.get("share_uuid", ""),
                "question": question,
                "question_preview": question_preview,
                "winner": winner,
                "tool_count": tool_count,
                "judge": result.get("judge", "").title(),
                "created_at": date_str,
                "category": result.get("category", "general")  # Use DB category or default to general
            })
        
        return templates.TemplateResponse("archive.html", {
            "request": request,
            "title": "Scrutinium Archive",
            "subtitle": "Browse all collected benchmark results",
            "results": processed_results,
            "total_count": len(processed_results)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-formatting")
async def test_formatting():
    """Test endpoint to verify metric formatting"""
    return {
        "success": True,
        "table_data": [
            {
                "Tool": "TestTool1",
                "Truthfulness": 8.123,
                "Creativity": 7.456,
                "Coherence & Reasoning": 9.789,
                "Utility/Actionability": 8.012,
                "Overall Score": 8.345
            },
            {
                "Tool": "TestTool2", 
                "Truthfulness": 9.000,
                "Creativity": 8.000,
                "Coherence & Reasoning": 9.000,
                "Utility/Actionability": 9.000,
                "Overall Score": 8.750
            }
        ]
    }

@app.get("/share/{share_uuid}", response_class=HTMLResponse)
async def share_results(request: Request, share_uuid: str):
    """Share page to display evaluation results by UUID"""
    try:
        # Get the benchmark result by UUID
        result = await benchmark_handler.get_benchmark_result_by_uuid(share_uuid)
        
        if not result:
            raise HTTPException(status_code=404, detail="Shared result not found")
        
        # Debug: Check if judge_answer exists
        judge_answer_exists = bool(result.get('judge_answer', '').strip())
        show_judge_answer_setting = int(os.getenv('SHOW_JUDGE_ANSWER', '0')) == 1
        
        print(f"DEBUG: Judge answer exists: {judge_answer_exists}")
        print(f"DEBUG: Judge answer content: '{result.get('judge_answer', 'NOT_FOUND')[:100]}...'")
        print(f"DEBUG: SHOW_JUDGE_ANSWER env var: '{os.getenv('SHOW_JUDGE_ANSWER', 'NOT_SET')}'")
        print(f"DEBUG: Show judge answer setting: {show_judge_answer_setting}")
        print(f"DEBUG: Both conditions met: {show_judge_answer_setting and judge_answer_exists}")
        print(f"DEBUG: Result keys: {list(result.keys())}")
        
        # Prepare data for template
        answers = {
            "ChatGPT": result.get("chatgpt_answer", ""),
            "Kimi": result.get("kimi_answer", ""),
            "DeepSeek": result.get("deepseek_answer", ""),
            "Qwen": result.get("qwen_answer", ""),
            "Mistral": result.get("mistral_answer", ""),
            "Claude": result.get("claude_answer", ""),
            "Grok": result.get("grok_answer", "")
        }
        
        # Filter out empty answers
        answers = {k: v for k, v in answers.items() if v.strip()}
        
        # Prepare metrics data
        metrics = {
            "truthfulness": {
                "scores": result.get("truthfulness", {}),
                "details": result.get("truthfulness_details", {})
            },
            "creativity": {
                "scores": result.get("creativity", {}),
                "details": result.get("creativity_details", {})
            },
            "coherence": {
                "scores": result.get("coherence", {}),
                "details": result.get("coherence_details", {})
            },
            "utility": {
                "scores": result.get("utility", {}),
                "details": result.get("utility_details", {})
            },
            "overall_score": {
                "scores": result.get("overall_score", {}),
                "details": {}
            }
        }
        
        # Create results table data (sorted by overall score)
        table_data = []
        for tool in answers.keys():
            tool_lower = tool.lower()
            overall_score = metrics["overall_score"]["scores"].get(tool_lower, 0)
            # Ensure overall_score is a number
            try:
                overall_score = float(overall_score) if overall_score else 0
            except (ValueError, TypeError):
                overall_score = 0
                
            table_data.append({
                "tool": tool,
                "truthfulness": round(float(metrics["truthfulness"]["scores"].get(tool_lower, 0)), 3),
                "creativity": round(float(metrics["creativity"]["scores"].get(tool_lower, 0)), 3),
                "coherence": round(float(metrics["coherence"]["scores"].get(tool_lower, 0)), 3),
                "utility": round(float(metrics["utility"]["scores"].get(tool_lower, 0)), 3),
                "overall_score": round(overall_score, 3)
            })
        
        # Debug: Print scores before sorting
        print("Before sorting:")
        for item in table_data:
            print(f"{item['tool']}: {item['overall_score']}")
        
        # Sort by overall score descending
        table_data.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Debug: Print scores after sorting
        print("After sorting:")
        for item in table_data:
            print(f"{item['tool']}: {item['overall_score']}")
        
        # Create title with question
        question = result.get("question", "")
        title = f"Scrutinium - {question}" if question else "Scrutinium - Shared Results"
        
        # Get show_judge_answer setting with multiple fallback checks
        show_judge_answer_env = os.getenv('SHOW_JUDGE_ANSWER', '0').strip()
        show_judge_answer = (
            show_judge_answer_env == '1' or 
            show_judge_answer_env.lower() == 'true' or 
            show_judge_answer_env.lower() == 'yes'
        )
        
        print(f"DEBUG: SHOW_JUDGE_ANSWER raw: '{show_judge_answer_env}'")
        print(f"DEBUG: SHOW_JUDGE_ANSWER parsed: {show_judge_answer}")
        
        return templates.TemplateResponse("share.html", {
            "request": request,
            "title": title,
            "result": result,
            "question": question,
            "answers": answers,
            "metrics": metrics,
            "table_data": table_data,
            "judge": result.get("judge", ""),
            "created_at": result.get("created_at", ""),
            "share_uuid": share_uuid,
            "show_judge_answer": show_judge_answer
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8014)
