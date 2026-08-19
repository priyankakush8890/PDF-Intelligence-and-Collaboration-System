from django import forms
from django.contrib.auth.models import User
from .models import PDFDocument, Comment
import bleach

class SignUpForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User; fields=["username","email","password"]
    def save(self,commit=True):
        user=super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit: user.save()
        return user

class UploadPDFForm(forms.ModelForm):
    class Meta: model=PDFDocument; fields=["title","file"]
    def clean_file(self):
        f=self.cleaned_data["file"]
        if not f.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        if f.size > 20*1024*1024:
            raise forms.ValidationError("Maximum file size is 20 MB.")
        return f

class CommentForm(forms.ModelForm):
    guest_name = forms.CharField(required=False)

    class Meta:
        model = Comment
        fields = ["guest_name", "body"]

    def clean_body(self):
        body = self.cleaned_data["body"]

        allowed_tags = [
            "strong",
            "b",
            "em",
            "i",
            "ul",
            "ol",
            "li",
            "br",
            "p",
        ]

        return bleach.clean(
            body,
            tags=allowed_tags,
            attributes={},
            strip=True,
        )
