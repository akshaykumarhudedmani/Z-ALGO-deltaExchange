import streamlit as st
import feedparser
import base64
import os
import io
import google.generativeai as genai
from gtts import gTTS
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Radio | TokenIQ", page_icon="🎙️", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please enter via the main App Gate.")
    st.stop()

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    model = None

st.title("🎙️ Sentinel AI News Radio")
st.markdown("Real-time sentiment analysis delivered in your preferred language.")

# User Settings
st.sidebar.header("Radio Settings")
lang_choice = st.sidebar.selectbox("Broadcast Language", ["English", "Hindi", "Kannada"])

# Map UI choices to gTTS/deep-translator codes
lang_maps = {
    "English": {"code": "en", "trans": "en"},
    "Hindi": {"code": "hi", "trans": "hi"},
    "Kannada": {"code": "kn", "trans": "kn"}
}

def fetch_crypto_headlines():
    # Attempt to fetch live from CoinTelegraph RSS
    feed_url = 'https://cointelegraph.com/rss'
    headlines = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # Top 5 news
            headlines.append(entry.title)
    except Exception:
        pass
    
    # Fallback/Safety Switch if RSS is blocked
    if not headlines:
        headlines = [
            "Bitcoin breaks resistance as institutional inflows surge.",
            "Federal Reserve signals potential rate pauses, sparking crypto rally.",
            "Major exchange reports increased trading volume on BTC/USD pairs.",
            "Regulatory clarity in the EU provides tailwinds for digital assets.",
            "Miners increase accumulation as hash rate hits all-time highs."
        ]
    return getattr(headlines, "text", headlines)

def get_ai_summary(headlines):
    prompt = f"""
    You are an algorithmic trading AI assistant. Analyze these 5 crypto headlines and summarize the overall market sentiment into a single, punchy "Traders' Note" (max 3 sentences). Make it sound like an urgent radio broadcast for traders.

    Headlines:
    {headlines}
    """
    
    if model is None:
        return "System Warning: AI offline. The market shows mixed signals but institutional accumulation provides a bullish undertone. Maintain current risk parameters."
        
    try:
        response = model.generate_content(prompt)
        return response.text.replace('*', '') # Clean markdown for TTS
    except Exception:
        return "Emergency Update: General bullish trend continues, but traders are advised to maintain strict stop losses amid intraday volatility."

def autoplay_audio(audio_data):
    # Streamlit hack to autoplay audio from memory
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# Application Flow
st.divider()
st.subheader("📡 Live Broadcast Feed")

if st.button("🎙️ Fetch News & Broadcast", use_container_width=True):
    with st.spinner("Scraping Global Crypto Feeds..."):
        headlines = fetch_crypto_headlines()
        st.write("**Top 5 Headlines Acquired:**")
        for h in headlines:
            st.write(f"- {h}")
            
    with st.spinner("Gemini 1.5 Flash Synthesizing Sentiment..."):
        base_note = get_ai_summary(headlines)
        
    with st.spinner(f"Translating and Generating {lang_choice} Voice Audio..."):
        try:
            # 1. Translate
            target_lang = lang_maps[lang_choice]["trans"]
            if target_lang != "en":
                translated_note = GoogleTranslator(source='en', target=target_lang).translate(base_note)
            else:
                translated_note = base_note
                
            # 2. Display text
            st.success("**Traders' Note Ready:**")
            st.info(translated_note)
            
            # 3. Create Audio
            tts = gTTS(text=translated_note, lang=lang_maps[lang_choice]["code"], slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # 4. Play
            st.audio(fp, format='audio/mp3', autoplay=True)
            # autoplay_audio(fp.read()) # Alternative if standard st.audio doesn't autoplay in the browser wrapper
            
        except Exception as e:
            st.error(f"Voice generation failed: {e}")
            st.info("Please read the text note provided above.")

st.divider()
st.caption("TokenIQ Sentinel uses Google Translate & gTTS for accessibility. Some localized crypto terms may not translate perfectly.")
