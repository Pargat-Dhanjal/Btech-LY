import simpy
import random
import numpy as np

# Simulation parameters
SIM_TIME = 100000  # Total simulation time in minutes
PEAK_HOURS = [50000, 60000]  # Define peak hour time range (minutes)
ARRIVAL_RATE_PEAK = 0.8  # Average arrival rate during peak hours (vehicles per minute)
ARRIVAL_RATE_OFF_PEAK = 0.3  # Average arrival rate during off-peak hours (vehicles per minute)
SERVICE_MEAN_PEAK = 0.7  # Average service time during peak hours (minutes)
SERVICE_STD_PEAK = 0.2  # Standard deviation for service time during peak hours
SERVICE_MEAN_OFF_PEAK = 0.5  # Average service time during off-peak hours (minutes)
SERVICE_STD_OFF_PEAK = 0.1  # Standard deviation for service time during off-peak hours

class MG1Queue:
    def __init__(self, env):
        self.env = env
        self.server = simpy.Resource(env, capacity=1)
        self.wait_times = []
        self.queue_lengths = []
        self.server_utilization_time = 0
        self.customer_count = 0

    def process_vehicle(self, arrival_time, service_time):
        with self.server.request() as request:
            yield request
            # Calculate waiting time in the queue
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            
            # Service the vehicle (Normal distribution for service times)
            yield self.env.timeout(service_time)
            self.server_utilization_time += service_time

        self.customer_count += 1
        self.queue_lengths.append(len(self.server.queue))

    def vehicle_arrivals(self):
        while True:
            current_time = self.env.now
            if PEAK_HOURS[0] <= current_time <= PEAK_HOURS[1]:
                inter_arrival_time = random.expovariate(ARRIVAL_RATE_PEAK)
                service_time = max(0, random.gauss(SERVICE_MEAN_PEAK, SERVICE_STD_PEAK))
            else:
                inter_arrival_time = random.expovariate(ARRIVAL_RATE_OFF_PEAK)
                service_time = max(0, random.gauss(SERVICE_MEAN_OFF_PEAK, SERVICE_STD_OFF_PEAK))
            
            yield self.env.timeout(inter_arrival_time)
            self.env.process(self.process_vehicle(self.env.now, service_time))

# Simulation function
def run_simulation():
    env = simpy.Environment()
    mg1_queue = MG1Queue(env)
    env.process(mg1_queue.vehicle_arrivals())
    env.run(until=SIM_TIME)

    # Performance metrics calculations
    avg_waiting_time = np.mean(mg1_queue.wait_times)
    avg_queue_length = np.mean(mg1_queue.queue_lengths)
    utilization = mg1_queue.server_utilization_time / SIM_TIME

    print(f"Results for Peak and Off-Peak Hours:")
    print(f"Average Waiting Time (Wq): {avg_waiting_time:.2f} minutes")
    print(f"Average Queue Length: {avg_queue_length:.2f} vehicles")
    print(f"Server Utilization (ρ): {utilization:.2f}")

# Run the simulation
run_simulation()