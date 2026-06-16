"""
Command-line interface for the canvas-tools package.

This module provides the entry point for the CLI, handling argument parsing
and dispatching commands to the appropriate functions.
"""

import argparse
import sys
from canvasapi.exceptions import CanvasException
from .courses import list_course_assignments, list_courses
from .grades import post_submission_comment, post_submission_grade
from .submissions import download_submission_artifacts

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
    dl_parser.add_argument(
        "--include-links",
        action="store_true",
        help="Attempt downloading URL-based submissions as files",
    )

    courses_parser = subparsers.add_parser("list-courses", help="List courses")
    courses_parser.add_argument("--state", default=None, help="Optional enrollment state filter")

    assignments_parser = subparsers.add_parser("list-assignments", help="List assignments for a course")
    assignments_parser.add_argument("course_id", type=int, help="Canvas Course ID")

    grade_parser = subparsers.add_parser("post-grade", help="Post a grade (and optional comment)")
    grade_parser.add_argument("course_id", type=int, help="Canvas Course ID")
    grade_parser.add_argument("assignment_id", type=int, help="Canvas Assignment ID")
    grade_parser.add_argument("user_id", type=int, help="Canvas User ID")
    grade_parser.add_argument("posted_grade", help="Grade value accepted by Canvas")
    grade_parser.add_argument("--comment", default=None, help="Optional comment")

    comment_parser = subparsers.add_parser("post-comment", help="Post a comment without grading")
    comment_parser.add_argument("course_id", type=int, help="Canvas Course ID")
    comment_parser.add_argument("assignment_id", type=int, help="Canvas Assignment ID")
    comment_parser.add_argument("user_id", type=int, help="Canvas User ID")
    comment_parser.add_argument("comment", help="Comment text")

    args = parser.parse_args()

    if args.command == "download":
        try:
            result = download_submission_artifacts(
                args.course_id,
                args.assignment_id,
                output_dir=args.output,
                include_links=args.include_links,
            )
            print(f"Downloaded: {result['downloaded_count']}")
            if result["errors"]:
                print(f"Errors: {len(result['errors'])}")

        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

        except CanvasException as e:
            print(f"Canvas API Error: {e}", file=sys.stderr)
            sys.exit(1)

        except OSError as e:
            print(f"File System Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list-courses":
        try:
            for course in list_courses(state=args.state):
                print(f"{course['id']}: {course['name']}")

        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

        except CanvasException as e:
            print(f"Canvas API Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list-assignments":
        try:
            for assignment in list_course_assignments(args.course_id):
                print(f"{assignment['id']}: {assignment['name']}")

        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

        except CanvasException as e:
            print(f"Canvas API Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "post-grade":
        try:
            post_submission_grade(
                args.course_id,
                args.assignment_id,
                args.user_id,
                args.posted_grade,
                comment=args.comment,
            )
            print("Grade posted")

        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

        except CanvasException as e:
            print(f"Canvas API Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "post-comment":
        try:
            post_submission_comment(
                args.course_id,
                args.assignment_id,
                args.user_id,
                args.comment,
            )
            print("Comment posted")

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
