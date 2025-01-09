import simpy
import random
import numpy as np

# Simulation parameters
SIM_TIME = 50000  # Total simulation time in minutes

# Arrival and service rates for each station
ARRIVAL_RATE_CHECKIN = 1/2  # Customers arrive every 2 minutes on average
SERVICE_RATE_CHECKIN = 1/3  # Check-in takes on average 3 minutes (M/M/1)

SERVICE_RATE_SERVICE_DESK = 1/4  # Service desk takes on average 4 minutes (M/M/1)

SERVICE_RATE_SPECIALIZED = 1/5  # Specialized service takes on average 5 minutes (M/M/3)
SPECIALIZED_SERVERS = 3  # M/M/3 configuration

class QueueSystem:
    def __init__(self, env, servers, service_rate, label):
        self.env = env
        self.server = simpy.Resource(env, capacity=servers)
        self.service_rate = service_rate
        self.label = label
        self.wait_times = []
        self.queue_lengths = []
        self.server_utilization_time = 0
        self.customer_count = 0

    def process_customer(self, arrival_time):
        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            # Service the customer
            service_time = random.expovariate(self.service_rate)
            yield self.env.timeout(service_time)
            self.server_utilization_time += service_time

        self.customer_count += 1
        self.queue_lengths.append(len(self.server.queue))

# Simulate the check-in counter
class CheckInCounter(QueueSystem):
    def __init__(self, env):
        super().__init__(env, 1, SERVICE_RATE_CHECKIN, "Check-in Counter")

# Simulate the service desk
class ServiceDesk(QueueSystem):
    def __init__(self, env):
        super().__init__(env, 1, SERVICE_RATE_SERVICE_DESK, "Service Desk")

# Simulate the specialized service counters (M/M/3)
class SpecializedServiceCounter(QueueSystem):
    def __init__(self, env):
        super().__init__(env, SPECIALIZED_SERVERS, SERVICE_RATE_SPECIALIZED, "Specialized Counter")

# Simulation function
def run_simulation():
    env = simpy.Environment()

    check_in = CheckInCounter(env)
    service_desk = ServiceDesk(env)
    specialized_counter = SpecializedServiceCounter(env)

    def customer_arrival(env):
        while True:
            # Customer arrives at the check-in counter
            yield env.timeout(random.expovariate(ARRIVAL_RATE_CHECKIN))
            env.process(check_in.process_customer(env.now))
            
            # After check-in, customer goes to service desk
            yield env.process(service_desk.process_customer(env.now))
            
            # After the service desk, customer goes to one of the specialized service counters
            yield env.process(specialized_counter.process_customer(env.now))

    # Start the customer arrival process
    env.process(customer_arrival(env))
    env.run(until=SIM_TIME)

    # Performance metrics calculations
    def print_metrics(queue_system):
        avg_waiting_time = np.mean(queue_system.wait_times)
        avg_queue_length = np.mean(queue_system.queue_lengths)
        utilization = queue_system.server_utilization_time / (SIM_TIME * queue_system.server.capacity)

        print(f"Results for {queue_system.label}:")
        print(f"Average Waiting Time (Wq): {avg_waiting_time:.2f} minutes")
        print(f"Average Queue Length: {avg_queue_length:.2f} customers")
        print(f"Server Utilization (ρ): {utilization:.2f}\n")

    # Print metrics for each station
    print_metrics(check_in)
    print_metrics(service_desk)
    print_metrics(specialized_counter)

# Run the simulation
run_simulation()