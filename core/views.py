import json

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
        return JsonResponse({"error": str(exc)}, status=500)
    except Exception as exc:
        return JsonResponse({"error": f"Processing failed: {exc}"}, status=500)

    return JsonResponse(
        {
            "task_id": task.pk,
            "intent": task.intent,
            "status": task.status,
            "employee_category": task.employee_category,
            "risk_score": task.risk_score,
            "structured_data": structured,
        }
    )
