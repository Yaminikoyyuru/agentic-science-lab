import json
import html

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

from agents.orchestrator import Orchestrator
from state.student_state import StudentState


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Agentic AI 3D Kids Science Lab",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Agentic AI 3D Kids Science Lab")
st.write(
    "Explore science through AI-generated experiments and "
    "interactive 3D simulations."
)


# ---------------------------------------------------------
# GEMINI CONFIGURATION
# ---------------------------------------------------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY is not configured in Streamlit Secrets."
    )
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")
except Exception as error:
    st.error(f"Unable to configure Gemini: {error}")
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
    "Enter any science topic",
    placeholder="Example: Why do plants need sunlight?"
)


# ---------------------------------------------------------
# START SESSION
# ---------------------------------------------------------

if st.button("🚀 Start Learning Session", type="primary"):

    if not topic.strip():
        st.warning("Please enter a science topic first.")
        st.stop()

    # Reset state for new session
    st.session_state.student_state = StudentState()
    st.session_state.prediction = ""
    st.session_state.evaluation = None
    st.session_state.experiment_values = {}

    with st.spinner(
        "AI Science, Teacher and Experiment Agents are working..."
    ):

        try:
            session_data = orchestrator.start_learning_session(
                topic.strip()
            )

            if "error" in session_data:
                st.error(
                    "The AI session could not be started."
                )
                st.error(session_data["error"])
                st.stop()

            st.session_state.session_data = session_data
            st.session_state.student_state.topic = topic.strip()

        except Exception as error:
            st.error(
                "The AI session could not be started."
            )
            st.error(str(error))
            st.stop()


# ---------------------------------------------------------
# DISPLAY SESSION
# ---------------------------------------------------------

session_data = st.session_state.session_data

