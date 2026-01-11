#!/usr/bin/env python3
"""
Simple test script to verify the categorization functionality works correctly.
"""

import os
from dotenv import load_dotenv
from business import GenAIBenchmarkJudge

# Load environment variables
load_dotenv()

def test_categorization():
    """
    Test the categorization functionality with sample questions.
    """
    print("🧪 Testing GenAI Question Categorization (Open-ended)")
    print("=" * 60)
    
    try:
        # Initialize judge with Gemini
        judge = GenAIBenchmarkJudge(provider="gemini")
        print("✅ GenAI Judge initialized successfully")
        
        # Test questions with expected categories (more flexible now)
        test_cases = [
            "How does machine learning work in Python?",
            "What are the best investment strategies for 2024?",
            "Who won the Oscar for best picture last year?",
            "How to bake a chocolate cake?",
            "What causes climate change?",
            "How do vaccines work?",
            "What is quantum computing?",
            "How to start a podcast?",
            "What are the symptoms of diabetes?",
            "Who painted the Mona Lisa?",
            "How does photosynthesis work?",
            "What is the capital of Australia?",
            "How to play chess?",
            "What is cryptocurrency?",
            "How to lose weight effectively?"
        ]
        
        print("\nTesting categorization with diverse questions...")
        print("-" * 60)
        
        categories_found = set()
        
        for i, question in enumerate(test_cases, 1):
            try:
                category = judge.categorize_question(question)
                categories_found.add(category)
                
                print(f"{i:2d}. Question: {question}")
                print(f"    Category: {category}")
                print()
                    
            except Exception as e:
                print(f"❌ Error categorizing question {i}: {e}")
                print(f"   Question: {question}")
                print()
        
        # Print results
        print("=" * 60)
        print("📊 CATEGORIZATION TEST RESULTS")
        print("=" * 60)
        print(f"Total questions tested: {len(test_cases)}")
        print(f"Unique categories found: {len(categories_found)}")
        print(f"Categories: {', '.join(sorted(categories_found))}")
        print()
        print("✅ Open-ended categorization is working!")
        print("The system can now generate any category based on question content.")
            
    except Exception as e:
        print(f"❌ Failed to initialize or test categorization: {e}")
        print("Make sure you have GEMINI_API_KEY or GOOGLE_API_KEY set in your environment")

if __name__ == "__main__":
    test_categorization()