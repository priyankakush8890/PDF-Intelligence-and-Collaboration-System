from django.contrib import admin
from .models import PDFDocument,Comment,ChatMessage
admin.site.register([PDFDocument,Comment,ChatMessage])
