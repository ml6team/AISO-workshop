"""
Google ADK Agent Runner using API Server.
This module provides a function to run the ADK agent via HTTP requests to the API server.
"""
import atexit
import os
import requests
import subprocess
import time
import uuid


class ADKAgentRunner:
    """
    Client for interacting with ADK agent via FastAPI server.
    Automatically starts and manages the API server lifecycle.
    """

    def __init__(self, base_url: str = "http://localhost:8000", agent_name: str = "my_agent", user_id: str = "dev_user"):
        self.base_url = base_url
        self.agent_name = agent_name
        self.user_id = user_id  # User ID for sessions (use same as web UI to see eval chats there)
        self.server_process = None
        self._session_counter = 0
        self._we_started_server = False  # Track if we started the server

    def _is_server_running(self) -> bool:
        """Check if an ADK API server is already running."""
        try:
            response = requests.get(f"{self.base_url}/list-apps", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def start_server(self):
        """Start the ADK API server in the background if not already running."""
        # First check if a server is already running
        if self._is_server_running():
            print(f"✓ Using existing ADK API server at {self.base_url}")
            return

        if self.server_process is not None:
            print("Server process already started by us")
            return

        print("Starting ADK API server...")
        # Start the server in the background
        self.server_process = subprocess.Popen(
            ["adk", "api_server", "--host", "127.0.0.1", "--port", "8000", "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )

        self._we_started_server = True

        # Register cleanup on exit (only if we started it)
        atexit.register(self.stop_server)

        # Wait for server to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/list-apps", timeout=1)
                if response.status_code == 200:
                    print(f"✓ ADK API server started successfully on {self.base_url}")
                    return
            except requests.exceptions.RequestException:
                time.sleep(1)

        raise RuntimeError("Failed to start ADK API server")

    def stop_server(self):
        """Stop the ADK API server (only if we started it)."""
        if self.server_process is not None and self._we_started_server:
            print("\nStopping ADK API server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
            self._we_started_server = False

    def run_agent(self, question: str, file_paths: list[str] | None = None) -> str:
        """
        Run agent via REST API.

        Args:
            question: The question to answer
            file_paths: Optional list of file paths (not yet fully implemented)

        Returns:
            The agent's response
        """
        # Ensure server is running (checks for existing server first)
        if self.server_process is None and not self._is_server_running():
            self.start_server()

        # Generate unique session ID using UUID to avoid conflicts with existing sessions
        # Using configured user_id (default: "dev_user")
        # To see evaluation chats in web UI, use the same user_id as the web UI
        # To find web UI's user_id: Open browser DevTools > Network tab > Check /run_sse request > Look for user_id in payload
        session_id = f"eval_{uuid.uuid4().hex[:12]}"

        # Create session
        try:
            session_response = requests.post(
                f"{self.base_url}/apps/{self.agent_name}/users/{self.user_id}/sessions/{session_id}",
                json={"state": {}},
                timeout=10
            )
            session_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to create session for agent '{self.agent_name}': {e}") from e

        # Prepare message
        message_parts = [{"text": question}]

        # Add file paths to the question
        if file_paths:
            # For now, just mention the files in the text
            file_info = f"\n\nNote: The following files are relevant: {', '.join(file_paths)}"
            message_parts[0]["text"] += file_info

        # Send message using /run endpoint
        try:
            response = requests.post(
                f"{self.base_url}/run",
                json={
                    "app_name": self.agent_name,
                    "user_id": self.user_id,
                    "session_id": session_id,
                    "new_message": {
                        "role": "user",
                        "parts": message_parts
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            events = response.json()

            # Extract text from response events
            response_text = ""
            for event in events:
                if "content" in event and event["content"]:
                    parts = event["content"].get("parts", [])
                    for part in parts:
                        if "text" in part:
                            response_text += part["text"]

            return response_text.strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to run agent on question: {e}") from e


# Global runner instance
_runner = None


def run_agent(question: str, file_paths: list[str] | None = None, user_id: str = "dev_user") -> str:
    """
    Run the Google ADK agent on a given question.
    This function manages the API server lifecycle automatically.

    Args:
        question: The question to answer
        file_paths: Optional list of file paths that may be needed to answer the question
        user_id: User ID for the session (default: "dev_user"). Use same as web UI to see eval chats there.

    Returns:
        The agent's response as a string
    """
    global _runner

    if _runner is None:
        _runner = ADKAgentRunner(user_id=user_id)
        _runner.start_server()

    return _runner.run_agent(question, file_paths)
