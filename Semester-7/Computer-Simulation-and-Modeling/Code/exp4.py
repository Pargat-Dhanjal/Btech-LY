import random
from tabulate import tabulate

class Truck:
    def __init__(self, truck_id):
        self.truck_id = truck_id
        self.status = "Init"
        self.time_left = 0

    def get_load_time(self):
        rand = random.random()
        if 0 <= rand <= 0.3:
            load_time = 5
        elif 0.3 < rand <= 0.8:
            load_time = 10
        else:
            load_time = 15
        return load_time

    def get_weigh_time(self):
        rand = random.random()
        if 0 <= rand <= 0.7:
            weigh_time = 12
        else:
            weigh_time = 16
        return weigh_time

    def get_travel_time(self):
        rand = random.random()
        if 0 <= rand <= 0.4:
            travel_time = 40
        elif 0.4 < rand <= 0.7:
            travel_time = 60
        elif 0.7 < rand <= 0.9:
            travel_time = 80
        else:
            travel_time = 100
        return travel_time

def truck_parser(trucks):
    return [f"DT{truck.truck_id}" for truck in trucks]

def future_event_list(traveling_trucks):
    return [f"(EL, {truck.time_left}, DT{truck.truck_id})" for truck in traveling_trucks]

test = True

def print_stuff_as_table(clock, loader_queue, in_loader, weighing_queue, in_weigh, traveling_trucks, loader_busy_time, scale_busy_time):
    # Create a table with the desired format
    table = [
        [
            clock,  # Clock
            len(loader_queue),  # LQ(t)
            len(in_loader),  # L(t)
            len(weighing_queue),  # WQ(t)
            len(in_weigh),  # W(t)
            ', '.join(truck_parser(loader_queue)),  # Loader Queue
            ', '.join(truck_parser(weighing_queue)),  # Weigh Queue
            ', '.join(future_event_list(traveling_trucks)),  # Future Event List
            loader_busy_time,  # BL (Loader Busy Time)
            scale_busy_time  # BS (Scale Busy Time)
        ]
    ]


    print(tabulate(table, headers=["Clock t", "LQ(t)", "L(t)", "WQ(t)", "W(t)", "Loader Queue", "Weigh Queue", "Future Event List", "BL", "BS"], tablefmt="grid"))

def simulate_trucks():
    trucks = [Truck(i) for i in range(1, 7)]
    loader_queue = trucks[:]
    in_loader = []  # Only 2 trucks at a time
    weighing_queue = []
    in_weigh = []  # Only 1 truck at a time
    traveling_trucks = []

    Time = 0
    loader_busy_time = 0
    scale_busy_time = 0

    while Time < 100:
        # print(f"Time: {Time}")

        # Start Loading
        for truck in loader_queue:
            if len(in_loader) < 2:
                if truck.status == "Init" or truck.status == "Returning":
                    in_loader.append(truck)
                    loader_queue.remove(truck)
                    truck.status = "Loading"
                    truck.time_left = truck.get_load_time()
                    # print(f"Truck {truck.truck_id} starts loading for {truck.time_left} time units.")

        # Process loading
        for truck in in_loader[:]:
            if truck.status == "Loading":
                truck.time_left -= 1
                if truck.time_left == 0:
                    truck.status = "WaitingForWeighing"
                    in_loader.remove(truck)
                    weighing_queue.append(truck)
                    # print(f"Truck {truck.truck_id} finished loading and moves to weighing queue.")
        
        # Increment loader busy time
        if len(in_loader) > 0:
            loader_busy_time += 1

        # Start Weighing
        for truck in weighing_queue[:]:
            if len(in_weigh) == 0:
                if truck.status == "WaitingForWeighing":
                    in_weigh.append(truck)
                    weighing_queue.remove(truck)
                    truck.status = "Weighing"
                    truck.time_left = truck.get_weigh_time()
                    # print(f"Truck {truck.truck_id} starts weighing for {truck.time_left} time units.")

        # Process weighing
        for truck in in_weigh[:]:
            if truck.status == "Weighing":
                truck.time_left -= 1
                if truck.time_left == 0:
                    truck.status = "Traveling"
                    in_weigh.remove(truck)
                    traveling_trucks.append(truck)
                    truck.time_left = truck.get_travel_time()
                    # print(f"Truck {truck.truck_id} finished weighing and starts traveling for {truck.time_left} time units.")
        
        # Increment scale busy time
        if len(in_weigh) > 0:
            scale_busy_time += 1

        # Process traveling trucks
        for truck in traveling_trucks[:]:
            if truck.status == "Traveling":
                truck.time_left -= 1
                if truck.time_left == 0:
                    truck.status = "Returning"
                    traveling_trucks.remove(truck)
                    loader_queue.append(truck)
                    # print(f"Truck {truck.truck_id} finished traveling and returns to loader queue.")
        
        # Print the table at each clock cycle
        print_stuff_as_table(Time, loader_queue, in_loader, weighing_queue, in_weigh, traveling_trucks, loader_busy_time, scale_busy_time)
        
        Time += 1

simulate_trucks()
