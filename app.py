import json

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

from agents.orchestrator import Orchestrator
from state.student_state import StudentState


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Agentic AI 3D Kids Science Lab",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Agentic AI 3D Kids Science Lab")
st.write(
    "Explore science through AI-generated experiments "
    "and interactive 3D simulations."
)


# =========================================================
# GEMINI
# =========================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")
except Exception as error:
    st.error(f"Unable to configure Gemini: {error}")
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================

if "student_state" not in st.session_state:
    st.session_state.student_state = StudentState()

if "session_data" not in st.session_state:
    st.session_state.session_data = None

if "prediction" not in st.session_state:
    st.session_state.prediction = ""

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None


# =========================================================
# ORCHESTRATOR
# =========================================================

orchestrator = Orchestrator(model)


# =========================================================
# GENERIC 3D ENGINE
# =========================================================

def render_3d_simulation(simulation, experiment_title, variable_values):
    """Render an AI-generated generic 3D science scene safely.

    The Experiment Agent supplies semantic object types such as plant, leaf,
    sun, water, eye, lens, particle, etc. This renderer maps those types to
    reusable Three.js primitives without hard-coding a particular experiment.
    """

    simulation = simulation if isinstance(simulation, dict) else {}
    variable_values = variable_values if isinstance(variable_values, dict) else {}

    simulation_json = json.dumps(simulation, ensure_ascii=False)
    values_json = json.dumps(variable_values, ensure_ascii=False)
    title_json = json.dumps(experiment_title, ensure_ascii=False)

    # IMPORTANT:
    # This is deliberately NOT a Python f-string.
    # JavaScript braces remain untouched.
    html_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {
    margin: 0;
    overflow: hidden;
    font-family: Arial, sans-serif;
    background: #eef2f7;
}

#scene {
    width: 100%;
    height: 560px;
}

#info {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 10;
    background: rgba(255,255,255,0.95);
    padding: 12px 16px;
    border-radius: 10px;
    max-width: 390px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}

#title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 6px;
}

#status {
    font-size: 14px;
    margin-bottom: 8px;
}

button {
    padding: 8px 14px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}
</style>
</head>

<body>

<div id="info">
    <div id="title"></div>
    <div id="status">Interactive 3D experiment</div>
    <button id="runButton">▶ Run Experiment</button>
</div>

<div id="scene"></div>

<script type="module">

import * as THREE from
    'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const simulation = __SIMULATION__;
const variableValues = __VALUES__;
const experimentTitle = __TITLE__;

document.getElementById("title").textContent = experimentTitle;

const container = document.getElementById("scene");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f4f8);

const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
);

camera.position.set(0, 3.5, 13);

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setSize(
    container.clientWidth,
    container.clientHeight
);

renderer.setPixelRatio(
    Math.min(window.devicePixelRatio || 1, 2)
);

container.appendChild(renderer.domElement);

/* =========================================================
   LIGHTING
   ========================================================= */

const ambientLight = new THREE.AmbientLight(0xffffff, 1.7);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 2.2);
directionalLight.position.set(6, 10, 8);
scene.add(directionalLight);

/* =========================================================
   GROUND
   ========================================================= */

const groundGeometry = new THREE.PlaneGeometry(24, 20);

const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0xdfe6e9,
    roughness: 0.9
});

const ground = new THREE.Mesh(
    groundGeometry,
    groundMaterial
);

ground.rotation.x = -Math.PI / 2;
ground.position.y = -2.2;
scene.add(ground);

/* =========================================================
   OBJECT STORAGE
   ========================================================= */

const objectMeshes = {};
const animatedObjects = [];

/* =========================================================
   HELPERS
   ========================================================= */

function safeNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function normalizedType(value) {
    return String(value || "box")
        .toLowerCase()
        .trim()
        .replace(/[-_ ]+/g, "_");
}

function getSize(properties, fallback = 1) {
    const value = safeNumber(properties && properties.size, fallback);
    return Math.max(0.05, value);
}

