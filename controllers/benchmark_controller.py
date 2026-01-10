from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
from db import benchmark_handler

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])

class BenchmarkCreate(BaseModel):
    judge: str
    question: str
    chatgpt_answer: Optional[str] = ""
    kimi_answer: Optional[str] = ""
    deepseek_answer: Optional[str] = ""
    qwen_answer: Optional[str] = ""
    mistral_answer: Optional[str] = ""
    claude_answer: Optional[str] = ""
    grok_answer: Optional[str] = ""
    truthfulness: Optional[Dict] = None
    creativity: Optional[Dict] = None
    coherence: Optional[Dict] = None
    utility: Optional[Dict] = None
    overall_score: Optional[Dict] = None

class BenchmarkUpdate(BaseModel):
    judge: Optional[str] = None
    question: Optional[str] = None
    chatgpt_answer: Optional[str] = None
    kimi_answer: Optional[str] = None
    deepseek_answer: Optional[str] = None
    qwen_answer: Optional[str] = None
    mistral_answer: Optional[str] = None
    claude_answer: Optional[str] = None
    grok_answer: Optional[str] = None
    truthfulness: Optional[Dict] = None
    creativity: Optional[Dict] = None
    coherence: Optional[Dict] = None
    utility: Optional[Dict] = None
    overall_score: Optional[Dict] = None

@router.get("/")
async def get_all_benchmark_results():
    """
    Get all benchmark results
    """
    try:
        results = await benchmark_handler.get_all_benchmark_results()
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_benchmark_stats():
    """
    Get benchmark statistics
    """
    try:
        stats = await benchmark_handler.get_benchmark_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scid}")
async def get_benchmark_result(scid: int):
    """
    Get a specific benchmark result by SCID
    """
    try:
        result = await benchmark_handler.get_benchmark_result_by_scid(scid)
        if not result:
            raise HTTPException(status_code=404, detail="Benchmark result not found")
        return {
            "success": True,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_benchmark_result(benchmark_data: BenchmarkCreate):
    """
    Create a new benchmark result
    """
    try:
        scid = await benchmark_handler.create_benchmark_result(
            judge=benchmark_data.judge,
            question=benchmark_data.question,
            chatgpt_answer=benchmark_data.chatgpt_answer,
            kimi_answer=benchmark_data.kimi_answer,
            deepseek_answer=benchmark_data.deepseek_answer,
            qwen_answer=benchmark_data.qwen_answer,
            mistral_answer=benchmark_data.mistral_answer,
            claude_answer=benchmark_data.claude_answer,
            grok_answer=benchmark_data.grok_answer,
            truthfulness=benchmark_data.truthfulness,
            creativity=benchmark_data.creativity,
            coherence=benchmark_data.coherence,
            utility=benchmark_data.utility,
            overall_score=benchmark_data.overall_score
        )
        return {
            "success": True,
            "message": "Benchmark result created successfully",
            "scid": scid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{scid}")
async def update_benchmark_result(scid: int, benchmark_data: BenchmarkUpdate):
    """
    Update an existing benchmark result
    """
    try:
        success = await benchmark_handler.update_benchmark_result(
            scid, 
            benchmark_data.dict(exclude_unset=True)
        )
        if not success:
            raise HTTPException(status_code=404, detail="Benchmark result not found")
        return {
            "success": True,
            "message": "Benchmark result updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{scid}")
async def delete_benchmark_result(scid: int):
    """
    Delete a benchmark result
    """
    try:
        success = await benchmark_handler.delete_benchmark_result(scid)
        if not success:
            raise HTTPException(status_code=404, detail="Benchmark result not found")
        return {
            "success": True,
            "message": "Benchmark result deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))