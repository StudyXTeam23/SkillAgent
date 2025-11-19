"""测试parts循环"""
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
    
    stream = await client.aio.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="生成JSON: {\"test\": \"hello\"}",
        config=config
    )
    
    async for chunk in stream:
        if chunk.candidates:
            cand = chunk.candidates[0]
            if cand.content and cand.content.parts:
                print(f"Parts count: {len(cand.content.parts)}")
                print(f"Parts type: {type(cand.content.parts)}")
                print(f"Parts: {cand.content.parts}")
                
                for i, part in enumerate(cand.content.parts):
                    print(f"\n--- Part {i} ---")
                    print(f"Type: {type(part)}")
                    print(f"Has thought: {hasattr(part, 'thought')}")
                    print(f"Has text: {hasattr(part, 'text')}")
                    if hasattr(part, 'text'):
                        print(f"Text: {part.text}")

asyncio.run(main())
