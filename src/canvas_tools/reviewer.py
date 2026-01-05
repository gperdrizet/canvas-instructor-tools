import os
from pathlib import Path
from typing import List, Dict
from .llm_client import LLMClient
from .config import get_config

class Reviewer:
    def __init__(self):
        self.client = LLMClient()
        self.config = get_config()

    def review_submission(self, directory: Path, stdout: str, stderr: str) -> str:
        """
        Generates a review for a single submission.
        """
        files = [f for f in directory.iterdir() if f.is_file() and f.name != "run_submission.sh" and not f.name.endswith(".md")]
        
        code_content = ""
        for f in files:
            # Limit file size to avoid context overflow
            if f.stat().st_size < 20000: 
                try:
                    content = f.read_text(errors='replace')
                    code_content += f"\n--- File: {f.name} ---\n{content}\n"
                except Exception:
                    pass

        prompt = f"""
You are an expert Computer Science instructor. Please review the following student submission.

### Execution Output
STDOUT:
{stdout}

STDERR:
{stderr}

### Source Code
{code_content}

### Instructions
1. Analyze the code quality, style, and correctness.
2. Check if the execution output indicates success or failure.
3. Provide constructive feedback.
4. Assign a tentative grade (0-100) based on functionality and code quality.

Format the output as Markdown.
"""
        
        # Determine provider based on config. If reviewer_model is claude, use anthropic.
        provider = "anthropic" if "claude" in self.config.reviewer_model.lower() else "ollama"
        
        review = self.client.generate_text(
            prompt=prompt,
            model=self.config.reviewer_model,
            provider=provider,
            system_prompt="You are a helpful and strict teaching assistant."
        )
        
        return review

    def generate_metareview(self, reviews: List[str]) -> str:
        """
        Generates a summary of all reviews.
        """
        # If reviews are too long, we might need to summarize chunks.
        # For now, let's assume we can fit a summary of reviews.
        
        combined_reviews = "\n\n".join([f"--- Review {i+1} ---\n{r[:1000]}..." for i, r in enumerate(reviews)]) # Truncate for context
        
        prompt = f"""
You are the Head Instructor. Here are summaries of the reviews generated for the class submissions.

{combined_reviews}

Please generate a "Meta-Review" for the whole class that:
1. Identifies common errors or misconceptions.
2. Highlights areas where the class performed well.
3. Suggests topics to review in the next lecture.
4. Provides an overall assessment of the cohort's performance.

Format as Markdown.
"""
        
        provider = "anthropic" if "claude" in self.config.reviewer_model.lower() else "ollama"

        metareview = self.client.generate_text(
            prompt=prompt,
            model=self.config.reviewer_model,
            provider=provider,
            system_prompt="You are an educational data analyst."
        )
        
        return metareview