function getColor(properties, fallback = 0x7aa6d8) {
    if (!properties) {
        return fallback;
    }

    const value = properties.color;

    if (typeof value === "number") {
        return value;
    }

    if (typeof value === "string") {
        const trimmed = value.trim();

        if (trimmed.startsWith("#")) {
            const parsed = Number.parseInt(trimmed.slice(1), 16);
            if (Number.isFinite(parsed)) {
                return parsed;
            }
        }

        const named = {
            red: 0xff4d4d,
            green: 0x45b649,
            blue: 0x4d79ff,
            yellow: 0xffd447,
            orange: 0xff9f43,
            purple: 0x9b59b6,
            pink: 0xff7eb6,
            white: 0xffffff,
            black: 0x222222,
            brown: 0x8b5a2b,
            gray: 0x888888,
            grey: 0x888888,
            cyan: 0x33c7cc
        };

        if (Object.prototype.hasOwnProperty.call(named, trimmed.toLowerCase())) {
            return named[trimmed.toLowerCase()];
        }
    }

    return fallback;
}

function materialFor(properties, fallbackColor) {
    return new THREE.MeshStandardMaterial({
        color: getColor(properties, fallbackColor),
        roughness: 0.72,
        metalness: 0.03
    });
}

function meshGroup() {
    return new THREE.Group();
}

function addMesh(group, geometry, material, position) {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(
        safeNumber(position && position.x),
        safeNumber(position && position.y),
        safeNumber(position && position.z)
    );
    group.add(mesh);
    return mesh;
}

function addSphere(group, radius, position, material) {
    return addMesh(
        group,
        new THREE.SphereGeometry(radius, 28, 20),
        material,
        position
    );
}

function addCylinder(group, radius, height, position, material) {
    return addMesh(
        group,
        new THREE.CylinderGeometry(radius, radius, height, 28),
        material,
        position
    );
}

function addBox(group, width, height, depth, position, material) {
    return addMesh(
        group,
        new THREE.BoxGeometry(width, height, depth),
        material,
        position
    );
}

function addCone(group, radius, height, position, material) {
    return addMesh(
        group,
        new THREE.ConeGeometry(radius, height, 24),
        material,
        position
    );
}

/* =========================================================
   SEMANTIC OBJECT BUILDERS
   ========================================================= */

function createPlant(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const stemMaterial = materialFor(properties, 0x3f8f4b);
    const leafMaterial = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0x4caf50),
        roughness: 0.8
    });
    const soilMaterial = new THREE.MeshStandardMaterial({
        color: 0x76502f,
        roughness: 1
    });

    addCylinder(
        group,
        0.10 * s,
        1.55 * s,
        {x: 0, y: 0.65 * s, z: 0},
        stemMaterial
    );

    addSphere(
        group,
        0.32 * s,
        {x: 0, y: 1.55 * s, z: 0},
        leafMaterial
    );

    const leafPositions = [
        [-0.36, 1.20, 0],
        [0.36, 1.25, 0],
        [-0.30, 1.70, 0],
        [0.30, 1.72, 0],
        [0, 1.95, 0]
    ];

    leafPositions.forEach((p, index) => {
        const leaf = addSphere(
            group,
            0.20 * s,
            {x: p[0] * s, y: p[1] * s, z: p[2] * s},
            leafMaterial
        );
        leaf.scale.set(1.4, 0.45, 0.8);
        leaf.rotation.z = index % 2 === 0 ? -0.35 : 0.35;
    });

    addCylinder(
        group,
        0.70 * s,
        0.35 * s,
        {x: 0, y: -0.15 * s, z: 0},
        soilMaterial
    );

    return group;
}

