import os
from locust import HttpUser, task, between

class APIUser(HttpUser):
    # Thời gian chờ giữa các request của mỗi user (giây)
    wait_time = between(1, 3)
    
    # API key để xác thực
    api_key = os.getenv("AGENT_API_KEY", "my-secret-key")
    
    @task
    def ask_question(self):
        """
        Mô phỏng một user gửi câu hỏi đến endpoint /ask.
        """
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        payload = {
            "question": "Hãy kể một câu chuyện cười ngắn."
        }
        
        # Gửi request POST đến server
        self.client.post("/ask", json=payload, headers=headers)