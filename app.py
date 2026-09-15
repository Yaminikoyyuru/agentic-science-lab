import streamlit as st
import json
import html

from agents.orchestrator import Orchestrator
from state.student_state import StudentState


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Agentic AI 3D Kids Science Lab",
    page_icon="🔬",
    layout="wide"
)


# ---------------------------------------------------------
# GEMINI SETUP
# ---------------------------------------------------------

st.title("🔬 Agentic AI 3D Kids Science Lab")
st.write(
    "Explore science through AI-generated questions, "
    "experiments, predictions, observations and simulations."
)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "Gemini API key is not configured. "
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )
    st.stop()


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

try:
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-3.6-flash")

except Exception as error:
    st.error(f"Unable to initialize Gemini: {error}")
    st.stop()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "student_state" not in st.session_state:
    st.session_state.student_state = StudentState()

if "session_data" not in st.session_state:
    st.session_state.session_data = None

if "prediction" not in st.session_state:
    st.session_state.prediction = ""

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

if "experiment_values" not in st.session_state:
    st.session_state.experiment_values = {}


# ---------------------------------------------------------
# ORCHESTRATOR
# ---------------------------------------------------------

orchestrator = Orchestrator(model)


# ---------------------------------------------------------
# TOPIC INPUT
# ---------------------------------------------------------

topic = st.text_input(
    "What science topic do you want to explore?",
    placeholder="Example: Gravity, plants, electricity, density..."
)


if st.button("🚀 Start Learning Session"):

    if not topic.strip():
        st.warning("Please enter a science topic.")
        st.stop()

    # Reset old session
    st.session_state.prediction = ""
    st.session_state.evaluation = None
    st.session_state.experiment_values = {}

    try:

        session = orchestrator.start_learning_session(
            topic.strip()
        )

        if "error" in session:
            st.error(
                "The AI session could not be started."
            )
            st.error(session["error"])
            st.stop()

        st.session_state.session_data = session

        # Save topic
        st.session_state.student_state.topic = topic.strip()

        # Save experiment
        st.session_state.student_state.experiment = (
            session.get("experiment", {})
        )

        # Save question
        teacher = session.get("teacher", {})

        st.session_state.student_state.current_question = (
            teacher.get("question", "")
        )

        st.rerun()

    except Exception as error:

        st.error(
            "The AI session could not be started."
        )

        st.error(str(error))


# ---------------------------------------------------------
# STOP IF SESSION NOT CREATED
# ---------------------------------------------------------

if not st.session_state.session_data:
    st.info(
        "Enter a science topic above and start a learning session."
    )
    st.stop()


session = st.session_state.session_data

science = session.get("science", {})
teacher = session.get("teacher", {})
experiment = session.get("experiment", {})


# ---------------------------------------------------------
# SCIENCE ANALYSIS
# ---------------------------------------------------------

with st.expander("🧠 Science Agent Analysis"):

    st.write(
        f"**Core concept:** "
        f"{science.get('concept', '')}"
    )

    if science.get("relationships"):
        st.write("**Cause-and-effect relationships:**")

        for relationship in science["relationships"]:
            st.write(f"- {relationship}")

    if science.get("explanation"):
        st.write(
            f"**Explanation:** "
            f"{science.get('explanation')}"
        )


# ---------------------------------------------------------
# TEACHER QUESTION
# ---------------------------------------------------------

st.header("👩‍🏫 Your Prediction")

st.write(
    teacher.get(
        "question",
        "What do you think will happen?"
    )
)

option_a = teacher.get("option_a", "")
option_b = teacher.get("option_b", "")

if option_a:
    st.write(f"**A.** {option_a}")

if option_b:
    st.write(f"**B.** {option_b}")


prediction = st.text_area(
    "Make your prediction:",
    value=st.session_state.prediction,
    placeholder="I think..."
)

if st.button("💭 Save Prediction"):

    st.session_state.prediction = prediction

    st.session_state.student_state.set_prediction(
        prediction
    )

    st.success("Prediction saved!")


# ---------------------------------------------------------
# EXPERIMENT
# ---------------------------------------------------------

