import streamlit as st
import os
import shutil
import time
from dotenv import load_dotenv
from modules.document_processor import DocumentProcessor
from modules.vector_store import VectorStore
from modules.llm_interface import LLMInterface

# --- Configuration & Setup ---
load_dotenv()  # Load variables from .env file

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="PCC AI Assistant", layout="wide")

# --- Custom CSS for Modern Simple Look ---
st.markdown("""
<style>
    .stApp {
        background-color: #f9f9f9;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .main-header {
        font-weight: 700;
        color: #333;
        margin-bottom: 0px;
    }
    .sub-text {
        color: #666;
        font-size: 16px;
        margin-bottom: 20px;
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stToast {
        background-color: #e6fffa;
        color: #2c7a7b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'processor' not in st.session_state:
    st.session_state['processor'] = DocumentProcessor()
if 'vector_store' not in st.session_state:
    st.session_state['vector_store'] = VectorStore()
if 'documents_meta' not in st.session_state:
    st.session_state['documents_meta'] = {}  # {filename: summary}
if 'llm_interface' not in st.session_state:
    st.session_state['llm_interface'] = None

# Try auto-load key if not loaded
if st.session_state['llm_interface'] is None:
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        try:
            st.session_state['llm_interface'] = LLMInterface(api_key=env_key)
        except Exception as e:
            st.error(f"Error initializing from .env: {e}")

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=60)
    st.title("⚙️ Settings")

    # API Key Handling
    if st.session_state['llm_interface']:
        st.success("✅ OpenAI Connected")
        with st.expander("Change Key"):
             new_key = st.text_input("New API Key", type="password")
             if new_key:
                 st.session_state['llm_interface'] = LLMInterface(api_key=new_key)
                 st.rerun()
    else:
        st.warning("⚠️ No API Key Detected")
        user_key = st.text_input("Enter OpenAI Key", type="password")
        if user_key:
            try:
                st.session_state['llm_interface'] = LLMInterface(api_key=user_key)
                st.success("Key Loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Invalid Key: {e}")
        else:
            st.stop() # Stop execution if no key

    language = st.selectbox("Language", ["tr", "en"], index=0)
    top_k = st.slider("Retrieval Count (Top K)", 2, 8, 3)

    st.divider()
    
    # Upload Section
    st.header("1. Upload Documents")
    uploaded_file = st.file_uploader("PDF or TXT", type=['pdf', 'txt'], label_visibility="collapsed")
    
    if uploaded_file:
        if st.button("Process & Index", type="primary"):
            with st.spinner("Processing..."):
                try:
                    # 1. Save File
                    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 2. Extract Text (Deterministic)
                    doc = st.session_state['processor'].build_document(file_path)
                    
                    # 3. Create Chunks & Embeddings
                    chunks = st.session_state['processor'].chunk_text(doc.text)
                    embeddings = st.session_state['llm_interface'].embed_texts(chunks)
                    
                    # 4. Store Vector Data
                    st.session_state['vector_store'].add_document(
                        doc_id=doc.doc_id,
                        filename=doc.filename,
                        chunks=chunks,
                        embeddings=embeddings
                    )
                    
                    # 5. Generate Summary (Short)
                    summary = st.session_state['llm_interface'].summarize_short(doc.text, language=language)
                    st.session_state['documents_meta'][doc.filename] = summary
                    
                    # Feedback & Refund
                    st.toast(f"✅ Indexed: {doc.filename}", icon="🎉")
                    st.success("File Processed Successfully!")
                    time.sleep(1.0)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing file: {e}")

    # File Listing
    if st.session_state['documents_meta']:
        st.markdown("### 📂 Uploaded Files")
        for fname, summ in st.session_state['documents_meta'].items():
            with st.expander(f"📄 {fname}"):
                st.caption(summ)

# --- Main Interface ---
st.markdown("<h1 class='main-header'>🎓 Document Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Search, ask questions, and analyze with AI.</p>", unsafe_allow_html=True)

if not st.session_state['documents_meta']:
    st.info("👋 Welcome! Please upload a PDF or TXT file in the sidebar to get started.")
else:
    tab1, tab2, tab3 = st.tabs(["🔎 Search", "💬 Q & A", "🛠️ Debug Mode"])
    
    # --- TAB 1: Search ---
    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**Search Options**")
            search_type = st.radio("Type", ["Semantic (AI)", "Keyword (Exact)"], label_visibility="collapsed")
        
        with col2:
            query = st.text_input("Search query...", placeholder="e.g. 'Neural Networks'")
        
        if query:
            st.markdown("### Results")
            results = []
            
            if search_type == "Keyword (Exact)":
                # Linear scan of all chunks
                for chunk in st.session_state['vector_store'].chunks:
                    if query.lower() in chunk['chunk_text'].lower():
                        results.append(chunk)
                results = results[:top_k] # Limit display
            else:
                # Vector Search
                q_vec = st.session_state['llm_interface'].embed_query(query)
                if q_vec:
                    results = st.session_state['vector_store'].search(q_vec, top_k=top_k)
            
            if not results:
                st.warning("No matches found.")
            else:
                for req in results:
                    score_display = f"(Relevance: {req.get('score', 0):.2f})" if 'score' in req else ""
                    with st.container():
                        st.markdown(f"**📄 {req['filename']}** {score_display}")
                        st.info(req['chunk_text'])

    # --- TAB 2: Q&A ---
    with tab2:
        st.caption("Ask questions based on your uploaded documents.")
        
        # Chat Input
        user_question = st.chat_input("Ask a question...")
        
        if user_question:
            # Show User Question
            with st.chat_message("user"):
                st.write(user_question)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing documents..."):
                    # 1. Retrieve Contexts
                    q_vec = st.session_state['llm_interface'].embed_query(user_question)
                    contexts = st.session_state['vector_store'].search(q_vec, top_k=top_k)
                    
                    # 2. Generate Answer
                    response = st.session_state['llm_interface'].answer_question(
                        question=user_question,
                        contexts=contexts,
                        language=language
                    )
                    
                    # 3. Display Answer
                    st.write(response['answer'])
                    
                    # 4. Display Citations
                    with st.expander("📚 Sources Used"):
                        if not response['citations']:
                            st.write("No relevant documents found.")
                        else:
                            for idx, cit in enumerate(response['citations']):
                                st.markdown(f"**{idx+1}. {cit['filename']}** (Score: {cit.get('score', 0):.2f})")
                                st.text(cit['chunk_text'])

    # --- TAB 3: Debug (Intentional Failure) ---
    with tab3:
        st.error("🚨 Intentional AI Failure Mode (For Report)")
        st.write("This mode forces the AI to ignore the correct context or behave erratically, allowing you to document 'hallucinations'.")
        
        force_fail = st.toggle("Activate Failure Mode", value=False)
        
        debug_q = st.text_input("Test Question", value="What is the main topic?")
        
        if st.button("Run Test"):
            with st.spinner("Running simulation..."):
                # 1. Retrieve Normal Contexts
                q_vec = st.session_state['llm_interface'].embed_query(debug_q)
                contexts = st.session_state['vector_store'].search(q_vec, top_k=3)
                
                # 2. Call LLM with forced failure flag
                res = st.session_state['llm_interface'].answer_question(
                    question=debug_q,
                    contexts=contexts,
                    language=language,
                    debug_force_wrong_citation=force_fail
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("AI Output")
                    st.write(res['answer'])
                
                with col2:
                    st.subheader("Retrieved Contexts")
                    # Show exactly what was sent (which might be shuffled/corrupted if flag is on)
                    st.json([{
                        "file": c['filename'], 
                        "text": c['chunk_text'][:200]+"..." 
                    } for c in contexts])
                
                if force_fail:
                    st.warning("⚠️ Note: Contexts may have been shuffled or ignored by the Prompt Injection.")
