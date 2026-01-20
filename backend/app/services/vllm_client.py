""" vLLM client service for generating completions."""
import httpx
import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class VLLMClient:
    """Client for interacting with vLLM completion service."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        """
        Initialize vLLM client.

        :param base_url: URL to query LLM (defaults to config)
        :type base_url: Optional[str]
        :param timeout: Request timeout in seconds (defaults to config)
        :type timeout: Optional[float]
        """
        self.base_url = base_url or settings.vllm_url
        self.timeout = timeout or settings.vllm_timeout
        self.model_name = settings.model_name

    async def generate_completion(
            self,
            prompt: str,
            max_tokens: int = 20,
            temperature: float = 0.7,
            top_p: float = 0.95,
    ) -> str:
        """
        Generate a completion from vLLM.

        :param prompt: Input text to complete
        :type prompt: str
        :param max_tokens: Maximum tokens to generate (default=20)
        :type max_tokens: int
        :param temperature: Sampling temperature (default=0.7)
        :type temperature: float
        :param top_p: Nucleus sampling parameter (default=0.95)
        :type top_p: float
        :return: Raw completion text from model
        :rtype: str
        :raises httpx.HTTPError: If vLLM request fails
        :raises KeyError: If response format is unexpected
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }

        logger.debug(f"vLLM request payload: {payload}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.base_url, json=payload)
            response.raise_for_status()
        
        result = response.json()
        completion = result["choices"][0]["text"]

        logger.debug(f"vLLM raw response: {completion}")

        return completion

# Singleton instance
vllm_client = VLLMClient()