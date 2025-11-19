"""测试无thinking模式"""
import asyncio
from app.services.gemini import GeminiClient

async def main():
    client = GeminiClient()
    
    prompt = """生成一个简单的JSON：{"name": "张三", "age": 25}"""
    
    print("🌊 测试流式生成（无thinking）...\n")
    
    content = []
    
    async for chunk in client.generate_stream(prompt=prompt, thinking_budget=0):
        t = chunk['type']
        if t == 'content':
            content.append(chunk.get('text', ''))
            print(f"📝 {chunk.get('text', '')}")
        elif t == 'done':
            print(f"\n✅ 内容: {len(''.join(content))} 字符")
            print(f"完整内容: {''.join(content)}")

asyncio.run(main())