if session_data:

    science = session_data.get("science", {})
    teacher = session_data.get("teacher", {})
    experiment = session_data.get("experiment", {})


    # -----------------------------------------------------
    # SCIENCE AGENT
    # -----------------------------------------------------

    st.header("🧠 Science Agent")

    st.subheader("Core Concept")
    st.write(science.get("concept", ""))

    if science.get("variables"):
        st.subheader("Scientific Variables")

        for variable in science["variables"]:
            st.write(
                f"**{variable.get('name', '')}:** "
                f"{variable.get('value', '')} "
                f"{variable.get('unit', '')} — "
                f"{variable.get('role', '')}"
            )

    if science.get("relationships"):
        st.subheader("Cause-and-Effect Relationships")

        for relationship in science["relationships"]:
            st.write(f"• {relationship}")

    st.write(
        f"**Experiment idea:** "
        f"{science.get('experiment', '')}"
    )

    st.write(
        f"**Expected observation:** "
        f"{science.get('expected_observation', '')}"
    )

    st.write(
        f"**Scientific explanation:** "
        f"{science.get('explanation', '')}"
    )


    # -----------------------------------------------------
    # TEACHER AGENT
    # -----------------------------------------------------

    st.header("👩‍🏫 Teacher Agent")

    st.subheader(
        teacher.get(
            "question",
            "No question generated."
        )
    )

    option_a = teacher.get("option_a", "")
    option_b = teacher.get("option_b", "")

    selected_option = st.radio(
        "Choose your answer:",
        [
            option_a,
            option_b
        ],
        key="answer_choice"
    )

    if st.button("Check Answer"):

        if selected_option == option_a:
            selected_letter = "A"
        else:
            selected_letter = "B"

        correct = teacher.get("correct_option", "")

        if selected_letter == correct:
            st.success("✅ Correct!")
        else:
            st.warning("❌ Not quite. Let's explore it through the experiment.")

    prediction_prompt = teacher.get(
        "prediction_prompt",
        "What do you predict will happen?"
    )

    st.subheader("🔮 Make a Prediction")
    st.write(prediction_prompt)

    prediction = st.text_area(
        "Your prediction",
        value=st.session_state.prediction,
        key="prediction_input"
    )

    if st.button("Save Prediction"):
        st.session_state.prediction = prediction
        st.session_state.student_state.set_prediction(
            prediction
        )
        st.success("Prediction saved!")


    # -----------------------------------------------------
    # EXPERIMENT AGENT
    # -----------------------------------------------------

    st.header("🧪 AI-Generated Experiment")

    st.subheader(
        experiment.get(
            "title",
            "Interactive Science Experiment"
        )
    )

    st.write(
        experiment.get(
            "expected_result",
            ""
        )
    )

    variables = experiment.get("variables", {})

    current_values = {}

    if variables:

        st.subheader("🎛️ Experiment Controls")

        for name, config in variables.items():

            try:
                minimum = float(config.get("min", 0))
                maximum = float(config.get("max", 100))
                default = float(config.get("default", minimum))
            except Exception:
                minimum = 0.0
                maximum = 100.0
                default = 50.0

            if minimum >= maximum:
                maximum = minimum + 100

            default = max(
                minimum,
                min(default, maximum)
            )

            # Streamlit slider step
            if (
                float(minimum).is_integer()
                and float(maximum).is_integer()
            ):
                step = 1.0
            else:
                step = (maximum - minimum) / 100.0

            value = st.slider(
                f"{name} ({config.get('unit', '')})",
                min_value=float(minimum),
                max_value=float(maximum),
                value=float(default),
                step=float(step),
                key=f"experiment_{name}"
            )

            current_values[name] = value

            st.caption(
                config.get(
                    "description",
                    ""
                )
            )

    st.session_state.experiment_values = current_values


    # -----------------------------------------------------
    # GENERIC 3D SIMULATION
    # -----------------------------------------------------

    st.header("🌐 3D Virtual Experiment")

    simulation = experiment.get("simulation", {})

    if not simulation:
        st.warning(
            "The Experiment Agent did not return a 3D "
            "simulation specification."
        )

    else:

        objects = simulation.get("objects", [])
        relationships = simulation.get("relationships", [])
        controls = simulation.get("controls", [])
        actions = simulation.get("actions", [])
        observations = simulation.get(
            "visual_observations",
            []
        )


        # Safely convert AI data to JSON for JavaScript
        simulation_json = json.dumps(
            simulation,
            ensure_ascii=False
        )

        values_json = json.dumps(
            current_values,
            ensure_ascii=False
        )

        title_json = json.dumps(
            experiment.get(
                "title",
                "Science Experiment"
            ),
            ensure_ascii=False
        )


        # -------------------------------------------------
        # GENERIC THREE.JS ENGINE
        # -------------------------------------------------

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
    background: #f5f5f5;
}}

#scene {{
    width: 100%;
    height: 520px;
}}

#info {{
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(255,255,255,0.92);
    padding: 12px;
    border-radius: 8px;
    max-width: 340px;
    z-index: 10;
}}

#action {{
    margin-top: 8px;
    padding: 8px 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}}

</style>

</head>

<body>

<div id="info">

<strong id="experiment-title"></strong>

<div id="description">
Interactive 3D experiment
</div>

<button id="action">
▶ Run Experiment
</button>

</div>

<div id="scene"></div>


<script type="module">

import * as THREE from
'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';


const simulation =
{simulation_json};


const variableValues =
{values_json};


const experimentTitle =
{title_json};


document.getElementById(
    "experiment-title"
).textContent = experimentTitle;


// -------------------------------------------------------
// SCENE
// -------------------------------------------------------

const container =
document.getElementById("scene");


const scene =
new THREE.Scene();


scene.background =
new THREE.Color(0xf0f4f8);


const camera =
new THREE.PerspectiveCamera(
    45,
    container.clientWidth /
    container.clientHeight,
    0.1,
    1000
);


camera.position.set(
    0,
    5,
    12
);


const renderer =
new THREE.WebGLRenderer({
    antialias: true
});


renderer.setSize(
    container.clientWidth,
    container.clientHeight
);


renderer.setPixelRatio(
    window.devicePixelRatio
);


container.appendChild(
    renderer.domElement
);


// -------------------------------------------------------
// LIGHTING
// -------------------------------------------------------

const ambientLight =
new THREE.AmbientLight(
    0xffffff,
    1.5
);

scene.add(
    ambientLight
);


const directionalLight =
new THREE.DirectionalLight(
    0xffffff,
    2
);

