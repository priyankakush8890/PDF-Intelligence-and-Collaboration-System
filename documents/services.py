import os, math, re
from collections import Counter
from PyPDF2 import PdfReader
import numpy as np


def get_embedding(text):
    from google import genai

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=key)

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values

def cosine_similarity(vector1, vector2):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    denominator = (
        np.linalg.norm(vector1)
        * np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 0

    return float(
        np.dot(vector1, vector2) / denominator
    )

def create_document_embeddings(document):
    from .models import PDFChunk

    # Delete old chunks if embeddings are regenerated
    document.chunks.all().delete()

    document_chunks = chunks(
        document.extracted_text,
        size=1200,
        overlap=200
    )

    for index, chunk_text in enumerate(document_chunks):

        if not chunk_text.strip():
            continue

        embedding = get_embedding(chunk_text)

        PDFChunk.objects.create(
            document=document,
            content=chunk_text,
            embedding=embedding,
            chunk_index=index
        )

def semantic_search(query, user, limit=10):
    from .models import PDFChunk

    query_embedding = get_embedding(query)

    chunks = PDFChunk.objects.filter(
        document__owner=user
    ).select_related("document")

    document_scores = {}

    for chunk in chunks:

        similarity = cosine_similarity(
            query_embedding,
            chunk.embedding
        )

        document_id = chunk.document.id

        # Keep the highest matching chunk
        # as the score for that PDF
        if (
            document_id not in document_scores
            or similarity > document_scores[document_id]["score"]
        ):
            document_scores[document_id] = {
                "document": chunk.document,
                "score": similarity,
                "matched_text": chunk.content[:250]
            }

    results = sorted(
        document_scores.values(),
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:limit]

def extract_pdf_text(path):
    reader=PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

def chunks(text, size=1400, overlap=200):
    text=re.sub(r"\s+"," ",text).strip()
    return [text[i:i+size] for i in range(0,len(text),max(1,size-overlap))]

def score(query, text):
    q=Counter(re.findall(r"\w+",query.lower()))
    d=Counter(re.findall(r"\w+",text.lower()))
    if not q or not d: return 0
    dot=sum(q[w]*d[w] for w in q)
    nq=math.sqrt(sum(v*v for v in q.values())); nd=math.sqrt(sum(v*v for v in d.values()))
    return dot/(nq*nd) if nq and nd else 0

def relevant_context(query, text, k=5):
    cs=chunks(text)
    ranked=sorted(cs,key=lambda c:score(query,c),reverse=True)[:k]
    return "\n\n---\n\n".join(ranked)

def gemini(prompt):
    from google import genai
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY is not configured.")
    client=genai.Client(api_key=key)
    response=client.models.generate_content(model="gemini-2.5-flash",contents=prompt)
    return response.text.strip()

def summarize(text):
    context=text[:45000]
    prompt=f'''You are a precise document analyst. Summarize the PDF below in 3-5 concise sentences.
Include the document's purpose, key obligations/facts, important entities or dates when present, and major conclusions.
Do not invent information. If information is missing, do not guess.

PDF:
{context}'''
    return gemini(prompt)

def answer_question(question, context, history):
    history_text="\n".join(f"{r.upper()}: {c}" for r,c in history)
    prompt=f'''You answer questions strictly using the provided PDF context.
If the answer is not supported by the context, clearly say that the document does not provide that information.
Be concise but useful. Follow-up questions should use the conversation history.

CONVERSATION HISTORY:
{history_text}

RELEVANT PDF CONTEXT:
{context}

USER QUESTION: {question}'''
    return gemini(prompt)

def stream_answer(question, context, history):
    """
    Generate the AI response in streaming mode.
    """

    from google import genai

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=key)

    history_text = "\n".join(
        f"{role.upper()}: {content}"
        for role, content in history
    )

    prompt = f"""
You answer questions strictly using the provided PDF context.

If the answer is not supported by the context, clearly say that
the document does not provide that information.

Be concise but useful. Follow-up questions should use the
conversation history.

CONVERSATION HISTORY:
{history_text}

RELEVANT PDF CONTEXT:
{context}

USER QUESTION:
{question}
"""

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt
    )

    for chunk in response:

        if chunk.text:
            yield chunk.text