from django.contrib import admin

from .models import Client, CommunicationLog, Task

admin.site.register(Client)
admin.site.register(Task)
admin.site.register(CommunicationLog)
