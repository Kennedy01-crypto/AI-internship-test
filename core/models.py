from django.db import models


class Client(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.full_name


class Task(models.Model):
    class Intent(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        BANKING = "banking", "Banking"
        COMPLIANCE = "compliance", "Compliance"
        LEGAL_SUPPORT = "legal_support", "Legal Support"
        UNKNOWN = "unknown", "Unknown"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    class EmployeeCategory(models.TextChoices):
        FINANCE = "finance", "Finance"
        OPERATIONS = "operations", "Operations"
        LEGAL = "legal", "Legal"

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    intent = models.CharField(max_length=50, choices=Intent.choices, default=Intent.UNKNOWN)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    employee_category = models.CharField(
        max_length=20,
        choices=EmployeeCategory.choices,
        default=EmployeeCategory.OPERATIONS,
    )
    risk_score = models.FloatField(default=0.0)
    raw_input = models.TextField()
    structured_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.get_intent_display()} ({self.get_status_display()})"


class CommunicationLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="communications")
    whatsapp_message = models.TextField(blank=True)
    email_message = models.TextField(blank=True)
    sms_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"CommunicationLog #{self.pk} for Task #{self.task_id}"
