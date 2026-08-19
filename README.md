# PDF Intelligence & Collaboration System

An AI-powered PDF intelligence and collaboration platform built with Django and PostgreSQL. Users can upload PDFs, generate AI summaries, ask questions grounded in document content, search documents semantically, share PDFs with others, collaborate through rich-text comments and threaded replies, and receive email invitations.

This project was developed as part of the **SpotDraft AI Engineering Intern Take-Home Assignment**.

---

## 🚀 Features

### 🔐 Authentication

- User registration
- Login and logout
- Password reset and account recovery
- Protected user dashboard
- Users can access only their own uploaded PDFs

---

## 📄 PDF Management

- Upload PDF documents
- PDF file validation
- Maximum upload size validation
- Extract text from uploaded PDFs
- View uploaded PDFs directly
- AI-generated summary for each PDF
- Document ownership and access control

---

## 🤖 AI PDF Intelligence

The application uses **Google Gemini** for AI-powered document understanding.

### AI Summary

After uploading a PDF:

1. Text is extracted using PyPDF2.
2. Document content is sent to Gemini.
3. Gemini generates a concise summary.

The summary focuses on:

- Document purpose
- Important facts
- Key obligations
- Important entities or dates
- Major conclusions

The AI is instructed not to invent information.

---

## 💬 Grounded AI Chat

Users can ask questions about an uploaded PDF.

The application:

1. Splits the PDF text into chunks.
2. Finds relevant chunks for the user's question.
3. Sends only relevant PDF context to the LLM.
4. Includes recent conversation history for follow-up questions.
5. Instructs Gemini to answer strictly from the provided document context.

If the answer is not present in the document, the AI is instructed to clearly state that the document does not provide that information.

---

## ⚡ Streaming AI Responses

AI responses are streamed to the chat interface instead of waiting for the complete response.

This provides:

- Faster perceived response time
- Real-time answer generation
- A more interactive chat experience

---

## 🔎 Semantic PDF Search

The dashboard supports both:

- Filename-based search
- Embedding-based semantic search

For semantic search:

1. PDF text is divided into overlapping chunks.
2. Each chunk is converted into an embedding using Gemini.
3. Embeddings are stored in PostgreSQL.
4. The search query is converted into an embedding.
5. Cosine similarity is calculated between the query and document chunks.
6. Documents are ranked based on their most relevant chunk.

This allows users to find PDFs based on their meaning rather than only their filename.

For example, searching:

> employment contract

can find a document titled:

> Agreement_v3.pdf

if its content is related to employment terms.

---

## 🔗 PDF Sharing

Users can share PDFs using a unique UUID-based share link.

Features include:

- Unique share tokens
- Copy share link functionality
- Shared document access
- Access control for document owners
- Secure PDF file access using share tokens

---

## 📧 Email Notifications

Users can share a PDF through email.

The recipient receives:

- Sender's username
- PDF title
- Link to access the shared document

For local development, Django's console email backend can be used.

For production, an SMTP email provider can be configured using environment variables.

---

## 💬 Collaboration and Comments

Users can collaborate on shared documents.

Features include:

- Logged-in user comments
- Guest comments on shared documents
- Comment author display
- Timestamps
- Threaded replies to existing comments

---

## ✍️ Rich Text Comments

Comments support basic formatting:

- **Bold text**
- *Italic text*
- Bullet points

User-generated HTML is sanitized using **Bleach** before rendering to help prevent unsafe HTML.

---

# 🛠 Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, Django |
| Database | PostgreSQL |
| AI | Google Gemini API |
| LLM Model | Gemini Flash |
| Embeddings | Gemini Embeddings |
| PDF Processing | PyPDF2 |
| Semantic Search | Embeddings, NumPy, Cosine Similarity |
| Frontend | Django Templates, HTML, CSS, JavaScript, Bootstrap |
| Rich Text Sanitization | Bleach |
| Environment Management | python-dotenv |
| Database URL Configuration | dj-database-url |
| Deployment Server | Gunicorn |

---

