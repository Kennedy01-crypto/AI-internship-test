import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CommunicationLog, Task
from .services import AIRequestProcessor


def index(request):
    return render(request, "index.html")


@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def process_request(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    user_input = body.get("user_input", "").strip()
    if not user_input:
        return JsonResponse({"error": "user_input is required."}, status=400)

    try:
        processor = AIRequestProcessor()
        structured = processor.process(user_input)

        task = Task.objects.create(
            intent=structured.get("intent", Task.Intent.UNKNOWN),
            status=Task.Status.PENDING,
            employee_category=structured.get("employee_category", Task.EmployeeCategory.OPERATIONS),
            risk_score=structured.get("risk_score", 0.0),
            raw_input=user_input,
            structured_data=structured,
        )

        messages = structured.get("messages", {})
        CommunicationLog.objects.create(
            task=task,
            whatsapp_message=messages.get("whatsapp", ""),
            email_message=messages.get("email", ""),
            sms_message=messages.get("sms", ""),
        )
    except ValueError as exc:
        return JsonResponse({"error": "Configuration Error", "details": str(exc)}, status=500)
    except Exception as exc:
        return JsonResponse({"error": f"Processing failed: {exc}"}, status=500)

    return JsonResponse(
        {
            "task_id": task.pk,
            "intent": task.intent,
            "status": task.status,
            "employee_category": task.employee_category,
            "risk_score": task.risk_score,
            "summary": structured.get("summary"),
            "structured_data": structured,
        }
    )

@require_http_methods(["GET"])
def list_tasks(request):
    """Returns all tasks ordered by newest first."""
    tasks = Task.objects.all().order_by('-created_at')
    data = [
        {
            "id": t.pk,
            "intent": t.get_intent_display(),
            "status": t.status,
            "risk_score": round(t.risk_score, 2),
            "employee_category": t.get_employee_category_display(),
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "summary": t.structured_data.get("summary", "No summary available")
        } for t in tasks
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["POST"])  # Using POST for simplicity in vanilla environments without complex middleware
def update_task_status(request, task_id):
    """Updates the status of a specific task."""
    try:
        task = Task.objects.get(pk=task_id)
        body = json.loads(request.body.decode("utf-8"))
        new_status = body.get("status")
        if new_status in Task.Status.values:
            task.status = new_status
            task.save()
            return JsonResponse({"success": True, "new_status": task.status})
        return JsonResponse({"error": "Invalid status value."}, status=400)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
