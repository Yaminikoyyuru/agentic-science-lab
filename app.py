import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# Securely grab the API Key
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing Gemini API Key. Please add it to your Streamlit Secrets Management dashboard.")
    st.stop()

# Configuration for the latest 2026 Frontier Models
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Agentic AI 3D Kids Lab", layout="centered")
st.title("🧠 Agentic AI 3D Kids Science Lab")
st.write("An Interactive 3D Simulation Science Game Powered by AI Agents")

if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.opt_a = ""
    st.session_state.opt_b = ""
    st.session_state.correct_answer = None

# Smart Feature: Let users choose from list OR type their own topic!
select_topic = st.selectbox("Choose a preset topic:", ["Water Physics", "Magnets", "Gravity", "Solar System", "Plant Biology", "Human Anatomy", "Electricity", "Other (Type below)"])

if select_topic == "Other (Type below)":
    topic = st.text_input("Type any Science Topic you want (e.g., Black Holes, Dinosaurs, Volcanoes):", "Volcanoes")
else:
    topic = select_topic

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
            
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        # Added beautiful spinner to handle loading states smoothly
        with st.spinner("🎬 AI Agent is autonomously rendering your interactive 3D simulation... Please wait a few seconds!"):
            # Enhanced 3D Animation prompt forcing visible meshes and real interactive bindings
            animation_prompt = f"""
            Generate a single, complete HTML page that imports Three.js and OrbitControls via CDN to render a fully functional, visible, and interactive 3D physics simulation for a 10-year-old child.
            Topic: '{topic}', Student Choice: '{user_choice}'.
            
            CRUCIAL REQUIREMENTS FOR 3D RENDERING:
            1. VISIBLE 3D OBJECTS: You MUST create actual, clearly visible 3D geometric shapes (like THREE.SphereGeometry for planets/atoms, THREE.BoxGeometry for blocks, or THREE.ConeGeometry) with bright, vivid, cartoonish colors using THREE.MeshStandardMaterial. Do not leave the canvas empty or black.
            2. INTERACTIVE HTML CONTROLS: Create a stylized absolute-positioned HTML overlay container on top of the canvas with action buttons/sliders (e.g., Change Angle, Pulse, Reset Position) relevant to the science topic.
            3. JAVASCRIPT EVENT LISTENERS: You MUST write explicit JavaScript code (`document.getElementById().addEventListener`) to link every single HTML button/slider to the Three.js scene. When a button is clicked, it MUST actively modify the 3D mesh properties (like position, rotation, scale, or velocity) inside the active `requestAnimationFrame` loop so the user sees immediate visual changes!
            4. LIGHTING & CAMERA: Include an AmbientLight for base visibility and a DirectionalLight to cast beautiful shadows. Set camera position appropriately so all 3D meshes are perfectly centered and visible inside the 500px container.
            
            Return ONLY valid, raw HTML/JavaScript code inside a container. No markdown, no triple backticks. Just raw HTML code.
            """
            html_code = model.generate_content(animation_prompt).text
            
            # Robust clean parsing logic to prevent List AttributeError bugs
            if "```html" in html_code:
                html_code = html_code.split("```html")[1].split("```")[0].strip()
            elif "```" in html_code:
                html_code = html_code.split("```")[1].split("```")[0].strip()
            else:
                html_code = html_code.strip()
                
            components.html(html_code, height=500)

