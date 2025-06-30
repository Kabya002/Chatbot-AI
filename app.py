import streamlit as st
import requests
import re
from datetime import datetime, timedelta
import dateparser

# Page settings
st.set_page_config(page_title="TailorTalk AI", page_icon="🤖")
st.title("🤖 TailorTalk: Book Appointments with AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Bot reply helper
def bot_reply(message, is_markdown=False):
    st.session_state.messages.append({"role": "assistant", "content": message})
    if is_markdown:
        st.chat_message("assistant").markdown(message)
    else:
        st.chat_message("assistant").write(message)

# Intent detection
def detect_intent(text):
    text = text.lower()
    keywords = [
        "free", "available", "availability", "free time", "this week", "this weekend",
        "check schedule", "my calendar", "my time"
    ]
    if any(word in text for word in ["book", "schedule", "set up"]):
        return "book"
    elif any(word in text for word in keywords):
        return "check"
    elif "help" in text:
        return "help"
    else:
        return "unknown"

# Clean up filler words
def clean_input(text):
    junk = ["book", "schedule", "meeting", "a", "the", "event", "please", "for", "me",
            "with", "call", "something", "set up", "appointment", "on", "to", "my"]
    cleaned = text.lower()
    for word in junk:
        cleaned = re.sub(rf"\b{word}\b", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

# Check if user input has time like '4 PM' or '10:30 AM'
def input_has_time(text):
    return bool(re.search(r"\d{1,2}(:\d{2})?\s?(am|pm)", text.lower()))

# Weekday parser (e.g. "next Tuesday")
def parse_weekday_phrase(text):
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    today = datetime.today()
    for i, day in enumerate(days):
        if day in text:
            current = today.weekday()
            delta = (i - current + 7) % 7
            if "next" in text:
                delta += 7 if delta == 0 else 0
            elif "this" in text and delta == 0:
                delta = 0
            elif "this" in text and delta > 0:
                pass
            return today + timedelta(days=delta)
    return None

# 📅 BOOKING function
def respond_with_booking(user_input):
    cleaned = clean_input(user_input)
    bot_reply(f"🧠 Trying to parse: `{cleaned}`")

    parsed_time = dateparser.parse(cleaned, settings={'PREFER_DATES_FROM': 'future'})

    if not parsed_time:
        date_only = parse_weekday_phrase(cleaned)
        if date_only:
            fallback_time = "10:00 AM" if not input_has_time(cleaned) else "12:00 AM"
            parsed_time = datetime.combine(date_only.date(), datetime.strptime(fallback_time, "%I:%M %p").time())
            bot_reply(f"📆 Weekday matched → `{parsed_time}`")
        else:
            bot_reply("⚠️ Couldn't understand your date. Try: `Book for 3 July at 10 AM`.")
            return

    start = parsed_time.isoformat()
    end = (parsed_time + timedelta(hours=1)).isoformat()
    bot_reply(f"📤 Booking from `{start}` to `{end}`...")
    try:
        res = requests.post("http://127.0.0.1:8000/book", params={
            "title": "Meeting with TailorTalk",
            "start": start,
            "end": end
        })
        res.raise_for_status()
        event = res.json()
        pretty = parsed_time.strftime("%A, %d %B %Y at %I:%M %p")
        bot_reply(f"✅ Meeting booked for **{pretty}**\n\n[📅 View in Google Calendar]({event.get('htmlLink', '#')})", is_markdown=True)
    except Exception as e:
        bot_reply(f"❌ Booking failed: {e}")

# 🧠 AVAILABILITY function
def respond_with_availability(user_input=None):
    try:
        now = datetime.utcnow()
        start = now.isoformat() + "Z"
        end = None

        if user_input:
            lower_input = user_input.lower()
            if "week" in lower_input:
                end = (now + timedelta(days=7)).isoformat() + "Z"
            elif "weekend" in lower_input:
                # Weekend: next Saturday and Sunday
                sat = now + timedelta((5 - now.weekday()) % 7)
                sun = sat + timedelta(days=1)
                end = (sun + timedelta(days=1)).isoformat() + "Z"

        url = "http://127.0.0.1:8000/available"
        params = {"start": start}
        if end:
            params["end"] = end

        response = requests.get(url, params=params)
        events = response.json().get("events", [])

        if not events:
            bot_reply("🎉 You're totally free in the selected time range!")
        else:
            bot_reply("📅 Here are your upcoming events:")
            for event in events:
                summary = event.get("summary", "No Title")
                start_time = event.get("start", {}).get("dateTime", "")
                readable = start_time.replace("T", " ").split("+")[0]
                bot_reply(f"- **{summary}** at `{readable}`", is_markdown=True)
    except Exception as e:
        bot_reply(f"❌ Couldn't check availability: `{e}`")

# Help command
def respond_with_help():
    bot_reply("""
Here’s what I can help you with:
- 🗓️ **"Book a meeting next Tuesday at 4 PM"**
- 🔍 **"What’s my availability this week?"**
- 📘 **"Show me free time this weekend"**

Try: `"Schedule something this Friday"` or `"Book 3 July at 2 PM"`
""", is_markdown=True)

# Main chat input
user_input = st.chat_input("Ask me to book or check your schedule")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    intent = detect_intent(user_input)

    if intent == "book":
        respond_with_booking(user_input)
    elif intent == "check":
        respond_with_availability(user_input)
    elif intent == "help":
        respond_with_help()
    else:
        bot_reply("🤔 I'm not sure what you meant. Try asking me to **book** or **check availability**.")

    st.rerun()
