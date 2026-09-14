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

# Initialize robust session states
if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.opt_a = ""
    st.session_state.opt_b = ""
    st.session_state.correct_answer = None
if 'q_counter' not in st.session_state:
    st.session_state.q_counter = 0
if 'show_simulation' not in st.session_state:
    st.session_state.show_simulation = False

# Premium Feature: Clean Slate. No dropdowns. Just open-ended typing!
topic = st.text_input(
    "Type ANY Science Topic you want to explore (e.g., Volcanoes, Solar System, Black Holes, Magnets):", 
    placeholder="e.g., Space Travel, How Plants Breathe, Atoms..."
)

if st.button("🚀 Ask a New Question"):
    if not topic.strip():
        st.warning("Please type a topic first to let the AI Agent build your lab!")
    else:
        # Clear EVERYTHING immediately before hitting the API to ensure no old data shows up
        st.session_state.question = None
        st.session_state.opt_a = ""
        st.session_state.opt_b = ""
        st.session_state.correct_answer = None
        st.session_state.show_simulation = False
        st.session_state.q_counter += 1  # Forces radio widget to completely refresh
        
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        # STRICT K-12 dynamic prompt preventing hardcoding, repetition, and high-level complexity
        prompt = f"""
        You are an advanced Agentic K-12 Science Educator AI. Create a highly engaging, conceptual science question suitable for a 10-year-old child (Grade 4-6 level) about the topic: '{topic}'.
        
        STRICT RULES FOR DYNAMIC GENERATION:
        1. NO REPETITION & RANDOMISATION: Every time you are called, you must formulate a completely fresh, unique question. Do not repeat standard textbook questions. Look for a creative angle.
        2. MANDATORY K-12 DOWN-SCALING: If the user types an advanced, complex college-level topic (like Quantum Mechanics, Advanced Calculus, Relativity, String Theory), you MUST automatically scale it down. Translate it into an everyday physical concept that a 10-year-old can easily understand and visualize (e.g., convert Quantum Mechanics into a basic question about how light/photons bounce or how basic atoms look).
        3. FORMAT: Provide the question, exactly 2 options (one right, one wrong), and specify which option letter is correct.
        
        Format your response EXACTLY like this:
        Question: [Your unique question in English]
        Option A: [Option A text in English]
        Option B: [Option B text in English]
        Correct: [Option A or Option B]
        """
        try:
            with st.spinner("🧠 AI Agent is dynamically brainstorming a fresh question..."):
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
    user_choice = st.radio("Think carefully and select an option:", 
                           [st.session_state.opt_a, st.session_state.opt_b], 
                           key=f"radio_q_{st.session_state.q_counter}")
    
    if st.button("✔️ Check Answer & Watch 3D Animation") or st.session_state.show_simulation:
        st.session_state.show_simulation = True
        is_correct = "correct" if (("Option A" in st.session_state.correct_answer and user_choice == st.session_state.opt_a) or ("Option B" in st.session_state.correct_answer and user_choice == st.session_state.opt_b)) else "incorrect"
        
        if is_correct == "correct":
            st.success("🎉 Brilliant! That is the correct answer.")
        else:
            st.error("❌ Oops! Incorrect answer. But explore the 3D physics simulation below to learn why!")
            
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        with st.spinner("🎬 AI Agent is autonomously rendering your clean 3D simulation... Please wait!"):
            # Enhanced 3D animation prompt enforcing K-12 visual scalability
            animation_prompt = f"""
            Generate a single, complete HTML page that imports Three.js and OrbitControls via CDN to render a fully functional, visible, and interactive 3D physics simulation.
            Topic: '{topic}', Student Choice: '{user_choice}'.
            
            STRICT VISUAL REQUIREMENTS:
            1. K-12 SIMPLICITY: The 3D scene must be visually intuitive for a 10-year-old child. Use bright, vibrant, cartoonish colors.
            2. NO COLLEGE COMPLEXITY: If the topic is complex (like Quantum Mechanics), render basic cartoonish spheres bouncing or moving like simple atoms/particles. Do NOT show complex mathematical graphs, wave distributions, or text blocks.
            3. STRICTLY NO TEXT OVERLAYS: Do NOT write any HTML headers, paragraphs, or explanations outside the canvas. Only the raw 3D scene and absolute-positioned functional buttons are allowed.
            4. INTERACTION: Create small, neat control buttons (e.g., "Animate", "Reset") absolute positioned at the bottom. Write explicit JS Event Listeners so clicking them visibly alters mesh parameters (position, speed, or rotation) inside the `requestAnimationFrame` loop.
            5. LIGHTING & FRAMING: Center the 3D objects perfectly. Ensure ambient and directional lights are active so nothing is pitch black.
            
            Return ONLY valid, raw HTML/JavaScript code inside a container. No markdown, no triple backticks. Just raw HTML code.
            """
            html_code = model.generate_content(animation_prompt).text
            
            # Robust clean parsing logic
            if "```html" in html_code:
                html_code = html_code.split("```html")[1].split("```")[0].strip()
            elif "```" in html_code:
                html_code = html_code.split("```")[1].split("```")[0].strip()
            else:
                html_code = html_code.strip()
                
            components.html(html_code, height=500)
