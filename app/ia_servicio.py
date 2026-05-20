import requests
import json

def analizar_ventas(data):
  prompt= f"""
        Analiza las ventas y enviame recomendaciones: {data}
  """
  response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    data=json.dumps({
      "model": "deepseek/deepseek-chat",
      "messages": [
        {
          "role": "user",
          "content": prompt
        }
      ]
    })
  )
  result = response;
  print