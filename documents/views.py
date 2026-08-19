import json

from django.shortcuts import render, redirect, get_object_or_404

from django.http import (
    JsonResponse,
    FileResponse,
    Http404,
    StreamingHttpResponse
)

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import PDFDocument, Comment, ChatMessage
from .forms import SignUpForm, UploadPDFForm, CommentForm

from django.core.mail import send_mail
from django.conf import settings

from .services import (
    extract_pdf_text,
    summarize,
    relevant_context,
    answer_question,
    stream_answer,
    create_document_embeddings,
    semantic_search,
)
def signup(request):
    if request.method=="POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            user=form.save(); login(request,user); return redirect("dashboard")
    else: form=SignUpForm()
    return render(request,"registration/signup.html",{"form":form})

def logout_view(request): logout(request); return redirect("login")

@login_required
def dashboard(request):

    q = request.GET.get("q", "").strip()

    # If the user has not searched anything,
    # show all their PDFs
    if not q:
        docs = PDFDocument.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        return render(
            request,
            "documents/dashboard.html",
            {
                "documents": docs,
                "q": q
            }
        )

    # Normal filename search
    filename_results = list(
        PDFDocument.objects.filter(
            owner=request.user,
            title__icontains=q
        )
    )

    try:
        # Semantic search
        semantic_results = semantic_search(
            q,
            request.user
        )

        # Combine filename + semantic results
        documents = []
        added_ids = set()

        # Add filename matches
        for doc in filename_results:
            documents.append(doc)
            added_ids.add(doc.id)

        # Add semantic matches
        for result in semantic_results:
            doc = result["document"]

            if doc.id not in added_ids:
                documents.append(doc)
                added_ids.add(doc.id)

    except Exception as e:
        # If semantic search fails,
        # normal filename search still works
        documents = filename_results

    return render(
        request,
        "documents/dashboard.html",
        {
            "documents": documents,
            "q": q
        }
    )

@login_required
def upload_pdf(request):
    if request.method == "POST":
        form = UploadPDFForm(request.POST, request.FILES)

        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()

            try:
                doc.extracted_text = extract_pdf_text(doc.file.path)

                if doc.extracted_text:
                    doc.summary = summarize(doc.extracted_text)
                else:
                    doc.summary = "No extractable text was found in this PDF."

                doc.save()

                # Create semantic search embeddings
                if doc.extracted_text:
                    create_document_embeddings(doc)

            except Exception as e:
                doc.summary = f"Processing failed: {str(e)}"
                doc.save()

            return redirect("document", pk=doc.pk)

    else:
        form = UploadPDFForm()

    return render(
        request,
        "documents/upload.html",
        {"form": form}
    )

def _session(request):
    if not request.session.session_key: request.session.create()
    return request.session.session_key

def _access(request,doc):
    return request.user.is_authenticated and request.user==doc.owner

def document(request,pk):
    doc=get_object_or_404(PDFDocument,pk=pk)
    if not _access(request,doc): raise Http404()
    return _document_page(request,doc,False)

def shared_document(request,token):
    doc=get_object_or_404(PDFDocument,share_token=token)
    return _document_page(request,doc,True)

