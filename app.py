import io
import os
from typing import Optional

import streamlit as st
from PIL import Image
import google.generativeai as genai

# ------------- Page Config -------------
st.set_page_config(
    page_title="Ollam LLaVA Image Storyteller",
    page_icon="📖",
    layout="wide",
)

# ------------- Basic Styling -------------
# Soft gradient background and centered card-style main panel
page_bg = """
<style>
body {
    background: radial-gradient(circle at top left, #6b8bff 0, #8a5bff 35%, #5a3cff 70%, #2d175f 100%);
}
#root > div:nth-child(1) > div.withScreencast > div {
    padding-top: 1.5rem;
}
.main-card {
    background-color: #f9f7ff;
    border-radius: 24px;
    padding: 2.5rem 3rem;
    max-width: 1100px;
    margin: 0 auto 3rem auto;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
}
.section-card {
    background-color: #ffffff;
    border-radius: 18px;
    padding: 1.5rem 1.75rem;
    border: 1px solid #e5e0ff;
}
.upload-box {
    border: 2px dashed #c3b7ff !important;
    border-radius: 18px !important;
    padding: 1.75rem 1.5rem !important;
    background: #f5f3ff;
}
.stButton>button {
    width: 100%;
    border-radius: 999px;
    border: none;
    background: linear-gradient(90deg, #7c5cff, #ff6fd8);
    color: white;
    height: 3rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.stButton>button:disabled {
    background: #d2ccff;
    color: #7b739c;
}
.lang-pill {
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.83rem;
    font-weight: 600;
    margin-right: 0.4rem;
    border: 1px solid rgba(148, 163, 184, 0.7);
}
.lang-pill-active {
    background: #4f46e5;
    color: #ffffff;
    border-color: transparent;
}
.app-footer {
    font-size: 0.75rem;
    text-align: center;
    color: #d0cff5;
    margin-top: 1rem;
}
.app-footer a {
    color: #f5f3ff;
    text-decoration: underline;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------- Title Block -------------
st.markdown(
    """
<div class="main-card">
  <div style="text-align:center; margin-bottom: 1.75rem;">
    <h1 style="margin-bottom:0.3rem; font-size:2.3rem;">
      Ollam LLaVA Image Storyteller
    </h1>
    <p style="margin:0; font-size:0.95rem; color:#64748b;">
      Transform images into captivating multilingual stories with AI
    </p>
    <p style="margin-top:0.4rem; font-size:0.9rem; color:#4b5563; font-weight:600;">
      Developed by Atinkut Molla at UCAS, 2025
    </p>
  </div>
""",
    unsafe_allow_html=True,
)

# ------------- Sidebar: API configuration -------------
with st.sidebar:
    st.header("Story Engine Settings")
    st.caption(
        "This demo uses the same Gemini deployment configuration. "
        "If the shared key is unavailable, you may provide your own in "
        "`.streamlit/secrets.toml` as `GEMINI_API_KEY`."
    )
    
    # Allow manual API key input in sidebar for debugging
    api_key_input = st.text_input("Enter Gemini API Key (optional)", type="password", help="Leave empty to use secrets")
    if api_key_input:
        api_key = api_key_input
        st.success("Using manually entered API key")
    else:
        # Try to get API key from Streamlit secrets
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("Using API key from secrets")
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
        # Use the latest stable model - you can change this based on your needs
        model_name = "gemini-1.5-flash"
        # Alternative models to try if the above fails:
        # model_name = "gemini-1.0-pro"
        # model_name = "gemini-pro"
        
        model = genai.GenerativeModel(model_name)
        
        # Test the model configuration
        st.sidebar.info(f"Using model: {model_name}")
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
            "Do not describe the task, only tell the story."
        )
        
        img = Image.open(io.BytesIO(image_bytes))
        
        # Generate content with error handling
        try:
            response = model.generate_content(
                [prompt, img],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
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
  <h3 style="margin-top:0; margin-bottom:0.75rem;">Story Image</h3>
  <p style="font-size:0.85rem; color:#64748b; margin-bottom:0.75rem;">
    Upload an image to inspire your story. Supports JPG, PNG, and WebP up to 10 MB.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container():
        uploaded_file = st.file_uploader(
            "Upload an Image for Storytelling",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

    if uploaded_file is not None:
        st.markdown("#### Preview")
        # Check file size
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        if file_size > 10:
            st.error("File size exceeds 10 MB limit. Please upload a smaller image.")
        else:
            st.image(uploaded_file, use_column_width=True, caption=f"Story image ({file_size:.2f} MB)")

# --- Right: Generated Story with language tabs ---
with right_col:
    st.markdown(
        """
<div class="section-card">
  <h3 style="margin-top:0; margin-bottom:0.75rem;">Generated Story</h3>
  <p style="font-size:0.85rem; color:#64748b; margin-bottom:0.5rem;">
    Choose a language and let the storyteller craft your narrative.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Language selection
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
    )

    # Placeholder for the story text
    story_placeholder = st.empty()

    # Generate button
    generate_clicked = st.button(
        "Generate Story",
        type="primary",
        disabled=uploaded_file is None or not api_key,
    )

    if not api_key:
        st.warning(
            "No Gemini API Key found. Please add it in the sidebar or in `.streamlit/secrets.toml` file."
        )

    if generate_clicked and uploaded_file is not None and api_key:
        with st.spinner("Weaving your story..."):
            image_bytes = uploaded_file.getvalue()
            story_text = generate_story_from_image(
                image_bytes=image_bytes,
                language=lang_map[selected_lang],
                api_key=api_key
            )
        
        # Display the story with proper formatting
        story_placeholder.markdown(
            f"""
<div class="section-card" style="margin-top: 1rem;">
    <h4 style="margin-top:0; color:#4f46e5;">Your Story in {selected_lang}</h4>
    <div style="line-height: 1.6; font-size: 0.95rem;">
        {story_text}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        
        # Add copy to clipboard button
        if not story_text.startswith("Error"):
            st.code(story_text, language="text")
            
    else:
        story_placeholder.markdown(
            """
<div style="border-radius:18px; border:1px dashed #e5e7eb; padding:1.4rem;
            background:#f9fafb; text-align:center; color:#94a3b8;
            font-size:0.9rem;">
  Your story awaits. Upload an image and select a language, then click
  <strong>Generate Story</strong> to begin.
</div>
""",
            unsafe_allow_html=True,
        )

# ------------- Footer -------------
st.markdown(
    """
<div class="app-footer">
  Ollam LLaVA Storyteller • Developed by Atinkut Molla at UCAS, 2025<br/>
  Note: First story generation may take a little longer as the AI model loads.
</div>
</div>
""",
    unsafe_allow_html=True,
)