function createTree(properties) {
    const s = getSize(properties, 1.2);
    const group = meshGroup();

    const trunkMaterial = new THREE.MeshStandardMaterial({
        color: 0x8b5a2b,
        roughness: 1
    });

    const crownMaterial = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0x3d9b50),
        roughness: 0.8
    });

    addCylinder(
        group,
        0.22 * s,
        2.2 * s,
        {x: 0, y: 0.7 * s, z: 0},
        trunkMaterial
    );

    [
        [-0.55, 1.75, 0],
        [0.55, 1.75, 0],
        [0, 2.15, 0],
        [0, 1.55, 0.35]
    ].forEach((p) => {
        addSphere(
            group,
            0.75 * s,
            {x: p[0] * s, y: p[1] * s, z: p[2] * s},
            crownMaterial
        );
    });

    return group;
}

function createSun(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const material = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0xffc107),
        emissive: getColor(properties, 0xff8f00),
        emissiveIntensity: 0.7,
        roughness: 0.5
    });

    addSphere(
        group,
        0.85 * s,
        {x: 0, y: 0, z: 0},
        material
    );

    for (let i = 0; i < 8; i++) {
        const angle = (Math.PI * 2 * i) / 8;
        const ray = addCylinder(
            group,
            0.045 * s,
            0.65 * s,
            {
                x: Math.cos(angle) * 1.15 * s,
                y: Math.sin(angle) * 1.15 * s,
                z: 0
            },
            material
        );

        ray.rotation.z = Math.PI / 2;
        ray.rotation.y = angle;
    }

    return group;
}

function createWater(properties) {
    const s = getSize(properties, 0.35);
    const group = meshGroup();

    const material = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0x3d9be9),
        transparent: true,
        opacity: 0.72,
        roughness: 0.15
    });

    const droplet = addSphere(
        group,
        s,
        {x: 0, y: 0, z: 0},
        material
    );

    droplet.scale.set(0.8, 1.25, 0.8);

    return group;
}

function createSoil(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const material = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0x76502f),
        roughness: 1
    });

    addBox(
        group,
        2.8 * s,
        0.55 * s,
        2.2 * s,
        {x: 0, y: 0, z: 0},
        material
    );

    return group;
}

function createEye(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const whiteMaterial = new THREE.MeshStandardMaterial({
        color: 0xf4f4f4,
        roughness: 0.4
    });

    const irisMaterial = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0x3f73b8),
        roughness: 0.35
    });

    const pupilMaterial = new THREE.MeshStandardMaterial({
        color: 0x111111,
        roughness: 0.3
    });

    addSphere(
        group,
        1.1 * s,
        {x: 0, y: 0, z: 0},
        whiteMaterial
    );

    addSphere(
        group,
        0.43 * s,
        {x: 0, y: 0, z: 0.95 * s},
        irisMaterial
    );

    addSphere(
        group,
        0.20 * s,
        {x: 0, y: 0, z: 1.27 * s},
        pupilMaterial
    );

    return group;
}

function createLens(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const material = new THREE.MeshPhysicalMaterial({
        color: getColor(properties, 0x8ed8ff),
        transparent: true,
        opacity: 0.42,
        roughness: 0.05,
        transmission: 0.25
    });

    const lens = addSphere(
        group,
        0.85 * s,
        {x: 0, y: 0, z: 0},
        material
    );

    lens.scale.set(0.55, 1.15, 0.25);

    return group;
}

function createScreen(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const frameMaterial = new THREE.MeshStandardMaterial({
        color: 0x555555,
        roughness: 0.75
    });

    const screenMaterial = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0xf5f5f5),
        roughness: 0.5
    });

    addBox(
        group,
        2.2 * s,
        1.5 * s,
        0.12 * s,
        {x: 0, y: 0, z: 0},
        frameMaterial
    );

    addBox(
        group,
        1.85 * s,
        1.15 * s,
        0.15 * s,
        {x: 0, y: 0, z: 0.08 * s},
        screenMaterial
    );

    return group;
}

