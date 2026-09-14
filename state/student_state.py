class StudentState:

    def __init__(self):

        self.topic = ""
        self.current_question = ""
        self.prediction = ""
        self.experiment = {}
        self.observations = []
        self.evaluations = []
        self.learning_history = []
        self.experiment_number = 0

    def add_observation(self, observation):

        self.observations.append(observation)

    def add_evaluation(self, evaluation):

        self.evaluations.append(evaluation)

    def add_history(self, data):

        self.learning_history.append(data)

    def set_prediction(self, prediction):

        self.prediction = prediction

    def next_experiment(self):

        self.experiment_number += 1
