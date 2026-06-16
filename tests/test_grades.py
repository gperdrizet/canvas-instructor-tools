"""Unit tests for grade and comment posting helpers."""

import unittest
from unittest.mock import MagicMock, patch

from canvas_tools.grades import post_grades_batch, post_submission_comment, post_submission_grade


class TestGrades(unittest.TestCase):
    @patch("canvas_tools.grades.get_client")
    def test_post_submission_grade(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()
        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment
        mock_assignment.get_submission.return_value = mock_submission

        result = post_submission_grade(1, 2, 3, "95", comment="Nice work")

        mock_submission.edit.assert_called_once_with(
            submission={"posted_grade": "95"},
            comment={"text_comment": "Nice work"},
        )
        self.assertTrue(result["success"])

    @patch("canvas_tools.grades.get_client")
    def test_post_submission_comment(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_assignment = MagicMock()
        mock_submission = MagicMock()
        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course
        mock_course.get_assignment.return_value = mock_assignment
        mock_assignment.get_submission.return_value = mock_submission

        result = post_submission_comment(1, 2, 3, "Revision requested")

        mock_submission.edit.assert_called_once_with(comment={"text_comment": "Revision requested"})
        self.assertTrue(result["success"])

    @patch("canvas_tools.grades.post_submission_grade")
    def test_post_grades_batch_collects_errors(self, mock_post_grade):
        mock_post_grade.side_effect = [
            {"success": True, "user_id": 10},
            ValueError("bad payload"),
        ]

        result = post_grades_batch(
            1,
            2,
            [
                {"user_id": 10, "posted_grade": "90"},
                {"user_id": 11, "posted_grade": "80"},
            ],
        )

        self.assertTrue(result[0]["success"])
        self.assertFalse(result[1]["success"])
        self.assertEqual(result[1]["user_id"], 11)


if __name__ == "__main__":
    unittest.main()