function createParticle(properties) {
    const s = getSize(properties, 0.16);
    const group = meshGroup();

    const material = new THREE.MeshStandardMaterial({
        color: getColor(properties, 0xffb300),
        emissive: getColor(properties, 0xff8f00),
        emissiveIntensity: 0.2
    });

    addSphere(
        group,
        s,
        {x: 0, y: 0, z: 0},
        material
    );

    return group;
}

function createRay(properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();

    const material = new THREE.MeshBasicMaterial({
        color: getColor(properties, 0xffc107)
    });

    addCylinder(
        group,
        0.035 * s,
        2.4 * s,
        {x: 0, y: 0, z: 0},
        material
    );

    return group;
}

function createGenericPrimitive(type, properties) {
    const s = getSize(properties, 1);
    const group = meshGroup();
    const material = materialFor(properties, 0x6c8ebf);

    if (type === "sphere" || type === "ball") {
        addSphere(
            group,
            s,
            {x: 0, y: 0, z: 0},
            material
        );
    } else if (type === "cylinder") {
        addCylinder(
            group,
            s,
            2 * s,
            {x: 0, y: 0, z: 0},
            material
        );
    } else if (type === "cone") {
        addCone(
            group,
            s,
            2 * s,
            {x: 0, y: 0, z: 0},
            material
        );
    } else if (type === "plane") {
        addBox(
            group,
            2 * s,
            0.10 * s,
            2 * s,
            {x: 0, y: 0, z: 0},
            material
        );
    } else {
        addBox(
            group,
            2 * s,
            2 * s,
            2 * s,
            {x: 0, y: 0, z: 0},
            material
        );
    }

    return group;
}

/* =========================================================
   CREATE SEMANTIC OBJECT
   ========================================================= */

function createObject(objectData, index) {
    if (!objectData || typeof objectData !== "object") {
        return;
    }

    const properties = objectData.properties || {};
    const type = normalizedType(objectData.type);

    let group;

    if (type === "plant" || type === "seedling" || type === "flower") {
        group = createPlant(properties);
    } else if (type === "tree") {
        group = createTree(properties);
    } else if (
        type === "leaf" ||
        type === "leaves" ||
        type === "foliage"
    ) {
        group = createPlant(properties);
        group.scale.set(0.7, 0.7, 0.7);
    } else if (
        type === "sun" ||
        type === "sunlight" ||
        type === "light_source"
    ) {
        group = createSun(properties);
    } else if (
        type === "water" ||
        type === "droplet" ||
        type === "water_drop"
    ) {
        group = createWater(properties);
    } else if (
        type === "soil" ||
        type === "earth" ||
        type === "ground"
    ) {
        group = createSoil(properties);
    } else if (
        type === "eye" ||
        type === "eyeball"
    ) {
        group = createEye(properties);
    } else if (
        type === "lens" ||
        type === "corrective_lens" ||
        type === "convex_lens" ||
        type === "concave_lens"
    ) {
        group = createLens(properties);
    } else if (
        type === "screen" ||
        type === "retina" ||
        type === "wall"
    ) {
        group = createScreen(properties);
    } else if (
        type === "particle" ||
        type === "particles" ||
        type === "molecule"
    ) {
        group = createParticle(properties);
    } else if (
        type === "ray" ||
        type === "light_ray" ||
        type === "arrow"
    ) {
        group = createRay(properties);
    } else {
        group = createGenericPrimitive(type, properties);
    }

    const position = properties.position || {};

    group.position.set(
        safeNumber(position.x),
        safeNumber(position.y),
        safeNumber(position.z)
    );

    const id = objectData.id || ("object_" + index);

    group.userData.semanticType = type;
    group.userData.objectData = objectData;

    scene.add(group);
    objectMeshes[id] = group;

    /*
     * Only objects that are naturally dynamic are animated.
     * Static scientific objects such as plants, eyes, lenses and boxes
     * must not rotate just because they exist.
     */
    const dynamicTypes = [
        "particle",
        "particles",
        "molecule",
        "droplet",
        "water_drop",
        "sun",
        "sunlight",
        "light_source"
    ];

    if (dynamicTypes.includes(type)) {
        animatedObjects.push({
            mesh: group,
            type: type,
            phase: index * 0.7
        });
    }
}

