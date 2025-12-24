import io
import os
from typing import Optional

import streamlit as st
from PIL import Image
import google.generativeai as genai

# ------------- Page Config -------------
st.set_page_config(
    page_title="Image Storytelling Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------- Attractive Dark Mode Styling -------------
page_bg = """
<style>
    /* Main dark gradient background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        min-height: 100vh;
    }
    
    /* Hide Streamlit default elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Main card styling */
    .main-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        backdrop-filter: blur(20px);
        border-radius: 28px;
        padding: 3rem 4rem;
        max-width: 1200px;
        margin: 2rem auto;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    }
    
    /* Section card styling */
    .section-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .section-card:hover {
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }
    
    /* Upload box styling */
    .upload-box {
        border: 3px dashed rgba(139, 92, 246, 0.4) !important;
        border-radius: 20px !important;
        padding: 3rem 2rem !important;
        background: rgba(15, 23, 42, 0.5);
        text-align: center;
        transition: all 0.3s ease;
        margin: 1.5rem 0;
    }
    .upload-box:hover {
        border-color: rgba(168, 85, 247, 0.6) !important;
        background: rgba(15, 23, 42, 0.6);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 16px;
        border: none;
        background: linear-gradient(90deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%);
        color: white;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        margin-top: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        background: linear-gradient(90deg, #7c3aed 0%, #4f46e5 50%, #2563eb 100%);
    }
    .stButton>button:disabled {
        background: linear-gradient(90deg, #475569 0%, #334155 50%, #1e293b 100%);
        box-shadow: none;
    }
    
    /* Language tabs/pills */
    .stRadio [role="radiogroup"] {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 0.5rem;
        margin: 1.5rem 0;
    }
    .stRadio [role="radiogroup"] label {
        background: transparent !important;
        color: #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        margin: 0 0.25rem !important;
        border: 1px solid transparent !important;
        transition: all 0.3s ease !important;
    }
    .stRadio [role="radiogroup"] label:hover {
        background: rgba(99, 102, 241, 0.1) !important;
    }
    .stRadio [role="radiogroup"] [data-testid="stRadio"]:first-child {
        margin-left: 0;
    }
    .stRadio [role="radiogroup"] div[data-testid="stMarkdownContainer"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Selected language styling */
    .stRadio [role="radiogroup"] label[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(90deg, #e2e8f0 0%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Footer styling */
    .app-footer {
        font-size: 0.85rem;
        text-align: center;
        color: #94a3b8;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(99, 102, 241, 0.2);
    }
    .app-footer a {
        color: #c7d2fe;
        text-decoration: none;
        font-weight: 600;
    }
    .app-footer a:hover {
        text-decoration: underline;
    }
    
    /* File uploader customization */
    [data-testid="stFileUploader"] {
        width: 100%;
    }
    [data-testid="stFileUploader"] section {
        padding: 0;
        border: none;
    }
    [data-testid="stFileUploader"] section > div {
        flex-direction: column;
        gap: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        margin-top: 1rem;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-color: #8b5cf6 transparent transparent transparent;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.8);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b5cf6 0%, #6366f1 100%);
        border-radius: 10px;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------- Title Block -------------
st.markdown(
    """
<div class="main-card">
  <div style="text-align:center; margin-bottom: 2.5rem;">
    <div style="display: inline-block; padding: 0.5rem 2rem; background: rgba(99, 102, 241, 0.1); border-radius: 20px; margin-bottom: 1rem;">
      <span style="color: #c7d2fe; font-size: 0.9rem; font-weight: 600;">✨ AI-Powered Storytelling</span>
    </div>
    <h1 style="margin-bottom:0.5rem; font-size:3rem; font-weight:800; letter-spacing:-0.5px;">
      Transform images into captivating<br>multilingual stories with AI
    </h1>
    <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem;">
      <div style="height: 2px; width: 80px; background: linear-gradient(90deg, transparent, #8b5cf6, transparent);"></div>
      <p style="margin:0; font-size:1rem; color:#94a3b8; font-weight:500;">
        Developed by Atinkut Molla at UCAS, 2025
      </p>
      <div style="height: 2px; width: 80px; background: linear-gradient(90deg, transparent, #8b5cf6, transparent);"></div>
    </div>
  </div>
""",
    unsafe_allow_html=True,
)

# ------------- Sidebar: API configuration -------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 16px; margin-bottom: 2rem;">
            <h3 style="margin-top:0; color:#e2e8f0;">🔧 Story Engine Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption(
        "This demo uses the same Gemini deployment configuration. "
        "If the shared key is unavailable, you may provide your own in "
        "`.streamlit/secrets.toml` as `GEMINI_API_KEY`."
    )
    
    # Allow manual API key input in sidebar for debugging
    api_key_input = st.text_input("Enter Gemini API Key (optional)", 
                                 type="password", 
                                 help="Leave empty to use secrets",
                                 key="api_key_input")
    
    if api_key_input:
        api_key = api_key_input
        st.success("✓ Using manually entered API key")
    else:
        # Try to get API key from Streamlit secrets
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✓ Using API key from secrets")
        except Exception as e:
            api_key = None
            st.error(f"API key not found in secrets: {e}")

# ------------- Gemini Setup -------------
@st.cache_resource(show_spinner=False)
def get_story_model(api_key: str):
    """Initialize Gemini model with API key"""
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Use the latest stable model
        model_name = "gemini-flash-latest"
        
        model = genai.GenerativeModel(model_name)
        
        # Test the model configuration
        st.sidebar.info(f"🤖 Using model: {model_name}")
        return model
    except Exception as e:
        st.sidebar.error(f"Failed to initialize model: {str(e)}")
        return None


def generate_story_from_image(
    image_bytes: bytes,
    language: str,
    api_key: str
) -> str:
    """Call Gemini to generate a story given an image and target language."""
    try:
        model = get_story_model(api_key)
        if not model:
            return "Error: Model not initialized. Please check your API key."
        
        prompt = (
            "You are an imaginative storyteller. "
            "Look at the image and write a short, vivid narrative (about 3–5 paragraphs). "
            f"Write the story entirely in {language}. "
            "Do not describe the task, only tell the story. "
            "Make it engaging, emotional, and memorable."
        )
        
        img = Image.open(io.BytesIO(image_bytes))
        
        # Generate content with error handling
        try:
            response = model.generate_content(
                [prompt, img],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
            
            # Check if response has valid text
            if response and hasattr(response, 'text'):
                return response.text.strip()
            else:
                return "Error: Empty response from AI model."
                
        except Exception as gen_error:
            return f"Error generating story: {str(gen_error)}"
            
    except Exception as e:
        return f"Error: {str(e)}"


# ------------- Layout: Left / Right panels -------------
left_col, right_col = st.columns(2, gap="large")

# --- Left: Story Image Upload ---
with left_col:
    st.markdown(
        """
<div class="section-card">
  <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
    <div style="background: rgba(139, 92, 246, 0.2); padding: 0.5rem; border-radius: 12px;">
      <span style="color: #8b5cf6; font-size: 1.5rem;">🖼️</span>
    </div>
    <div>
      <h3 style="margin:0; color:#e2e8f0;">Story Image</h3>
      <p style="margin:0; font-size:0.9rem; color:#94a3b8;">
        Upload an image to inspire your story. Supports JPG, PNG, and WebP up to 10 MB.
      </p>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Custom upload area
    st.markdown("""
        <div class="upload-box">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
            <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Drag & drop your image here</h4>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
                Limit 10MB per file • JPG, JPEG, PNG, WEBP
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        uploaded_file = st.file_uploader(
            "Upload an Image for Storytelling",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="file_uploader"
        )

    if uploaded_file is not None:
        st.markdown("#### 📸 Image Preview")
        # Check file size
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        if file_size > 10:
            st.error("⚠️ File size exceeds 10 MB limit. Please upload a smaller image.")
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(uploaded_file, 
                        use_column_width=True, 
                        caption=f"Uploaded image • {file_size:.2f} MB",
                        output_format="auto")
            
            st.markdown(f"""
                <div style="background: rgba(34, 197, 94, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #22c55e;">
                    <p style="margin:0; color:#86efac; font-size:0.9rem;">
                        ✓ Image uploaded successfully! Now select a language and generate your story.
                    </p>
                </div>
            """, unsafe_allow_html=True)

# --- Right: Generated Story with language tabs ---
with right_col:
    st.markdown(
        """
<div class="section-card">
  <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
    <div style="background: rgba(59, 130, 246, 0.2); padding: 0.5rem; border-radius: 12px;">
      <span style="color: #3b82f6; font-size: 1.5rem;">📝</span>
    </div>
    <div>
      <h3 style="margin:0; color:#e2e8f0;">Generated Story</h3>
      <p style="margin:0; font-size:0.9rem; color:#94a3b8;">
        Choose a language and let the storyteller craft your narrative.
      </p>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Language selection with attractive styling
    st.markdown("""
        <div style="margin: 1.5rem 0 0.5rem 0;">
            <p style="color: #cbd5e1; font-size: 0.95rem; font-weight: 600; margin-bottom: 0.75rem;">
                Select Story Language:
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    lang_tabs = ["English", "Amharic", "Chinese"]
    lang_map = {
        "English": "English",
        "Amharic": "Amharic",
        "Chinese": "Chinese",
    }

    selected_lang = st.radio(
        "Language",
        lang_tabs,
        horizontal=True,
        label_visibility="collapsed",
        key="language_radio"
    )

    # Placeholder for the story text
    story_placeholder = st.empty()

    # Generate button with icon
    generate_clicked = st.button(
        "🚀 Generate Story",
        type="primary",
        disabled=uploaded_file is None or not api_key,
        key="generate_button"
    )

    if not api_key:
        st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #ef4444; margin-top: 1.5rem;">
                <p style="margin:0; color:#fca5a5; font-size:0.9rem;">
                    ⚠️ No Gemini API Key found. Please add it in the sidebar or in <code>.streamlit/secrets.toml</code> file.
                </p>
            </div>
        """, unsafe_allow_html=True)

    if generate_clicked and uploaded_file is not None and api_key:
        with st.spinner("✨ Weaving your story... This may take a moment."):
            image_bytes = uploaded_file.getvalue()
            story_text = generate_story_from_image(
                image_bytes=image_bytes,
                language=lang_map[selected_lang],
                api_key=api_key
            )
        
        # Display the story with proper formatting
        if story_text.startswith("Error"):
            st.error(story_text)
        else:
            story_placeholder.markdown(
                f"""
<div class="section-card" style="margin-top: 1.5rem; animation: fadeIn 0.5s ease;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="margin:0; color:#e2e8f0;">
            📖 Your Story in {selected_lang}
        </h4>
        <div style="background: rgba(34, 197, 94, 0.2); padding: 0.25rem 0.75rem; border-radius: 12px;">
            <span style="color:#86efac; font-size:0.8rem; font-weight:600;">AI Generated</span>
        </div>
    </div>
    <div style="line-height: 1.8; font-size: 1rem; color:#cbd5e1; background: rgba(15, 23, 42, 0.5); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #8b5cf6;">
        {story_text.replace('\n', '<br>')}
    </div>
</div>
<style>
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>
""",
                unsafe_allow_html=True,
            )
            
            # Add copy to clipboard button
            st.code(story_text, language="text")
            
            st.markdown("""
                <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
                    <button style="background: rgba(99, 102, 241, 0.2); color: #c7d2fe; border: 1px solid #6366f1; padding: 0.5rem 1.5rem; border-radius: 12px; cursor: pointer;">
                        📋 Copy Story
                    </button>
                    <button style="background: rgba(139, 92, 246, 0.2); color: #c7d2fe; border: 1px solid #8b5cf6; padding: 0.5rem 1.5rem; border-radius: 12px; cursor: pointer;">
                        💾 Save as PDF
                    </button>
                </div>
            """, unsafe_allow_html=True)
            
    else:
        story_placeholder.markdown(
            """
<div style="border-radius:20px; border:2px dashed rgba(99, 102, 241, 0.3); padding:3rem 2rem;
            background: rgba(15, 23, 42, 0.5); text-align:center; color:#94a3b8;
            font-size:0.95rem; margin-top: 1.5rem;">
  <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
  <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Your story awaits</h4>
  <p style="margin:0; color:#94a3b8;">
    Upload an image and select a language, then click
    <span style="color:#c7d2fe; font-weight:600;">Generate Story</span> to begin your magical journey.
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

# ------------- Footer -------------
st.markdown(
    """
<div class="app-footer">
    <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
        <div style="width: 40px; height: 1px; background: linear-gradient(90deg, transparent, #8b5cf6, transparent);"></div>
        <span style="color: #c7d2fe;">✨</span>
        <div style="width: 40px; height: 1px; background: linear-gradient(90deg, transparent, #8b5cf6, transparent);"></div>
    </div>
    <div>
        <strong>Image Storytelling Generator</strong> • Developed by Atinkut Molla at UCAS, 2025<br/>
        <span style="font-size: 0.8rem; color: #64748b;">
            Powered by Gemini AI • First story generation may take a moment as the AI model loads
        </span>
    </div>
</div>
</div>
""",
    unsafe_allow_html=True,
)
