"""
Test script for BrandKnowledgeTool (CrewAI)
"""
import sys
import os

# Add src to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.rag_tool import BrandKnowledgeTool

def test_rag_tool():
    print("🚀 Testing BrandKnowledgeTool...")
    
    try:
        # Initialize Tool
        tool = BrandKnowledgeTool()
        print("✅ Tool initialized successfully.")
        
        # Test Queries
        queries = [
            "What is the brand tone?",
            "What are the forbidden words?",
            "Tell me about target audience"
        ]
        
        for q in queries:
            print(f"\n🔍 Query: '{q}'")
            result = tool._run(q)
            print("-" * 50)
            print(result)
            print("-" * 50)
            
            if result and "Error" not in result:
                print("✅ Retrieval successful")
            else:
                print("❌ Retrieval failed")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_rag_tool()
