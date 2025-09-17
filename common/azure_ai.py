"""
Azure AI Foundry client wrapper for GPT-4.1.

This module provides a framework-free client for Azure OpenAI services
with support for JSON and text responses, automatic retries, and proper error handling.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional, cast

import httpx
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Azure AI Projects SDK imports for assistant functionality
try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from azure.ai.agents.models import ListSortOrder
    AZURE_AI_SDK_AVAILABLE = True
except ImportError:
    AZURE_AI_SDK_AVAILABLE = False
    logger.warning("Azure AI Projects SDK not available. Assistant functionality will use HTTP fallback.")

# Load environment variables
load_dotenv()


class AzureAIError(Exception):
    """Base exception for Azure AI client errors."""
    pass


class AzureAITimeoutError(AzureAIError):
    """Raised when Azure AI request times out."""
    pass


class AzureAIRateLimitError(AzureAIError):
    """Raised when Azure AI rate limit is exceeded."""
    pass


class JSONParseError(AzureAIError):
    """Raised when response cannot be parsed as JSON."""
    pass


def ensure_json(response_text: str) -> Dict[str, Any]:
    """
    Extract and validate JSON from response text.
    
    Strips markdown code fences and validates JSON format.
    
    Args:
        response_text: Raw response text that may contain JSON
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        JSONParseError: If JSON cannot be extracted or parsed
    """
    # Strip markdown code fences if present
    cleaned_text = response_text.strip()
    
    # Remove ```json and ``` markers
    json_pattern = r"```(?:json)?\s*(.*?)\s*```"
    match = re.search(json_pattern, cleaned_text, re.DOTALL)
    if match:
        cleaned_text = match.group(1).strip()
    
    # Try to parse JSON
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise JSONParseError(f"Failed to parse JSON from response: {e}\nResponse text: {cleaned_text}")


class AzureAIClient:
    """
    Azure AI Foundry client for both direct chat completions and assistant interactions.
    
    Supports both traditional OpenAI chat completions and Azure AI Foundry assistants.
    """
    
    def __init__(self, 
                 endpoint: Optional[str] = None,
                 api_key: Optional[str] = None, 
                 deployment: Optional[str] = None,
                 api_version: Optional[str] = None,
                 assistant_id: Optional[str] = None,
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        Initialize Azure AI client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL (defaults to AZURE_OPENAI_ENDPOINT env var)
            api_key: Azure OpenAI API key (defaults to AZURE_OPENAI_API_KEY env var)
            deployment: Azure OpenAI deployment name (defaults to AZURE_OPENAI_DEPLOYMENT_NAME env var)
            api_version: Azure OpenAI API version (defaults to AZURE_API_VERSION env var)
            assistant_id: Azure AI Foundry assistant ID (defaults to AZURE_ASSISTANT_ID env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries in seconds
        """
        # Get configuration from parameters or environment variables
        endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = api_version or os.getenv("AZURE_API_VERSION", "2024-02-01")
        assistant_id = assistant_id or os.getenv("AZURE_ASSISTANT_ID")
        
        # Validate required configuration
        missing_vars = []
        if not endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not api_key:
            missing_vars.append("AZURE_OPENAI_API_KEY")  
        if not deployment:
            missing_vars.append("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if missing_vars:
            missing_list = ", ".join(missing_vars)
            raise AzureAIError(
                f"Missing required Azure AI configuration. Please set the following environment variables: {missing_list}\n\n"
                f"Required setup:\n"
                f"1. Copy .env.example to .env\n"
                f"2. Fill in your Azure AI Foundry credentials:\n"
                f"   - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL\n"
                f"   - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key\n"
                f"   - AZURE_OPENAI_DEPLOYMENT_NAME: Your GPT model deployment name\n"
                f"   - AZURE_API_VERSION: API version (optional, defaults to 2024-02-01)\n"
                f"   - AZURE_ASSISTANT_ID: Assistant ID (optional, for Azure AI Foundry assistants)\n\n"
                f"Get these values from: Azure AI Foundry -> Projects -> Your Project -> Settings"
            )
        
        # Store validated configuration with type assertion
        self.endpoint = cast(str, endpoint)
        self.api_key = cast(str, api_key)
        self.deployment = cast(str, deployment)
        self.api_version = cast(str, api_version)
        self.assistant_id = assistant_id
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Build the API URL (safe after validation above)
        self.api_url = (
            f"{cast(str, self.endpoint).rstrip('/')}/openai/deployments/{self.deployment}"
            f"/chat/completions?api-version={self.api_version}"
        )
        
        # Create HTTP client with timeout
        self.client = httpx.Client(timeout=httpx.Timeout(timeout))
        
        # Initialize Azure AI Projects client for assistant functionality
        self.ai_project_client = None
        if self.assistant_id and AZURE_AI_SDK_AVAILABLE:
            try:
                self.ai_project_client = AIProjectClient(
                    credential=DefaultAzureCredential(),
                    endpoint=self.endpoint
                )
                logger.debug("Azure AI Projects client initialized for assistant functionality")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure AI Projects client: {e}. Will use HTTP fallback.")
                self.ai_project_client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Content-Type": "application/json",
            "api-key": cast(str, self.api_key)
        }
    
    def _make_request(self, messages: list, temperature: float = 0.1) -> str:
        """
        Make a request to Azure OpenAI API with retries.
        
        Args:
            messages: List of message objects for the chat completion
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Response content as string
            
        Raises:
            AzureAIError: For various API errors
            AzureAITimeoutError: For timeout errors
            AzureAIRateLimitError: For rate limiting errors
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        raise AzureAIError("No choices in response")
                
                elif response.status_code == 429:
                    if attempt < self.max_retries:
                        retry_after = response.headers.get("retry-after", self.retry_delay)
                        time.sleep(float(retry_after))
                        continue
                    else:
                        raise AzureAIRateLimitError("Rate limit exceeded")
                
                else:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise AzureAIError(error_msg)
                    
            except httpx.TimeoutException as e:
                last_exception = AzureAITimeoutError(f"Request timed out after {self.timeout}s")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
            except httpx.RequestError as e:
                last_exception = AzureAIError(f"Request error: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise AzureAIError("All retry attempts failed")
    
    def llm_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text completion using Azure OpenAI.
        
        Args:
            system_prompt: System message to set context and behavior
            user_prompt: User message with the actual request
            
        Returns:
            Generated text response
            
        Raises:
            AzureAIError: For various API errors
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages)
    
    def llm_json(self, system_prompt: str, user_prompt: str, response_schema_hint: str) -> Dict[str, Any]:
        """
        Generate JSON completion using Azure OpenAI.
        
        Args:
            system_prompt: System message to set context and behavior
            user_prompt: User message with the actual request
            response_schema_hint: Hint about expected JSON schema structure
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            AzureAIError: For various API errors
            JSONParseError: If response cannot be parsed as JSON
        """
        # Enhance system prompt to ensure JSON response
        enhanced_system_prompt = f"""{system_prompt}

