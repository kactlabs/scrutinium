from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import os
from business import GenAIBenchmarkJudge

app = FastAPI(title="GenAI Benchmark Tool", description="Compare and evaluate responses from various GenAI tools")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8014)