/* =========================================================
   CREATE AI-GENERATED OBJECTS
   ========================================================= */

if (Array.isArray(simulation.objects)) {
    simulation.objects.forEach(createObject);
}

/* =========================================================
   LABELS
   ========================================================= */

function createLabel(text, position) {
    if (!text) {
        return;
    }

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    canvas.width = 640;
    canvas.height = 150;

    context.fillStyle = "rgba(255,255,255,0.92)";
    context.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    context.fillStyle = "#111111";
    context.font = "28px Arial";
    context.textBaseline = "middle";

    const labelText = String(text).slice(0, 42);

    context.fillText(
        labelText,
        20,
        75
    );

    const texture = new THREE.CanvasTexture(canvas);

    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true
    });

    const sprite = new THREE.Sprite(material);

    sprite.scale.set(4.4, 1.03, 1);
    sprite.position.copy(position);

    scene.add(sprite);
}

if (Array.isArray(simulation.objects)) {
    simulation.objects.forEach((objectData, index) => {
        if (!objectData || typeof objectData !== "object") {
            return;
        }

        const id = objectData.id || ("object_" + index);
        const mesh = objectMeshes[id];

        if (mesh && objectData.label) {
            const labelPosition = mesh.position.clone();
            labelPosition.y += 1.8;

            createLabel(
                objectData.label,
                labelPosition
            );
        }
    });
}

/* =========================================================
   RELATIONSHIP LINES
   ========================================================= */

if (Array.isArray(simulation.relationships)) {
    simulation.relationships.forEach(relationship => {
        if (!relationship || typeof relationship !== "object") {
            return;
        }

        const source = objectMeshes[relationship.source];
        const target = objectMeshes[relationship.target];

        if (!source || !target) {
            return;
        }

        const points = [
            source.position.clone(),
            target.position.clone()
        ];

        const geometry =
            new THREE.BufferGeometry().setFromPoints(points);

        const material =
            new THREE.LineBasicMaterial({
                color: 0x555555
            });

        const line =
            new THREE.Line(
                geometry,
                material
            );

        scene.add(line);
    });
}

/* =========================================================
   VARIABLE DISPLAY
   ========================================================= */

const variableEntries =
    Object.entries(variableValues || {});

if (variableEntries.length > 0) {
    const variableText = variableEntries
        .slice(0, 5)
        .map(([key, value]) => {
            return key + ": " + value;
        })
        .join("  |  ");

    const variableDiv = document.createElement("div");
    variableDiv.style.position = "absolute";
    variableDiv.style.left = "12px";
    variableDiv.style.bottom = "12px";
    variableDiv.style.zIndex = "10";
    variableDiv.style.background = "rgba(255,255,255,0.92)";
    variableDiv.style.padding = "8px 12px";
    variableDiv.style.borderRadius = "8px";
    variableDiv.style.fontSize = "13px";
    variableDiv.textContent = variableText;

    container.appendChild(variableDiv);
}

/* =========================================================
   EXPERIMENT CONTROL
   ========================================================= */

let running = false;

const button =
    document.getElementById("runButton");

const status =
    document.getElementById("status");

button.onclick = function() {
    running = !running;

    if (running) {
        button.textContent = "⏸ Pause Experiment";
        status.textContent = "Experiment running...";
    } else {
        button.textContent = "▶ Run Experiment";
        status.textContent = "Experiment paused.";
    }
};

/* =========================================================
   ANIMATION
   ========================================================= */

