import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# Securely grab the New AQ. Format API Key
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing Gemini API Key. Please add it to your Streamlit Secrets Management dashboard.")
    st.stop()

# Configuration for the latest 2026 Frontier Models
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Agentic AI Kids Lab", layout="centered")
st.title("🧠 Agentic AI Kids Science Lab")
st.write("A Live Animation Science Game Powered by AI Agents")

if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.opt_a = ""
    st.session_state.opt_b = ""
    st.session_state.correct_answer = None

topic = st.selectbox("Select a Science Topic:", ["Water Physics", "Magnets", "Gravity", "Solar System", "Plant Biology", "Human Anatomy", "Electricity"])

if st.button("🚀 Ask a New Question"):
    # Updated to the latest stable model: gemini-3.6-flash
    model = genai.GenerativeModel('gemini-3.6-flash')
    prompt = f"""
    Create a conceptual science question for a 10-year-old child about {topic}. 
    Provide the question, exactly 2 options (one right, one wrong), and specify which one is correct.
    Format your response EXACTLY like this:
    Question: [Your question in English]
    Option A: [Option A text in English]
    Option B: [Option B text in English]
    Correct: [Option A or Option B]
    """
    try:
        response = model.generate_content(prompt)
        lines = response.text.split('\n')
        for line in lines:
            if line.startswith("Question:"): st.session_state.question = line.replace("Question:", "").strip()
            if line.startswith("Option A:"): st.session_state.opt_a = line.replace("Option A:", "").strip()
            if line.startswith("Option B:"): st.session_state.opt_b = line.replace("Option B:", "").strip()
            if line.startswith("Correct:"): st.session_state.correct_answer = line.replace("Correct:", "").strip()
    except Exception as e:
        st.error(f"Sync Error. Details: {e}")

if st.session_state.question:
    st.subheader(st.session_state.question)
    user_choice = st.radio("Think carefully and select an option:", [st.session_state.opt_a, st.session_state.opt_b])
    
    if st.button("✔️ Check Answer & Watch Animation"):
        is_correct = "correct" if (("Option A" in st.session_state.correct_answer and user_choice == st.session_state.opt_a) or ("Option B" in st.session_state.correct_answer and user_choice == st.session_state.opt_b)) else "incorrect"
        
        if is_correct == "correct":
            st.success("🎉 Brilliant! That is the correct answer.")
        else:
            st.error("❌ Oops! Incorrect answer. But watch the live animation below to learn why!")
            
        st.write("🎬 AI Agent is creating your live simulation...")
        # Updated to the latest stable model here as well
        model = genai.GenerativeModel('gemini-3.6-flash')
        animation_prompt = f"""
        Generate a single HTML page with inline CSS animations showing the physics outcome of this choice: '{user_choice}' under the topic '{topic}'.
        Example: If it is about putting a coin in water, show a clean blue box representing water and a gold circle representing a coin moving down to the bottom.
        Return ONLY valid, raw HTML/CSS code inside a container. No markdown, no triple backticks. Just raw HTML code.
        """
        html_code = model.generate_content(animation_prompt).text
        
        if "```html" in html_code:
            html_code = html_code.split("```html")[-1].split("```").strip()
        elif "```" in html_code:
            html_code = html_code.split("```").split("```").strip()
            
        components.html(html_code, height=300)
