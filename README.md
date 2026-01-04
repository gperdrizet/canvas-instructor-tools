# Canvas Tools

A Python package for automating common instructor operations on the Canvas LMS.

## Features

*   **Download Submissions**: Bulk download all file submissions for a specific assignment, automatically renaming them with the student's name.

## Installation

```bash
pip install canvas-tools
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

### Python API

```python
from canvas_tools import download_assignment_submissions

download_assignment_submissions(
    course_id=12345, 
    assignment_id=67890, 
    output_dir="my_downloads"
)
```

## Development

1.  Clone the repository.
2.  Install dependencies: `pip install -e .`
3.  Run tests: `pytest`
