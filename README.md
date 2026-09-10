# 🧠 Agentic AI 3D Kids Science Lab

An advanced, interactive 3D simulation science learning web platform engineered using Python, Streamlit, and powered by a Multi-Agent workflow using the latest **Gemini 3.6-Flash Frontier Model**.

🔗 **Live Application Link:** [Click Here to Play the Game](https://agentic-science-lab-l24p7ehnm9pdlkdprnwq5f.streamlit.app/)

## 🚀 Key Architectural Features
- **Multi-Agent Orchestration:** Deployed distinct AI agents sequentially. Agent 1 synthesizes dynamic science conceptual queries, while Agent 2 acts as a Generative UI compiler to produce 3D animation code on-the-fly.
- **Generative UI via Three.js:** The background compiler structures localized HTML5/JavaScript execution containers, generating fully manipulable 3D physical models via WebGL and OrbitControls dynamically.
- **Infinite Scope Runtime:** Extends standard hardcoded drop-downs using customized text vector input spaces to handle any physics or science prompt dynamically (e.g., Black Holes, Volcanoes).
- **Session State Logic:** Implements memory persistence tracking via `st.session_state` to process user accuracy records and multi-turn state flows seamlessly without backend loss.

## 🛠️ Tech Stack & Integrations
- **Core Engineering:** Python 3
- **Frontend Framework:** Streamlit UI Architecture
- **AI Core Pipeline:** Google Generative AI (Gemini 3.6-Flash)
- **3D Render Graphics Engine:** Three.js (WebGL Component Integration)
- **Deployment Platform:** Streamlit Community Cloud Hub via GitHub Webhooks
