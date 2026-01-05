import shutil
from pathlib import Path
from typing import List

class SubmissionOrganizer:

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def organize(self) -> List[Path]:
        """
        Scans the base directory for submission files, creates student directories,
        and moves files into them. Returns a list of student directories.
        """

        if not self.base_dir.exists():
            raise FileNotFoundError(f"Directory {self.base_dir} does not exist.")

        student_dirs = set()

        # Canvas file format: "Student Name_ID_Question_ID_Original_Filename"
        # Or sometimes just "Student Name_ID_Original_Filename"
        # We'll try to extract the student name.

        # We need to be careful not to process directories we just created.
        files = [f for f in self.base_dir.iterdir() if f.is_file()]

        # System files and data files to ignore
        ignore_files = {"assignment_description.md", "class_summary.md"}
        data_extensions = {".csv", ".json", ".txt", ".xlsx", ".tsv", ".xml", ".ipynb"}

        for file_path in files:

            filename = file_path.name

            # Skip system files and data files (these should stay in the parent directory)
            if filename in ignore_files or file_path.suffix.lower() in data_extensions:
                continue

            # Simple heuristic: split by first underscore to get student name
            # This assumes the format is consistent with what was described earlier.
            if '_' in filename:

                # Try to get First_Last (2 tokens) to avoid collisions with common first names
                parts = filename.split('_')

                if len(parts) >= 2:
                    student_name = "_".join(parts[:2])

                else:
                    student_name = parts[0]

                # Create directory
                student_dir = self.base_dir / student_name
                student_dir.mkdir(exist_ok=True)

                # Move file
                new_path = student_dir / filename
                shutil.move(str(file_path), str(new_path))

                student_dirs.add(student_dir)

            else:
                # If no underscore, maybe it's a meta file or weirdly named.
                # We might skip or move to a 'misc' folder. For now, skip.
                pass

        # Also include directories that might have already existed (idempotency)
        for item in self.base_dir.iterdir():
            if item.is_dir() and item not in student_dirs:

                # Check if it looks like a student dir (not hidden)
                if not item.name.startswith('.'):
                    student_dirs.add(item)

        return list(student_dirs)
