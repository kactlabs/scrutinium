#!/usr/bin/env python3
"""
Debug script to test the new 1000-scale scoring system
"""

from business import GenAIBenchmarkJudge
import json

def test_1000_scale_conversion():
    """Test the 1000-scale to 10-scale conversion"""
    
    print("=== Testing 1000-Scale Conversion ===")
    
    # Sample evaluation data with 1000-scale scores
    sample_evaluation = {
        "evaluations": [
            {
                "tool": "ChatGPT",
                "truthfulness": {"score": 862, "reasoning": "Good accuracy"},
                "creativity": {"score": 745, "reasoning": "Decent creativity"},
                "coherence": {"score": 923, "reasoning": "Very coherent"},
                "utility": {"score": 801, "reasoning": "Quite useful"},
                "overall_score": 833,
                "notes": "Good overall performance"
            },
            {
                "tool": "Claude",
                "truthfulness": {"score": 934, "reasoning": "Excellent accuracy"},
                "creativity": {"score": 876, "reasoning": "Creative approach"},
                "coherence": {"score": 945, "reasoning": "Well structured"},
                "utility": {"score": 912, "reasoning": "Very practical"},
                "overall_score": 917,
                "notes": "Top performer"
            }
        ],
        "winner": "Claude",
        "winner_reasoning": "Best overall performance",
        "ranking": ["Claude", "ChatGPT"]
    }
    
    print("Original 1000-scale scores:")
    for eval_item in sample_evaluation["evaluations"]:
        tool = eval_item["tool"]
        print(f"\n{tool}:")
        print(f"  Truthfulness: {eval_item['truthfulness']['score']}/1000")
        print(f"  Creativity: {eval_item['creativity']['score']}/1000")
        print(f"  Coherence: {eval_item['coherence']['score']}/1000")
        print(f"  Utility: {eval_item['utility']['score']}/1000")
        print(f"  Overall: {eval_item['overall_score']}/1000")
    
    # Test the create_results_table method
    judge = GenAIBenchmarkJudge()
    df = judge.create_results_table(sample_evaluation)
    
    if df is not None:
        print("\n=== Converted to 10-scale ===")
        print(df.to_string(index=False))
        
        print("\n=== Expected Results ===")
        print("ChatGPT: 8.620, 7.450, 9.230, 8.010, 8.330")
        print("Claude: 9.340, 8.760, 9.450, 9.120, 9.170")
        
        print("\n=== DataFrame as dict records ===")
        table_data = df.to_dict('records')
        for record in table_data:
            print(f"\nTool: {record['Tool']}")
            print(f"  Truthfulness: {record['Truthfulness']}/10")
            print(f"  Creativity: {record['Creativity']}/10")
            print(f"  Coherence & Reasoning: {record['Coherence & Reasoning']}/10")
            print(f"  Utility/Actionability: {record['Utility/Actionability']}/10")
            print(f"  Overall Score: {record['Overall Score']}/10")
    else:
        print("ERROR: create_results_table returned None")

def test_llm_with_1000_scale():
    """Test what the LLM returns with 1000-scale prompting"""
    
    print("\n" + "="*60)
    print("=== Testing LLM with 1000-Scale Prompting ===")
    
    judge = GenAIBenchmarkJudge()
    
    # Simple test question and responses
    question = "What is the capital of France?"
    responses = {
        "ChatGPT": "The capital of France is Paris. It's a beautiful city known for the Eiffel Tower.",
        "Claude": "Paris is the capital and largest city of France, established as the capital in 987 AD."
    }
    
    print(f"Question: {question}")
    print(f"Responses: {responses}")
    
    try:
        # Get evaluation results
        evaluation_results = judge.evaluate(question, responses)
        
        if "error" not in evaluation_results:
            print("\n=== LLM Returned (1000-scale) ===")
            for eval_item in evaluation_results.get("evaluations", []):
                tool = eval_item["tool"]
                print(f"\n{tool}:")
                print(f"  Truthfulness: {eval_item['truthfulness']['score']}/1000")
                print(f"  Creativity: {eval_item['creativity']['score']}/1000")
                print(f"  Coherence: {eval_item['coherence']['score']}/1000")
                print(f"  Utility: {eval_item['utility']['score']}/1000")
                print(f"  Overall: {eval_item['overall_score']}/1000")
            
            # Test conversion
            df = judge.create_results_table(evaluation_results)
            if df is not None:
                print("\n=== Converted to 10-scale ===")
                print(df.to_string(index=False))
        else:
            print(f"Error in evaluation: {evaluation_results['error']}")
            
    except Exception as e:
        print(f"Error testing LLM: {e}")

if __name__ == "__main__":
    test_1000_scale_conversion()
    test_llm_with_1000_scale()