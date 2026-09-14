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

Your job is to design a simple interactive experiment
that allows a 10-year-old student to explore the
scientific concept.

The experiment should contain:

1. A clear experiment title
2. Controllable scientific variables
3. A safe default value for each variable
4. Minimum and maximum values
5. A simple description of what changing each variable does
6. Scientifically reasonable cause-and-effect rules
7. An expected result

Keep the experiment scientifically meaningful.
Do not invent impossible scientific relationships.

Return ONLY valid JSON.

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
        }},
        "variable2": {{
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
    "expected_result": "..."
}}
"""

        response = self.model.generate_content(prompt)

        text = response.text.strip()

        try:
            return json.loads(text)

        except Exception:

            return {
                "title": topic,
                "variables": {},
                "rules": [],
                "expected_result": ""
            }
