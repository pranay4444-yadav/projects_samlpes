
import streamlit as st
from langdetect import detect
import datetime
import speech_recognition as sr
from googletrans import Translator

# -------------------------------
# Knowledge Base: Diseases & Symptoms
# -------------------------------
disease_symptoms = {
    "fever": ["High temperature", "Chills", "Sweating", "Headache"],
    "covid": ["Fever", "Dry cough", "Loss of taste/smell", "Shortness of breath"],
    "diabetes": ["Frequent urination", "Excessive thirst", "Weight loss", "Fatigue"],
    "malaria": ["Fever", "Shivering", "Sweating", "Muscle pain"],
    "asthma": ["Coughing", "Wheezing", "Shortness of breath", "Chest tightness"]
}

# -------------------------------
# Vaccination Schedule (Demo)
# -------------------------------
vaccines = {
    "BCG": "At birth",
    "Hepatitis B": "At birth, 6 weeks, 10 weeks, 14 weeks",
    "Polio": "At birth, 6 weeks, 10 weeks, 14 weeks",
    "Measles": "9 months, 16 months",
    "COVID-19": "As per govt. guidelines (2 doses + booster)"
}

# -------------------------------
# Helpers
# -------------------------------
translator = Translator()

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def chatbot_response(user_input):
    user_input = user_input.lower()
    # Disease symptoms
    for disease, symptoms in disease_symptoms.items():
        if disease in user_input:
            return f"**Symptoms of {disease.capitalize()}:** " + ", ".join(symptoms)
    # Vaccination reminder
    if "vaccine" in user_input or "vaccination" in user_input:
        v_list = "\n".join([f"- {k}: {v}" for k,v in vaccines.items()])
        return f"**Vaccination Schedule:**\n{v_list}"
    return "I'm not sure about that. Please consult a doctor for proper guidance."

def save_chat(chat_history):
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for entry in chat_history:
            f.write(f"You: {entry['user']}\n")
            f.write(f"Bot: {entry['bot']}\n\n")
    return filename

def listen_and_recognize():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening… Speak now (English or Kannada)")
        audio = r.listen(source, phrase_time_limit=5)
        try:
            # Try Kannada first
            text = r.recognize_google(audio, language='kn-IN')
            detected_lang = 'kn'
        except sr.UnknownValueError:
            try:
                text = r.recognize_google(audio, language='en-US')
                detected_lang = 'en'
            except:
                return None, None
        return text, detected_lang

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="AI Health Chatbot", page_icon="🩺", layout="centered")

st.title("🩺 AI-Powered Multilingual Health Chatbot")
st.write("Disease awareness, vaccination reminders, and symptom checker (SIH Hackathon Prototype).")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# Chat Section
# -------------------------------
st.subheader("💬 Chat with the Bot")

col1, col2 = st.columns([8,1])
with col1:
    user_input = st.text_input("Ask me about a disease, symptoms, or vaccines:")
with col2:
    if st.button("🎤 Voice Input"):
        spoken_text, lang = listen_and_recognize()
        if spoken_text:
            st.success(f"Detected ({lang}): {spoken_text}")
            # Translate Kannada to English for chatbot
            if lang == 'kn':
                spoken_text_en = translator.translate(spoken_text, src='kn', dest='en').text
            else:
                spoken_text_en = spoken_text
            response = chatbot_response(spoken_text_en)
            st.session_state.chat_history.append({"user": spoken_text, "bot": response})
        else:
            st.error("Could not understand. Please try again.")

if st.button("Send"):
    if user_input.strip() != "":
        lang = detect_language(user_input)
        response = chatbot_response(user_input)
        st.session_state.chat_history.append({"user": user_input, "bot": response})
    else:
        st.warning("Please type something before sending.")

# Display chat history
for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")

# Download chat history
if st.session_state.chat_history:
    if st.button("📥 Download Chat History"):
        file = save_chat(st.session_state.chat_history)
        with open(file, "rb") as f:
            st.download_button("Click to Download", f, file_name=file)

# -------------------------------
# Symptom Checker Section
# -------------------------------
st.subheader("🩺 Quick Symptom Checker")

with st.expander("Open Symptom Checker"):
    with st.form("symptom_checker"):
        st.write("Answer a few quick questions:")

        q1 = st.radio("Do you have fever?", ["Yes", "No"])
        q2 = st.radio("Do you have difficulty breathing?", ["Yes", "No"])
        q3 = st.radio("Do you have chest pain?", ["Yes", "No"])

        submitted = st.form_submit_button("Get triage result")

        if submitted:
            if q3 == "Yes":
                st.error("⚠️ High Risk: Please seek emergency medical care immediately!")
            elif q2 == "Yes":
                st.warning("⚠️ Medium Risk: Consult a doctor soon.")
            elif q1 == "Yes":
                st.info("ℹ️ Low Risk: Monitor your symptoms and rest.")
            else:
                st.success("✅ No major symptoms detected. Stay healthy!")
