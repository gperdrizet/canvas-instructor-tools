#import os
from pathlib import Path
from typing import List #, Dict
from .llm_client import LLMClient
from .config import get_config

class Reviewer:

    def __init__(self):
        self.client = LLMClient()
        self.config = get_config()

    def review_submission(self, directory: Path, stdout: str, stderr: str) -> str:
        """
        Generates a review for a single submission using a multi-step process.
        1. Generate a review plan (select files).
        2. Analyze code quality of selected files.
        3. Incorporate execution output for final grade.
        """
        all_files = [f for f in directory.iterdir() if f.is_file() and f.name != "run_submission.sh" and not f.name.endswith(".md")]
        file_list_str = "\n".join([f.name for f in all_files])

        # Step 1: Generate Review Plan
        plan_prompt = f"""
You are an expert Computer Science instructor. You need to review a student's submission.
The submission contains the following files:
{file_list_str}

Which of these files are source code or configuration files that are critical for understanding the student's implementation?
Ignore data files (csv, json, txt), images, compiled binaries, or system files unless they seem critical.

Return ONLY a list of filenames to review, one per line. Do not include any other text.
"""
        try:
            plan_response = self.client.generate_text(
                prompt=plan_prompt,
                model=self.config.reviewer_model,
                provider=self.config.reviewer_provider,
                system_prompt="You are a helpful teaching assistant."
            )
            # Parse the plan
            files_to_review = [line.strip() for line in plan_response.splitlines() if line.strip()]

            # Filter valid files
            selected_files = [f for f in all_files if f.name in files_to_review]

            # Fallback if model returns nothing or garbage
            if not selected_files:
                print(f"Warning: Review plan returned no valid files. Falling back to all files. Plan: {plan_response}")
                selected_files = all_files

        except Exception as e:
            print(f"Error generating review plan: {e}. Falling back to all files.")
            selected_files = all_files

        code_content = ""

        # We still need some limit to avoid hard API errors, but we can be generous if we split.
        # 200k tokens is roughly 800k characters.
        # Let's set a safety limit of 500k chars for code.
        max_total_code_len = 500000 
        total_code_len = 0

        for f in selected_files:

            # Skip very large files (likely data or binaries)
            if f.stat().st_size > 100000:
                code_content += f"\n--- File: {f.name} (Skipped - Too Large > 100KB) ---\n"
                continue

            try:
                content = f.read_text(errors='replace')

                if total_code_len + len(content) > max_total_code_len:
                    code_content += f"\n--- File: {f.name} (Skipped - Total Limit Reached) ---\n"
                    continue

                code_content += f"\n--- File: {f.name} ---\n{content}\n"
                total_code_len += len(content)

            except Exception:
                pass

        # Step 2: Code Analysis
        code_prompt = f"""
You are an expert Computer Science instructor. Please analyze the following student source code for quality, style, and correctness.

### Source Code
{code_content}

### Instructions
1. Analyze the code structure, variable naming, and adherence to best practices (PEP 8 for Python, etc.).
2. Identify any potential logic errors or security vulnerabilities.
3. Summarize the implementation approach.

Do not provide a grade yet. Focus on the code itself.
"""
        try:
            code_analysis = self.client.generate_text(
                prompt=code_prompt,
                model=self.config.reviewer_model,
                provider=self.config.reviewer_provider,
                system_prompt="You are a helpful and strict teaching assistant."
            )
        except Exception as e:
            code_analysis = f"Error analyzing code: {e}"

        # Step 2: Final Review with Execution Output
        # Truncate output if necessary, but be generous.
        # If we have 200k context, and code analysis is small (e.g. 2k tokens), we have lots of room for output.
        # Let's limit output to 100k chars each to be safe.
        max_output_len = 100000
        if len(stdout) > max_output_len:
            stdout = stdout[:max_output_len] + "\n... [Output Truncated] ..."
        if len(stderr) > max_output_len:
            stderr = stderr[:max_output_len] + "\n... [Output Truncated] ..."

        final_prompt = f"""
You are an expert Computer Science instructor. You have previously analyzed the student's code. Now, incorporate the execution results to provide a final review and grade.

### Code Analysis Summary
{code_analysis}

### Execution Output
STDOUT:
{stdout}

STDERR:
{stderr}

### Instructions
1. Combine your code analysis with the execution results.
2. Did the code run successfully? Does the output match expectations?
3. Provide a final comprehensive review including feedback on both code and execution.
4. Assign a tentative grade (0-100) based on functionality and code quality.

Format the output as Markdown.
"""

        review = self.client.generate_text(
            prompt=final_prompt,
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

        metareview = self.client.generate_text(
            prompt=prompt,
            model=self.config.reviewer_model,
            provider=self.config.reviewer_provider,
            system_prompt="You are an educational data analyst."
        )

        return metareview
