````python
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

    def _extract_json(self, text):
        """Safely extract a JSON object from Gemini's response."""

        if not text:
            raise ValueError("Gemini returned an empty response.")

        text = text.strip()

        # Remove markdown code fences
        if text.startswith("```json"):
            text = text[7:].strip()

        elif text.startswith("```"):
            text = text[3:].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

        # First attempt: response is already pure JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Second attempt: find the first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Gemini response did not contain a valid JSON object."
            )

        json_text = text[start:end + 1]

        return json.loads(json_text)

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

Do NOT use markdown.
Do NOT use ```json.
Do NOT add any explanation before or after the JSON.

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

            # Safely obtain Gemini response text
            text = getattr(response, "text", "")

            if text is None:
                text = ""

            text = str(text).strip()

            if not text:
                return {
                    "error": (
                        "Science Agent received an empty response "
                        "from Gemini."
                    )
                }

            try:

                result = self._extract_json(text)

            except json.JSONDecodeError as error:

                return {
                    "error": (
                        "Science Agent returned invalid JSON: "
                        f"{error}"
                    ),
                    "raw_response": text[:3000]
                }

            except ValueError as error:

                return {
                    "error": f"Science Agent response error: {error}",
                    "raw_response": text[:3000]
                }

            if not isinstance(result, dict):

                return {
                    "error": (
                        "Science Agent returned JSON, "
                        "but it was not a JSON object."
                    ),
                    "raw_response": text[:3000]
                }

            return result

        except Exception as error:

            return {
                "error": f"Science Agent error: {error}"
            }
````

**Important:** GitHub lo **only `agents/science_agent.py`** replace cheyyi. `app.py`, `orchestrator.py` ippudu touch cheyyaku.

After saving, Streamlit redeploy ayyaka same topic tho **Start Learning Session** test cheyyi. Ippudu error vaste, raw Gemini response kuda UI lo chupinchagalugutam, so next issue exact ga identify cheyyachu.

Also, this fixes the **JSON parsing robustness**; it does not yet address the separate `google.generativeai` deprecation warning.
