import os
import requests
from pathlib import Path
from .client import get_client

def download_assignment_submissions(course_id, assignment_id, output_dir="data"):
    """
    Download all submissions for a specific assignment.
    
    Args:
        course_id (int): The Canvas Course ID.
        assignment_id (int): The Canvas Assignment ID.
        output_dir (str): Directory to save downloaded files.
    """
    canvas = get_client()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    
    print(f"Downloading submissions for: {assignment.name}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get submissions with user data to name files nicely
    submissions = assignment.get_submissions(include=["user", "submission_history"])
    
    count = 0
    for submission in submissions:
        # Skip if no user (e.g. test student sometimes) or no attachments
        if not hasattr(submission, "user") or not hasattr(submission, "attachments"):
            continue
            
        user_name = submission.user["name"].replace(" ", "_").replace("/", "-")
        
        for attachment in submission.attachments:
            file_url = attachment.url
            original_filename = attachment.display_name
            
            # Construct new filename: Student_Name_OriginalFilename
            new_filename = f"{user_name}_{original_filename}"
            file_path = os.path.join(output_dir, new_filename)
            
            print(f"Downloading {new_filename}...")
            
            try:
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    count += 1
                else:
                    print(f"Failed to download {original_filename}: Status {response.status_code}")
            except Exception as e:
                print(f"Error downloading {original_filename}: {e}")
                
    print(f"\nDownload complete! {count} files saved to {output_dir}/")
