#!/usr/bin/env python3
"""
Test script to verify the formatting is working correctly
"""

def test_formatting():
    """Test the formatting logic"""
    
    # Simulate data that would come from the API
    test_data = [
        {
            "Tool": "ChatGPT",
            "Truthfulness": 8.0,
            "Creativity": 7.0,
            "Coherence & Reasoning": 9.0,
            "Utility/Actionability": 8.0,
            "Overall Score": 8.0
        },
        {
            "Tool": "Claude", 
            "Truthfulness": 9.123,
            "Creativity": 8.456,
            "Coherence & Reasoning": 9.789,
            "Utility/Actionability": 9.012,
            "Overall Score": 8.845
        }
    ]
    
    print("=== Testing JavaScript-style Formatting ===")
    for row in test_data:
        print(f"\nTool: {row['Tool']}")
        print(f"Truthfulness: {float(row['Truthfulness']):.3f}/10")
        print(f"Creativity: {float(row['Creativity']):.3f}/10") 
        print(f"Coherence: {float(row['Coherence & Reasoning']):.3f}/10")
        print(f"Utility: {float(row['Utility/Actionability']):.3f}/10")
        print(f"Overall: {float(row['Overall Score']):.3f}/10")
    
    print("\n=== Testing Jinja2-style Formatting ===")
    for row in test_data:
        print(f"\nTool: {row['Tool']}")
        print(f"Truthfulness: {'%.3f' % row['Truthfulness']}/10")
        print(f"Creativity: {'%.3f' % row['Creativity']}/10")
        print(f"Coherence: {'%.3f' % row['Coherence & Reasoning']}/10") 
        print(f"Utility: {'%.3f' % row['Utility/Actionability']}/10")
        print(f"Overall: {'%.3f' % row['Overall Score']}/10")

if __name__ == "__main__":
    test_formatting()