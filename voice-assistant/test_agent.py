"""
Test script for agent-based RAG system
Tests: follow-up detection, tool selection, and query handling
"""

from rag import DitaRAGAssistant
import time

def test_agent_conversation():
    """Test agent with follow-up questions"""
    
    print("\n" + "="*70)
    print("TESTING AGENT-BASED RAG SYSTEM")
    print("="*70 + "\n")
    
    # Initialize assistant
    assistant = DitaRAGAssistant()
    
    # Test scenario
    test_queries = [
        "apakah ada berita terbaru demo",
        "apakah ada tindakan pejabat tentang itu",
        "ada rekomendasi terhadap berita itu",
        "kirim rekomendasi tadi ke whatsapp"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query}")
        print(f"{'='*70}")
        
        start = time.time()
        result = assistant.ask(query)
        duration = time.time() - start
        
        print(f"\n[RESULT]")
        print(f"Status: {result['status']}")
        print(f"Response time: {duration:.2f}s")
        print(f"Sources: {result['source_count']} articles")
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\n{'='*70}\n")
        
        # Wait a bit before next query
        time.sleep(2)
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_agent_conversation()
