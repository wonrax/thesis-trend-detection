from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/trending/category/moi-nhat")
        self.client.get("/topic/628a5e330946a413d61293bc/0")