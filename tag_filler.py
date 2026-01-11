#!/usr/bin/env python3
"""
One-time runner to categorize existing benchmark results and add category tags to the database.
This script will:
1. Fetch all existing benchmark results from MongoDB
2. Use the GenAI categorization method to determine the category for each question
3. Update the database records with the new category field
"""

import asyncio
import os
from dotenv import load_dotenv
from business import GenAIBenchmarkJudge
from db import benchmark_handler

# Load environment variables
load_dotenv()

async def categorize_and_update_existing_results():
    """
    Main function to categorize existing results and update the database.
    """
    print("🚀 Starting tag filler process...")
    
    # Initialize the categorization judge with Gemini (free option)
    try:
        judge = GenAIBenchmarkJudge(provider="gemini")
        print("✅ GenAI Judge initialized with Gemini")
    except Exception as e:
        print(f"❌ Failed to initialize GenAI Judge: {e}")
        print("Make sure you have GEMINI_API_KEY or GOOGLE_API_KEY set in your environment")
        return
    
    # Fetch all existing benchmark results
    try:
        results = await benchmark_handler.get_all_benchmark_results()
        print(f"📊 Found {len(results)} existing benchmark results")
    except Exception as e:
        print(f"❌ Failed to fetch benchmark results: {e}")
        return
    
    if not results:
        print("ℹ️ No existing results found. Nothing to update.")
        return
    
    # Process each result
    updated_count = 0
    failed_count = 0
    
    for i, result in enumerate(results, 1):
        scid = result.get("scid")
        question = result.get("question", "")
        
        print(f"\n[{i}/{len(results)}] Processing SCID: {scid}")
        print(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
        
        # Skip if already has category (optional - remove this if you want to re-categorize)
        if result.get("category"):
            print(f"⏭️ Already has category: {result.get('category')}")
            continue
        
        # Skip if no question
        if not question.strip():
            print("⚠️ No question found, skipping...")
            failed_count += 1
            continue
        
        try:
            # Categorize the question
            category = judge.categorize_question(question)
            print(f"🏷️ Categorized as: {category}")
            
            # Update the database record
            update_data = {"category": category}
            success = await benchmark_handler.update_benchmark_result(scid, update_data)
            
            if success:
                print(f"✅ Updated SCID {scid} with category: {category}")
                updated_count += 1
            else:
                print(f"❌ Failed to update SCID {scid}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error processing SCID {scid}: {e}")
            failed_count += 1
        
        # Add a small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 TAG FILLER SUMMARY")
    print("="*60)
    print(f"Total results processed: {len(results)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed/Skipped: {failed_count}")
    print(f"Already categorized: {len(results) - updated_count - failed_count}")
    print("="*60)
    
    if updated_count > 0:
        print("🎉 Tag filling completed successfully!")
    else:
        print("ℹ️ No records were updated.")

async def test_categorization():
    """
    Test function to verify the categorization works correctly.
    """
    print("🧪 Testing categorization functionality...")
    
    try:
        judge = GenAIBenchmarkJudge(provider="gemini")
        
        test_questions = [
            "How does machine learning work in Python?",
            "What are the best investment strategies for 2024?",
            "Who won the Oscar for best picture last year?",
            "Explain blockchain technology and its applications",
            "How to start a successful startup?",
            "What are the top movies of 2023?"
        ]
        
        for question in test_questions:
            category = judge.categorize_question(question)
            print(f"Question: {question}")
            print(f"Category: {category}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """
    Main entry point with options for testing or running the full update.
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test mode...")
        asyncio.run(test_categorization())
    else:
        print("Running full tag filler process...")
        print("⚠️ This will update all existing benchmark results in the database.")
        
        # Ask for confirmation
        response = input("Do you want to continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled.")
            return
        
        asyncio.run(categorize_and_update_existing_results())

if __name__ == "__main__":
    main()