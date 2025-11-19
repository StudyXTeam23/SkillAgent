"""快速测试Gemini流式"""
import asyncio
from app.services.gemini import GeminiClient

async def main():
    client = GeminiClient()
    
    prompt = """生成一个简单的JSON对象，包含name和age字段。

在思考后，必须输出JSON内容。

示例：
{"name": "张三", "age": 25}

请输出JSON。
"""
    
    print("🌊 测试流式生成...\n")
    
    thinking = []
    content = []
    
    async for chunk in client.generate_stream(prompt=prompt, thinking_budget=128):
        t = chunk['type']
        if t == 'thinking':
            thinking.append(chunk.get('text', ''))
            print(f"💭 {chunk.get('text', '')[:50]}...")
        elif t == 'content':
            content.append(chunk.get('text', ''))
            print(f"📝 {chunk.get('text', '')[:50]}...")
        elif t == 'done':
            print(f"\n✅ 完成")
            print(f"  思考: {len(''.join(thinking))} 字符")
            print(f"  内容: {len(''.join(content))} 字符")
            if content:
                print(f"  JSON: {''.join(content)[:100]}")

asyncio.run(main())
