import argparse
import sys
from .submissions import download_assignment_submissions

def main():
    parser = argparse.ArgumentParser(description="Canvas LMS Automation Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Download Submissions Command
    dl_parser = subparsers.add_parser("download", help="Download assignment submissions")
    dl_parser.add_argument("course_id", type=int, help="Canvas Course ID")
    dl_parser.add_argument("assignment_id", type=int, help="Canvas Assignment ID")
    dl_parser.add_argument("--output", "-o", default="submissions", help="Output directory")
    
    args = parser.parse_args()
    
    if args.command == "download":
        try:
            download_assignment_submissions(args.course_id, args.assignment_id, args.output)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
