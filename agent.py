import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

class ZeroDebugAgent:
    def __init__(self, team="ZERO_DEBUG", leader="AKASH_BR"):
        self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
        self.model = "Qwen/Qwen2.5-Coder-32B-Instruct"

    def generate_fix(self, logs: str, code: str) -> str:
        prompt = (
            f"FIX THE BUG IN THIS PYTHON CODE.\n\n"
            f"TEST FAILURE LOGS:\n{logs}\n\n"
            f"CURRENT CODE:\n{code}\n\n"
            f"INSTRUCTION: Analyze the logs, find the bug, and return ONLY the full corrected Python code. "
            f"No explanations, no markdown, just code."
        )
        
        response = self.client.chat_completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0 
        )
        
        content = response.choices[0].message.content
        # Strip markdown if the AI includes it despite instructions
        if "```python" in content:
            content = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return content.strip()