st.header("🧪 AI-Generated Experiment")

st.write(
    f"### {experiment.get('title', 'Interactive Experiment')}"
)

if experiment.get("expected_result"):
    st.write(
        f"**Expected result:** "
        f"{experiment.get('expected_result')}"
    )


# ---------------------------------------------------------
# EXPERIMENT VARIABLES
# ---------------------------------------------------------

variables = experiment.get("variables", {})

current_values = {}

if variables:

    st.subheader("🎛️ Experiment Controls")

    for name, config in variables.items():

        try:
            minimum = float(config.get("min", 0))
            maximum = float(config.get("max", 100))
            default = float(config.get("default", minimum))
            unit = config.get("unit", "")

            # Keep default inside allowed range
            default = max(
                minimum,
                min(default, maximum)
            )

            value = st.slider(
                f"{name} ({unit})",
                min_value=minimum,
                max_value=maximum,
                value=default
            )

            current_values[name] = value

            description = config.get(
                "description",
                ""
            )

            if description:
                st.caption(description)

        except Exception:
            continue


st.session_state.experiment_values = current_values


# ---------------------------------------------------------
# 3D SIMULATION ENGINE
# ---------------------------------------------------------

st.header("🌐 3D Virtual Experiment")


def is_gravity_experiment(topic_text, experiment_data, variable_data):

    text = (
        str(topic_text)
        + " "
        + str(experiment_data.get("title", ""))
        + " "
        + str(experiment_data.get("expected_result", ""))
        + " "
        + str(experiment_data.get("rules", ""))
        + " "
        + " ".join(variable_data.keys())
    ).lower()

    gravity_words = [
        "gravity",
        "fall",
        "falling",
        "drop",
        "dropped",
        "free fall",
        "mass",
        "weight",
        "height"
    ]

    return any(
        word in text
        for word in gravity_words
    )


def find_value(variable_data, keywords, default_value):

    for name, value in variable_data.items():

        name_lower = name.lower()

        for keyword in keywords:

            if keyword in name_lower:
                return value

    return default_value


gravity_experiment = is_gravity_experiment(
    session.get("topic", ""),
    experiment,
    variables
)


