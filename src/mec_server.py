class MECServer:
    """A single-processor MEC server with a time-based FCFS queue."""

    def __init__(self, sid, x, y, cpu, radius):
        self.id = sid
        self.x = float(x)
        self.y = float(y)
        self.cpu = float(cpu)          # Maximum CPU capacity in cycles/second
        self.radius = float(radius)
        self.available_at = 0.0        # Time when the server becomes free
        self.completed_tasks = 0
        self.busy_time = 0.0

    def waiting_time(self, task_ready_time=0.0):
        """How long a task must wait for this server after it is ready."""
        return max(0.0, self.available_at - task_ready_time)

    def reserve(self, start_time, finish_time):
        """Reserve this server for a task selected by the scheduler."""
        if finish_time < start_time:
            raise ValueError("Task finish time cannot be before start time")
        self.available_at = finish_time
        self.busy_time += finish_time - start_time
        self.completed_tasks += 1

    def utilization(self, simulation_end_time):
        if simulation_end_time <= 0:
            return 0.0
        return min(100.0, 100.0 * self.busy_time / simulation_end_time)
