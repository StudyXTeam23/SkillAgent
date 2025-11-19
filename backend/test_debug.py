"""调试Gemini流式API"""
import asyncio
from google import genai
from google.genai import types
import os

async def main():
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
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
        print(f"Has candidates: {hasattr(chunk, 'candidates')}")
        
        if hasattr(chunk, 'candidates') and chunk.candidates:
            cand = chunk.candidates[0]
            print(f"Has content: {hasattr(cand, 'content')}")
            
            if hasattr(cand, 'content') and cand.content:
                print(f"Content: {cand.content}")
                print(f"Has parts: {hasattr(cand.content, 'parts')}")
                
                if hasattr(cand.content, 'parts') and cand.content.parts:
                    print(f"Parts count: {len(cand.content.parts)}")
                    for i, part in enumerate(cand.content.parts):
                        print(f"  Part {i}:")
                        print(f"    Has thought: {hasattr(part, 'thought')}")
                        print(f"    Has text: {hasattr(part, 'text')}")
                        if hasattr(part, 'text'):
                            print(f"    Text: {part.text[:50]}")

asyncio.run(main())