directionalLight.position.set(
    5,
    10,
    8
);

scene.add(
    directionalLight
);


// -------------------------------------------------------
// GROUND
// -------------------------------------------------------

const groundGeometry =
new THREE.PlaneGeometry(
    20,
    20
);


const groundMaterial =
new THREE.MeshStandardMaterial({
    color: 0xdfe6e9
});


const ground =
new THREE.Mesh(
    groundGeometry,
    groundMaterial
);


ground.rotation.x =
-Math.PI / 2;


ground.position.y =
-2;


scene.add(
    ground
);


// -------------------------------------------------------
// OBJECT CREATION
// -------------------------------------------------------

const objectMeshes = {};


function createGeometry(type, size) {{

    const s =
        Number(size) || 1;

    if (type === "sphere") {{

        return new THREE.SphereGeometry(
            s,
            32,
            32
        );

    }}

    if (type === "cylinder") {{

        return new THREE.CylinderGeometry(
            s,
            s,
            s * 2,
            32
        );

    }}

    if (type === "plane") {{

        return new THREE.BoxGeometry(
            s * 2,
            0.1,
            s * 2
        );

    }}

    return new THREE.BoxGeometry(
        s * 2,
        s * 2,
        s * 2
    );
}}


function createObject(objectData, index) {{

    const properties =
        objectData.properties || {{}};

    const geometry =
        createGeometry(
            objectData.type,
            properties.size
        );


    const material =
        new THREE.MeshStandardMaterial({{
            color:
                new THREE.Color(
                    0.25 + (index * 0.13) % 0.6,
                    0.45 + (index * 0.09) % 0.4,
                    0.65 + (index * 0.07) % 0.3
                )
        }});


    const mesh =
        new THREE.Mesh(
            geometry,
            material
        );


    const position =
        properties.position || {{}};


    mesh.position.set(
        Number(position.x) || 0,
        Number(position.y) || 0,
        Number(position.z) || 0
    );


    scene.add(
        mesh
    );


    const id =
        objectData.id ||
        "object_" + index;


    objectMeshes[id] =
        mesh;

}}


// Create every AI-described object

objects.forEach(
    createObject
);


// -------------------------------------------------------
// LABELS
// -------------------------------------------------------

function createLabel(text, position) {{

    const canvas =
        document.createElement("canvas");

    const context =
        canvas.getContext("2d");

    canvas.width =
        512;

    canvas.height =
        128;

    context.fillStyle =
        "white";

    context.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    context.fillStyle =
        "black";

    context.font =
        "28px Arial";

    context.fillText(
        text,
        20,
        70
    );

    const texture =
        new THREE.CanvasTexture(
            canvas
        );

    const material =
        new THREE.SpriteMaterial({{
            map: texture
        }});

    const sprite =
        new THREE.Sprite(
            material
        );

    sprite.scale.set(
        4,
        1,
        1
    );

    sprite.position.copy(
        position
    );

    scene.add(
        sprite
    );
}}


// Add labels

objects.forEach(
    (objectData, index) => {{

        const id =
            objectData.id ||
            "object_" + index;

        const mesh =
            objectMeshes[id];

        if (mesh && objectData.label) {{

            createLabel(
                objectData.label,
                mesh.position.clone().add(
                    new THREE.Vector3(
                        0,
                        1.2,
                        0
                    )
                )
            );

        }}

    }}
);


// -------------------------------------------------------
// RELATIONSHIP LINES
// -------------------------------------------------------

relationships.forEach(
    relationship => {{

        const source =
            objectMeshes[
                relationship.source
            ];

        const target =
            objectMeshes[
                relationship.target
            ];

        if (
            source &&
            target
        ) {{

            const points = [
                source.position.clone(),
                target.position.clone()
            ];

            const geometry =
                new THREE.BufferGeometry()
                    .setFromPoints(
                        points
                    );

            const material =
                new THREE.LineBasicMaterial({{
                    color: 0x555555
                }});

            const line =
                new THREE.Line(
                    geometry,
                    material
                );

            scene.add(
                line
            );

        }}

    }}
);


// -------------------------------------------------------
// RUN EXPERIMENT
// -------------------------------------------------------

let running = false;

