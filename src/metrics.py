class Metrics:
    def __init__(self):
        self.task_completion_times = []
        self.queue_delays = []
        self.execution_times = []
        self.upload_times = []

    def add_task_result(self, result):
        self.task_completion_times.append(result["finish_time"])
        self.queue_delays.append(result["queue_wait"])
        self.execution_times.append(result["execution_time"])
        self.upload_times.append(result["upload_time"])

    def average(self, values):
        if not values:
            return 0.0
        return sum(values) / float(len(values))

    def avg_completion(self):
        return self.average(self.task_completion_times)

    def avg_queue_delay(self):
        return self.average(self.queue_delays)

    def avg_execution_time(self):
        return self.average(self.execution_times)

    def avg_upload_time(self):
        return self.average(self.upload_times)
