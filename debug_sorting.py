import asyncio
from db.benchmark_handler import get_all_benchmark_results

async def test_data():
    results = await get_all_benchmark_results()
    if results:
        result = results[0]
        print('Sample result overall_score:', result.get('overall_score', {}))
        print('Type of overall_score values:')
        for k, v in result.get('overall_score', {}).items():
            print(f'  {k}: {v} (type: {type(v)})')
        
        # Test sorting logic
        answers = {
            "ChatGPT": result.get("chatgpt_answer", ""),
            "Kimi": result.get("kimi_answer", ""),
            "DeepSeek": result.get("deepseek_answer", ""),
            "Qwen": result.get("qwen_answer", ""),
            "Mistral": result.get("mistral_answer", ""),
            "Claude": result.get("claude_answer", ""),
            "Grok": result.get("grok_answer", "")
        }
        
        # Filter out empty answers
        answers = {k: v for k, v in answers.items() if v.strip()}
        
        overall_scores = result.get("overall_score", {})
        
        table_data = []
        for tool in answers.keys():
            tool_lower = tool.lower()
            overall_score = overall_scores.get(tool_lower, 0)
            try:
                overall_score = float(overall_score) if overall_score else 0
            except (ValueError, TypeError):
                overall_score = 0
                
            table_data.append({
                "tool": tool,
                "overall_score": overall_score
            })
        
        print("\nBefore sorting:")
        for item in table_data:
            print(f"{item['tool']}: {item['overall_score']}")
        
        table_data.sort(key=lambda x: x["overall_score"], reverse=True)
        
        print("\nAfter sorting:")
        for item in table_data:
            print(f"{item['tool']}: {item['overall_score']}")

if __name__ == "__main__":
    asyncio.run(test_data())