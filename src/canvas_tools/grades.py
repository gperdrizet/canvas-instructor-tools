"""Grade and submission comment write helpers."""

from canvasapi.exceptions import CanvasException

from .client import get_client


def post_submission_grade(course_id, assignment_id, user_id, posted_grade, comment=None):
    """Post a grade (and optional comment) for a submission."""
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    submission = assignment.get_submission(user_id)
    payload = {"submission": {"posted_grade": posted_grade}}
    if comment:
        payload["comment"] = {"text_comment": comment}

    updated = submission.edit(**payload)

    return {
        "success": True,
        "course_id": course_id,
        "assignment_id": assignment_id,
        "user_id": user_id,
        "posted_grade": posted_grade,
        "comment": comment,
        "canvas_response": updated,
    }


def post_submission_comment(course_id, assignment_id, user_id, comment):
    """Post a comment on an existing submission without changing grade."""
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    submission = assignment.get_submission(user_id)
    updated = submission.edit(comment={"text_comment": comment})

    return {
        "success": True,
        "course_id": course_id,
        "assignment_id": assignment_id,
        "user_id": user_id,
        "comment": comment,
        "canvas_response": updated,
    }


def post_grades_batch(course_id, assignment_id, grade_updates):
    """Post grades/comments for multiple users and collect per-user outcomes."""
    results = []

    for item in grade_updates:
        user_id = item["user_id"]
        posted_grade = item.get("posted_grade")
        comment = item.get("comment")

        try:
            if posted_grade is None and comment:
                result = post_submission_comment(
                    course_id=course_id,
                    assignment_id=assignment_id,
                    user_id=user_id,
                    comment=comment,
                )
            else:
                result = post_submission_grade(
                    course_id=course_id,
                    assignment_id=assignment_id,
                    user_id=user_id,
                    posted_grade=posted_grade,
                    comment=comment,
                )
            results.append(result)
        except (CanvasException, ValueError, KeyError) as exc:
            results.append(
                {
                    "success": False,
                    "course_id": course_id,
                    "assignment_id": assignment_id,
                    "user_id": user_id,
                    "error": str(exc),
                }
            )

    return results
