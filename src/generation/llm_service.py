"""LLM service for resume generation using OpenAI or Anthropic."""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMService:
    """Service for interacting with LLM APIs."""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize LLM service.

        Args:
            provider: LLM provider to use
            model: Model name (defaults based on provider)
            api_key: API key (reads from env if not provided)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set default models
        if model is None:
            if provider == LLMProvider.OPENAI:
                self.model = "gpt-3.5-turbo"
            elif provider == LLMProvider.ANTHROPIC:
                self.model = "claude-3-5-sonnet-20241022"
        else:
            self.model = model

        # Get API key
        if api_key:
            self.api_key = api_key
        else:
            if provider == LLMProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            print(f"⚠️  Warning: No API key found for {provider.value}")
            print(f"   Set {provider.value.upper()}_API_KEY in .env file")

        # Initialize client
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if not self.api_key:
            return

        try:
            if self.provider == LLMProvider.OPENAI:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(f"✓ OpenAI client initialized (model: {self.model})")

            elif self.provider == LLMProvider.ANTHROPIC:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                print(f"✓ Anthropic client initialized (model: {self.model})")

        except ImportError as e:
            print(f"⚠️  Error: {e}")
            print(f"   Install required package: pip install {self.provider.value}")
        except Exception as e:
            print(f"⚠️  Error initializing {self.provider.value} client: {e}")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate text using the LLM.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system_message: System message (for supported models)

        Returns:
            Generated text response
        """
        if not self.client:
            raise ValueError("LLM client not initialized. Please set API key.")

        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        try:
            if self.provider == LLMProvider.OPENAI:
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tok
                )
                return response.choices[0].message.content.strip()

            elif self.provider == LLMProvider.ANTHROPIC:
                system = system_message if system_message else "You are a helpful assistant."

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tok,
                    temperature=temp,
                    system=system,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()

        except Exception as e:
            print(f"Error generating response: {e}")
            raise

    def generate_batch(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """
        Generate responses for multiple prompts.

        Args:
            prompts: List of prompts
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            List of generated responses
        """
        responses = []
        for i, prompt in enumerate(prompts):
            print(f"  Generating {i+1}/{len(prompts)}...", end="\r")
            response = self.generate(prompt, temperature, max_tokens)
            responses.append(response)

        print()  # New line after progress
        return responses

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for API call (rough estimate).

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Rough pricing as of 2024 (check current pricing)
        if self.provider == LLMProvider.OPENAI:
            if "gpt-4" in self.model:
                input_cost = input_tokens * 0.03 / 1000  # $0.03 per 1K tokens
                output_cost = output_tokens * 0.06 / 1000  # $0.06 per 1K tokens
            else:  # gpt-3.5-turbo
                input_cost = input_tokens * 0.001 / 1000
                output_cost = output_tokens * 0.002 / 1000

        elif self.provider == LLMProvider.ANTHROPIC:
            if "opus" in self.model:
                input_cost = input_tokens * 0.015 / 1000
                output_cost = output_tokens * 0.075 / 1000
            elif "sonnet" in self.model:
                input_cost = input_tokens * 0.003 / 1000
                output_cost = output_tokens * 0.015 / 1000
            else:  # haiku
                input_cost = input_tokens * 0.00025 / 1000
                output_cost = output_tokens * 0.00125 / 1000

        else:
            return 0.0

        return input_cost + output_cost


def get_default_llm_service() -> LLMService:
    """
    Get default LLM service based on available API keys.

    Returns:
        Configured LLM service
    """
    # Check which API keys are available (exclude placeholder values)
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # Check if keys are valid (not placeholders)
    openai_valid = openai_key and openai_key != "your_openai_api_key_here" and openai_key.startswith("sk-")
    anthropic_valid = anthropic_key and anthropic_key != "your_anthropic_api_key_here" and anthropic_key.startswith("sk-ant-")

    if anthropic_valid:
        print("Using Anthropic Claude for generation")
        return LLMService(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=800
        )
    elif openai_valid:
        print("Using OpenAI GPT for generation")
        return LLMService(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=800
        )
    else:
        print("⚠️  No valid API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
        return LLMService(provider=LLMProvider.OPENAI)  # Returns uninitialized service
