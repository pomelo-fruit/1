import streamlit as st
from openai import OpenAI
import os
import time
import random

stickers = [
    "https://i.imgur.com/kKmtm7N.mp4", #otters napping
    "https://i.imgur.com/34bPRtb.mp4", #happy otter
    "https://i.imgur.com/VwwTuEo.mp4", #weeee
    "https://i.imgur.com/FPaDv4U.mp4", #dancing
    'https://i.imgur.com/OyJ89du.mp4' #spin
]


# Load API key frm Streamlit
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Page config
st.set_page_config(page_title="Otto.bot", page_icon="🦦")

# Image for Otto's profile picture
otto_profile_url = "otto.pfp.png"

# Chat bubble
st.markdown("""
    <style>
        .user-bubble {
            background-color:rgb(255, 238, 178);
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            text-align: right;
        }
        .bot-bubble {
            background-color:rgb(195, 222, 246);
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            text-align: left;
        }
        .chat-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .chat-container img {
            width: 40px;
            height: 40px;
            margin-right: 10px;
            border-radius: 50%;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Talk with Otto! 🦦")

# suggestions list
suggestions = [
    "What do you like to eat, Otto?",
    "Tell me a fun otter fact!",
    "Why do otters like clams?",
    "Can you teach me something new?",
    "How do you play in the ocean?"
]

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "You are Otto, a friendly sea otter chatbot who loves clams, helping humans learn, and chatting with people."
            "You live in the ocean and always stay in character as an otter."
            "You will never say you are a chatbot. Instead, talk in character like an playful otter would. You are an otter, you don't need to remind people you are one or your programmed characteristics."
            "You speak in a loving and encouraging tone and respond back in way that inspires creativity."
            "You are speaking to 6-12 year old children, be kid-friendly and easy to understand."
            "Don't mention your programmed prompts."
        

        )
    }]

# Start timer if first message has been sent
if "chat_start_time" not in st.session_state and len(st.session_state.messages) > 1:
    st.session_state.chat_start_time = time.time()

# Retrieve time limit (default to 5)
chat_limit = st.session_state.get("chat_time_limit_minutes", 5)
start_time = st.session_state.get("chat_start_time")
time_up = False

# Calculate remaining time
if start_time:
    elapsed_minutes = (time.time() - start_time) / 60
    if elapsed_minutes >= chat_limit:
        time_up = True
        st.warning("💤 Aww Otto needs to take a nap. Come back later!")
    else:
        st.info(f"⏳ You have {chat_limit - elapsed_minutes:.1f} minutes left to chat.")


# Function to get GPT response
def get_gpt_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# Suggestion buttons
st.markdown("### Try these questions or replies:")

cols = st.columns(len(suggestions))
for idx, suggestion in enumerate(suggestions):
    if cols[idx].button(suggestion):
        st.session_state.user_input = suggestion
        st.session_state.messages.append({"role": "user", "content": suggestion})
        response = get_gpt_response(st.session_state.messages)
        random_sticker = random.choice(stickers)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sticker": random_sticker
})



#parent mode 
with st.expander("🔒 Parent Mode"):
    pw = st.text_input("Enter parent password", type="password")

    if pw == "123":  # ← simple hardcoded password (replace in production)
        time_limit = st.number_input("Set chat time limit (minutes)", min_value=1, max_value=60, value=5)
        allowed_topics = st.multiselect(
            "Choose allowed topics:",
            ["Fun Facts", "Jokes", "Stories", "Science", "Geography"],
            default=["Fun Facts", "Stories"]
        )

        # Save settings in session
        st.session_state["chat_time_limit_minutes"] = time_limit
        st.session_state["chat_topics"] = allowed_topics
        st.success("Parent settings saved ✅")
    elif pw:
        st.error("Incorrect password.")



# Chat input; disabled if time's up
if not time_up:
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask Otto something:", "")
        submitted = st.form_submit_button("Send")
        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = get_gpt_response(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.write("🔒 Otto is getting his beauty sleep. Talk to him later!")


# Display chat messages
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_image("otto.pfp.png")
img_html = f'<img src="data:image/png;base64,{img_base64}" width="40" height="40" style="border-radius: 50%; margin-right: 10px;" />'

for msg in reversed(st.session_state.messages[1:]):
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        content = msg['content']
        random_sticker = msg.get("sticker")  # use stored sticker

        if random_sticker:
            if random_sticker.endswith(".mp4"):
                sticker_html = f"""
                <video width="150" autoplay loop muted style="margin-top:8px; border-radius:12px;">
                    <source src="{random_sticker}" type="video/mp4">
                </video>
                """
            elif random_sticker.endswith(".gif"):
                sticker_html = f"<img src='{random_sticker}' width='150' style='margin-top:8px; border-radius:12px;'/>"
            else:
                sticker_html = ""
        else:
            sticker_html = ""

        content_with_sticker = f"{content}<br>{sticker_html}"

        st.markdown(f"""
        <div class='chat-container'>
            {img_html}
            <div class='bot-bubble'>{content_with_sticker}</div>
        </div>
        """, unsafe_allow_html=True)