const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    const time = clock.getElapsedTime();

    if (running) {
        animatedObjects.forEach(item => {
            if (!item.mesh) {
                return;
            }

            if (
                item.type === "particle" ||
                item.type === "particles" ||
                item.type === "molecule"
            ) {
                item.mesh.position.y +=
                    Math.sin(time * 2 + item.phase) * 0.002;
            } else if (
                item.type === "droplet" ||
                item.type === "water_drop"
            ) {
                item.mesh.position.y +=
                    Math.sin(time * 2.5 + item.phase) * 0.004;
            } else if (
                item.type === "sun" ||
                item.type === "sunlight" ||
                item.type === "light_source"
            ) {
                item.mesh.rotation.z =
                    Math.sin(time * 0.6 + item.phase) * 0.05;
            }
        });
    }

    renderer.render(
        scene,
        camera
    );
}

animate();

/* =========================================================
   RESIZE
   ========================================================= */

window.addEventListener(
    "resize",
    function() {
        camera.aspect =
            container.clientWidth /
            container.clientHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            container.clientWidth,
            container.clientHeight
        );
    }
);

</script>

</body>
</html>
"""

    simulation_html = (
        html_template
        .replace("__SIMULATION__", simulation_json)
        .replace("__VALUES__", values_json)
        .replace("__TITLE__", title_json)
    )

    components.html(
        simulation_html,
        height=590,
        scrolling=False
    )


# =========================================================
# TOPIC
# =========================================================

topic = st.text_input(
    "Enter any science topic",
    placeholder="Example: Why do plants need sunlight?"
)


# =========================================================
# START LEARNING SESSION
# =========================================================

if st.button(
    "🚀 Start Learning Session",
    type="primary"
):

    if not topic.strip():

        st.warning(
            "Please enter a science topic first."
        )

        st.stop()


    st.session_state.student_state = StudentState()

    st.session_state.session_data = None

    st.session_state.prediction =  ""

    st.session_state.evaluation = None


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

                st.error(
                    session_data["error"]
                )

                st.stop()


            st.session_state.session_data = session_data


            st.session_state.student_state.topic = topic.strip()


        except Exception as error:

            st.error(
                "The AI session could not be started."
            )

            st.error(
                str(error)
            )

            st.stop()


# =========================================================
# SESSION DISPLAY
# =========================================================

session_data = st.session_state.session_data


if session_data:

    science =   session_data.get(
            "science",
            {}
        )

    teacher =  session_data.get(
            "teacher",
            {}
        )

    experiment = session_data.get(
            "experiment",
            {}
        )


    # =====================================================
    # SCIENCE AGENT
    # =====================================================

    st.header("🧠 Science Agent")

    st.subheader("Core Concept")

    st.write(
        science.get(
            "concept",
            ""
        )
    )


    if science.get("variables"):

        st.subheader(
            "Scientific Variables"
        )

        for variable in science["variables"]:

            st.write(
                f"**{variable.get('name', '')}:** "
                f"{variable.get('value', '')} "
                f"{variable.get('unit', '')} — "
                f"{variable.get('role', '')}"
            )


    if science.get("relationships"):

        st.subheader(
            "Cause-and-Effect Relationships"
        )

        for relationship in science["relationships"]:

            st.write(
                f"• {relationship}"
            )


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


    # =====================================================
    # TEACHER AGENT
    # =====================================================

    st.header("👩‍🏫 Teacher Agent")

    st.subheader(
        teacher.get(
            "question",
            "No question generated."
        )
    )


    option_a =  teacher.get(
            "option_a",
            ""
        )

    option_b =  teacher.get(
            "option_b",
            ""
        )


    selected_option =   st.radio(
            "Choose your answer:",
            [
                option_a,
                option_b
            ],
            key="answer_choice"
        )


    if st.button(
        "Check Answer"
    ):

        if selected_option == option_a:

            selected_letter = "A"

        else:

            selected_letter = "B"


        correct =   teacher.get(
                "correct_option",
                ""
            )


        if selected_letter == correct:

            st.success(
                "✅ Correct!"
            )

        else:

            st.warning(
                "❌ Not quite. Let's explore it through the experiment."
            )


    # =====================================================
    # PREDICTION
    # =====================================================

    prediction_prompt =  teacher.get(
            "prediction_prompt",
            "What do you predict will happen?"
        )


    st.subheader(
        "🔮 Make a Prediction"
    )

    st.write(
        prediction_prompt
    )


    prediction = st.text_area(
            "Your prediction",
            value=st.session_state.prediction,
            key="prediction_input"
        )


    if st.button(
        "Save Prediction"
    ):

        st.session_state.prediction = prediction


        st.session_state.student_state.set_prediction(
            prediction
        )


        st.success(
            "Prediction saved!"
        )


    # =====================================================
    # EXPERIMENT
    # =====================================================

    st.header(
        "🧪 AI-Generated Experiment"
    )


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


    variables = experiment.get(
            "variables",
            {}
        )


    current_values = {}


    if variables:

        st.subheader(
            "🎛️ Experiment Controls"
        )


        for name, config in variables.items():

            try:

                minimum =  float(
                        config.get(
                            "min",
                            0
                        )
                    )

                maximum = float(
                        config.get(
                            "max",
                            100
                        )
                    )

                default = float(
                      config.get(
                            "default",
                            minimum
                        )
                    )

            except Exception:

                minimum = 0.0
                maximum = 100.0
                default = 50.0


            if minimum >= maximum:

                maximum =  minimum + 100


            default = max(
                    minimum,
                    min(
                        default,
                        maximum
                    )
                )


            if (
                minimum.is_integer()
                and maximum.is_integer()
            ):

                step = 1.0

            else:

                step = (maximum - minimum) / 100.0


            value = st.slider(
                    f"{name} ({config.get('unit', '')})",
                    min_value=minimum,
                    max_value=maximum,
                    value=default,
                    step=step,
                    key=f"experiment_{name}"
                )


            current_values[name] = value


            st.caption(
                config.get(
                    "description",
                    ""
                )
            )


    # =====================================================
    # 3D
    # =====================================================

    st.header(
        "🌐 3D Virtual Experiment"
    )


    simulation = experiment.get(
            "simulation",
            {}
        )


    if not simulation:

        st.warning(
            "The Experiment Agent did not return "
            "a 3D simulation specification."
        )

    else:

        render_3d_simulation(
            simulation,
            experiment.get(
                "title",
                "Science Experiment"
            ),
            current_values
        )


        controls = simulation.get(
                "controls",
                []
            )


        if controls:

            st.subheader(
                "🎛️ AI Simulation Controls"
            )

            for control in controls:

                st.write(
                    f"**{control.get('variable', '')}:** "
                    f"{control.get('effect', '')}"
                )


        actions = simulation.get(
                "actions",
                []
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


        observations = simulation.get(
                "visual_observations",
                []
            )


        if observations:

            st.subheader(
                "👀 What to Observe"
            )

            for observation_item in observations:

                st.write(
                    f"• {observation_item}"
                )


    # =====================================================
    # OBSERVATION
    # =====================================================

    st.header(
        "🔎 Student Observation"
    )


    observation =  st.text_area(
            "What did you observe in the experiment?",
            key="observation_input"
        )


    if st.button(
        "🧠 Evaluate My Observation"
    ):

        if not observation.strip():

            st.warning(
                "Please describe your observation first."
            )

        else:

            with st.spinner(
                "Evaluator Agent is analyzing your observation..."
            ):

                try:

                    evaluation =  orchestrator.evaluate_student_action(
                            topic,
                            experiment,
                            observation,
                            st.session_state.prediction
                        )


                    st.session_state.evaluation =  evaluation


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


    # =====================================================
    # EVALUATION
    # =====================================================

    evaluation = st.session_state.evaluation


    if evaluation:

        st.header(
            "🧠 Evaluator Agent"
        )


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


        if evaluation.get(
            "misconception"
        ):

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


    # =====================================================
    # RULES
    # =====================================================

    if experiment.get("rules"):

        st.header(
            "📐 Experiment Rules"
        )


        for rule in experiment["rules"]:

            st.write(
                f"• {rule}"
            )
