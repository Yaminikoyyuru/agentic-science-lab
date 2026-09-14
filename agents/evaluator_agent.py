import json


class EvaluatorAgent:

    def __init__(self, model):
        self.model = model

    def evaluate(
        self,
        topic,
        experiment,
        observation,
        prediction=""
    ):

        prompt = f"""
You are an Evaluation Agent inside an
AI-powered K-12 virtual science laboratory.

Your responsibility is to evaluate a student's
experimental observation and decide what the
learning system should do next.

Topic:
{topic}

Experiment:
{json.dumps(experiment, indent=2)}

Student prediction:
{prediction}

Student observation:
{observation}

Analyze the student's observation.

Determine:

1. Whether the observation is scientifically reasonable
2. What the student discovered
3. Whether the prediction was supported
4. Whether there is a possible misconception
5. What the student should explore next
6. A useful next question

Do not shame the student for an incorrect answer.
Use the result to guide the next learning step.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "observation_valid": true,
    "discovery": "...",
    "prediction_supported": true,
    "misconception": "...",
    "next_action": "...",
    "next_question": "..."
}}
"""

        response = self.model.generate_content(prompt)

        text = response.text.strip()

        try:
            return json.loads(text)

        except Exception:

            return {
                "observation_valid": False,
                "discovery": response.text,
                "prediction_supported": False,
                "misconception": "",
                "next_action": "",
                "next_question": ""
            }
