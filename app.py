import streamlit as st
from deep_translator import GoogleTranslator
import os
import time

st.set_page_config(
    page_title="AI Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    """Securely injects custom CSS."""
    if os.path.exists("style.css"):
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_intro_screen():
    """Displays the beautiful animated intro screen."""
    st.markdown(
        """
        <div class="intro-container">
            <div class="intro-content">
                <span class="intro-emoji">🌍</span>
                <h1 class="typewriter">Welcome to AI-Powered Multi-Language<br>Translator</h1>
                <div class="loading-bar"></div>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Pause for 3.5 seconds to let the animations play out
    time.sleep(3.5)
    
    # Update session state and force a smooth UI rerun
    st.session_state.has_seen_intro = True
    st.rerun()

def main():
    # 1. Load generic global styles first
    load_css()
    
    # 2. Track Session State for the Intro Animation 
    # Ensures it only plays once per browser session
    if 'has_seen_intro' not in st.session_state:
        st.session_state.has_seen_intro = False
        
    # 3. Check if we need to show the animation
    if not st.session_state.has_seen_intro:
        show_intro_screen()
        return # Halt main execution until intro finishes
    
    # ---------------------------------------------------------
    # 4. MAIN APPLICATION UI 
    # ---------------------------------------------------------

    # Header and Subtitle 
    st.markdown('<div class="title">🌍 AI-Powered Multi-Language Translator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Translate text instantly using AI-based NLP precision</div>', unsafe_allow_html=True)

    # Load Supported Languages dynamically
    supported_langs = GoogleTranslator().get_supported_languages(as_dict=True)
    lang_options = {k.title(): v for k, v in supported_langs.items()}
    default_index = list(lang_options.keys()).index("English") if "English" in lang_options else 0

    # Ensure memory states persist visually
    if "source_text" not in st.session_state:
        st.session_state.source_text = ""
    if "result" not in st.session_state:
        st.session_state.result = "Translation will appear here..."

    # Use Streamlit's Native Column Grid Layout - No Broken HTML Containers!
    col1, padding, col2 = st.columns([10, 1, 10])

    with col1:
        st.markdown("### 📝 Source Text")
        st.session_state.source_text = st.text_area(
            "Input",
            value=st.session_state.source_text,
            height=260,
            label_visibility="collapsed",
            placeholder="Start typing or paste your text here..."
        )

        # Interactive Button Layouts
        btn1, btn2 = st.columns(2)
        with btn1:
            translate = st.button("✨ Translate", use_container_width=True, type="primary")
        with btn2:
            if st.button("🗑️ Clear", use_container_width=True, type="secondary"):
                st.session_state.source_text = ""
                st.session_state.result = "Translation will appear here..."
                st.rerun()

    with col2:
        st.markdown("### 🎯 Target Language & Output")
        target = st.selectbox(
            "Target Language",
            options=list(lang_options.keys()),
            index=default_index,
            label_visibility="collapsed"
        )

        # Render translations
        if translate:
            if not st.session_state.source_text.strip():
                st.warning("⚠️ Please provide some text to translate in the left column.")
            else:
                with st.spinner("Analyzing and Translating..."):
                    try:
                        code = lang_options[target]
                        translator = GoogleTranslator(source='auto', target=code)
                        st.session_state.result = translator.translate(st.session_state.source_text)
                    except Exception as e:
                        st.error("❌ Translation failed. Please check your network connection.")
                        st.caption(f"Error log: {e}")

        # Render Output Block cleanly mapped to CSS class
        st.markdown(f'<div class="output">{st.session_state.result}</div>', unsafe_allow_html=True)

    # Unbroken Footer
    st.markdown('<div class="footer">Built with ❤️ using Streamlit & NLP</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
