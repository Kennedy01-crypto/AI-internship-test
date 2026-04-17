from django.urls import path

from .views import index, process_request

urlpatterns = [
    path("", index, name="index"),
    path("api/process-request/", process_request, name="process_request"),
]
