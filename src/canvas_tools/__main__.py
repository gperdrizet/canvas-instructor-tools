"""
Command-line interface for the canvas-tools package.

This module provides the entry point for the CLI, handling argument parsing
and dispatching commands to the appropriate functions.
"""

import argparse
import sys
from canvasapi.exceptions import CanvasException
from .submissions import download_assignment_submissions

def main():
    """
    Main entry point for the CLI.
    
    Parses command-line arguments and executes the requested command.
    Currently supported commands:
        - download: Download assignment submissions.
    """

    # Instantiate the argument parser
    parser = argparse.ArgumentParser(description="Canvas LMS Automation Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download Submissions Command
    dl_parser = subparsers.add_parser("download", help="Download assignment submissions")
    dl_parser.add_argument("course_id", type=int, help="Canvas Course ID")
    dl_parser.add_argument("assignment_id", type=int, help="Canvas Assignment ID")
    dl_parser.add_argument("--output", "-o", default=".", help="Base output directory (default: current directory)")
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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
