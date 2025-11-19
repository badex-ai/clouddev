from controllers.tasks import send_verification_email_task

# Test if task can be queued
result = send_verification_email_task.delay("test@example.com", "Test User")
print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")