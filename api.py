# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    # api_key=os.environ.get('DEEPSEEK_API_KEY'),
    api_key = '请输入文本',
    base_url="https://api.deepseek.com")

with open('output.txt', 'r', encoding='utf-8') as f:
    pt = f.read()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": """你是雀宝，专业的日本麻将（立直麻将）分析助手。

请分析用户上传的麻将牌局截图，给出专业实用的建议。

**输出格式：**

【局面分析】
- 当前状态：听牌/一向听/两向听
- 有效牌：X种X枚
- 危险牌：X牌、X牌

【切牌建议】
1. 切X牌（最优）：牌效最高，听牌最快
2. 切X牌（备选）：更安全，改良空间大

【注意事项】
- 防守要点：小心X牌
- 进攻时机：当前适合进攻/防守

分析要简洁实用，直接给建议。"""},
        {"role": "user", "content": f"{pt}"},
    ],
    stream=True
)

for chunk in response:  # 必须遍历chunk
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end='', flush=True)