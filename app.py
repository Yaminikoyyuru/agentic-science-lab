import streamlit as st
import google.generativeai as genai

from agents.orchestrator import Orchestrator
from state.student_state import StudentState


st.set_page_config(
    page_title="Agentic AI Science Lab",
    page_icon="🔬",
    layout="wide"
)


st.title("🔬 Agentic AI 3D Science Lab")
st.write(
    "Explore a science topic through AI agents, "
    "experiments, predictions, and observations."
)


# -----------------------------
# Gemini configuration
# -----------------------------

api_key = st.text_input(
    "Enter your Gemini API Key",
    type="password"
)

if not api_key:
    st.info("Enter your Gemini API key to start.")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-3.6-flash"
)


# -----------------------------
# Create agents and state
# -----------------------------

orchestrator = Orchestrator(model)

if "student_state" not in st.session_state:
    st.session_state.student_state = StudentState()

state = st.session_state.student_state


# -----------------------------
# Topic input
# -----------------------------

st.header("1. Choose a Science Topic")

topic = st.text_input(
    "What do you want to explore?",
    placeholder="Example: gravity, plants, electricity"
)


if st.button("Start Learning Session"):

    if not topic.strip():

        st.warning("Please enter a science topic.")

    else:

        with st.spinner("AI agents are preparing your experiment..."):

            session = orchestrator.start_learning_session(
                topic
            )

        state.topic = topic
        state.current_question = (
            session["teacher"]["question"]
        )
        state.experiment = session["experiment"]
        state.next_experiment()

        st.session_state.session = session


# -----------------------------
# Display learning session
# -----------------------------

if "session" in st.session_state:

    session = st.session_state.session

    science = session["science"]
    teacher = session["teacher"]
    experiment = session["experiment"]

    st.divider()

    st.header("2. Science Agent")

    st.write(
        "**Core concept:**",
        science.get("concept", "")
    )

    st.write(
        "**Scientific explanation:**",
        science.get("explanation", "")
    )

    st.header("3. Teacher Agent")

    st.write(
        teacher.get("question", "")
    )

    option_a = teacher.get("option_a", "")
    option_b = teacher.get("option_b", "")

    answer = st.radio(
        "Choose your answer:",
        [
            f"A. {option_a}",
            f"B. {option_b}"
        ]
    )

    if st.button("Check Answer"):

        selected = "A" if answer.startswith("A.") else "B"

        correct = teacher.get(
            "correct_option",
            ""
        )

        if selected == correct:
            st.success(
                "Correct! Now let's experiment."
            )
        else:
            st.warning(
                "Not quite. Let's investigate it through the experiment."
            )

    st.header("4. Make Your Prediction")

    prediction = st.text_input(
        teacher.get(
            "prediction_prompt",
            "What do you think will happen?"
        )
    )

    st.header("5. Experiment Agent")

    st.subheader(
        experiment.get("title", "Science Experiment")
    )

    variables = experiment.get(
        "variables",
        {}
    )

    selected_values = {}

    for name, config in variables.items():

        minimum = config.get("min", 0)
        maximum = config.get("max", 100)
        default = config.get("default", 50)
        unit = config.get("unit", "")

        value = st.slider(
            f"{name} ({unit})",
            min_value=float(minimum),
            max_value=float(maximum),
            value=float(default)
        )

        selected_values[name] = value

        st.caption(
            config.get("description", "")
        )

    st.write(
        "**Expected result:**",
        experiment.get(
            "expected_result",
            ""
        )
    )

    st.header("6. Student Observation")

    observation = st.text_area(
        "What did you observe after changing the variables?",
        placeholder="Example: When I increased the value, the object moved faster."
    )

    if st.button("Evaluate My Experiment"):

        if not observation.strip():

            st.warning(
                "Please describe your observation first."
            )

        else:

            with st.spinner(
                "Evaluator Agent is analyzing your observation..."
            ):

                evaluation = orchestrator.evaluate_student_action(
                    topic,
                    experiment,
                    observation,
                    prediction
                )

            state.add_observation(
                observation
            )

            state.add_evaluation(
                evaluation
            )

            state.add_history({
                "topic": topic,
                "prediction": prediction,
                "observation": observation,
                "evaluation": evaluation
            })

            st.session_state.evaluation = evaluation


# -----------------------------
# Evaluation result
# -----------------------------

if "evaluation" in st.session_state:

    evaluation = st.session_state.evaluation

    st.divider()

    st.header("7. Evaluator Agent")

    st.write(
        "**What you discovered:**",
        evaluation.get(
            "discovery",
            ""
        )
    )

    st.write(
        "**Prediction supported:**",
        evaluation.get(
            "prediction_supported",
            False
        )
    )

    misconception = evaluation.get(
        "misconception",
        ""
    )

    if misconception:
        st.info(
            f"💡 Learning hint: {misconception}"
        )

    st.write(
        "**Next action:**",
        evaluation.get(
            "next_action",
            ""
        )
    )

    st.write(
        "**Next question:**",
        evaluation.get(
            "next_question",
            ""
        )
    )
      
      
