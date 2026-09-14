import json

from tools.calculator import calculate


class ScienceAgent:

    def __init__(self, model):
        self.model = model

    def calculate_value(self, expression):

        try:
            return calculate(expression)

        except Exception as error:
            return f"Calculation error: {error}"

    def analyze_topic(self, topic):

        prompt = f"""
You are a Science Reasoning Agent inside an AI-powered
K-12 virtual science laboratory.

Student topic:
{topic}

Your job is to analyze the topic and identify:

1. Core scientific concept
2. Important variables
3. Cause-and-effect relationships
4. A simple experiment suitable for a 10-year-old
5. Expected observation
6. Scientific explanation

Keep the science accurate but explain the reasoning
at a level that can later be adapted for a child.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "concept": "...",
    "variables": [
        {{
            "name": "...",
            "value": 50,
            "unit": "...",
            "role": "..."
        }}
    ],
    "relationships": [
        "..."
    ],
    "experiment": "...",
    "expected_observation": "...",
    "explanation": "..."
}}
"""

        try:
            response = self.model.generate_content(prompt)

            text = response.text.strip()

            return json.loads(text)

        except Exception as error:

            return {
                "error": str(error),
                "concept": topic,
                "variables": [],
                "relationships": [],
                "experiment": "",
                "expected_observation": "",
                "explanation": ""
            }
