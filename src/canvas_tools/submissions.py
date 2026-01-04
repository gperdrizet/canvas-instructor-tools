"""
Submission Management Module.

This module provides functionality for interacting with assignment submissions,
specifically downloading student submission files and organizing them into directories.
"""

import os
import re
import requests
from pathlib import Path
from .client import get_client

def download_assignment_submissions(course_id, assignment_id, output_dir="."):
    """
    Download all submissions for a specific assignment.
    
    Args:
        course_id (int): The Canvas Course ID.
        assignment_id (int): The Canvas Assignment ID.
        output_dir (str): Directory to save downloaded files. Default is current directory.
    """

    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    print(f"Downloading submissions for: {assignment.name}")

    # Sanitize assignment name for directory usage
    # Replace slashes with hyphens first to preserve separation
    name_no_slashes = assignment.name.replace("/", "-")

    # Remove punctuation (keep alphanumeric, spaces, underscores, hyphens)
    clean_name = re.sub(r'[^\w\s-]', '', name_no_slashes)
    safe_assignment_name = clean_name.replace(" ", "_")
    target_dir = os.path.join(output_dir, safe_assignment_name)

    # Create output directory
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Get submissions with user data to name files nicely
    submissions = assignment.get_submissions(include=["user", "submission_history"])

    count = 0

    for submission in submissions:

        # Skip if no user (e.g. test student sometimes) or no attachments
        if not hasattr(submission, "user") or not hasattr(submission, "attachments"):
            continue

        user_name = submission.user["name"].replace(" ", "_").replace("/", "-")

        for attachment in submission.attachments:

            # Get file info
            file_url = attachment.url
            original_filename = attachment.display_name

            # Construct new filename: Student_Name_OriginalFilename
            new_filename = f"{user_name}_{original_filename}"
            file_path = os.path.join(target_dir, new_filename)

            print(f"Downloading {new_filename}...")

            try:
                response = requests.get(file_url, timeout=30)

                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    count += 1

                else:
                    print(f"Failed to download {original_filename}: Status {response.status_code}")

            except requests.RequestException as e:
                print(f"Network error downloading {original_filename}: {e}")

            except OSError as e:
                print(f"File error saving {original_filename}: {e}")

    print(f"\nDownload complete! {count} files saved to {target_dir}/")
