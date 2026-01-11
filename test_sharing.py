#!/usr/bin/env python3
"""
Test script for sharing functionality
"""

import asyncio
import uuid
from db.benchmark_handler import (
    save_evaluation_results,
    get_benchmark_result_by_uuid
)

async def test_sharing_functionality():
    """Test the sharing functionality with sample data"""
    
    print("Testing sharing functionality...")
    
    try:
        # Sample data for testing
        sample_responses = {
            "ChatGPT": "Paris is the capital of France. It's located in the north-central part of the country and is known for its iconic landmarks like the Eiffel Tower.",
            "DeepSeek": "The capital of France is Paris. This beautiful city serves as the political, economic, and cultural center of the country.",
            "Claude": "Paris is the capital and largest city of France. It has been the country's capital since 987 AD and is home to approximately 2.1 million people."
        }
        
        sample_evaluation = {
            "evaluations": [
                {
                    "tool": "ChatGPT",
                    "truthfulness": {"score": 9, "reasoning": "Accurate information about Paris being the capital, with correct geographical details"},
                    "creativity": {"score": 6, "reasoning": "Standard response with basic landmark mention"},
                    "coherence": {"score": 8, "reasoning": "Well-structured and clear"},
                    "utility": {"score": 7, "reasoning": "Provides useful basic information"},
                    "overall_score": 7.5
                },
                {
                    "tool": "DeepSeek", 
                    "truthfulness": {"score": 9, "reasoning": "Correct factual information about Paris"},
                    "creativity": {"score": 7, "reasoning": "Mentions multiple aspects - political, economic, cultural"},
                    "coherence": {"score": 9, "reasoning": "Very coherent and well-organized"},
                    "utility": {"score": 8, "reasoning": "Comprehensive overview of Paris's role"},
                    "overall_score": 8.25
                },
                {
                    "tool": "Claude",
                    "truthfulness": {"score": 10, "reasoning": "Highly accurate with specific historical detail (987 AD) and population data"},
                    "creativity": {"score": 8, "reasoning": "Includes historical context and specific statistics"},
                    "coherence": {"score": 9, "reasoning": "Excellent logical flow and structure"},
                    "utility": {"score": 9, "reasoning": "Most comprehensive with historical and demographic details"},
                    "overall_score": 9.0
                }
            ],
            "winner": "Claude",
            "winner_reasoning": "Claude provided the most comprehensive answer with historical context and specific data",
            "ranking": ["Claude", "DeepSeek", "ChatGPT"]
        }
        
        # Test 1: Save evaluation results and get share UUID
        print("\n1. Saving evaluation results...")
        scid, share_uuid = await save_evaluation_results(
            judge="gemini",
            question="What is the capital of France?",
            responses=sample_responses,
            evaluation_data=sample_evaluation
        )
        
        print(f"✓ Created benchmark result with SCID: {scid}")
        print(f"✓ Generated share UUID: {share_uuid}")
        print(f"✓ Share URL would be: /share/{share_uuid}")
        
        # Test 2: Retrieve by UUID
        print(f"\n2. Retrieving result by UUID...")
        result = await get_benchmark_result_by_uuid(share_uuid)
        
        if result:
            print(f"✓ Successfully retrieved shared result")
            print(f"  - Question: {result['question']}")
            print(f"  - Judge: {result['judge']}")
            print(f"  - Number of answers: {len([k for k in result.keys() if k.endswith('_answer') and result[k]])}")
            print(f"  - Has detailed metrics: {bool(result.get('truthfulness_details'))}")
            
            # Verify all expected fields are present
            expected_fields = [
                'scid', 'share_uuid', 'judge', 'question',
                'truthfulness', 'creativity', 'coherence', 'utility', 'overall_score',
                'truthfulness_details', 'creativity_details', 'coherence_details', 'utility_details'
            ]
            
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print("✓ All expected fields are present")
                
        else:
            print("✗ Failed to retrieve result by UUID")
            return False
        
        # Test 3: Verify data structure for UI
        print(f"\n3. Verifying data structure for sharing UI...")
        
        # Check answers
        answers = {
            "ChatGPT": result.get("chatgpt_answer", ""),
            "DeepSeek": result.get("deepseek_answer", ""),
            "Claude": result.get("claude_answer", "")
        }
        non_empty_answers = {k: v for k, v in answers.items() if v.strip()}
        print(f"✓ Found {len(non_empty_answers)} non-empty answers")
        
        # Check metrics structure
        metrics = {
            "truthfulness": {
                "scores": result.get("truthfulness", {}),
                "details": result.get("truthfulness_details", {})
            },
            "creativity": {
                "scores": result.get("creativity", {}),
                "details": result.get("creativity_details", {})
            }
        }
        
        truthfulness_tools = len(metrics["truthfulness"]["scores"])
        creativity_details = len(metrics["creativity"]["details"])
        print(f"✓ Truthfulness scores for {truthfulness_tools} tools")
        print(f"✓ Creativity details for {creativity_details} tools")
        
        print(f"\n🎉 All sharing functionality tests passed!")
        print(f"\n📋 Test Summary:")
        print(f"   - SCID: {scid}")
        print(f"   - Share UUID: {share_uuid}")
        print(f"   - Share URL: /share/{share_uuid}")
        print(f"   - Ready for UI display: ✓")
        
        return True
        
    except Exception as e:
        print(f"✗ Sharing functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
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
    asyncio.run(test_sharing_functionality())