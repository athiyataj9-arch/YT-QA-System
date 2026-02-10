import streamlit as st
import requests, re

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="VidWhisper | Video Intelligence", page_icon="🎥", layout="wide")

# --- INTERFACE STYLING ---
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.92)), 
                    url('https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070&auto=format&fit=crop'); 
        background-size: cover; 
        background-attachment: fixed; 
        color: #f0f2f6; 
    }
    .main .block-container { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(12px); 
        border-radius: 24px; 
        padding: 40px; 
        border: 1px solid rgba(255,255,255,0.1); 
        margin-top: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
    }
    [data-testid="stSidebar"] { 
        background-color: rgba(20, 20, 20, 0.7) !important; 
        backdrop-filter: blur(10px); 
        border-right: 1px solid rgba(255,255,255,0.05); 
    }
    .brand-title { 
        font-size: 2rem; 
        font-weight: 700; 
        background: linear-gradient(90deg, #FF4B4B, #FF8E8E); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }
    div.stButton > button { 
        background-color: #FF4B4B !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 8px !important; 
        width: 100%; 
        font-weight: 600 !important; 
        transition: 0.3s all ease; 
    }
    div.stButton > button:hover { 
        background-color: #FF3333 !important; 
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4); 
        transform: translateY(-1px); 
    }
    .time-pill { 
        color: #FF4B4B !important; 
        background: rgba(255, 255, 255, 0.07); 
        padding: 4px 10px; 
        border-radius: 6px; 
        text-decoration: none; 
        font-weight: 500; 
        border: 1px solid rgba(255, 75, 75, 0.4); 
        display: inline-block;
        margin: 2px;
    }
    .time-pill:hover { background: #FF4B4B; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- UTILS ---
def link_timestamps(text, vid_url):
    vid_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", vid_url)
    if not vid_match: return text
    vid_id = vid_match.group(1)
    def repl(m):
        sec = int(m.group(1))*60 + int(m.group(2))
        return f'<a href="https://youtu.be/{vid_id}?t={sec}" class="time-pill">▶ {m.group(1)}:{m.group(2)}</a>'
    return re.sub(r"\[(\d+):(\d{2})\]", repl, text)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<p class="brand-title">VidWhisper</p><p style="color: grey; font-size: 0.8em; margin-top:-15px;">Video Intelligence</p><hr>', unsafe_allow_html=True)
    yt_url = st.text_input("YouTube URL", placeholder="https://...")
    
    if st.button("Process Video") and yt_url:
        with st.spinner("Analyzing..."):
            try:
                res = requests.post(f"{API_URL}/load_video", json={"url": yt_url})
                if res.status_code == 200:
                    st.session_state.update({"ready": True, "url": yt_url, "chat": []})
                    st.success("✅ Analysis Complete")
                else: st.error("Failed to load video.")
            except: st.error("Backend offline.")

# --- MAIN UI ---
st.markdown("<h2 style='text-align: center; font-weight: 300;'>Interactive Video Dialogue</h2>", unsafe_allow_html=True)

if not st.session_state.get("ready"):
    st.markdown("<div style='text-align:center; margin-top:100px; color: rgba(255,255,255,0.4);'><h3>System Standby</h3><p>Enter a URL to begin.</p></div>", unsafe_allow_html=True)
else:
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)

    if q := st.chat_input("Ask about this video..."):
        st.session_state.chat.append({"role": "user", "content": q})
        with st.chat_message("user"): st.write(q)

        with st.chat_message("assistant"):
            # --- PERSONALITY LAYER ---
            thanks_keywords = ["thank you", "thanks", "thx", "appreciate", "great job"]
            hello_keywords = ["hello", "hi ", "hey "]
            
            if any(word in q.lower() for word in thanks_keywords):
                response = "You're very welcome! 😊 I'm happy to help you navigate this video. What else would you like to know?"
            elif any(word in q.lower() for word in hello_keywords):
                response = "Hello! 👋 I'm ready to analyze this video for you. Ask me anything about the content!"
            else:
                # --- STANDARD API CALL ---
                try:
                    res = requests.post(f"{API_URL}/ask", json={"question": q})
                    response = link_timestamps(res.json()["answer"], st.session_state.url) if res.status_code == 200 else "Engine failed."
                except: response = "Communication error."
            
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.chat.append({"role": "assistant", "content": response})