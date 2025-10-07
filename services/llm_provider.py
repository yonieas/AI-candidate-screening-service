# services/llm_provider.py
import asyncio
import json
from google.generativeai.types import GenerationConfig
from config import GENERATIVE_MODEL_NAME, logger, LLM_TEMPERATURE, LLM_RETRIES, LLM_RETRY_DELAY
import google.generativeai as genai

class LLMProvider:
    """
    A wrapper for the Gemini LLM provider, containing retry logic.
    """
    def __init__(self, model_name: str = GENERATIVE_MODEL_NAME):
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"LLM Provider initialized with model: {model_name}")

    async def generate_text_async(self, prompt: str) -> str:
        """
        Runs a prompt against the LLM with asynchronous retry logic from config.
        """
        config = GenerationConfig(
            temperature=LLM_TEMPERATURE,
            top_p=0.95,
            top_k=40
        )
        for attempt in range(LLM_RETRIES):
            try:
                logger.info(f"LLM call attempt {attempt + 1}...")
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config=config
                )
                return response.text
            except Exception as e:
                logger.error(f"LLM API call failed on attempt {attempt + 1}: {e}")
                if attempt < LLM_RETRIES - 1:
                    await asyncio.sleep(LLM_RETRY_DELAY)
                else:
                    logger.error("LLM call failed after all retries.")
                    raise

    def safe_json_loads(self, json_string: str) -> dict:
        """
        Safely parses a JSON string that might be wrapped in markdown.
        """
        try:
            # Clean the string from markdown formatting
            cleaned_string = json_string.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_string)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {json_string}")
            raise ValueError("LLM returned invalid JSON.")
