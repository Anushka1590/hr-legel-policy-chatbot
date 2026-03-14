import sys
import os
from duckduckgo_search import DDGS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import MAX_SEARCH_RESULTS

def web_search(query):
    """Perform a real-time web search using DuckDuckGo (no API key needed)"""
    try:
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=MAX_SEARCH_RESULTS
            )
            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "body":  r.get("body", ""),
                    "url":   r.get("href", "")
                })
        
        if not results:
            return "No search results found."
        
        # Format results into readable string
        formatted = ""
        for i, r in enumerate(results, 1):
            formatted += f"\n[{i}] {r['title']}\n{r['body']}\nSource: {r['url']}\n"
        
        return formatted
    
    except Exception as e:
        return f"Web search error: {str(e)}"