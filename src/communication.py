import math
from config import BANDWIDTH
from config import NOISE_POWER
from config import TX_POWER

def distance(vehicle, server):

    return math.sqrt(
        (vehicle.x - server.x)**2 +
        (vehicle.y - server.y)**2
    )

def snr(d):

    h = 1/(1+d*d)

    return (TX_POWER*h)/NOISE_POWER

def transmission_rate(d):

    return BANDWIDTH * math.log2(
        1 + snr(d)
    )
