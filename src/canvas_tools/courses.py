"""Course and assignment discovery helpers."""

from .client import get_client


def list_courses(state=None):
    """List courses available to the authenticated user."""
    canvas = get_client()
    kwargs = {}
    if state:
        kwargs["enrollment_state"] = state
    courses = canvas.get_courses(**kwargs)

    return [
        {
            "id": course.id,
            "name": course.name,
            "course_code": getattr(course, "course_code", None),
            "workflow_state": getattr(course, "workflow_state", None),
            "start_at": getattr(course, "start_at", None),
            "end_at": getattr(course, "end_at", None),
        }
        for course in courses
    ]


def list_course_assignments(course_id):
    """List assignments for a course."""
    canvas = get_client()
    course = canvas.get_course(course_id)

    return [
        {
            "id": assignment.id,
            "name": assignment.name,
            "description": getattr(assignment, "description", "") or "",
            "points_possible": getattr(assignment, "points_possible", None),
            "due_at": getattr(assignment, "due_at", None),
            "published": getattr(assignment, "published", None),
        }
        for assignment in course.get_assignments()
    ]
