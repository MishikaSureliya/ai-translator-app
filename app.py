import streamlit as st
from deep_translator import GoogleTranslator
import os
import time
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io

st.set_page_config(
    page_title="AI Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    if os.path.exists("style.css"):
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_intro_screen():
    st.markdown("""
        <div class="intro-container">
            <div class="intro-content">
                <span class="intro-emoji">🌍</span>
                <h1 class="typewriter">Welcome to AI-Powered Multi-Language<br>Translator</h1>
                <div class="loading-bar"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3.5)
    st.session_state.has_seen_intro = True
    st.rerun()

def transcribe_audio(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        audio_io = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_io) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "NO_SPEECH"
    except sr.RequestError as e:
        return f"ERROR:{e}"
    except Exception:
        try:
            recognizer2 = sr.Recognizer()
            audio_segment = sr.AudioData(audio_bytes, sample_rate=16000, sample_width=2)
            return recognizer2.recognize_google(audio_segment)
        except Exception as e2:
            return f"ERROR:{e2}"

def main():
    load_css()

    if 'has_seen_intro' not in st.session_state:
        st.session_state.has_seen_intro = False
    if not st.session_state.has_seen_intro:
        show_intro_screen()
        return

    # Init state
    for key, default in [
        ("input_text", ""),
        ("result", "Translation will appear here..."),
        ("last_audio_hash", None),
        ("voice_status", ""),
        ("textarea_key", 0),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    st.markdown('<div class="title">🌍 AI-Powered Multi-Language Translator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Translate text instantly using AI-based NLP precision</div>', unsafe_allow_html=True)

    supported_langs = GoogleTranslator().get_supported_languages(as_dict=True)
    lang_options = {k.title(): v for k, v in supported_langs.items()}
    default_index = list(lang_options.keys()).index("English") if "English" in lang_options else 0

    col1, padding, col2 = st.columns([10, 1, 10])

    with col1:
        st.markdown("### 📝 Source Text")

        # ✅ KEY FIX: use dynamic key (textarea_key counter) so widget fully re-renders when voice updates it
        user_text = st.text_area(
            "Input",
            value=st.session_state.input_text,
            height=220,
            label_visibility="collapsed",
            placeholder="Start typing, paste text, or use 🎤 Voice Input below...",
            key=f"source_text_{st.session_state.textarea_key}"
        )
        # Only update if user typed manually
        if user_text != st.session_state.input_text:
            st.session_state.input_text = user_text

        # Voice status
        if st.session_state.voice_status:
            if "✅" in st.session_state.voice_status:
                st.success(st.session_state.voice_status)
            elif "⚠" in st.session_state.voice_status:
                st.warning(st.session_state.voice_status)
            elif "❌" in st.session_state.voice_status:
                st.error(st.session_state.voice_status)

        st.markdown("""
        <style>
        div[data-testid="stCustomComponentV1"] iframe {
            border: none !important;
            height: 50px !important;
            width: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True)

        audio_bytes = audio_recorder(
            text="🔍 Voice Search — Click to speak",
            recording_color="#e74c3c",
            neutral_color="#4A00E0",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=3.0,
            sample_rate=16000,
            energy_threshold=0.01
        )

        if audio_bytes:
            audio_hash = hash(audio_bytes)
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                with st.spinner("🎙️ Converting speech to text..."):
                    result = transcribe_audio(audio_bytes)

                if result == "NO_SPEECH":
                    st.session_state.voice_status = "⚠️ No speech detected. Try again."
                elif result and result.startswith("ERROR:"):
                    st.session_state.voice_status = "❌ Recognition failed. Check internet connection."
                elif result:
                    # ✅ Set text AND increment key to force full textarea re-render
                    st.session_state.input_text = result
                    st.session_state.voice_status = f"✅ Heard: \"{result}\""
                    st.session_state.textarea_key += 1
                else:
                    st.session_state.voice_status = "⚠️ Could not understand. Try again."
                st.rerun()

        btn1, btn2 = st.columns(2)
        with btn1:
            translate = st.button("✨ Translate", use_container_width=True, type="primary")
        with btn2:
            if st.button("🗑️ Clear", use_container_width=True, type="secondary"):
                st.session_state.input_text = ""
                st.session_state.result = "Translation will appear here..."
                st.session_state.voice_status = ""
                st.session_state.textarea_key += 1
                st.rerun()

    with col2:
        st.markdown("### 🎯 Target Language & Output")
        target = st.selectbox(
            "Target Language",
            options=list(lang_options.keys()),
            index=default_index,
            label_visibility="collapsed"
        )

        if translate:
            text_to_translate = st.session_state.input_text.strip()
            if not text_to_translate:
                st.warning("⚠️ Please provide some text to translate.")
            else:
                with st.spinner("Analyzing and Translating..."):
                    try:
                        code = lang_options[target]
                        translator = GoogleTranslator(source='auto', target=code)
                        st.session_state.result = translator.translate(text_to_translate)
                        st.session_state.voice_status = ""
                    except Exception as e:
                        st.error("❌ Translation failed.")
                        st.caption(f"Error: {e}")

        st.markdown(f'<div class="output">{st.session_state.result}</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">Built with ❤️ using Streamlit & NLP</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
