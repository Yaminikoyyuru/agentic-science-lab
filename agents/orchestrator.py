from agents.science_agent import ScienceAgent
from agents.teacher_agent import TeacherAgent
from agents.experiment_agent import ExperimentAgent
from agents.evaluator_agent import EvaluatorAgent


class Orchestrator:

    def __init__(self, model):

        self.science_agent = ScienceAgent(model)
        self.teacher_agent = TeacherAgent(model)
        self.experiment_agent = ExperimentAgent(model)
        self.evaluator_agent = EvaluatorAgent(model)

    def start_learning_session(self, topic):

        # Step 1: Science reasoning
        science_result = self.science_agent.analyze_topic(
            topic
        )

        if "error" in science_result:
            return {
                "error": science_result["error"]
            }

        # Step 2: Teacher creates learning task
        teacher_result = self.teacher_agent.create_learning_task(
            topic,
            science_result
        )

        if "error" in teacher_result:
            return {
                "error": teacher_result["error"]
            }

        # Step 3: Experiment design
        experiment_result = self.experiment_agent.create_experiment(
            topic,
            science_result
        )

        if "error" in experiment_result:
            return {
                "error": experiment_result["error"]
            }

        return {
            "topic": topic,
            "science": science_result,
            "teacher": teacher_result,
            "experiment": experiment_result
        }

    def calculate_for_experiment(self, expression):

        return self.science_agent.calculate_value(
            expression
        )

    def evaluate_student_action(
        self,
        topic,
        experiment,
        observation,
        prediction=""
    ):

        evaluation = self.evaluator_agent.evaluate(
            topic,
            experiment,
            observation,
            prediction
        )

        return evaluation
