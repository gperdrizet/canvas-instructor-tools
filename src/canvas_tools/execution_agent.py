#import os
from pathlib import Path
#from typing import List
from .llm_client import LLMClient
from .config import get_config

class ExecutionAgent:

    def __init__(self):

        self.client = LLMClient()
        self.config = get_config()

    def generate_execution_script(self, directory: Path) -> str:
        """
        Analyzes files in the directory and generates a bash script to run the submission.
        """
    
        files = [f.name for f in directory.iterdir() if f.is_file()]
        file_list_str = "\n".join(files)

        # We can optionally read the contents of requirements.txt or main files if needed,
        # but for now let's just give the file list to the model.

        prompt = f"""
You are an expert DevOps and Python engineer. You need to create a bash script to execute a student's submission.
The submission is located in the current directory.
The available files are:
{file_list_str}

The environment is a Docker container based on {self.config.docker_image} (likely Ubuntu/Debian based with Python installed).
You have root access.

Your goal is to:
1. Install any necessary dependencies (check for requirements.txt, Pipfile, etc.). If you see imports in python files that are not standard, try to install them.
2. Run the main entry point of the application. Look for main.py, app.py, or similar. If it's a Jupyter notebook (.ipynb), convert it to python and run it, or run it using nbconvert.
3. Ensure all output is printed to stdout/stderr.

Return ONLY the bash script content. Do not use markdown code blocks. Start with #!/bin/bash.
If you cannot determine how to run it, print an error message in the script and exit with status 1.
"""

        # Log the prompt and file list
        log_path = directory / "execution_agent.log"

        with open(log_path, "w") as log_file:

            log_file.write(f"--- Processing Directory: {directory} ---\n")
            log_file.write(f"Files found: {files}\n\n")
            log_file.write("--- Prompt Sent to Model ---\n")
            log_file.write(prompt + "\n\n")

        script_content = self.client.generate_text(
            prompt=prompt,
            model=self.config.execution_model,
            provider=self.config.execution_provider,
            system_prompt="You are a helpful coding assistant that generates bash scripts."
        )

        # Log the response
        with open(log_path, "a") as log_file:

            log_file.write("--- Model Response (Generated Script) ---\n")
            log_file.write(script_content + "\n")

        # Clean up markdown code blocks if the model ignores instructions
        script_content = script_content.replace("```bash", "").replace("```", "").strip()

        return script_content