@login_required
def share_via_email(request, pk):
    doc = get_object_or_404(
        PDFDocument,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":
        recipient_email = request.POST.get(
            "email",
            ""
        ).strip()

        if recipient_email:
            share_url = request.build_absolute_uri(
                f"/share/{doc.share_token}/"
            )

            try:
                send_mail(
                    subject=f"{request.user.username} shared a PDF with you",
                    message=(
                        f"Hi,\n\n"
                        f"{request.user.username} has shared the PDF "
                        f"'{doc.title}' with you.\n\n"
                        f"Open the PDF using this link:\n"
                        f"{share_url}\n\n"
                        f"Thanks,\n"
                        f"PDF Intelligence"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )

                return redirect(
                    "document",
                    pk=doc.pk
                )

            except Exception as e:
                return JsonResponse(
                    {"error": str(e)},
                    status=500
                )

    return redirect("document", pk=doc.pk)

def _document_page(request, doc, is_shared):

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)
            comment.document = doc

            # Check if this comment is a reply
            parent_id = request.POST.get("parent_id")

            if parent_id:
                parent_comment = get_object_or_404(
                    Comment,
                    id=parent_id,
                    document=doc
                )

                comment.parent = parent_comment

            # Set logged-in user as author
            if request.user.is_authenticated:
                comment.author = request.user

            comment.save()

            return redirect(request.path)

    else:
        form = CommentForm()

    # Only top-level comments
    comments = (
        doc.comments
        .filter(parent__isnull=True)
        .order_by("-created_at")
    )

    return render(
        request,
        "documents/viewer.html",
        {
            "doc": doc,
            "comments": comments,
            "form": form,
            "is_shared": is_shared,
        }
    )
def pdf_file(request, pk):
    doc = get_object_or_404(PDFDocument, pk=pk)

    token = request.GET.get("token")

    # Allow the owner
    if request.user.is_authenticated and request.user == doc.owner:
        allowed = True

    # Allow anyone with the valid share token
    elif token and str(token) == str(doc.share_token):
        allowed = True

    else:
        allowed = False

    if not allowed:
        raise Http404("You do not have permission to access this PDF.")

    try:
        response = FileResponse(
            doc.file.open("rb"),
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'inline; filename="{doc.title}.pdf"'
        )

        return response

    except FileNotFoundError:
        raise Http404("PDF file not found.")
def chat(request,pk):
    doc=get_object_or_404(PDFDocument,pk=pk)
    token=request.GET.get("token")
    if not _access(request,doc) and str(doc.share_token)!=token: return JsonResponse({"error":"Unauthorized"},status=403)
    if request.method!="POST": return JsonResponse({"error":"POST required"},status=405)
    data=json.loads(request.body); question=data.get("question","").strip()
    if not question: return JsonResponse({"error":"Question required"},status=400)
    sid=_session(request)
    history=list(ChatMessage.objects.filter(document=doc,session_key=sid).order_by("-created_at")[:10])
    history=[(m.role,m.content) for m in reversed(history)]
    context=relevant_context(question,doc.extracted_text)
    try: answer=answer_question(question,context,history)
    except Exception as e: return JsonResponse({"error":str(e)},status=500)
    ChatMessage.objects.create(document=doc,session_key=sid,role="user",content=question)
    ChatMessage.objects.create(document=doc,session_key=sid,role="assistant",content=answer)
    return JsonResponse({"answer":answer})


def stream_chat(request, pk):

    doc = get_object_or_404(
        PDFDocument,
        pk=pk
    )

    token = request.GET.get("token")

    if (
        not _access(request, doc)
        and str(doc.share_token) != token
    ):
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403
        )

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405
        )

    data = json.loads(request.body)

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:
        return JsonResponse(
            {"error": "Question required"},
            status=400
        )

    sid = _session(request)

    history = list(
        ChatMessage.objects.filter(
            document=doc,
            session_key=sid
        )
        .order_by("-created_at")[:10]
    )

    history = [
        (message.role, message.content)
        for message in reversed(history)
    ]

    context = relevant_context(
        question,
        doc.extracted_text
    )

    # Save user question first
    ChatMessage.objects.create(
        document=doc,
        session_key=sid,
        role="user",
        content=question
    )

    def generate():

        full_answer = ""

        try:

            for chunk in stream_answer(
                question,
                context,
                history
            ):

                full_answer += chunk

                yield chunk

            # Save complete AI response
            ChatMessage.objects.create(
                document=doc,
                session_key=sid,
                role="assistant",
                content=full_answer
            )

        except Exception as e:

            yield f"\n\nError: {str(e)}"

    return StreamingHttpResponse(
        generate(),
        content_type="text/plain"
    )
