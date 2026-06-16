"""Unit tests for course and assignment discovery helpers."""

import unittest
from unittest.mock import MagicMock, patch

from canvas_tools.courses import list_course_assignments, list_courses


class TestCourses(unittest.TestCase):
    @patch("canvas_tools.courses.get_client")
    def test_list_courses(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_get_client.return_value = mock_canvas

        course = MagicMock()
        course.id = 11
        course.name = "Intro to Testing"
        course.course_code = "TEST-101"
        course.workflow_state = "available"
        course.start_at = "2026-01-10"
        course.end_at = None
        mock_canvas.get_courses.return_value = [course]

        result = list_courses()

        mock_canvas.get_courses.assert_called_once_with()
        self.assertEqual(result[0]["id"], 11)
        self.assertEqual(result[0]["name"], "Intro to Testing")

    @patch("canvas_tools.courses.get_client")
    def test_list_course_assignments(self, mock_get_client):
        mock_canvas = MagicMock()
        mock_course = MagicMock()
        mock_get_client.return_value = mock_canvas
        mock_canvas.get_course.return_value = mock_course

        assignment = MagicMock()
        assignment.id = 22
        assignment.name = "Project 1"
        assignment.description = "Build a parser"
        assignment.points_possible = 100
        assignment.due_at = "2026-02-01"
        assignment.published = True
        mock_course.get_assignments.return_value = [assignment]

        result = list_course_assignments(123)

        mock_canvas.get_course.assert_called_once_with(123)
        self.assertEqual(result[0]["id"], 22)
        self.assertEqual(result[0]["description"], "Build a parser")


if __name__ == "__main__":
    unittest.main()
