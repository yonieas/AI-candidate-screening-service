# services/llm_provider.py
import asyncio
from config import GENERATIVE_MODEL_NAME, logger
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

class LLMProvider:
    """
    A wrapper for the Gemini LLM provider, containing retry logic.
    """
    def __init__(self, model_name: str = GENERATIVE_MODEL_NAME):
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"LLM Provider initialized with model: {model_name}")

    async def generate_text_async(self, prompt: str, retries: int = 3, delay: int = 5) -> str:
        """
        Runs a prompt against the LLM with asynchronous retry logic.
        """
        config = GenerationConfig(
            temperature=0.1,  # Lower temperature for more deterministic, JSON-friendly output
            top_p=0.95,
            top_k=40
        )
        for attempt in range(retries):
            try:
                logger.info(f"LLM call attempt {attempt + 1}...")
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config=config
                    )
                return response.text
            except Exception as e:
                logger.error(f"LLM API call failed on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    logger.error("LLM call failed after all retries.")
                    raise # Re-raise the final exception
