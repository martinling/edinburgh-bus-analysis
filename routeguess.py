import sys,math
import numpy
from common import get
from matplotlib import pyplot

if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "<service number>"
    sys.exit(1)

service = sys.argv[1]

class Direction(object):
    compassAngles = dict(
        zip(['N','NE','E','SE','S','SW','W','NW'],
        range(0, 360, 45)))

    def __init__(self, value):
        if type(value) is numpy.ndarray:
            # Angle from vector
            self.angle = math.atan2(*value)
        elif type(value) is str:
            # Angle from compass point
            self.angle = math.radians(self.compassAngles.get(value, numpy.nan))
        else:
            self.angle = value

    def unitVector(self):
        return numpy.array([
            math.sin(self.angle),
            math.cos(self.angle)])

    def angleWith(self, other):
        delta = math.fmod(other.angle - self.angle, 2*math.pi)
        if abs(delta) > math.pi:
            delta -= math.copysign(2*math.pi, delta)
        return delta

class Stop(object):

    stops = dict()

    def __init__(self, naptan):
        self.naptan = naptan
        data = get('stop', naptan).nodes
        # Latitude and longitude are swapped in the API
        self.location = numpy.array([
            float(str(data['lat'])),
            float(str(data['long']))])
        self.direction = Direction(str(data['OnStreet_CompassPoint']))
        Stop.stops[naptan] = self

    def others(self):
        return filter(lambda s: s is not self, Stop.stops.values())

    def vectorTo(self, other):
        return other.location - self.location

    def directionTo(self, other):
        return Direction(self.vectorTo(other))

    def distanceTo(self, other):
        return math.sqrt(sum(self.vectorTo(other)**2))

    def possibleNextStop(self, other):
        angleWithNextStop = self.direction.angleWith(self.directionTo(other))
        angleWithNextDir = self.direction.angleWith(other.direction)
        angleOfNextTurn = self.directionTo(other).angleWith(other.direction)
        for angle, limit in [
            (angleWithNextStop, 90),
            (angleWithNextDir, 90),
            (angleOfNextTurn, 135)]:
            if not numpy.isnan(angle) and abs(math.degrees(angle)) > limit:
                return False
        return True

    def possibleNextStops(self):
        return filter(self.possibleNextStop, self.others())

    def guessNextStop(self):
        candidates = self.possibleNextStops()
        if len(candidates) > 0:
            return min(candidates, key=self.distanceTo)
        else:
            return None

stops = [Stop(str(s.naptan)) for s in get('servicestops', service).nodes['serviceStop']]

for stop in stops:
    x, y = stop.location
    ax, ay = stop.location + stop.direction.unitVector() * 0.001
    pyplot.plot(x, y, color='blue', marker='.')
    pyplot.plot([x, ax], [y, ay], color='red', linestyle='-')
    pyplot.plot([x, ax], [y, ay], color='red', linestyle='-')
    pyplot.text(x, y, stop.naptan)
    next = stop.guessNextStop()
    if next is not None:
        nx, ny = next.location
        pyplot.plot([x, nx], [y, ny], color='green', linestyle='-')

pyplot.show()
