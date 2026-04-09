import json
import asyncio
from litellm import acompletion
from app.core.config import settings
import os

# LiteLLM reads from environment variables automatically. 
# You can also set them explicitly if they aren't in your env:
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

SYSTEM_PROMPT = """
You are an expert DevSecOps and SOC2 compliance auditor.
Analyze the provided GitHub code diff. Look for OWASP Top 10 vulnerabilities, hardcoded secrets, and SOC2 compliance violations.

You MUST respond strictly in valid JSON format using the following schema:
{
    "vulnerabilities": [
        {
            "filename": "path/to/file",
            "severity": "high|medium|low",
            "title": "Short title of issue",
            "description": "Detailed explanation of the vulnerability and how to fix it."
        }
    ]
}
If no vulnerabilities are found, return an empty array for "vulnerabilities".
"""

async def analyze_code_chunk(filename: str, diff_content: str) -> dict:
    """
    Sends a specific file's diff to the LLM for security analysis using LiteLLM.
    """
    try:
        # acompletion handles the async request across ANY provider
        response = await acompletion(
            model=settings.LITELLM_MODEL,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"File: {filename}\n\nDiff:\n{diff_content}"}
            ],
            temperature=0.1, # Lower temperature for more deterministic output
            num_retries=2, # <--- LiteLLM specific: automatically retry if local Ollama is busy
            drop_params=True # Drop provider-specific parameters to ensure compatibility across different LLMs
        )

        # Accessing content remains identical to the OpenAI SDK structure
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        # LiteLLM maps all provider errors to standard OpenAI exception types
        print(f"AI Analysis failed for {filename}: {str(e)}")
        return {"vulnerabilities": []}