const button =
document.getElementById(
    "action"
);


button.onclick = () => {{

    running =
        !running;

    button.textContent =
        running
        ? "⏸ Pause Experiment"
        : "▶ Run Experiment";

}};


// -------------------------------------------------------
// ANIMATION
// -------------------------------------------------------

const clock =
new THREE.Clock();


function animate() {{

    requestAnimationFrame(
        animate
    );


    const time =
        clock.getElapsedTime();


    if (running) {{

        objects.forEach(
            (objectData, index) => {{

                const id =
                    objectData.id ||
                    "object_" + index;

                const mesh =
                    objectMeshes[id];

                if (!mesh) return;


                /*
                 Generic educational motion.

                 The AI describes the experiment,
                 while the renderer provides a
                 simple interactive movement.

                 This is intentionally conservative:
                 it does not execute AI-generated code.
                */

                mesh.rotation.y =
                    time * 0.4;

            }}
        );

    }}


    renderer.render(
        scene,
        camera
    );
}}


animate();


// -------------------------------------------------------
// RESPONSIVE RESIZE
// -------------------------------------------------------

window.addEventListener(
    "resize",
    () => {{

        camera.aspect =
            container.clientWidth /
            container.clientHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            container.clientWidth,
            container.clientHeight
        );

    }}
);

</script>

</body>

</html>
"""


        components.html(
            simulation_html,
            height=550,
            scrolling=False
        )


        # -------------------------------------------------
        # AI SIMULATION DESCRIPTION
        # -------------------------------------------------

        if controls:

            st.subheader(
                "🎛️ What the AI says the controls do"
            )

            for control in controls:

                st.write(
                    f"**{control.get('variable', '')}:** "
                    f"{control.get('effect', '')}"
                )


        if actions:

            st.subheader(
                "🖐️ Student Actions"
            )

            for action in actions:

                st.write(
                    f"• **{action.get('name', '')}:** "
                    f"{action.get('description', '')}"
                )


        if observations:

            st.subheader(
                "👀 What to Observe"
            )

            for observation in observations:

                st.write(
                    f"• {observation}"
                )


    # -----------------------------------------------------
    # OBSERVATION
    # -----------------------------------------------------

    st.header("🔎 Student Observation")

    observation = st.text_area(
        "What did you observe in the experiment?",
        key="observation_input"
    )


    if st.button("🧠 Evaluate My Observation"):

        if not observation.strip():

            st.warning(
                "Please describe your observation first."
            )

        else:

            with st.spinner(
                "Evaluator Agent is analyzing your observation..."
            ):

                try:

                    evaluation =
                        orchestrator.evaluate_student_action(
                            topic,
                            experiment,
                            observation,
                            st.session_state.prediction
                        )

                    st.session_state.evaluation =
                        evaluation

                    st.session_state.student_state.add_observation(
                        observation
                    )

                    st.session_state.student_state.add_evaluation(
                        evaluation
                    )

                except Exception as error:

                    st.error(
                        f"Evaluation failed: {error}"
                    )


    # -----------------------------------------------------
    # EVALUATION RESULT
    # -----------------------------------------------------

    evaluation =
        st.session_state.evaluation

    if evaluation:

        st.header("🧠 Evaluator Agent")

        st.write(
            f"**Observation valid:** "
            f"{evaluation.get('observation_valid', '')}"
        )

        st.write(
            f"**Discovery:** "
            f"{evaluation.get('discovery', '')}"
        )

        st.write(
            f"**Prediction supported:** "
            f"{evaluation.get('prediction_supported', '')}"
        )

        if evaluation.get("misconception"):

            st.write(
                f"**Possible misconception:** "
                f"{evaluation.get('misconception', '')}"
            )

        st.write(
            f"**Next action:** "
            f"{evaluation.get('next_action', '')}"
        )

        st.write(
            f"**Next question:** "
            f"{evaluation.get('next_question', '')}"
        )


    # -----------------------------------------------------
    # EXPERIMENT RULES
    # -----------------------------------------------------

    if experiment.get("rules"):

        st.header("📐 Experiment Rules")

        for rule in experiment["rules"]:

            st.write(
                f"• {rule}"
            )
