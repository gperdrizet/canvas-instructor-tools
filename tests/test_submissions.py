"""
Unit tests for the submissions module.

This module contains tests for the submission downloading functionality,
verifying API interaction, file handling, and error management.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from canvas_tools.submissions import download_assignment_submissions

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
    @patch('canvas_tools.submissions.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('canvas_tools.submissions.Path')

    def test_download_assignment_submissions(self, mock_path, mock_file, mock_get, mock_get_client):
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

        # Mock requests response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'file content'
        mock_get.return_value = mock_response

        # Run function
        download_assignment_submissions(123, 456, output_dir="test_submissions")

        # Assertions
        mock_canvas.get_course.assert_called_with(123)
        mock_course.get_assignment.assert_called_with(456)
        mock_assignment.get_submissions.assert_called_with(include=["user", "submission_history"])

        # Check if directory creation was called
        # Expecting join of output_dir and sanitized assignment name
        # We can't easily predict the exact string due to os.path.join separator, 
        # but we can check if it ends with the assignment name
        mock_path.assert_called()
        args, _ = mock_path.call_args
        self.assertIn("Test_Assignment", args[0])
        mock_path.return_value.mkdir.assert_called_with(parents=True, exist_ok=True)

        # Check if file download was attempted
        mock_get.assert_called_with('http://file.url', timeout=30)

        # Check if file was written
        # Note: We can't easily check the exact path since os.path.join is used inside, 
        # but we can check that open was called with 'wb' mode
        mock_file.assert_called()
        args, kwargs = mock_file.call_args
        self.assertIn('test.pdf', args[0]) # Check filename part
        self.assertIn('Test_User', args[0]) # Check username part
        self.assertEqual(args[1], 'wb')

        mock_file().write.assert_called_with(b'file content')

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

if __name__ == '__main__':
    unittest.main()
