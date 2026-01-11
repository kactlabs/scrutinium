import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
ID_STARTING_INDEX = int(os.getenv("ID_STARTING_INDEX", 12001))

# MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
benchmark_collection = db["benchmark_results"]

async def create_benchmark_result(
    judge: str,
    question: str,
    chatgpt_answer: str = "",
    kimi_answer: str = "",
    deepseek_answer: str = "",
    qwen_answer: str = "",
    mistral_answer: str = "",
    claude_answer: str = "",
    grok_answer: str = "",
    truthfulness: Dict = None,
    creativity: Dict = None,
    coherence: Dict = None,
    utility: Dict = None,
    overall_score: Dict = None,
    truthfulness_details: Dict = None,
    creativity_details: Dict = None,
    coherence_details: Dict = None,
    utility_details: Dict = None,
    share_uuid: str = None
):
    """
    Create a new benchmark result with auto-increment scid starting from ID_STARTING_INDEX
    """
    # Get the next scid by finding the maximum existing scid
    last_result = await benchmark_collection.find_one(
        {}, 
        sort=[("scid", -1)]
    )
    
    # Start from ID_STARTING_INDEX if no results exist, otherwise increment from the last scid
    if not last_result or "scid" not in last_result:
        next_scid = ID_STARTING_INDEX
    else:
        next_scid = max(last_result["scid"] + 1, ID_STARTING_INDEX)
    
    # Generate UUID for sharing if not provided
    if not share_uuid:
        share_uuid = str(uuid.uuid4())
    
    # Default empty JSON structures for scoring metrics
    default_scores = {}
    default_details = {}
    
    benchmark_doc = {
        "scid": next_scid,
        "share_uuid": share_uuid,
        "judge": judge,
        "question": question,
        "chatgpt_answer": chatgpt_answer,
        "kimi_answer": kimi_answer,
        "deepseek_answer": deepseek_answer,
        "qwen_answer": qwen_answer,
        "mistral_answer": mistral_answer,
        "claude_answer": claude_answer,
        "grok_answer": grok_answer,
        "truthfulness": truthfulness or default_scores,
        "creativity": creativity or default_scores,
        "coherence": coherence or default_scores,
        "utility": utility or default_scores,
        "overall_score": overall_score or default_scores,
        "truthfulness_details": truthfulness_details or default_details,
        "creativity_details": creativity_details or default_details,
        "coherence_details": coherence_details or default_details,
        "utility_details": utility_details or default_details,
        "created_at": datetime.utcnow()
    }
    
    await benchmark_collection.insert_one(benchmark_doc)
    return next_scid, share_uuid

async def save_evaluation_results(
    judge: str,
    question: str,
    responses: Dict[str, str],
    evaluation_data: Dict
):
    """
    Save evaluation results to MongoDB with proper structure including detailed explanations
    """
    # Extract individual responses
    chatgpt_answer = responses.get("ChatGPT", "")
    kimi_answer = responses.get("Kimi", "")
    deepseek_answer = responses.get("DeepSeek", "")
    qwen_answer = responses.get("Qwen", "")
    mistral_answer = responses.get("Mistral", "")
    claude_answer = responses.get("Claude", "")
    grok_answer = responses.get("Grok", "")
    
    # Process evaluation data to create score dictionaries
    truthfulness_scores = {}
    creativity_scores = {}
    coherence_scores = {}
    utility_scores = {}
    overall_scores = {}
    
    # Process detailed explanations
    truthfulness_details = {}
    creativity_details = {}
    coherence_details = {}
    utility_details = {}
    
    # Extract scores and details from evaluation data
    for eval_item in evaluation_data.get("evaluations", []):
        tool_name = eval_item["tool"].lower()
        
        # Scores
        truthfulness_scores[tool_name] = eval_item["truthfulness"]["score"]
        creativity_scores[tool_name] = eval_item["creativity"]["score"]
        coherence_scores[tool_name] = eval_item["coherence"]["score"]
        utility_scores[tool_name] = eval_item["utility"]["score"]
        overall_scores[tool_name] = eval_item["overall_score"]
        
        # Detailed explanations
        truthfulness_details[tool_name] = eval_item["truthfulness"]["reasoning"]
        creativity_details[tool_name] = eval_item["creativity"]["reasoning"]
        coherence_details[tool_name] = eval_item["coherence"]["reasoning"]
        utility_details[tool_name] = eval_item["utility"]["reasoning"]
    
    # Create the benchmark result
    scid, share_uuid = await create_benchmark_result(
        judge=judge,
        question=question,
        chatgpt_answer=chatgpt_answer,
        kimi_answer=kimi_answer,
        deepseek_answer=deepseek_answer,
        qwen_answer=qwen_answer,
        mistral_answer=mistral_answer,
        claude_answer=claude_answer,
        grok_answer=grok_answer,
        truthfulness=truthfulness_scores,
        creativity=creativity_scores,
        coherence=coherence_scores,
        utility=utility_scores,
        overall_score=overall_scores,
        truthfulness_details=truthfulness_details,
        creativity_details=creativity_details,
        coherence_details=coherence_details,
        utility_details=utility_details
    )
    
    return scid, share_uuid

async def get_benchmark_result_by_uuid(share_uuid: str):
    """
    Fetch a specific benchmark result by share UUID
    """
    result = await benchmark_collection.find_one(
        {"share_uuid": share_uuid}, 
        {"_id": 0}
    )
    return result

async def get_all_benchmark_results():
    """
    Fetch all benchmark results
    """
    results = []
    cursor = benchmark_collection.find({}, {"_id": 0})
    
    async for result in cursor:
        results.append(result)
    
    return results

async def get_benchmark_result_by_scid(scid: int):
    """
    Fetch a specific benchmark result by scid
    """
    result = await benchmark_collection.find_one(
        {"scid": scid}, 
        {"_id": 0}
    )
    return result

async def update_benchmark_result(scid: int, update_data: dict):
    """
    Update an existing benchmark result
    """
    if not update_data:
        return False
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await benchmark_collection.update_one(
        {"scid": scid},
        {"$set": update_data}
    )
    
    return result.modified_count > 0

async def delete_benchmark_result(scid: int):
    """
    Delete a benchmark result by scid
    """
    result = await benchmark_collection.delete_one({"scid": scid})
    return result.deleted_count > 0

async def get_benchmark_stats():
    """
    Get statistics about benchmark results
    """
    total_count = await benchmark_collection.count_documents({})
    
    # Get judge distribution
    judge_pipeline = [
        {"$group": {"_id": "$judge", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    judge_stats = []
    async for doc in benchmark_collection.aggregate(judge_pipeline):
        judge_stats.append({"judge": doc["_id"], "count": doc["count"]})
    
    return {
        "total_results": total_count,
        "judge_distribution": judge_stats
    }