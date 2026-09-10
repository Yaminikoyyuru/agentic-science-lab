import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# Securely grab the API Key
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing Gemini API Key. Please add it to your Streamlit Secrets Management dashboard.")
    st.stop()

# Configuration for 2026 Frontier Models
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Agentic AI 3D Kids Lab", layout="centered")
st.title("🧠 Agentic AI 3D Kids Science Lab")
st.write("An Interactive 3D Simulation Science Game Powered by AI Agents")

if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.opt_a = ""
    st.session_state.opt_b = ""
    st.session_state.correct_answer = None

topic = st.selectbox("Select a Science Topic:", ["Water Physics", "Magnets", "Gravity", "Solar System", "Plant Biology", "Human Anatomy", "Electricity"])

if st.button("🚀 Ask a New Question"):
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
    
    if st.button("✔️ Check Answer & Watch 3D Animation"):
        is_correct = "correct" if (("Option A" in st.session_state.correct_answer and user_choice == st.session_state.opt_a) or ("Option B" in st.session_state.correct_answer and user_choice == st.session_state.opt_b)) else "incorrect"
        
        if is_correct == "correct":
            st.success("🎉 Brilliant! That is the correct answer.")
        else:
            st.error("❌ Oops! Incorrect answer. But explore the 3D physics simulation below to learn why!")
            
        st.write("🎬 AI Agent is rendering your interactive 3D simulation...")
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        # Powering up the prompt with Three.js engine capabilities
        animation_prompt = f"""
        Generate a single HTML page that imports the Three.js library via CDN script to render a complete, beautiful interactive 3D physics animation showing the realistic scientific outcome of this choice: '{user_choice}' under the topic '{topic}'.
        Include OrbitControls so the user can rotate the 3D scene using their mouse. Add proper 3D lighting (Ambient and Directional). 
        Example: If a coin is dropped in water, render a 3D translucent blue box container (water) and a golden 3D cylinder/sphere (coin) moving smoothly downwards to the bottom.
        Make the colors bright, vivid, and cartoonish for a 10-year-old child.
        Return ONLY valid, raw HTML/JavaScript code inside a container. No markdown, no triple backticks. Just raw HTML code.
        """
        html_code = model.generate_content(animation_prompt).text
        
        if "```html" in html_code:
            html_code = html_code.split("```html")[-1].split("```")[0].strip()
        elif "```" in html_code:
            html_code = html_code.split("```")[1].split("```")[0].strip()
            
        # Expanded box height to comfortably render the 3D canvas viewport without cuts
        components.html(html_code, height=500)

    
