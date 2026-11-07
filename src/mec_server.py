class MECServer:

    def __init__(self, sid, x, y, cpu, radius):

        self.id = sid
        self.x = x
        self.y = y

        self.cpu = cpu

        self.radius = radius

        self.queue_cycles = 0

    def waiting_time(self):

        return self.queue_cycles / self.cpu

    def add_task(self, cycles):

        self.queue_cycles += cycles

    def process(self, dt=1):

        self.queue_cycles = max(
            0,
            self.queue_cycles - self.cpu * dt
        )
