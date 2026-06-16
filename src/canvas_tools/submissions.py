"""Submission management helpers for Canvas assignments."""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

from .client import get_client
from .http_safety import download_remote_file


def _sanitize_assignment_name(name):
    name_no_slashes = name.replace("/", "-")
    clean_name = re.sub(r"[^\w\s-]", "", name_no_slashes)
    return clean_name.replace(" ", "_")


def _safe_filename(name):
    return name.replace("/", "-").replace(" ", "_")


def _submission_to_dict(submission):
    user = getattr(submission, "user", None)
    attachments = []
    for attachment in getattr(submission, "attachments", []) or []:
        attachments.append(
            {
                "id": getattr(attachment, "id", None),
                "display_name": getattr(attachment, "display_name", None),
                "url": getattr(attachment, "url", None),
                "size": getattr(attachment, "size", None),
                "content_type": getattr(attachment, "content-type", None),
            }
        )

    return {
        "id": getattr(submission, "id", None),
        "user_id": getattr(submission, "user_id", None),
        "submission_type": getattr(submission, "submission_type", None),
        "workflow_state": getattr(submission, "workflow_state", None),
        "submitted_at": getattr(submission, "submitted_at", None),
        "grade": getattr(submission, "grade", None),
        "score": getattr(submission, "score", None),
        "url": getattr(submission, "url", None),
        "user": {
            "id": user.get("id") if isinstance(user, dict) else None,
            "name": user.get("name") if isinstance(user, dict) else None,
        },
        "attachments": attachments,
    }


def _download_file(url, destination_path):
    download_remote_file(url, destination_path)

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

    safe_assignment_name = _sanitize_assignment_name(assignment.name)
    target_dir = os.path.join(output_dir, safe_assignment_name)

    # Create output directory
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    summary = download_submission_artifacts(
        course_id=course_id,
        assignment_id=assignment_id,
        output_dir=target_dir,
        include_links=False,
    )
    count = summary["downloaded_count"]

    print(f"\nDownload complete! {count} files saved to {target_dir}/")


def list_assignment_submissions(course_id, assignment_id, include_history=True):
    """Return normalized submission payloads for an assignment."""
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    include = ["user"]
    if include_history:
        include.append("submission_history")

    return [
        _submission_to_dict(submission)
        for submission in assignment.get_submissions(include=include)
    ]


def get_assignment_description(course_id, assignment_id):
    """Return assignment metadata and description text."""
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    return {
        "id": assignment.id,
        "name": assignment.name,
        "description": getattr(assignment, "description", "") or "",
        "points_possible": getattr(assignment, "points_possible", None),
        "due_at": getattr(assignment, "due_at", None),
    }


def download_submission_artifacts(course_id, assignment_id, output_dir=".", include_links=True):
    """Download attachments (and optionally URL submissions) for an assignment."""
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    result = {
        "downloaded_count": 0,
        "errors": [],
        "artifacts": [],
    }

    submissions = assignment.get_submissions(include=["user", "submission_history"])
    for submission in submissions:
        user = getattr(submission, "user", None)
        user_name = "unknown_user"
        if isinstance(user, dict):
            user_name = _safe_filename(user.get("name", user_name))

        for attachment in getattr(submission, "attachments", []) or []:
            original_filename = getattr(attachment, "display_name", "attachment.bin")
            safe_name = _safe_filename(original_filename)
            new_filename = f"{user_name}_{safe_name}"
            file_path = os.path.join(output_dir, new_filename)

            try:
                _download_file(getattr(attachment, "url"), file_path)
                result["downloaded_count"] += 1
                result["artifacts"].append(
                    {
                        "submission_id": getattr(submission, "id", None),
                        "user_id": getattr(submission, "user_id", None),
                        "kind": "attachment",
                        "source_url": getattr(attachment, "url", None),
                        "local_path": file_path,
                    }
                )
            except (ValueError, OSError) as exc:
                result["errors"].append(
                    {
                        "submission_id": getattr(submission, "id", None),
                        "artifact": original_filename,
                        "error": str(exc),
                    }
                )

        if include_links and getattr(submission, "submission_type", None) == "online_url":
            submission_url = getattr(submission, "url", None)
            if not submission_url:
                continue

            parsed = urlparse(submission_url)
            basename = os.path.basename(parsed.path) or "linked_submission"
            basename = _safe_filename(basename)
            link_filename = f"{user_name}_{basename}"
            link_path = os.path.join(output_dir, link_filename)

            try:
                _download_file(submission_url, link_path)
                result["downloaded_count"] += 1
                result["artifacts"].append(
                    {
                        "submission_id": getattr(submission, "id", None),
                        "user_id": getattr(submission, "user_id", None),
                        "kind": "online_url",
                        "source_url": submission_url,
                        "local_path": link_path,
                    }
                )
            except (ValueError, OSError) as exc:
                result["errors"].append(
                    {
                        "submission_id": getattr(submission, "id", None),
                        "artifact": submission_url,
                        "error": str(exc),
                    }
                )

    return result
