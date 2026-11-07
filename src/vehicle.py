class Vehicle:

    def __init__(self, vid, x, y, speed):

        self.id = vid
        self.x = x
        self.y = y
        self.speed = speed

    def update(self, dt):

        self.x += self.speed * dt
