"""
LLM Handler for VibeTerminal
Manages communication with local Ollama and provides test data fallback
"""

import json
import requests
from config import CONFIG


class LLMHandler:
    """Handles Ollama communication with fallback to test data"""

    # def __init__(self, logger=None):
    def __init__(self, logger):
        self.enabled = CONFIG["llm_enabled"]
        self.model = CONFIG["llm_model"]
        self.use_test_data = CONFIG["use_test_data"]
        self.url = CONFIG.get(
            "ollama_url",
            "http://localhost:11434/api/chat"
        )

        self.logger = logger

        self._log(
            f"LLMHandler initialized | "
            f"enabled={self.enabled} | "
            f"model={self.model} | "
            f"url={self.url}"
        )

    def _log(self, message, level="info"):
    # def _log(self, message, level="debug"):
        """Internal logger helper"""
        if self.logger:
            getattr(self.logger, level)(message)
        else:
            print(f"[{level.upper()}] {message}")

    def get_response(
        self,
        prompt,
        system_prompt=None,
        max_tokens=None,
        use_test=None,
    ):
        """
        Get complete response from Ollama
        """

        self._log("get_response() called")

        should_use_test = (
            use_test
            if use_test is not None
            else not self.enabled
        )

        if should_use_test and self.use_test_data:
            self._log("Using test response")
            return self._get_test_response(prompt)

        if not self.enabled:
            self._log("LLM is disabled", "warning")
            return None

        try:
            messages = []

            if system_prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": system_prompt,
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }

            self._log("Sending request to Ollama")
            # self.logger.info("Sending request to Ollama")

            response = requests.post(
                self.url,
                json=payload,
                timeout=300,
            )

            response.raise_for_status()

            data = response.json()

            content = data["message"]["content"]

            self._log(
                # f"Received response ({len(content)} chars)"
                f"Received response ({(content)})"
            )

            return content

        except Exception as e:
            self._log(f"LLM Error: {e}", "error")

            if self.use_test_data:
                self._log(
                    "Falling back to test response",
                    "warning",
                )
                return self._get_test_response(prompt)

            return None

    def get_stream_response(
        self,
        prompt,
        system_prompt=None,
        use_test=None,
    ):
        """
        Stream response from Ollama
        Yields text chunks as they arrive.
        """

        self._log("get_stream_response() called")

        should_use_test = (
            use_test
            if use_test is not None
            else not self.enabled
        )

        if should_use_test and self.use_test_data:
            self._log("Using test stream response")
            yield self._get_test_response(prompt)
            return

        if not self.enabled:
            self._log("LLM is disabled", "warning")
            return

        try:
            messages = []

            if system_prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": system_prompt,
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
            }

            self._log("Starting Ollama stream")

            response = requests.post(
                self.url,
                json=payload,
                stream=True,
                timeout=300,
            )

            response.raise_for_status()

            result = ""

            for line in response.iter_lines():

                if not line:
                    continue


                data = json.loads(
                    line.decode("utf-8")
                )


                if "message" in data:
                    content = data["message"].get(
                        "content",
                        "",
                    )

                    if content:
                        self._log(f"chunks - {content} ")
                        result += content
                        yield content


                if data.get("done", False):
                    # self._log(f"payload: {payload}")
                    self._log(
                        "payload:\n" +
                        json.dumps(payload, indent=4)
                    )
                    self._log(f"response: {result}")
                    break

        except Exception as e:
            self._log(
                f"LLM Stream Error: {e}",
                "error",
            )

            if self.use_test_data:
                self._log(
                    "Falling back to test stream response",
                    "warning",
                )
                yield self._get_test_response(prompt)

    def _get_test_response(self, prompt):
        """Fallback response"""
        return (
            "Test response mode: "
            "No LLM available. "
            "Using predefined data."
        )


class MockLLMHandler(LLMHandler):
    """Mock LLM handler"""

    def __init__(self, logger=None):
        self.enabled = False
        self.use_test_data = True
        self.logger = logger

    def _get_test_response(self, prompt):
        return (
            "[Mock Response] "
            "This is a test response "
            "without LLM connectivity."
        )
