import json


class TeacherAgent:

    def __init__(self, model):
        self.model = model

    def create_learning_task(self, topic, science_result):

        prompt = f"""
You are a K-12 Science Teacher Agent.

The student wants to learn about:

{topic}

The Science Agent has already analyzed the topic:

{json.dumps(science_result, indent=2)}

Your job is to transform this scientific information into
a fun learning activity suitable for a 10-year-old child.

Create:

1. One simple conceptual science question
2. Exactly 2 answer options
3. One correct answer
4. A prediction prompt that encourages the child to think
   before seeing the experiment
5. A clear learning goal

IMPORTANT RULES:

- Use simple English.
- Keep the science accurate.
- Do not use advanced mathematical formulas.
- Make the question conceptual and interesting.
- Exactly one option must be correct.
- Do not explain the answer yet.

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

        response = self.model.generate_content(prompt)

        text = response.text.strip()

        # Remove Markdown code fences if the model adds them
        if text.startswith("```"):
            text = text.split("```", 2)[1]

            if text.startswith("json"):
                text = text[4:]

        text = text.strip()

        try:
            return json.loads(text)

        except Exception:

            return {
                "question": "Could not generate a learning question.",
                "option_a": "",
                "option_b": "",
                "correct_option": "",
                "prediction_prompt": "",
                "learning_goal": ""
            }
