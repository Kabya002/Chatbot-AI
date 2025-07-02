# TimeMate AI Assistant

TimeMate is an intelligent personal assistant that helps users **book Google Calendar meetings** and **check availability** via a natural language interface powered by **Streamlit + FastAPI**. This version works fully **offline** (no GPT) and smartly handles phrases like:

- "Book a meeting next Tuesday at 4 PM"
- "What’s my availability this weekend?"
- "Schedule something this Friday"

---

## Features
- Book meetings using natural language  
- Parses smart phrases like `next Thursday` or `tomorrow at 2 PM`  
- Check upcoming availability for today, week, or weekend  
- Chat interface using Streamlit  
- OAuth2-based Google Calendar API integration  
- Built using Python, FastAPI, Streamlit
- GPT-free fallback logic – works without internet or quota issues

---

## 🛠️ Tech Stack

| Frontend     | Backend   | AI Parsing       | Auth       | API          |
|--------------|-----------|------------------|------------|--------------|
| Streamlit    | FastAPI   | `dateparser`     | Google OAuth | Google Calendar |

---

## Installation
   ### 1. Clone the repo
    -git clone https://github.com/Kabya002/ChatBotAI.git
    -cd ChatBotAI.git
   ### 2. Setup Virtual Environment
    -python3 -m venv venv
    -source venv/bin/activate
    -pip install -r requirements.txt
   ### 3. Add your Google OAuth Credentials
    #Place your credentials.json in the project root.
    #Then run:
    python authorize.py
    #It will generate token.json after successful login.
    #Running the App
   ### 4. Start the FastAPI Backend
    uvicorn backend:app --reload
   ### 5. In a new terminal, run the Streamlit Frontend
    streamlit run app.py
    #Supported Commands
    #Example: Input	Result
    #Book something next Friday at 2 PM:	Books a meeting
    #Schedule something on July 5:	Books with default time (10 AM)
    #Book a meeting tomorrow:	Books for tomorrow at 10 AM
    #Check availability this week:	Lists events for 7 days
    #Show free time this weekend:	Lists Sat/Sun events
    #Help	Lists supported examples
### Security
---
-Your Google token is stored securely in token.json
-OAuth scopes are limited to Google Calendar only
-All communication happens on localhost
