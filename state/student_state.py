class StudentState:

    def __init__(self):

        # Current learning topic
        self.topic = ""

        # Current question
        self.current_question = ""

        # Student's prediction
        self.prediction = ""

        # Current experiment
        self.experiment = {}

        # All observations from the student
        self.observations = []

        # All evaluator results
        self.evaluations = []

        # Complete learning history
        self.learning_history = []

        # Experiment counter
        self.experiment_number = 0

    def add_observation(self, observation):

        self.observations.append(observation)

    def add_evaluation(self, evaluation):

        self.evaluations.append(evaluation)

    def add_history(self, data):

        self.learning_history.append(data)

    def next_experiment(self):

        self.experiment_number += 1
