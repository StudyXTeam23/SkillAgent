"""测试我们的流式方法"""
import asyncio
import sys
sys.path.insert(0, '.')
from app.services.gemini import GeminiClient

async def main():
    client = GeminiClient()
    
    prompt = """生成JSON: {"test": "hello"}"""
    
    print("🔍 测试我们的generate_stream方法\n")
    
    async for chunk in client.generate_stream(prompt=prompt, thinking_budget=0):
        print(f"Chunk type: {chunk['type']}")
        if chunk['type'] == 'thinking':
            print(f"  Thinking: {chunk.get('text', '')[:100]}")
        elif chunk['type'] == 'content':
            print(f"  Content: {chunk.get('text', '')[:100]}")
        elif chunk['type'] == 'done':
            print(f"  Done - thinking:{len(chunk.get('thinking', ''))}, content:{len(chunk.get('content', ''))}")
        elif chunk['type'] == 'error':
            print(f"  Error: {chunk.get('error')}")

asyncio.run(main())
