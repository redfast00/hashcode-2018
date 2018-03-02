import sys
from .solve import Ride, Vehicle, parse_input

def check_output(filename):
    rides_seen = set()
    with open(filename) as infile:
        for line in infile.readlines():
            num_rides, *ride_ids = (int(part) for part in line.split())
            assert num_rides == len(ride_ids), "Wrong format"
            assert num_rides == len(set(ride_ids)), "ride ridden twice on same vehicle"
            assert not rides_seen.intersection(ride_ids), "Ride ridden twice on different car"
            rides_seen.update(ride_ids)

if __name__ == '__main__':
    check_output(sys.argv[1])
