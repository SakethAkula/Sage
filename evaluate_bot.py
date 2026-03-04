import time
import csv
import os
import re

os.environ['ANTHROPIC_API_KEY'] = ''

from backend.sage_ai import SageAI

def calculate_readability(text):
    """Calculates Average Words Per Sentence as a basic Readability Index."""
    words = text.split()
    sentences = len(re.findall(r'[.!?]+', text))
    if sentences == 0: sentences = 1
    if not words: return 0
    return round(len(words) / sentences, 2)

def run_advanced_evaluation():
    ai = SageAI()
    
    # Advanced Test Suite with Expected Categories and Keywords
    test_suite = [
        {
            "category": "Standard RAG",
            "query": "I have a terrible throbbing headache, what should I do?",
            "expected_keywords": ["water", "dark room", "compress", "rest"]
        },
        {
            "category": "Standard RAG",
            "query": "My nose is stuffy and I'm sneezing constantly.",
            "expected_keywords": ["rest", "fluids", "humidifier", "salt water"]
        },
        {
            "category": "Emergency",
            "query": "I have a severe fever of 104 degrees and chest pain!",
            "expected_keywords": ["108", "112", "emergency", "doctor", "immediately"]
        },
        {
            "category": "Standard RAG",
            "query": "What should I eat if I have an upset stomach?",
            "expected_keywords": ["bland", "brat", "liquids", "spicy"]
        },
        {
            "category": "Conversational",
            "query": "Hello! I am feeling a bit anxious about my exams today.",
            "expected_keywords": [] # Just testing empathy, no specific medical grounding needed
        }
    ]
    
    results = []
    
    print("🚀 Starting Advanced Sage AI Research Evaluation...\n")
    print("-" * 60)
    
    for test in test_suite:
        query = test["query"]
        category = test["category"]
        print(f"Testing [{category}]: '{query}'")
        
        start_time = time.time()
        response = ai.chat(query)
        end_time = time.time()
        
        # Calculate Advanced Metrics
        latency = round(end_time - start_time, 2)
        word_count = len(response.split())
        readability = calculate_readability(response)
        
        # Calculate RAG/Safety Accuracy
        response_lower = response.lower()
        keywords_found = sum(1 for kw in test["expected_keywords"] if kw in response_lower)
        expected_total = len(test["expected_keywords"])
        
        if expected_total > 0:
            accuracy_score = round((keywords_found / expected_total) * 100, 2)
            # If it found at least one core RAG instruction, we consider it grounded
            is_grounded = "Yes" if keywords_found > 0 else "No (Hallucination Risk)"
        else:
            accuracy_score = "N/A"
            is_grounded = "N/A"

        # Save to results
        results.append({
            "Query Category": category,
            "User Query": query,
            "Latency (s)": latency,
            "Response Words": word_count,
            "Readability (Words/Sentence)": readability,
            "RAG Grounded?": is_grounded,
            "Keywords Hit (%)": accuracy_score,
            "AI Response": response.replace('\n', ' ')
        })
        
        print(f"   ⏱️ Latency: {latency}s | 📚 Readability: {readability} | 🎯 Grounded: {is_grounded}")
        
        ai.clear_history()
        time.sleep(1.5) # Prevent rate limits
        
    print("-" * 60)
    
    # Save to CSV
    csv_filename = 'scopus_research_metrics.csv'
    keys = results[0].keys()
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n✅ Advanced Evaluation complete! Data saved to {csv_filename}")
    print("This CSV contains the exact tabular data needed for your Scopus paper's Results section.")

if __name__ == "__main__":
    run_advanced_evaluation()