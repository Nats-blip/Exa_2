import requests
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def analizar_ventas(data):
  prompt = f"""
Eres un analista senior especializado en inteligencia de negocios para empresas de servicios técnicos.

Tu trabajo es analizar la información del sistema y generar conclusiones estratégicas automáticas.

# DATOS DEL SISTEMA

{data}

INSTRUCCIONES IMPORTANTES:
- Responde ÚNICAMENTE en HTML.
- NO uses markdown.
- NO uses ```html
- El diseño debe verse moderno y profesional.
- Usa tarjetas visuales.
- Usa colores oscuros modernos.
- Usa iconos emoji.
- Usa títulos elegantes.
- Usa listas y métricas visuales.
- Usa estilos inline CSS.
- Todo debe estar listo para renderizar directamente en Flask con |safe.

ESTRUCTURA HTML OBLIGATORIA:

1. Tarjeta resumen ejecutivo
2. Tarjetas KPI métricas
3. Tarjeta de patrones detectados
4. Tarjeta de riesgos
5. Tarjeta de recomendaciones
6. Tarjeta de conclusión final

ESTILO:
- Fondo: #111827
- Tarjetas: #1f2937
- Texto: white
- Bordes redondeados
- Sombras modernas
- Tipografía elegante
- Espaciado profesional

Las métricas deben verse en grid.

El resultado debe verse como un dashboard premium de inteligencia artificial empresarial.
# OBJETIVOS DEL ANÁLISIS

Analiza:

- Rendimiento general del negocio
- Servicios más demandados
- Técnicos con mayor actividad
- Comportamiento de ingresos
- Patrones detectados
- Posibles problemas operativos
- Oportunidades de crecimiento
- Recomendaciones estratégicas

# INSTRUCCIONES IMPORTANTES

- Usa lenguaje profesional
- Explica patrones importantes
- Genera recomendaciones accionables
- Habla como un consultor empresarial
- Usa emojis moderadamente
- NO inventes datos inexistentes
- Usa formato Markdown

# FORMATO OBLIGATORIO

## 📊 RESUMEN EJECUTIVO

## 📈 MÉTRICAS CLAVE

## 🔍 PATRONES DETECTADOS

## 👨‍🔧 ANÁLISIS OPERATIVO

## 💰 ANÁLISIS FINANCIERO

## 🚨 RIESGOS DETECTADOS

## 💡 RECOMENDACIONES ESTRATÉGICAS

## 🎯 CONCLUSIÓN GENERAL

---
Análisis generado automáticamente por IA.

"""
  response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    json={
      "model": "deepseek/deepseek-chat",
      "messages": [
        {
          "role": "user",
          "content": prompt
        }
      ]
    },
    timeout=10
    )
  
  result = response.json();
  print (result)
  return result["choices"][0]["message"]["content"]