class Metrics:

    def __init__(self):

        self.completion_times=[]

        self.queue_delays=[]

        self.deadline_violations=0

        self.utilizations=[]

    def avg_completion(self):

        if not self.completion_times:

            return 0

        return sum(
            self.completion_times
        )/len(
            self.completion_times
        )
