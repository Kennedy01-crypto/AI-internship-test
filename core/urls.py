from django.urls import path

from .views import index, list_tasks, process_request, update_task_status

urlpatterns = [
    path("", index, name="index"),
    path("api/process-request/", process_request, name="process_request"),
    path("api/tasks/", list_tasks, name="list_tasks"),
    path("api/tasks/<int:task_id>/status/", update_task_status, name="update_task_status"),
]
