import json
import asyncio
import structlog
from litellm import acompletion
from app.core.config import settings
import os

logger = structlog.get_logger(__name__)

# LiteLLM reads from environment variables automatically. 
# You can also set them explicitly if they aren't in your env:
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

BASE_SYSTEM_PROMPT = """
You are an expert DevSecOps and SOC2 compliance auditor.
Analyze the provided GitHub code diff. Look for OWASP Top 10 vulnerabilities, hardcoded secrets, and SOC2 compliance violations.
"""

SYSTEM_PROMPT = """
You MUST respond strictly in valid JSON format using the following schema:
{
    "vulnerabilities": [
        {
            "filename": "path/to/file",
            "line_number": 42,
            "severity": "high|medium|low",
            "title": "Short title of issue",
            "description": "Detailed explanation of the vulnerability and how to fix it."
        }
    ]
}
IMPORTANT: "line_number" MUST be the exact line number from the NEW code (the right side of the diff) where the vulnerability exists.
If no vulnerabilities are found, return an empty array for "vulnerabilities".
"""

async def analyze_code_chunk(filename: str, diff_content: str, custom_rules: list[str] = None) -> dict:
    """
    Sends a specific file's diff to the LLM for security analysis using LiteLLM.
    """
    log = logger.bind(filename=filename)
    try:
        dynamic_prompt = BASE_SYSTEM_PROMPT

        if custom_rules:
            dynamic_prompt += "\n\nCRITICAL COMPANY-SPECIFIC RULES TO ENFORCE:\n"
            for i, rule in enumerate(custom_rules, 1):
                dynamic_prompt += f"{i}. {rule}\n"

        dynamic_prompt += SYSTEM_PROMPT

        log.info("ai_request_sent", message=f"Sending AI analysis request for {filename}")
        # acompletion handles the async request across ANY provider
        response = await acompletion(
            model=settings.LITELLM_MODEL,
            # Removed response_format={"type": "json_object"} as it causes some local models (like Qwen via Ollama) 
            # to return empty responses. We use robust parsing instead.
            messages=[
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": f"File: {filename}\n\nDiff:\n{diff_content}"}
            ],
            temperature=0.1, # Lower temperature for more deterministic output
            num_retries=2, # <--- LiteLLM specific: automatically retry if local Ollama is busy
            drop_params=True # Drop provider-specific parameters to ensure compatibility across different LLMs
        )

        # Accessing content remains identical to the OpenAI SDK structure
        content = response.choices[0].message.content
        
        if not content:
            log.error("ai_analysis_empty_response", message=f"AI returned an empty response for {filename}")
            return {"vulnerabilities": []}

        # Robust JSON parsing
        try:
            # 1. Try direct JSON parsing
            result = json.loads(content)
        except json.JSONDecodeError:
            # 2. Try to extract JSON from markdown blocks if present
            log.warning("ai_json_parse_failed_direct", message="Direct JSON parsing failed, attempting markdown extraction", raw_content=content)
            import re
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    log.error("ai_json_parse_failed_markdown", message="JSON parsing from markdown block failed")
                    return {"vulnerabilities": []}
            else:
                log.error("ai_json_parse_failed_no_match", message="Could not find JSON in response")
                return {"vulnerabilities": []}

        vuln_count = len(result.get("vulnerabilities", []))
        log.info("ai_response_received", 
                 message=f"Received AI response for {filename}. Found {vuln_count} vulnerabilities", 
                 vulnerability_count=vuln_count)
        
        return result
    except Exception as e:
        # LiteLLM maps all provider errors to standard OpenAI exception types
        log.error("ai_analysis_failed", 
                  message=f"AI Analysis failed for {filename}", 
                  error=str(e), 
                  error_type=type(e).__name__)
        return {"vulnerabilities": []}