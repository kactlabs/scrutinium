#!/usr/bin/env python3
"""
Setup MongoDB collections and indexes for the benchmark system
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_mongodb():
    """Setup MongoDB collections and indexes"""
    
    # MongoDB connection
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    
    if not MONGO_URI or not DB_NAME:
        print("❌ MongoDB configuration missing!")
        print("Please set MONGO_URI and DB_NAME in your .env file")
        return False
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        
        print(f"🔗 Connected to MongoDB: {DB_NAME}")
        
        # Create benchmark_results collection
        collection_name = "benchmark_results"
        collection = db[collection_name]
        
        # Create indexes for better performance
        print(f"📊 Setting up indexes for {collection_name}...")
        
        # Index on scid (unique)
        await collection.create_index("scid", unique=True)
        print("✓ Created unique index on 'scid'")
        
        # Index on judge for filtering
        await collection.create_index("judge")
        print("✓ Created index on 'judge'")
        
        # Index on created_at for sorting
        await collection.create_index("created_at")
        print("✓ Created index on 'created_at'")
        
        # Compound index for common queries
        await collection.create_index([("judge", 1), ("created_at", -1)])
        print("✓ Created compound index on 'judge' and 'created_at'")
        
        # Create a sample document to verify the schema
        print(f"\n📝 Creating sample document to verify schema...")
        
        sample_doc = {
            "scid": 12001,
            "judge": "gemini",
            "question": "Sample question for schema verification",
            "chatgpt_answer": "Sample ChatGPT answer",
            "kimi_answer": "Sample Kimi answer", 
            "deepseek_answer": "Sample DeepSeek answer",
            "qwen_answer": "Sample Qwen answer",
            "mistral_answer": "Sample Mistral answer",
            "claude_answer": "Sample Claude answer",
            "grok_answer": "Sample Grok answer",
            "truthfulness": {
                "chatgpt": 8,
                "deepseek": 9,
                "claude": 9
            },
            "creativity": {
                "chatgpt": 7,
                "deepseek": 8,
                "claude": 9
            },
            "coherence": {
                "chatgpt": 9,
                "deepseek": 8,
                "claude": 9
            },
            "utility": {
                "chatgpt": 8,
                "deepseek": 9,
                "claude": 8
            },
            "overall_score": {
                "chatgpt": 8.0,
                "deepseek": 8.5,
                "claude": 8.75
            }
        }
        
        # Check if sample already exists
        existing = await collection.find_one({"scid": 12001})
        if not existing:
            await collection.insert_one(sample_doc)
            print("✓ Created sample document with SCID 12001")
        else:
            print("✓ Sample document already exists")
        
        # Verify collection setup
        doc_count = await collection.count_documents({})
        indexes = await collection.list_indexes().to_list(length=None)
        
        print(f"\n📈 Collection Summary:")
        print(f"   - Collection: {collection_name}")
        print(f"   - Documents: {doc_count}")
        print(f"   - Indexes: {len(indexes)}")
        
        print(f"\n🎉 MongoDB setup completed successfully!")
        
        # Close connection
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_mongodb())