

import uuid
from django.db import models
from django.contrib.auth.models import User


class PDFDocument(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pdfs"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="pdfs/")
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)

    share_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PDFChunk(models.Model):
    document = models.ForeignKey(
        PDFDocument,
        on_delete=models.CASCADE,
        related_name="chunks"
    )

    content = models.TextField()

    # Store Gemini embedding as JSON
    embedding = models.JSONField()

    chunk_index = models.IntegerField()

    class Meta:
        ordering = ["chunk_index"]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class Comment(models.Model):
    document = models.ForeignKey(
        PDFDocument,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Parent comment for threaded replies
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    guest_name = models.CharField(
        max_length=100,
        blank=True
    )

    body = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def display_name(self):
        return self.author.username if self.author else (
            self.guest_name or "Guest"
        )


class ChatMessage(models.Model):
    document = models.ForeignKey(
        PDFDocument,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )

    session_key = models.CharField(max_length=64)

    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "user"),
            ("assistant", "assistant")
        ]
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]