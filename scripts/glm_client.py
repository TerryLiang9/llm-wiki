"""
GLM API Client

This module provides a client for interacting with the GLM (智谱 AI) API.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class GLMStats:
    """Statistics for GLM API usage."""
    total_requests: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    failed_requests: int = 0
    cache_hits: int = 0


@dataclass
class GLMResponse:
    """Response from GLM API."""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached: bool = False


class GLMClientError(Exception):
    """Base exception for GLM client errors."""
    pass


class GLMAPIError(GLMClientError):
    """Exception for API errors."""
    pass


class GLMRateLimitError(GLMClientError):
    """Exception for rate limiting errors."""
    pass


class GLMClient:
    """
    Client for GLM (智谱 AI) API.

    Features:
    - Automatic retry with exponential backoff
    - Token usage tracking
    - Response caching (optional)
    - JSON mode support
    - Batch completion
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Literal["glm-4-flash", "glm-4-plus"] = "glm-4-flash",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
        max_tokens: int = 8192,
        temperature: float = 0.3,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_multiplier: float = 2.0,
        timeout: float = 60.0,
        enable_cache: bool = True,
    ):
        """
        Initialize GLM client.

        Args:
            api_key: GLM API key (defaults to GLM_API_KEY env var)
            model: Model to use (glm-4-flash or glm-4-plus)
            base_url: API base URL
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            max_retries: Maximum number of retries
            retry_delay: Initial retry delay in seconds
            retry_multiplier: Multiplier for exponential backoff
            timeout: Request timeout in seconds
            enable_cache: Enable response caching
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "GLM_API_KEY not found. "
                "Set it in .env file or pass as parameter."
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.timeout = timeout
        self.enable_cache = enable_cache

        # Statistics
        self.stats = GLMStats()

        # Cache
        self._cache: Dict[str, GLMResponse] = {}

        # HTTP client
        self._client = httpx.Client(timeout=timeout)

    def _make_request(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> GLMResponse:
        """
        Make API request with retry logic.

        Args:
            prompt: The prompt to send
            json_mode: Whether to request JSON response

        Returns:
            GLMResponse object

        Raises:
            GLMAPIError: If API request fails after retries
            GLMRateLimitError: If rate limit is hit
        """
        # Check cache
        if self.enable_cache:
            cache_key = f"{hash(prompt)}_{json_mode}"
            if cache_key in self._cache:
                self.stats.cache_hits += 1
                cached_response = self._cache[cache_key]
                return GLMResponse(
                    content=cached_response.content,
                    model=cached_response.model,
                    prompt_tokens=cached_response.prompt_tokens,
                    completion_tokens=cached_response.completion_tokens,
                    total_tokens=cached_response.total_tokens,
                    cached=True,
                )

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        # Add JSON mode if requested
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        # Retry loop
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                # Parse response
                data = response.json()
                message = data["choices"][0]["message"]
                content = message["content"]
                usage = data.get("usage", {})

                glm_response = GLMResponse(
                    content=content,
                    model=data["model"],
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    cached=False,
                )

                # Update stats
                self.stats.total_requests += 1
                self.stats.total_tokens += glm_response.total_tokens
                self.stats.prompt_tokens += glm_response.prompt_tokens
                self.stats.completion_tokens += glm_response.completion_tokens

                # Cache response
                if self.enable_cache:
                    self._cache[cache_key] = glm_response

                return glm_response

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (self.retry_multiplier ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        self.stats.failed_requests += 1
                        raise GLMRateLimitError(
                            f"Rate limit exceeded after {self.max_retries} attempts"
                        )
                else:
                    self.stats.failed_requests += 1
                    raise GLMAPIError(
                        f"API request failed: {e.response.status_code} - {e.response.text}"
                    )

            except httpx.RequestError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (self.retry_multiplier ** attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    self.stats.failed_requests += 1
                    raise GLMAPIError(f"Request failed after {self.max_retries} attempts: {e}")

        # Should not reach here
        if last_error:
            raise GLMAPIError(f"Request failed: {last_error}")

    def complete(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> str:
        """
        Complete a prompt.

        Args:
            prompt: The prompt to complete
            json_mode: Whether to request JSON response

        Returns:
            Completed text
        """
        response = self._make_request(prompt, json_mode=json_mode)
        return response.content

    def complete_json(
        self,
        prompt: str,
    ) -> Dict[str, Any]:
        """
        Complete a prompt and parse JSON response.

        Args:
            prompt: The prompt to complete

        Returns:
            Parsed JSON object

        Raises:
            GLMAPIError: If JSON parsing fails
        """
        response = self._make_request(prompt, json_mode=True)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            raise GLMAPIError(f"Failed to parse JSON response: {e}")

    def batch_complete(
        self,
        prompts: List[str],
        json_mode: bool = False,
    ) -> List[str]:
        """
        Complete multiple prompts in sequence.

        Note: This does not use concurrent requests to avoid overwhelming the API.
        For concurrent requests, use batch_complete_async.

        Args:
            prompts: List of prompts to complete
            json_mode: Whether to request JSON responses

        Returns:
            List of completed texts
        """
        results = []
        for prompt in prompts:
            result = self.complete(prompt, json_mode=json_mode)
            results.append(result)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_requests": self.stats.total_requests,
            "total_tokens": self.stats.total_tokens,
            "prompt_tokens": self.stats.prompt_tokens,
            "completion_tokens": self.stats.completion_tokens,
            "failed_requests": self.stats.failed_requests,
            "cache_hits": self.stats.cache_hits,
            "cache_size": len(self._cache),
        }

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._client.close()


def create_client(
    model: Literal["glm-4-flash", "glm-4-plus"] = "glm-4-flash",
    **kwargs
) -> GLMClient:
    """
    Convenience function to create a GLM client.

    Args:
        model: Model to use
        **kwargs: Additional arguments for GLMClient

    Returns:
        GLMClient instance
    """
    return GLMClient(model=model, **kwargs)


# Example usage
if __name__ == "__main__":
    # Test the client
    try:
        with create_client() as client:
            # Simple completion
            response = client.complete("Say 'Hello, GLM!' in one sentence.")
            print(f"Response: {response}")

            # JSON completion
            json_response = client.complete_json(
                'Return JSON: {"name": "test", "value": 123}'
            )
            print(f"JSON Response: {json_response}")

            # Statistics
            stats = client.get_stats()
            print(f"Stats: {stats}")

    except GLMClientError as e:
        print(f"Error: {e}")