IMPORTANT: You must respond with valid JSON only. Do not include any explanations, 
markdown formatting, or text outside the JSON structure.

Expected response schema hint: {response_schema_hint}

Respond with valid JSON that matches the expected structure."""
        
        messages = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_text = self._make_request(messages, temperature=0.0)
        return ensure_json(response_text)
    
    def llm_text_with_assistant(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text completion using Azure AI Assistant.
        
        Args:
            user_prompt: User message with the actual request
            system_prompt: Optional system prompt (will be added as additional instructions)
            
        Returns:
            Generated text response
            
        Raises:
            AzureAIError: For various API errors
        """
        if not self.assistant_id:
            raise AzureAIError("Assistant ID not configured. Use llm_text() instead or set AZURE_ASSISTANT_ID.")
        
        try:
            # Use Azure AI Projects SDK if available
            if self.ai_project_client:
                return self._run_assistant_with_sdk(user_prompt, system_prompt)
            else:
                # Fallback to HTTP approach
                return self._run_assistant_with_http(user_prompt, system_prompt)
            
        except Exception as e:
            logger.error(f"Assistant request failed: {str(e)}")
            raise AzureAIError(f"Assistant request failed: {str(e)}")
    
    def _run_assistant_with_sdk(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """Run assistant using Azure AI Projects SDK."""
        if not self.ai_project_client:
            raise AzureAIError("AI Project client not initialized")
        
        # Create thread
        thread = self.ai_project_client.agents.threads.create()
        
        # Create message
        message = self.ai_project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )
        
        # Create and process run
        run = self.ai_project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=cast(str, self.assistant_id),
            additional_instructions=system_prompt
        )
        
        if run.status == "failed":
            raise AzureAIError(f"Assistant run failed: {run.last_error}")
        
        # Get messages
        messages = self.ai_project_client.agents.messages.list(
            thread_id=thread.id, 
            order=ListSortOrder.ASCENDING if AZURE_AI_SDK_AVAILABLE else None
        )
        
        # Find the latest assistant response
        for message in reversed(list(messages)):
            if message.role == "assistant" and message.text_messages:
                return message.text_messages[-1].text.value
        
        raise AzureAIError("No assistant response found")
    
    def _run_assistant_with_http(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """Fallback HTTP implementation for assistant functionality."""
        # Create a thread
        thread_id = self._create_thread()
        
        # Add system prompt as additional instructions if provided
        instructions = system_prompt if system_prompt else None
        
        # Add user message
        self._add_message(thread_id, user_prompt)
        
        # Run the assistant
        response = self._run_assistant(thread_id, instructions)
        
        return response
    
    def llm_text_with_specific_assistant(self, user_prompt: str, assistant_id: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text completion using a specific Azure AI Assistant by ID.
        
        Args:
            user_prompt: User message with the actual request
            assistant_id: Specific assistant ID to use (overrides default)
            system_prompt: Optional system prompt (will be added as additional instructions)
            
        Returns:
            Generated text response
            
        Raises:
            AzureAIError: For various API errors
        """
        if not assistant_id:
            raise AzureAIError("Assistant ID is required for this method.")
        
        try:
            # Use Azure AI Projects SDK if available
            if self.ai_project_client:
                return self._run_specific_assistant_with_sdk(user_prompt, assistant_id, system_prompt)
            else:
                raise AzureAIError("Azure AI Projects SDK not available for specific assistant calls")
            
        except Exception as e:
            logger.error(f"Specific assistant request failed: {str(e)}")
            raise AzureAIError(f"Specific assistant request failed: {str(e)}")
    
    def _run_specific_assistant_with_sdk(self, user_prompt: str, assistant_id: str, system_prompt: Optional[str] = None) -> str:
        """Run a specific assistant using Azure AI Projects SDK."""
        if not self.ai_project_client:
            raise AzureAIError("AI Project client not initialized")
        
        # Create thread
        thread = self.ai_project_client.agents.threads.create()
        
        # Create message
        message = self.ai_project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )
        
        # Create and process run with specific assistant
        run = self.ai_project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=assistant_id,
            additional_instructions=system_prompt
        )
        
        if run.status == "failed":
            raise AzureAIError(f"Assistant run failed: {run.last_error}")
        
        # Get messages
        messages = self.ai_project_client.agents.messages.list(
            thread_id=thread.id, 
            order=ListSortOrder.ASCENDING if AZURE_AI_SDK_AVAILABLE else None
        )
        
        # Find the latest assistant response
        for message in reversed(list(messages)):
            if message.role == "assistant" and message.text_messages:
                return message.text_messages[-1].text.value
        
        raise AzureAIError("No assistant response found")
    
    def _create_thread(self) -> str:
        """Create a new conversation thread."""
        url = f"{cast(str, self.endpoint).rstrip('/')}/openai/threads?api-version={self.api_version}"
        
        response = self.client.post(
            url,
            headers=self._get_headers(),
            json={}
        )
        
        if response.status_code != 200:
            raise AzureAIError(f"Thread creation failed: {response.status_code} - {response.text}")
        
        return response.json()["id"]
    
    def _add_message(self, thread_id: str, content: str):
        """Add a message to a thread."""
        url = f"{cast(str, self.endpoint).rstrip('/')}/openai/threads/{thread_id}/messages?api-version={self.api_version}"
        
        response = self.client.post(
            url,
            headers=self._get_headers(),
            json={
                "role": "user",
                "content": content
            }
        )
        
        if response.status_code != 200:
            raise AzureAIError(f"Message creation failed: {response.status_code} - {response.text}")
    
    def _run_assistant(self, thread_id: str, additional_instructions: Optional[str] = None) -> str:
        """Run the assistant on a thread and return the response."""
        # Start the run
        run_url = f"{cast(str, self.endpoint).rstrip('/')}/openai/threads/{thread_id}/runs?api-version={self.api_version}"
        
        run_data = {
            "assistant_id": self.assistant_id
        }
        
        if additional_instructions:
            run_data["additional_instructions"] = additional_instructions
        
        response = self.client.post(
            run_url,
            headers=self._get_headers(),
            json=run_data
        )
        
        if response.status_code != 200:
            raise AzureAIError(f"Run creation failed: {response.status_code} - {response.text}")
        
        run_id = response.json()["id"]
        
        # Poll for completion
        status_url = f"{cast(str, self.endpoint).rstrip('/')}/openai/threads/{thread_id}/runs/{run_id}?api-version={self.api_version}"
        max_attempts = 30  # 30 seconds timeout
        
        for _ in range(max_attempts):
            status_response = self.client.get(status_url, headers=self._get_headers())
            
            if status_response.status_code != 200:
                raise AzureAIError(f"Run status check failed: {status_response.status_code}")
            
            run_status = status_response.json()["status"]
            
            if run_status == "completed":
                # Get the messages
                messages_url = f"{cast(str, self.endpoint).rstrip('/')}/openai/threads/{thread_id}/messages?api-version={self.api_version}"
                messages_response = self.client.get(messages_url, headers=self._get_headers())
                
                if messages_response.status_code != 200:
                    raise AzureAIError(f"Messages retrieval failed: {messages_response.status_code}")
                
                messages = messages_response.json()["data"]
                # Get the latest assistant message
                for message in messages:
                    if message["role"] == "assistant":
                        return message["content"][0]["text"]["value"]
                
                raise AzureAIError("No assistant response found")
            
            elif run_status in ["failed", "cancelled", "expired"]:
                raise AzureAIError(f"Assistant run {run_status}")
            
            # Wait before next check
            import time
            time.sleep(1)
        
        raise AzureAIError("Assistant run timed out")
    
    def __del__(self):
        """Clean up HTTP client on deletion."""
        if hasattr(self, 'client'):
            self.client.close()


# Global client instance (lazy-initialized)
_client: Optional[AzureAIClient] = None


def get_client() -> AzureAIClient:
    """
    Get or create global Azure AI client instance.
    
    Returns:
        AzureAIClient instance
    """
    global _client
    if _client is None:
        _client = AzureAIClient()
    return _client


def llm_text(system_prompt: str, user_prompt: str) -> str:
    """
    Generate text completion using Azure OpenAI (module-level convenience function).
    
    Args:
        system_prompt: System message to set context and behavior
        user_prompt: User message with the actual request
        
    Returns:
        Generated text response
        
    Raises:
        AzureAIError: For various API errors
    """
    return get_client().llm_text(system_prompt, user_prompt)


def llm_json(system_prompt: str, user_prompt: str, response_schema_hint: str) -> Dict[str, Any]:
    """
    Generate JSON completion using Azure OpenAI (module-level convenience function).
    
    Args:
        system_prompt: System message to set context and behavior
        user_prompt: User message with the actual request
        response_schema_hint: Hint about expected JSON schema structure
        
    Returns:
        Parsed JSON response as dictionary
        
    Raises:
        AzureAIError: For various API errors
        JSONParseError: If response cannot be parsed as JSON
    """
    return get_client().llm_json(system_prompt, user_prompt, response_schema_hint)