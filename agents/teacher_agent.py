import json


class TeacherAgent:

    def __init__(self, model):
        self.model = model

    def create_learning_task(self, topic, science_result):

        prompt = f"""
You are a K-12 Science Teacher Agent inside an
AI-powered interactive science laboratory.

Student topic:
{topic}

Scientific analysis:
{json.dumps(science_result, indent=2)}

Your task is to convert the scientific analysis into
an engaging learning task suitable for a 10-year-old child.

The learning task should encourage the student to:

1. Think about the concept
2. Choose an answer
3. Make a prediction
4. Prepare to explore the concept through an experiment

Create exactly one conceptual question with exactly
two options.

One option must be correct and one must be incorrect.

Do not make the question unnecessarily difficult.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "question": "...",
    "option_a": "...",
    "option_b": "...",
    "correct_option": "A",
    "prediction_prompt": "...",
    "learning_goal": "..."
}}
"""

        try:

            response = self.model.generate_content(prompt)

            text = response.text.strip()

            return json.loads(text)

        except Exception as error:

            return {
                "error": str(error),
                "question": "",
                "option_a": "",
                "option_b": "",
                "correct_option": "",
                "prediction_prompt": "",
                "learning_goal": ""
            }
