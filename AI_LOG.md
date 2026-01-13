# AI Decision Log

This log documents the collaboration between Human Developers and AI Assistants (Cursor/AntiGravity, ChatGPT) throughout the project lifecycle.

## 📋 development Log

| Phase | AI Tool | AI Suggestion | Final Human Decision | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **System Design** | ChatGPT | Use LangChain for RAG pipeline. | **Reject** | LangChain is too abstract for an undergrad project. We need to demonstrate understanding of the underlying logic (vectors, cosine sim). |
| **Architecture** | Cursor | Put all logic in `app.py` for simplicity. | **Modify** | Split into `modules/` (document_processor, vector_store) to ensure separation of concerns and testability. |
| **Parsing** | Cursor | Use `PyMuPDF` for advanced OCR. | **Reject** | `pypdf` is lighter and sufficient for text-based PDFs. We are not focusing on OCR. |
| **Chunking** | AntiGravity | Use Semantic Chunking (recursive). | **Modify** | Used simple **Character Spitting** (800 chars, 120 overlap). Recursive splitting is harder to visualize/explain in a basic demo. |
| **Embeddings** | ChatGPT | Use `text-embedding-ada-002`. | **Accept (Modified)** | Updated to `text-embedding-3-small`. It is cheaper and more efficient for student budgets. |
| **Vector DB** | AntiGravity | Use FAISS or ChromaDB. | **Reject** | Used `numpy` + `scikit-learn`. Configuring a Vector DB adds deployment complexity. In-memory `numpy` is explainable and sufficient for <50 docs. |
| **Prompting** | Cursor | "Answer the question based on context." | **Modify** | Added strict grounding: "Answer ONLY based on the provided sources. If unknown, say so." to reduce hallucinations. |
| **UI Design** | AntiGravity | Use default Streamlit layout. | **Modify** | Added custom CSS and a 2-column layout to make it look "Modern" and "Professional" as per project rules. |
| **Testing** | Cursor | Write unit tests for the API connection. | **Reject** | We mock the API connection in tests to avoid spending credits on CI/testing. |
| **Debug Mode** | Human | Create a "force failure" toggle. | **Accept** | Implemented `debug_force_wrong_citation` to satisfy the course requirement of "Intentional AI Failure". |

---

## 🚨 Intentional AI Failure (Debug Mode)

**Goal:** To demonstrate the limitations of LLMs when context is disregarded or "Creative Mode" is forced upon a RAG system.

1.  **What we Changed:**
    *   Added a toggle `debug_force_wrong_citation=True` in `llm_interface.py`.
    *   When active, the code **shuffles** the retrieved contexts (randomizing relevance).
    *   It injects a System Prompt: *"You are a creative writer. Ignore context if boring."*
    *   It increases Temperature to `0.9`.

2.  **The Failure (Wrong Output):**
    *   **Scenario:** Asked "What is the definition of an Expert System?" (present in the text).
    *   **Result:** The AI answered correctly but cited **"The AI Winter (1974)"** section as the source, which is completely irrelevant.
    *   **Detection:** The UI displays "Retrieved Contexts" alongside the answer. The user explicitly sees that *Source 1* does not contain the answer provided.

3.  **Mitigation:**
    *   In the real system (when flag is False), we enforce strict `Temperature=0.1` and use the prompt: *"Answer ONLY based on sources."*

---

## 🔒 Security, Privacy, Licensing

*   **Security:** API Keys are never hardcoded. They are loaded via `.env` (git-ignored) or entered temporarily in the UI session.
*   **Privacy:** Documents are processed logically in RAM. While OpenAI receives text chunks for embedding, no data is permanently stored on external vector databases.
*   **Licensing:** All project code is MIT Licensed. OpenAI models are subject to their usage policies (no generation of harmful content).
