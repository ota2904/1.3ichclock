import asyncio
import os
import json
from pathlib import Path

async def test():
    print("="*60)
    print("TEST GEMINI SMART KB FILTER")
    print("="*60)
    
    # Check both APPDATA locations
    APPDATA_LOCAL = Path(os.environ.get("LOCALAPPDATA", "")) / "miniZ_MCP"
    APPDATA_ROAMING = Path(os.environ.get("APPDATA", "")) / "miniZ_MCP"
    
    # Try different KB locations
    KB_PATHS = [
        APPDATA_LOCAL / "knowledge" / "knowledge_index.json",
        APPDATA_LOCAL / "knowledge_base" / "kb_index.json",
        APPDATA_ROAMING / "knowledge_base" / "kb_index.json",
    ]
    
    KNOWLEDGE_INDEX_FILE = None
    for path in KB_PATHS:
        if path.exists():
            KNOWLEDGE_INDEX_FILE = path
            break
    
    endpoints_file = Path(__file__).parent / "xiaozhi_endpoints.json"
    api_key = None
    if endpoints_file.exists():
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get("gemini_api_key", "")
            if api_key:
                print(f"API key loaded (ends with ...{api_key[-7:]})")
    
    if not api_key:
        print("No Gemini API key found")
        return
    
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print("Gemini configured")
    
    documents = []
    if KNOWLEDGE_INDEX_FILE and KNOWLEDGE_INDEX_FILE.exists():
        print(f"KB index found: {KNOWLEDGE_INDEX_FILE}")
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            documents = index_data.get("documents", [])
    else:
        print(f"KB index NOT found!")
        for p in KB_PATHS:
            print(f"  Checked: {p}")
    
    print(f"Found {len(documents)} documents")
    
    if not documents:
        print("No documents in KB - please add files via Web UI")
        return
    
    for i, doc in enumerate(documents[:5], 1):
        name = doc.get("file_name", "unknown")
        size = len(doc.get("content", ""))
        print(f"  {i}. {name} ({size:,} chars)")
    
    query = "Muon kiep nhan sinh noi ve dieu gi?"
    print(f"\nQuery: {query}")
    
    keywords = ["muon", "kiep", "nhan", "sinh"]
    filtered_docs = []
    for doc in documents:
        content = doc.get("content", "").lower()
        name = doc.get("file_name", "").lower()
        score = sum(1 for kw in keywords if kw in content or kw in name)
        if score > 0:
            filtered_docs.append({"score": score, "name": doc.get("file_name"), "content": doc.get("content", "")})
    
    filtered_docs.sort(key=lambda x: x["score"], reverse=True)
    top_docs = filtered_docs[:3] if filtered_docs else [{"name": d.get("file_name"), "content": d.get("content", "")} for d in documents[:3]]
    
    print(f"Pre-filtered: {len(top_docs)} docs")
    for doc in top_docs:
        print(f"  - {doc.get('name', 'unknown')}")
    
    context_parts = []
    for i, doc in enumerate(top_docs):
        content = doc["content"][:2000]
        context_parts.append(f"[Doc {i+1}: {doc['name']}]\n{content}")
    
    combined_context = "\n---\n".join(context_parts)
    
    prompt = f"Dua vao tai lieu sau, tra loi cau hoi: {query}\n\nTAI LIEU:\n{combined_context}\n\nTra loi ngan gon bang tieng Viet."
    
    print(f"\nCalling Gemini Flash... (context: {len(combined_context)} chars)")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = await model.generate_content_async(prompt)
    
    print("\n" + "="*60)
    print("GEMINI RESPONSE:")
    print("="*60)
    print(response.text)
    print("="*60)
    print("\nTEST PASSED!")

if __name__ == "__main__":
    asyncio.run(test())
