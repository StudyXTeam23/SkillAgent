"""调试Gemini流式API"""
import asyncio
import sys
sys.path.insert(0, '.')
from app.config import settings
from google import genai
from google.genai import types

async def main():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=200,
        response_modalities=["TEXT"],
    )
    
    prompt = """生成JSON: {"test": "hello"}"""
    
    print("🔍 调试Gemini流式API\n")
    
    stream = await client.aio.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    
    chunk_count = 0
    async for chunk in stream:
        chunk_count += 1
        print(f"\n--- Chunk {chunk_count} ---")
        print(f"Chunk type: {type(chunk)}")
        print(f"Chunk: {chunk}")
        
        if hasattr(chunk, 'candidates'):
            print(f"Candidates: {len(chunk.candidates) if chunk.candidates else 0}")

asyncio.run(main())
