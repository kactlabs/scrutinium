from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import os
from business import GenAIBenchmarkJudge
from db import benchmark_handler

# Import the new controller
from controllers.benchmark_controller import router as benchmark_router

app = FastAPI(title="GenAI Benchmark Tool", description="Compare and evaluate responses from various GenAI tools")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(benchmark_router)

class EvaluationRequest(BaseModel):
    question: str
    responses: Dict[str, str]
    provider: Optional[str] = "gemini"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page for GenAI benchmarking"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Scrutinium - Cross-GenAI Benchmarking",
        "subtitle": "Scrutinium - The first best Cross-GenAI benchmarking tool in the GenAI Era"
    })

@app.post("/evaluate")
async def evaluate_responses(request: EvaluationRequest):
    """Evaluate GenAI tool responses and return results"""
    try:
        # Initialize the judge with the specified provider
        judge = GenAIBenchmarkJudge(provider=request.provider)
        
        # Run evaluation
        evaluation_results = judge.evaluate(request.question, request.responses)
        
        if "error" in evaluation_results:
            raise HTTPException(status_code=500, detail=evaluation_results["error"])
        
        # Save results to MongoDB
        try:
            scid, share_uuid = await benchmark_handler.save_evaluation_results(
                judge=request.provider,
                question=request.question,
                responses=request.responses,
                evaluation_data=evaluation_results
            )
            evaluation_results["scid"] = scid
            evaluation_results["share_uuid"] = share_uuid
            evaluation_results["share_url"] = f"/share/{share_uuid}"
        except Exception as db_error:
            print(f"Warning: Failed to save to MongoDB: {db_error}")
            # Continue without failing the evaluation
        
        # Create results table data
        df = judge.create_results_table(evaluation_results)
        table_data = df.to_dict('records') if df is not None else []
        
        return {
            "success": True,
            "evaluation_results": evaluation_results,
            "table_data": table_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    """Results page to display evaluation results"""
    return templates.TemplateResponse("results.html", {
        "request": request,
        "title": "Evaluation Results",
        "subtitle": "GenAI Tool Comparison Results"
    })

@app.get("/share/{share_uuid}", response_class=HTMLResponse)
async def share_results(request: Request, share_uuid: str):
    """Share page to display evaluation results by UUID"""
    try:
        # Get the benchmark result by UUID
        result = await benchmark_handler.get_benchmark_result_by_uuid(share_uuid)
        
        if not result:
            raise HTTPException(status_code=404, detail="Shared result not found")
        
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
                "truthfulness": int(metrics["truthfulness"]["scores"].get(tool_lower, 0)),
                "creativity": int(metrics["creativity"]["scores"].get(tool_lower, 0)),
                "coherence": int(metrics["coherence"]["scores"].get(tool_lower, 0)),
                "utility": int(metrics["utility"]["scores"].get(tool_lower, 0)),
                "overall_score": overall_score
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
        
        return templates.TemplateResponse("share.html", {
            "request": request,
            "result": result,
            "question": result.get("question", ""),
            "answers": answers,
            "metrics": metrics,
            "table_data": table_data,
            "judge": result.get("judge", ""),
            "created_at": result.get("created_at", ""),
            "share_uuid": share_uuid
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8014)
