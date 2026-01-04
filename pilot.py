import os
from canvasapi import Canvas
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")
COURSE_ID = os.getenv("CANVAS_COURSE_ID")
ASSIGNMENT_ID = os.getenv("CANVAS_ASSIGNMENT_ID")

def pilot_test():
    if not all([API_URL, API_KEY, COURSE_ID, ASSIGNMENT_ID]):
        print("Error: Missing configuration. Please check your .env file.")
        return

    print(f"Connecting to Canvas at: {API_URL}")
    
    try:
        # Initialize a new Canvas object
        canvas = Canvas(API_URL, API_KEY)

        # Get the course
        print(f"Fetching Course ID: {COURSE_ID}...")
        course = canvas.get_course(COURSE_ID)
        print(f"Success! Found Course: {course.name}")

        # Get the assignment
        print(f"Fetching Assignment ID: {ASSIGNMENT_ID}...")
        assignment = course.get_assignment(ASSIGNMENT_ID)
        print(f"Success! Found Assignment: {assignment.name}")
        
        print("\nPilot study successful! Credentials and IDs are valid.")

    except Exception as e:
        print(f"\nError during pilot study: {e}")

if __name__ == "__main__":
    pilot_test()
