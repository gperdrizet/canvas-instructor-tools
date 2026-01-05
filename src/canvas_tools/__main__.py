"""
Command-line interface for the canvas-tools package.

This module provides the entry point for the CLI, handling argument parsing
and dispatching commands to the appropriate functions.
"""

import argparse
import sys
import shutil
from pathlib import Path
from canvasapi.exceptions import CanvasException
from .submissions import download_assignment_submissions
from .organizer import SubmissionOrganizer
from .execution_agent import ExecutionAgent
from .docker_runner import DockerRunner
from .reviewer import Reviewer
from .config import get_config
from .ollama_manager import OllamaManager

def main():
    """
    Main entry point for the CLI.
    
    Parses command-line arguments and executes the requested command.
    Currently supported commands:
        - download: Download assignment submissions.
        - review: Run and review downloaded submissions.
    """

    # Instantiate the argument parser
    parser = argparse.ArgumentParser(description="Canvas LMS Automation Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download Submissions Command
    dl_parser = subparsers.add_parser("download", help="Download assignment submissions")
    dl_parser.add_argument("course_id", type=int, help="Canvas Course ID")
    dl_parser.add_argument("assignment_id", type=int, help="Canvas Assignment ID")
    dl_parser.add_argument("--output", "-o", default=".", help="Output directory (default: current directory)")

    # Review Submissions Command
    rv_parser = subparsers.add_parser("review", help="Run and review submissions")
    rv_parser.add_argument("directory", help="Directory containing downloaded submissions")
    rv_parser.add_argument("--force-rebuild", action="store_true", help="Force pull and rebuild of Ollama container image")
    rv_parser.add_argument("--solution", help="Path to instructor solution file (optional)")

    args = parser.parse_args()

    if args.command == "download":
        try:
            download_assignment_submissions(args.course_id, args.assignment_id, args.output)

        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

        except CanvasException as e:
            print(f"Canvas API Error: {e}", file=sys.stderr)
            sys.exit(1)

        except OSError as e:
            print(f"File System Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "review":
        try:
            base_dir = Path(args.directory)
            if not base_dir.exists():
                print(f"Error: Directory {base_dir} does not exist.", file=sys.stderr)
                sys.exit(1)

            # Initialize Ollama if needed
            config = get_config()
            if config.execution_provider == "ollama" or config.reviewer_provider == "ollama":
                print("Initializing Ollama...")
                ollama_mgr = OllamaManager()
                ollama_mgr.ensure_ollama_running(force_pull=args.force_rebuild)
                
                if config.execution_provider == "ollama":
                    ollama_mgr.ensure_model_pulled(config.execution_model)
                
                if config.reviewer_provider == "ollama":
                    ollama_mgr.ensure_model_pulled(config.reviewer_model)

            print("Organizing submissions...")
            organizer = SubmissionOrganizer(base_dir)
            student_dirs = organizer.organize()
            print(f"Found {len(student_dirs)} student submissions.")

            agent = ExecutionAgent()
            runner = DockerRunner()
            reviewer = Reviewer()
            
            all_reviews = []

            for student_dir in student_dirs:
                print(f"Processing {student_dir.name}...")
                
                try:
                    # 0. Copy shared data files from parent directory
                    data_extensions = {".csv", ".json", ".txt", ".xlsx", ".tsv", ".xml"}
                    parent_dir = student_dir.parent
                    for data_file in parent_dir.iterdir():
                        if data_file.is_file() and data_file.suffix.lower() in data_extensions:
                            dest = student_dir / data_file.name
                            if not dest.exists():
                                shutil.copy2(data_file, dest)
                                print(f"  Copied data file: {data_file.name}")
                    
                    # 1. Generate Execution Script
                    print("  Generating execution script...")
                    script = agent.generate_execution_script(student_dir)
                    script_path = student_dir / "run_submission.sh"
                    script_path.write_text(script)
                    
                    # 2. Run in Docker
                    print("  Running code...")
                    stdout, stderr = runner.run_script(student_dir)
                    
                    # 3. Review
                    print("  Generating review...")
                    review = reviewer.review_submission(student_dir, stdout, stderr, solution_path=args.solution)
                    
                    review_path = student_dir / "review.md"
                    review_path.write_text(review)
                    all_reviews.append(review)
                    print("  Done.")
                    
                except Exception as e:
                    print(f"  Error processing {student_dir.name}: {e}")
                    error_review = f"# Review Error\n\nAn error occurred during processing:\n\n```\n{str(e)}\n```"
                    (student_dir / "review.md").write_text(error_review)
                    continue

            # 4. Meta-Review
            if all_reviews:
                print("Generating class meta-review...")
                metareview = reviewer.generate_metareview(all_reviews)
                (base_dir / "class_summary.md").write_text(metareview)
                print("Meta-review saved to class_summary.md")

        except Exception as e:
            print(f"An error occurred during review: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
