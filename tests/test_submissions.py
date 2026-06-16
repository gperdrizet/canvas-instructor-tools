"""
Unit tests for the submissions module.

This module contains tests for the submission downloading functionality,
verifying API interaction, file handling, and error management.
"""

import unittest
from unittest.mock import patch, MagicMock
from canvas_tools.submissions import (
    download_assignment_submissions,
    download_submission_artifacts,
    get_assignment_description,
    list_assignment_submissions,
)

import shutil
import os

class TestSubmissions(unittest.TestCase):
    """Test cases for the download_assignment_submissions function."""

    def tearDown(self):
        """Clean up any directories created during tests."""
        dirs_to_remove = ["Test_Assignment_No_Attachments", "test_submissions"]
        for d in dirs_to_remove:
            if os.path.exists(d):
                shutil.rmtree(d)

    @patch('canvas_tools.submissions.get_client')
    @patch('canvas_tools.submissions.download_remote_file')
    @patch('canvas_tools.submissions.Path')
    def test_download_assignment_submissions(self, mock_path, mock_download, mock_get_client):
        # Setup mocks
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()

        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment
        mock_assignment.name = "Test Assignment"

        # Mock submission data
        mock_submission.user = {'name': 'Test User'}

        # Create a mock for the attachment object
        mock_attachment = MagicMock()
        mock_attachment.url = 'http://file.url'
        mock_attachment.display_name = 'test.pdf'
        mock_submission.attachments = [mock_attachment]

        mock_assignment.get_submissions.return_value = [mock_submission]

        # Run function
        download_assignment_submissions(123, 456, output_dir="test_submissions")

        # Assertions
        mock_canvas.get_course.assert_called_with(123)
        mock_course.get_assignment.assert_called_with(456)
        mock_assignment.get_submissions.assert_called_with(include=["user", "submission_history"])

        # Check directory creation used the sanitized assignment name
        mock_path.assert_called()
        args, _ = mock_path.call_args
        self.assertIn("Test_Assignment", args[0])
        mock_path.return_value.mkdir.assert_called_with(parents=True, exist_ok=True)

        # Check download_remote_file called with the right URL and a path containing username + filename
        mock_download.assert_called_once()
        call_args = mock_download.call_args[0]
        self.assertEqual(call_args[0], 'http://file.url')
        self.assertIn('test.pdf', call_args[1])
        self.assertIn('Test_User', call_args[1])

    @patch('canvas_tools.submissions.get_client')
    def test_download_no_attachments(self, mock_get_client):
        # Setup mocks for a submission with no attachments
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()

        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment
        mock_assignment.name = "Test Assignment No Attachments"

        # Submission has user but no attachments
        mock_submission.user = {'name': 'Test User'}

        # No attachments attribute or empty list
        del mock_submission.attachments

        # We need to handle the hasattr check in the code
        # The code checks: if not hasattr(submission, "user") or not 
        # hasattr(submission, "attachments"):
        mock_assignment.get_submissions.return_value = [mock_submission]

        # Run function
        download_assignment_submissions(123, 456)

        # Should run without error and not attempt downloads
        # We can verify this implicitly if it doesn't crash,
        # or explicitly by mocking requests.get and asserting not called

    @patch('canvas_tools.submissions.get_client')
    def test_list_assignment_submissions(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()

        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment

        mock_submission.id = 999
        mock_submission.user_id = 111
        mock_submission.submission_type = "online_upload"
        mock_submission.workflow_state = "submitted"
        mock_submission.submitted_at = "2026-06-01"
        mock_submission.grade = None
        mock_submission.score = None
        mock_submission.url = None
        mock_submission.user = {"id": 111, "name": "Test User"}

        mock_attachment = MagicMock()
        mock_attachment.id = 222
        mock_attachment.display_name = "answer.py"
        mock_attachment.url = "http://file.url/answer.py"
        mock_submission.attachments = [mock_attachment]

        mock_assignment.get_submissions.return_value = [mock_submission]

        result = list_assignment_submissions(123, 456)

        self.assertEqual(result[0]["id"], 999)
        self.assertEqual(result[0]["user"]["name"], "Test User")
        self.assertEqual(result[0]["attachments"][0]["display_name"], "answer.py")

    @patch('canvas_tools.submissions.get_client')
    @patch('canvas_tools.submissions.download_remote_file')
    def test_download_submission_artifacts_includes_url_submissions(self, mock_download, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()

        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment

        mock_submission.id = 1
        mock_submission.user_id = 7
        mock_submission.user = {"name": "Student One"}
        mock_submission.submission_type = "online_url"
        mock_submission.url = "https://example.org/work/report.pdf"
        mock_submission.attachments = []

        mock_assignment.get_submissions.return_value = [mock_submission]

        result = download_submission_artifacts(10, 20, output_dir="test_submissions", include_links=True)

        self.assertEqual(result["downloaded_count"], 1)
        self.assertEqual(result["artifacts"][0]["kind"], "online_url")
        mock_download.assert_called_once()
        self.assertEqual(mock_download.call_args[0][0], "https://example.org/work/report.pdf")

    @patch('canvas_tools.submissions.get_client')
    def test_get_assignment_description(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()

        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment

        mock_assignment.id = 22
        mock_assignment.name = "Project"
        mock_assignment.description = "Write a compiler"
        mock_assignment.points_possible = 50
        mock_assignment.due_at = "2026-06-10"

        result = get_assignment_description(1, 22)

        self.assertEqual(result["id"], 22)
        self.assertEqual(result["description"], "Write a compiler")

if __name__ == '__main__':
    unittest.main()
