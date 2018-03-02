import sys
import collections
import queue
import random
import kdtree

class VehiclePriority(queue.PriorityQueue):
    def add_vehicle(self, vehicle):
        self.put((vehicle.time + random.uniform(0, 0.50), vehicle))
    def get_vehicle(self):
        _, vehicle = self.get()
        return vehicle

def distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

class Vehicle(object):
    def __init__(self, vehicle_id):
        self.column = 0
        self.row = 0
        self.rides = []
        self.vehicle_id = vehicle_id
        self.time = 0

    def time_to_route_begin(self, ride):
        return self.time + distance(self.row, self.column, ride.row_start, ride.column_start)

    def ride(self, ride):
        self.rides.append(ride)
        self.time = self.time_to_route_begin(ride) + ride.ride_time()
        ride.has_been_done = True
        self.row = ride.row_end
        self.column = ride.column_end

    def __repr__(self):
        return f'Vehicle #{self.vehicle_id}'

    def __str__(self):
        return f'{len(self.rides)} ' + ' '.join((str(ride.ride_id) for ride in self.rides)) if self.rides else '0'

    def find_closest_ride(self, num_steps):
        global rides
        current = (self.row, self.column)
        node = rides.search_nn(current)
        limit = 20
        while node is not None and limit > 0:
            candidate_ride = node[0].data
            limit -= 1
            if candidate_ride.can_be_claimed_by(self):
                rides = rides.remove(candidate_ride)
                return candidate_ride
            elif self.time_to_route_begin(candidate_ride) > num_steps:
                print("vehicle end found")
                return None
            rides = rides.remove(candidate_ride)
            node = rides.search_nn(current)
        if limit == 0:
            print("searchlimit exceeded")

    def calculate_best_route(self, num_steps):
        ride = self.find_closest_ride(num_steps)
        if ride is not None:
            self.ride(ride)
            print(f"vehicle {self.__repr__()} took {ride}")
        return ride is not None

class Ride(object):
    def __init__(self, line, ride_id):
        self.row_start, self.column_start, self.row_end, self.column_end, self.earliest_start, self.latest_finish = [int(part) for part in line.split()]
        self.ride_id = ride_id
        self.has_been_done = False

    def ride_time(self):
        return distance(self.row_start, self.column_start, self.row_end, self.column_end)

    def can_be_claimed_by(self, vehicle):
        return (not self.has_been_done) and vehicle.time_to_route_begin(self) + self.ride_time() <= self.latest_finish

    def __repr__(self):
        return f'Ride #({self.ride_id}) ({self.row_start}, {self.column_start}) to ({self.row_end}, {self.column_end})'

    # Overrided methods for k-dtree
    def __getitem__(self, i):
        if i == 0:
            return self.row_start
        elif i == 1:
            return self.column_start
        else:
            raise NotImplementedError

    def __len__(self):
        return 2

def parse_input(filename):
    global rides

    with open(infilename) as infile:
        line = infile.readline().strip().split()
        parts = [int(part) for part in line]
        rows, columns, vehicles_amount, rides_amount, per_ride_bonus, num_steps = parts
        ride_list = []
        for ride_id, line in enumerate(infile.readlines()):
            new = Ride(line, ride_id)
            ride_list.append(new)
        rides = kdtree.create(ride_list, dimensions=2)
    return vehicles_amount, per_ride_bonus, num_steps

def solve(vehicles_amount, per_ride_bonus, num_steps):
    priority_queue = VehiclePriority()

    vehicles = [Vehicle(vehicle_id) for vehicle_id in range(vehicles_amount)]
    for vehicle in vehicles:
        priority_queue.add_vehicle(vehicle)

    # Go over all rides
    while not priority_queue.empty():
        vehicle = priority_queue.get_vehicle()
        did_find_ride = vehicle.calculate_best_route(num_steps)
        if did_find_ride:
            priority_queue.add_vehicle(vehicle)
    return vehicles

def output(vehicles):
    with open(outfilename, 'w') as outfile:
        for vehicle in sorted(vehicles, key=lambda v: v.vehicle_id):
            print(str(vehicle), file=outfile)

if __name__ == '__main__':
    # global variable
    rides = None

    infilename = sys.argv[1]
    outfilename = sys.argv[2] if len(sys.argv) == 3 else infilename.split('.')[0] + '.out'

    parsed = parse_input(infilename)
    vehicles_amount, per_ride_bonus, num_steps = parsed
    solution = solve(*parsed)
    output(solution)
