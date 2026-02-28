import streamlit as st
from deep_translator import GoogleTranslator
import os

# ----------------------------------------
# 1. PAGE CONFIGURATION
# ----------------------------------------
st.set_page_config(
    page_title="AI Translator", 
    page_icon="🌍", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ----------------------------------------
# 2. LOAD EXTERNAL CSS
# ----------------------------------------
def load_css(file_name):
    """Utility function to read and inject an external CSS file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ----------------------------------------
# 3. MAIN APPLICATION LOGIC
# ----------------------------------------
def main():
    # Load the custom styles securely
    if os.path.exists("style.css"):
        load_css("style.css")
    
    # Header and Subtitle (rendered with RAW HTML to apply custom classes)
    st.markdown('<h1>🌍 AI-Powered Multi-Language Translator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Translate text instantly using AI-based NLP precision</p>', unsafe_allow_html=True)
    
    # Initialize the supported languages dynamically via deep-translator
    # Using 'deep-translator' ensures maximum Python 3.13+ compatibility unlike deprecated googletrans 
    supported_langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    lang_options = {name.title(): code for name, code in supported_langs_dict.items()}
    default_index = list(lang_options.keys()).index("English") if "English" in lang_options else 0

    # Manage text fields via Streamlit session_state
    if 'source_text' not in st.session_state:
        st.session_state.source_text = ""
    if 'translation_result' not in st.session_state:
        st.session_state.translation_result = "Translation will appear here..."

    # Create the main content card layout container
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # Two-column Layout: Left (Input) | Right (Output)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Source Text")
            # Text area bounded to session_state so we can clear it easily
            st.session_state.source_text = st.text_area(
                "Input text", 
                value=st.session_state.source_text,
                height=250, 
                placeholder="Start typing or paste your text here...", 
                label_visibility="collapsed" 
            )
            
            # Action buttons row
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                translate_btn = st.button("✨ Translate", type="primary", use_container_width=True)
            with btn_col2:
                # Clear button resets session state logic
                if st.button("🗑️ Clear", type="secondary", use_container_width=True):
                    st.session_state.source_text = ""
                    st.session_state.translation_result = "Translation will appear here..."
                    st.rerun() # Refresh the page to clear the UI
                    
        with col2:
            st.markdown("### 🎯 Target Language & Output")
            target_language_name = st.selectbox(
                "Select language", 
                options=list(lang_options.keys()), 
                index=default_index, 
                label_visibility="collapsed"
            )
            
            # Translation Execution logic tied to button click
            if translate_btn:
                # Handle empty input gracefully
                if not st.session_state.source_text.strip():
                    st.warning("⚠️ Please provide some text to translate in the left column.")
                else:
                    try:
                        # Required Loading spinner while NLP backend translates
                        with st.spinner("Analyzing NLP Model and Translating..."):
                            target_code = lang_options[target_language_name]
                            translator = GoogleTranslator(source='auto', target=target_code)
                            st.session_state.translation_result = translator.translate(st.session_state.source_text)
                            st.success(f"✅ Context translated to {target_language_name} successfully!")
                    except Exception as e:
                        st.error("❌ Translation failed. Please check your network connection.")
                        st.caption(f"Error log: {e}")

            # Display Output Result Box
            st.markdown(f'<div class="translation-output">{st.session_state.translation_result}</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True) # Close main-card container

    # Footer Section
    st.markdown('<div class="footer">Built with ❤️ using Streamlit & NLP</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
