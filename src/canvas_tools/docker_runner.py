import docker
import os
from pathlib import Path
from typing import Tuple
from .config import get_config

class DockerRunner:
    def __init__(self):
        self.config = get_config()
        self.client = docker.from_env()

    def run_script(self, host_dir: Path, script_name: str = "run_submission.sh", timeout: int = 300) -> Tuple[str, str]:
        """
        Runs a shell script inside a docker container with the host_dir mounted.
        Returns (stdout, stderr).
        """
        abs_host_dir = host_dir.resolve()
        
        # Ensure the script exists
        if not (abs_host_dir / script_name).exists():
            return "", f"Script {script_name} not found in {abs_host_dir}"

        # Make sure the script is executable
        os.chmod(abs_host_dir / script_name, 0o755)

        try:
            # We mount the student directory to /submission
            # We set the working directory to /submission
            container = self.client.containers.run(
                image=self.config.docker_image,
                command=["/bin/bash", f"./{script_name}"],
                volumes={str(abs_host_dir): {'bind': '/submission', 'mode': 'rw'}},
                working_dir="/submission",
                detach=True,
                # user='root', # Depending on image, might need root to install packages. 
                             # Jupyter images often run as 'jovyan' but have sudo access or allow pip.
                             # Let's try default user first, but if we need to install system deps, we might need root.
                             # For safety, running as non-root is better, but for student code that might need deps, 
                             # we might need flexibility.
                user='root' # Using root to allow apt-get/pip install if needed by the agent generated script
            )

            try:
                result = container.wait(timeout=timeout)
                logs = container.logs(stdout=True, stderr=True)
                
                # logs returns bytes, need to decode. 
                # It might be mixed stdout/stderr depending on how we call it, 
                # but container.logs() returns combined if not specified, or we can separate.
                # Actually docker-py logs() returns a single byte string if stream=False.
                # To get separate, we might need a different approach or just accept combined.
                # Let's try to get them.
                
                # Re-fetching logs separately
                stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
                stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
                
                exit_code = result.get('StatusCode', 0)
                if exit_code != 0:
                    stderr += f"\n\nProcess exited with code {exit_code}"

                return stdout, stderr

            except Exception as e:
                container.kill()
                return "", f"Execution timed out or failed: {str(e)}"
            finally:
                container.remove()

        except Exception as e:
            return "", f"Docker error: {str(e)}"