if gravity_experiment:

    mass_1 = find_value(
        current_values,
        ["mass", "weight"],
        20
    )

    height = find_value(
        current_values,
        ["height", "drop", "distance"],
        100
    )

    # Find a second mass if AI generated multiple
    # mass-like variables.
    mass_values = []

    for name, value in current_values.items():

        if (
            "mass" in name.lower()
            or "weight" in name.lower()
        ):
            mass_values.append(value)

    if len(mass_values) >= 2:
        mass_1 = mass_values[0]
        mass_2 = mass_values[1]
    else:
        mass_2 = mass_1 * 2


    # -----------------------------------------------------
    # SAFE HTML VALUES
    # -----------------------------------------------------

    mass_1 = float(mass_1)
    mass_2 = float(mass_2)
    height = float(height)

    mass_1_text = html.escape(
        f"{mass_1:g}"
    )

    mass_2_text = html.escape(
        f"{mass_2:g}"
    )

    height_text = html.escape(
        f"{height:g}"
    )


    # -----------------------------------------------------
    # THREE.JS FALLING BALL SIMULATION
    # -----------------------------------------------------

    simulation_html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            body {{
                margin: 0;
                overflow: hidden;
                font-family: Arial, sans-serif;
                background: #f5f7fa;
            }}

            #container {{
                width: 100%;
                height: 520px;
                position: relative;
            }}

            #info {{
                position: absolute;
                top: 15px;
                left: 15px;
                z-index: 10;
                background: white;
                padding: 12px 16px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.12);
                line-height: 1.5;
            }}

            #dropButton {{
                margin-top: 8px;
                padding: 8px 14px;
                border: none;
                border-radius: 7px;
                cursor: pointer;
                font-size: 14px;
            }}

        </style>

    </head>


    <body>

        <div id="container">

            <div id="info">

                <strong>Gravity Experiment</strong><br>

                Ball A mass:
                {mass_1_text} g<br>

                Ball B mass:
                {mass_2_text} g<br>

                Drop height:
                {height_text} cm<br>

                <button id="dropButton">
                    Drop Balls
                </button>

            </div>

        </div>


        <script type="module">

            import * as THREE
            from
            'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';


            // ---------------------------------------------
            // SCENE
            // ---------------------------------------------

            const scene = new THREE.Scene();

            scene.background =
                new THREE.Color(0xf5f7fa);


            // ---------------------------------------------
            // CAMERA
            // ---------------------------------------------

            const camera =
                new THREE.PerspectiveCamera(
                    45,
                    window.innerWidth / 520,
                    0.1,
                    1000
                );

            camera.position.set(
                0,
                3,
                10
            );


            // ---------------------------------------------
            // RENDERER
            // ---------------------------------------------

            const renderer =
                new THREE.WebGLRenderer({
                    antialias: true
                });

            renderer.setSize(
                window.innerWidth,
                520
            );

            renderer.setPixelRatio(
                window.devicePixelRatio
            );

            document
                .getElementById("container")
                .appendChild(
                    renderer.domElement
                );


            // ---------------------------------------------
            // LIGHTS
            // ---------------------------------------------

            const ambientLight =
                new THREE.AmbientLight(
                    0xffffff,
                    0.8
                );

            scene.add(
                ambientLight
            );


            const directionalLight =
                new THREE.DirectionalLight(
                    0xffffff,
                    1
                );

            directionalLight.position.set(
                5,
                10,
                5
            );

            scene.add(
                directionalLight
            );


            // ---------------------------------------------
            // GROUND
            // ---------------------------------------------

            const groundGeometry =
                new THREE.BoxGeometry(
                    8,
                    0.3,
                    4
                );

            const groundMaterial =
                new THREE.MeshStandardMaterial({
                    color: 0xcccccc
                });

            const ground =
                new THREE.Mesh(
                    groundGeometry,
                    groundMaterial
                );

            ground.position.y = -3;

            scene.add(
                ground
            );


            // ---------------------------------------------
            // HEIGHT MARKER
            // ---------------------------------------------

            const poleGeometry =
                new THREE.CylinderGeometry(
                    0.04,
                    0.04,
                    6,
                    16
                );

            const poleMaterial =
                new THREE.MeshStandardMaterial({
                    color: 0x555555
                });

            const pole =
                new THREE.Mesh(
                    poleGeometry,
                    poleMaterial
                );

            pole.position.set(
                -3,
                0,
                0
            );

            scene.add(
                pole
            );


            // ---------------------------------------------
            // BALLS
            // ---------------------------------------------

            const ballGeometry =
                new THREE.SphereGeometry(
                    0.45,
                    32,
                    32
                );


            const ballMaterial1 =
                new THREE.MeshStandardMaterial({
                    color: 0xff5555
                });

            const ballMaterial2 =
                new THREE.MeshStandardMaterial({
                    color: 0x5555ff
                });


            const ball1 =
                new THREE.Mesh(
                    ballGeometry,
                    ballMaterial1
                );

            const ball2 =
                new THREE.Mesh(
                    ballGeometry,
                    ballMaterial2
                );


            ball1.position.set(
                -1.5,
                2,
                0
            );

            ball2.position.set(
                1.5,
                2,
                0
            );


            scene.add(ball1);
            scene.add(ball2);


            // ---------------------------------------------
            // ANIMATION STATE
            // ---------------------------------------------

            let dropping = false;

            let startTime = 0;

            const startY = 2;

            const groundY = -2.55;


            // ---------------------------------------------
            // DROP BUTTON
            // ---------------------------------------------

            document
                .getElementById("dropButton")
                .addEventListener(
                    "click",
                    () => {{

                        ball1.position.y =
                            startY;

                        ball2.position.y =
                            startY;

                        dropping = true;

                        startTime =
                            performance.now();

                    }}
                );


            // ---------------------------------------------
            // ANIMATION LOOP
            // ---------------------------------------------

            function animate() {{

                requestAnimationFrame(
                    animate
                );


                if (dropping) {{

                    const elapsed =
                        (
                            performance.now()
                            - startTime
                        ) / 1000;


                    // Simple educational
                    // gravity visualization.
                    const g = 9.8;


                    let distance =
                        0.5 * g *
                        elapsed *
                        elapsed;


                    // Scale real-world
                    // distance to scene.
                    let visualDistance =
                        distance * 0.45;


                    let newY =
                        startY
                        - visualDistance;


                    if (
                        newY <= groundY
                    ) {{

                        newY =
                            groundY;

                        dropping = false;

                    }}


                    // Both objects receive
                    // the same gravitational
                    // acceleration.

                    ball1.position.y =
                        newY;

                    ball2.position.y =
                        newY;

                }}


                renderer.render(
                    scene,
                    camera
                );

            }}


            animate();


            // ---------------------------------------------
            // RESPONSIVE
            // ---------------------------------------------

            window.addEventListener(
                "resize",
                () => {{

                    camera.aspect =
                        window.innerWidth
                        / 520;

                    camera.updateProjectionMatrix();

                    renderer.setSize(
                        window.innerWidth,
                        520
                    );

                }}
            );

        </script>

    </body>

    </html>
    """


    st.components.v1.html(
        simulation_html,
        height=540,
        scrolling=False
    )


    st.info(
        "💡 Change the experiment values and press "
        "'Drop Balls' to observe the simulation."
    )


else:

    st.info(
        "The AI generated an experiment, but this "
        "first 3D engine currently supports gravity/"
        "falling-object experiments. The experiment "
        "itself is still generated dynamically by the AI."
    )


# ---------------------------------------------------------
# OBSERVATION
# ---------------------------------------------------------

st.header("👀 What did you observe?")

observation = st.text_area(
    "Describe what happened in the experiment:",
    placeholder="Example: Both balls reached the ground at nearly the same time."
)


if st.button("🔎 Evaluate My Experiment"):

    if not observation.strip():

        st.warning(
            "Please enter your observation first."
        )

    else:

        try:

            evaluation = (
                orchestrator.evaluate_student_action(
                    session.get("topic", ""),
                    experiment,
                    observation,
                    st.session_state.prediction
                )
            )

            st.session_state.evaluation = evaluation

            st.session_state.student_state.add_observation(
                observation
            )

            st.session_state.student_state.add_evaluation(
                evaluation
            )

            st.session_state.student_state.add_history(
                {
                    "prediction":
                        st.session_state.prediction,

                    "observation":
                        observation,

                    "experiment_values":
                        current_values,

                    "evaluation":
                        evaluation
                }
            )

        except Exception as error:

            st.error(
                "The experiment could not be evaluated."
            )

            st.error(str(error))


# ---------------------------------------------------------
# EVALUATION RESULT
# ---------------------------------------------------------

if st.session_state.evaluation:

    evaluation = st.session_state.evaluation

    st.header("🧠 Evaluator Agent")

    if evaluation.get("discovery"):
        st.write(
            f"**What you discovered:** "
            f"{evaluation.get('discovery')}"
        )

    if evaluation.get("prediction_supported") is not None:

        if evaluation.get(
            "prediction_supported"
        ):

            st.success(
                "Your prediction was supported by "
                "the observation."
            )

        else:

            st.info(
                "Your prediction was not fully supported. "
                "That's okay — experiments help us learn."
            )

    if evaluation.get("misconception"):
        st.write(
            f"**Possible misconception:** "
            f"{evaluation.get('misconception')}"
        )

    if evaluation.get("next_action"):
        st.write(
            f"**Next action:** "
            f"{evaluation.get('next_action')}"
        )

    if evaluation.get("next_question"):
        st.write(
            f"### 🔄 Next Question"
        )

        st.write(
            evaluation.get("next_question")
        )


# ---------------------------------------------------------
# EXPERIMENT RULES
# ---------------------------------------------------------

if experiment.get("rules"):

    with st.expander("⚙️ Experiment Rules"):

        for rule in experiment["rules"]:
            st.write(f"- {rule}")
