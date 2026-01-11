#!/usr/bin/env python3
"""
Debug script to test metric formatting
"""

from business import GenAIBenchmarkJudge
import json

def test_metric_formatting():
    """Test how metrics are being formatted"""
    
    # Sample evaluation data that might come from LLM
    sample_evaluation = {
        "evaluations": [
            {
                "tool": "ChatGPT",
                "truthfulness": {"score": 8, "reasoning": "Good accuracy"},
                "creativity": {"score": 7, "reasoning": "Decent creativity"},
                "coherence": {"score": 9, "reasoning": "Very coherent"},
                "utility": {"score": 8, "reasoning": "Quite useful"},
                "overall_score": 8.0,
                "notes": "Good overall performance"
            },
            {
                "tool": "Claude",
                "truthfulness": {"score": 9, "reasoning": "Excellent accuracy"},
                "creativity": {"score": 8, "reasoning": "Creative approach"},
                "coherence": {"score": 9, "reasoning": "Well structured"},
                "utility": {"score": 9, "reasoning": "Very practical"},
                "overall_score": 8.75,
                "notes": "Top performer"
            }
        ],
        "winner": "Claude",
        "winner_reasoning": "Best overall performance",
        "ranking": ["Claude", "ChatGPT"]
    }
    
    print("=== Testing Metric Formatting ===")
    print("\nOriginal evaluation data:")
    print(json.dumps(sample_evaluation, indent=2))
    
    # Test the create_results_table method
    judge = GenAIBenchmarkJudge()
    df = judge.create_results_table(sample_evaluation)
    
    if df is not None:
        print("\n=== DataFrame from create_results_table ===")
        print(df.to_string(index=False))
        
        print("\n=== DataFrame as dict records ===")
        table_data = df.to_dict('records')
        for record in table_data:
            print(f"Tool: {record['Tool']}")
            print(f"  Truthfulness: {record['Truthfulness']} (type: {type(record['Truthfulness'])})")
            print(f"  Creativity: {record['Creativity']} (type: {type(record['Creativity'])})")
            print(f"  Coherence & Reasoning: {record['Coherence & Reasoning']} (type: {type(record['Coherence & Reasoning'])})")
            print(f"  Utility/Actionability: {record['Utility/Actionability']} (type: {type(record['Utility/Actionability'])})")
            print(f"  Overall Score: {record['Overall Score']} (type: {type(record['Overall Score'])})")
            print()
    else:
        print("ERROR: create_results_table returned None")

if __name__ == "__main__":
    test_metric_formatting()