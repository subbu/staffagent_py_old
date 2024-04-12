import datetime

class User():
    def __init__(
            self,
            job_application_id: str,
            type: str | None,
            resume_content: str | None,
            captured_at: datetime.datetime,
            resume_path: str | None,
            position_applied_for: str) -> None:
        self.job_application_id = job_application_id 
        self.type = type 
        self.resume_content = resume_content  
        self.captured_at = captured_at 
        self.resume_path = resume_path  
        self.position_applied_for = position_applied_for 
