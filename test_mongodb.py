#!/usr/bin/env python3
"""
Test script for MongoDB integration
"""

import asyncio
import os
from dotenv import load_dotenv
from db.benchmark_handler import (
    create_benchmark_result,
    get_all_benchmark_results,
    get_benchmark_result_by_scid,
    save_evaluation_results,
    get_benchmark_stats
)

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    
    print("Testing MongoDB connection...")
    
    try:
        # Test 1: Create a sample benchmark result
        print("\n1. Creating sample benchmark result...")
        
        sample_responses = {
            "ChatGPT": "This is a ChatGPT response",
            "DeepSeek": "This is a DeepSeek response",
            "Claude": "This is a Claude response"
        }
        
        sample_evaluation = {
            "evaluations": [
                {
                    "tool": "ChatGPT",
                    "truthfulness": {"score": 8, "reasoning": "Good factual accuracy"},
                    "creativity": {"score": 7, "reasoning": "Decent creativity"},
                    "coherence": {"score": 9, "reasoning": "Very coherent"},
                    "utility": {"score": 8, "reasoning": "Quite useful"},
                    "overall_score": 8.0
                },
                {
                    "tool": "DeepSeek", 
                    "truthfulness": {"score": 9, "reasoning": "Excellent accuracy"},
                    "creativity": {"score": 8, "reasoning": "Creative approach"},
                    "coherence": {"score": 8, "reasoning": "Well structured"},
                    "utility": {"score": 9, "reasoning": "Very practical"},
                    "overall_score": 8.5
                },
                {
                    "tool": "Claude",
                    "truthfulness": {"score": 9, "reasoning": "Highly accurate"},
                    "creativity": {"score": 9, "reasoning": "Very creative"},
                    "coherence": {"score": 9, "reasoning": "Excellent flow"},
                    "utility": {"score": 8, "reasoning": "Useful insights"},
                    "overall_score": 8.75
                }
            ]
        }
        
        scid = await save_evaluation_results(
            judge="gemini",
            question="What is the capital of France?",
            responses=sample_responses,
            evaluation_data=sample_evaluation
        )
        
        print(f"✓ Created benchmark result with SCID: {scid}")
        
        # Test 2: Retrieve the created result
        print(f"\n2. Retrieving benchmark result {scid}...")
        result = await get_benchmark_result_by_scid(scid)
        if result:
            print(f"✓ Retrieved result: Judge={result['judge']}, Question='{result['question'][:50]}...'")
        else:
            print("✗ Failed to retrieve result")
        
        # Test 3: Get all results
        print("\n3. Getting all benchmark results...")
        all_results = await get_all_benchmark_results()
        print(f"✓ Found {len(all_results)} total benchmark results")
        
        # Test 4: Get statistics
        print("\n4. Getting benchmark statistics...")
        stats = await get_benchmark_stats()
        print(f"✓ Statistics: {stats}")
        
        print("\n🎉 All MongoDB tests passed!")
        
    except Exception as e:
        print(f"✗ MongoDB test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("MONGO_URI"):
        print("❌ MONGO_URI environment variable not set!")
        print("Please copy .env.sample to .env and configure your MongoDB connection.")
        exit(1)
    
    if not os.getenv("DB_NAME"):
        print("❌ DB_NAME environment variable not set!")
        print("Please copy .env.sample to .env and configure your database name.")
        exit(1)
    
    # Run the test
    asyncio.run(test_mongodb_connection())