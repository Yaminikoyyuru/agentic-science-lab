import json


class ExperimentAgent:
    def __init__(self, model):
        self.model = model

    def create_experiment(self, topic, science_result):
        prompt = f"""
You are an Experiment Design Agent inside an
AI-powered K-12 virtual science laboratory.

Student topic:
{topic}

Scientific analysis:
{json.dumps(science_result, indent=2)}

Your job is to design a scientifically meaningful,
interactive experiment for the student.

IMPORTANT:
The student may enter ANY science topic.
Do NOT assume a fixed list of topics.
Do NOT classify the topic into a predefined topic list.

The experiment must be designed dynamically from the
scientific concept.

The experiment should contain:

1. A clear experiment title
2. Important controllable scientific variables
3. Safe default values
4. Minimum and maximum values
5. A description of what changing each variable does
6. Scientifically reasonable cause-and-effect rules
7. An expected result

In addition, create a GENERIC 3D SIMULATION SPECIFICATION.

The 3D specification must describe what should be
shown in an interactive virtual laboratory.

The 3D simulation should be based on the actual science
concept and experiment you designed.

Describe:

1. Objects/entities that should appear in the 3D scene
2. Important properties of each object
3. Relationships between objects
4. Which variables control the objects
5. What should happen visually when the student changes
   a variable
6. What student actions should be possible
7. What observable result should be shown

Do NOT write JavaScript.
Do NOT write HTML.
Do NOT write Three.js code.
Only describe the simulation using structured JSON data.

The 3D scene must be generic and reusable.

Use simple 3D primitives where appropriate, such as:

- sphere
- box
- cylinder
- plane
- line
- particles
- arrows
- labels
- containers

But choose the appropriate objects based on the science
topic. Do not force these objects if they are not useful.

The simulation should help the student visually understand
the scientific cause-and-effect relationship.

Return ONLY valid JSON.
Do NOT use markdown.
Do NOT use ```json.
Do NOT add any explanation before or after the JSON.

Use exactly this structure:

{{
    "title": "...",

    "variables": {{
        "variable1": {{
            "min": 0,
            "max": 100,
            "default": 50,
            "unit": "...",
            "description": "..."
        }}
    }},

    "rules": [
        "..."
    ],

    "expected_result": "...",

    "simulation": {{
        "objects": [
            {{
                "id": "...",
                "type": "...",
                "label": "...",
                "properties": {{
                    "size": 1,
                    "position": {{
                        "x": 0,
                        "y": 0,
                        "z": 0
                    }}
                }}
            }}
        ],

        "relationships": [
            {{
                "source": "...",
                "target": "...",
                "relationship": "..."
            }}
        ],

        "controls": [
            {{
                "variable": "...",
                "effect": "..."
            }}
        ],

        "actions": [
            {{
                "name": "...",
                "description": "..."
            }}
        ],

        "visual_observations": [
            "..."
        ]
    }}
}}
"""

        try:
            response = self.model.generate_content(prompt)

            text = response.text.strip()

            # Remove markdown code fences if Gemini adds them
            if text.startswith("```json"):
                text = text[7:]

            if text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            if not text:
                return {
                    "error": "Experiment Agent returned an empty response."
                }

            return json.loads(text)

        except json.JSONDecodeError:
            return {
                "error": "Experiment Agent returned invalid JSON.",
                "raw_response": text if "text" in locals() else ""
            }

        except Exception as error:
            return {
                "error": f"Experiment Agent error: {error}"
            }
