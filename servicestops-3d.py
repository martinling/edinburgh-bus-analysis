import sys, time
from common import get
from numpy import array, mean, ptp
from enthought.mayavi.mlab import points3d, show

if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "<service number>"
    sys.exit(1)

service = sys.argv[1]

stops = get('servicestops', service).nodes['serviceStop']

points = []

for stop in stops:
    lat = float(str(stop.lat))
    long = float(str(stop.long))
    departures = get('stopdepartures', str(stop.naptan))
    if departures.nodes.has_key('stopDeparture'):
        for departure in departures.nodes['stopDeparture']:
            if str(departure.service) == service:
                t_string = str(departure.departure_time)
                t_struct = time.strptime(t_string, "%Y-%m-%dT%H:%M")
                t_float = time.mktime(t_struct)
                if t_struct.tm_hour < 3:
                    t_float += 24*60*60
                points.append([lat, long, t_float])

def normalise(data):
    return (data - mean(data)) / (ptp(data)/2)

lat, long, t = map(normalise, array(points).T)

points3d(lat, long, t, scale_factor=0.05)

show()
