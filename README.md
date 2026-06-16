# Canvas Tools

A Python package for automating common instructor operations on the Canvas LMS.

## Features

*   **Download Submissions**: Bulk download all file submissions for a specific assignment, automatically renaming them with the student's name.
*   **Course and Assignment Discovery**: List available courses and assignments.
*   **Submission Metadata**: Retrieve normalized submission payloads and assignment descriptions.
*   **Grade and Comment Posting**: Post grades/comments for individual students or batch updates.

## Installation

```bash
pip install canvas-instructor-tools
```

## Configuration

Create a `.env` file in your working directory with your Canvas credentials:

```ini
CANVAS_API_URL=https://your.institution.instructure.com
CANVAS_API_KEY=your_api_key_here
```

## Usage

### Command Line Interface

To download submissions for a specific assignment:

```bash
# Syntax: canvas-tools download <course_id> <assignment_id>
canvas-tools download 12345 67890
```

Optional arguments:
*   `--output` or `-o`: Specify the output directory (default: current directory)
*   `--include-links`: Attempt to download URL submissions as files

Additional commands:

```bash
canvas-tools list-courses
canvas-tools list-assignments <course_id>
canvas-tools post-grade <course_id> <assignment_id> <user_id> <posted_grade> --comment "Nice work"
canvas-tools post-comment <course_id> <assignment_id> <user_id> "Please add more tests"
```

### Python API

```python
from canvas_tools import (
    download_submission_artifacts,
    get_assignment_description,
    list_assignment_submissions,
    list_course_assignments,
    list_courses,
    post_submission_grade,
)

courses = list_courses()
assignments = list_course_assignments(course_id=12345)
submissions = list_assignment_submissions(course_id=12345, assignment_id=67890)
description = get_assignment_description(course_id=12345, assignment_id=67890)

download_submission_artifacts(course_id=12345, assignment_id=67890, output_dir="my_downloads", include_links=True)
post_submission_grade(course_id=12345, assignment_id=67890, user_id=111, posted_grade="95", comment="Strong submission")
```

## Development

1.  Clone the repository.
2.  Install dependencies: `pip install -e .`
3.  Run tests: `python -m unittest discover tests`

## CI/CD & Publishing

This project uses GitHub Actions for automated testing and publishing.

### Workflow Overview

*   **CI (`.github/workflows/ci.yml`)**: Runs on every Pull Request and push to `main`.
    *   Tests across Python 3.11, 3.12, and 3.13.
    *   Verifies the package builds successfully.
*   **Publish (`.github/workflows/publish.yml`)**: Runs on version tags (`v*`) or when a GitHub Release is published.
    *   Builds the package.
    *   Publishes to **TestPyPI** and **PyPI** using Trusted Publishing (OIDC).

### How to Publish a New Version

1.  **Update Version**:
    *   Edit `pyproject.toml` and increment the `version` (e.g., `0.0.1` -> `0.0.2`).
    *   Commit and push to `main`.

2.  **Create Release**:
    *   Go to the GitHub repository page.
    *   Click **Releases** > **Draft a new release**.
    *   **Tag version**: `v0.0.2` (matching your `pyproject.toml`).
    *   **Title**: `v0.0.2`.
    *   Click **Publish release**.

3.  **Verify**:
    *   Check the **Actions** tab to see the `Publish to PyPI` workflow running.
    *   Once green, verify the new version is available on [PyPI](https://pypi.org/project/canvas-instructor-tools/).
