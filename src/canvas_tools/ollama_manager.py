import time
import docker
import ollama

from docker.errors import NotFound, APIError
from docker.types import DeviceRequest
from .config import get_config

class OllamaManager:

    def __init__(self):
        self.config = get_config()
        self.docker_client = docker.from_env()
        self.container_name = "canvas_tools_ollama"
        self.client = ollama.Client(base_url=self.config.ollama_base_url)

    def ensure_ollama_running(self, force_pull: bool = False):
        """
        Ensures the Ollama container is running.
        If not, starts it.
        
        Args:
            force_pull: If True, pulls the latest Ollama Docker image before starting.
        """

        # Only manage if we are pointing to localhost
        base_url = str(self.config.ollama_base_url)
        if "localhost" not in base_url and "127.0.0.1" not in base_url:
            print(f"Ollama URL is {self.config.ollama_base_url}, assuming external management.")
            return

        # Pull the image if requested
        if force_pull:

            print(f"Pulling latest Ollama image: {self.config.ollama_docker_image}...")

            try:
                self.docker_client.images.pull(self.config.ollama_docker_image)
                print("Image pulled successfully.")

            except APIError as e:
                print(f"Warning: Failed to pull image: {e}")

        # Check for existing container and remove it to ensure we use the latest config (GPU, etc.)
        try:
            container = self.docker_client.containers.get(self.container_name)
            print("Removing existing Ollama container to ensure correct configuration...")
            container.remove(force=True)

        except NotFound:
            pass

        print("Starting new Ollama container with GPU support...")

        # We need to bind the port. Assuming 11434 based on default.
        # Also mounting a volume for models is good practice so we don't re-download every time.
        self.docker_client.containers.run(
            self.config.ollama_docker_image,
            name=self.container_name,
            ports={'11434/tcp': 11434},
            volumes={'canvas_tools_ollama_data': {'bind': '/root/.ollama', 'mode': 'rw'}},
            detach=True,
            auto_remove=False,
            device_requests=[DeviceRequest(device_ids=["1"], capabilities=[['gpu']])]
        )

        self._wait_for_server()

    def _wait_for_server(self, timeout=60):
        """Wait for Ollama API to be responsive."""

        print("Waiting for Ollama server to be ready...")

        start_time = time.time()

        while time.time() - start_time < timeout:

            try:
                # Try to list models as a health check
                self.client.list()
                print("Ollama server is ready.")
                return

            except Exception:
                time.sleep(1)

        raise TimeoutError("Ollama server failed to start within timeout.")

    def ensure_model_pulled(self, model_name: str):
        """
        Checks if the model exists, pulls it if not.
        """

        # Clean model name (remove tag if needed for check, but list() returns names with tags)
        # ollama.list() returns a dictionary with 'models' key which is a list of dicts.

        try:
            response = self.client.list()
            existing_models = [m['name'] for m in response.get('models', [])]

            # Check if model is present (exact match or match with :latest implied)
            if model_name in existing_models:
                return

            # Also handle the case where model_name has :latest but list has it, or vice versa
            if model_name + ":latest" in existing_models:
                return

            print(f"Pulling model {model_name} (this may take a while)...")

            # Stream the pull progress
            current_digest = None

            for progress in self.client.pull(model_name, stream=True):

                # Simple progress indication
                if 'status' in progress:
                    print(f"\r{progress['status']}", end="", flush=True)

            print("\nModel pulled successfully.")

        except Exception as e:
            print(f"Error checking/pulling model: {e}")
            raise
