# Guide: Replacing Claude with Another AI Model

## Current Implementation

Your `ai_service.py` uses Claude AI through:
```python
self.claude_client = get_claude_client()
```

## Option 1: Replace with OpenAI GPT

### 1. Install OpenAI
```bash
pip install openai
```

### 2. Create `utils/openai_client.py`
```python
import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.is_enabled = bool(os.getenv("OPENAI_API_KEY"))
    
    def generate_response(self, prompt, max_tokens=2048, temperature=0.7, system_prompt=None):
        if not self.is_enabled:
            return "OpenAI is not configured"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content

_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
```

### 3. Update `services/ai_service.py`
```python
# Change this line:
from utils.claude_client import get_claude_client

# To:
from utils.openai_client import get_openai_client

# In __init__:
def __init__(self):
    # ...existing code...
    self.ai_client = get_openai_client()  # Changed from claude_client
```

### 4. Update `.env`
```env
OPENAI_API_KEY=your_openai_key_here
```

## Option 2: Use Ollama (Local AI)

### 1. Install Ollama SDK
```bash
pip install ollama
```

### 2. Create `utils/ollama_client.py`
```python
import ollama

class OllamaClient:
    def __init__(self):
        self.is_enabled = True
    
    def generate_response(self, prompt, max_tokens=2048, temperature=0.7, system_prompt=None):
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = ollama.chat(
            model='llama2',  # or 'mistral', 'codellama', etc.
            messages=[{
                'role': 'user',
                'content': full_prompt
            }],
            options={
                'temperature': temperature,
                'num_predict': max_tokens
            }
        )
        
        return response['message']['content']

def get_ollama_client():
    return OllamaClient()
```

## Option 3: Use Hugging Face Models

### 1. Install transformers
```bash
pip install transformers torch
```

### 2. Create `utils/huggingface_client.py`
```python
from transformers import pipeline

class HuggingFaceClient:
    def __init__(self):
        self.generator = pipeline(
            'text-generation',
            model='meta-llama/Llama-2-7b-chat-hf',  # or any other model
            device=0  # GPU, use -1 for CPU
        )
        self.is_enabled = True
    
    def generate_response(self, prompt, max_tokens=2048, temperature=0.7, system_prompt=None):
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        result = self.generator(
            full_prompt,
            max_length=max_tokens,
            temperature=temperature,
            do_sample=True
        )
        
        return result[0]['generated_text']
```

## Option 4: Keep Claude (Recommended)

Your current implementation with Claude is excellent because:
- ? Claude excels at following formatting instructions
- ? Better at markdown generation
- ? Strong context understanding
- ? Already integrated and working

## Quick Test: Verify Current Setup

```python
# Test your current Claude integration
from utils.claude_client import get_claude_client

client = get_claude_client()
print(f"Claude enabled: {client.is_enabled}")

if client.is_enabled:
    response = client.generate_response(
        prompt="Give me 3 tips for Python",
        system_prompt="Format your response with markdown bullet points"
    )
    print(response)
```

## Environment Variables

Make sure your `.env` file has:

```env
# For Claude (current)
ANTHROPIC_API_KEY=your_anthropic_key

# For OpenAI (if switching)
OPENAI_API_KEY=your_openai_key

# For Ollama (if using local)
# No API key needed, just install Ollama
```

## Summary

**Your current implementation is complete and production-ready with Claude.**

If you want to switch AI providers:
1. Create a new client file (like the examples above)
2. Update the import in `ai_service.py`
3. Set the appropriate environment variable

The rest of your formatting pipeline (context analysis, format selection, markdown processing) works with any AI model!
