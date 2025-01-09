import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
SIM_TIME = 100000  # Total simulation time in minutes
SERVICE_RATE = 1    # Service rate (μ) is fixed at 1 customer per minute

# Traffic intensity levels
TRAFFIC_INTENSITIES = {
    'Low': 0.5,
    'Moderate': 0.75,
    'High': 0.9
}

class MM1Queue:
    def __init__(self, env, service_rate, traffic_intensity):
        self.env = env
        self.server = simpy.Resource(env, capacity=1)
        self.service_rate = service_rate
        self.arrival_rate = traffic_intensity * service_rate
        self.wait_times = []
        self.queue_lengths = []
        self.customers_in_system = []
        self.server_utilization_time = 0
        self.customer_count = 0

    def process_customer(self, customer_id):
        arrival_time = self.env.now
        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            # Service the customer
            service_time = random.expovariate(self.service_rate)
            yield self.env.timeout(service_time)
            self.server_utilization_time += service_time
        self.customers_in_system.append(self.server.count)
        self.customer_count += 1

    def customer_arrivals(self):
        while True:
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            self.env.process(self.process_customer(self.customer_count))
            self.queue_lengths.append(len(self.server.queue))

# Simulation function
def run_simulation(traffic_intensity_label, traffic_intensity):
    env = simpy.Environment()
    mm1_queue = MM1Queue(env, SERVICE_RATE, traffic_intensity)
    env.process(mm1_queue.customer_arrivals())
    env.run(until=SIM_TIME)

    # Performance metrics calculations
    avg_waiting_time = np.mean(mm1_queue.wait_times)
    avg_customers_in_system = np.mean(mm1_queue.customers_in_system)
    avg_queue_length = np.mean(mm1_queue.queue_lengths)
    utilization = mm1_queue.server_utilization_time / SIM_TIME

    return avg_waiting_time, avg_customers_in_system, utilization, mm1_queue.wait_times, mm1_queue.queue_lengths

# Arrays to store metrics for plotting
traffic_intensity_vals = []
waiting_times = []
customers_in_system_vals = []
utilizations = []
queue_lengths = []
wait_time_distributions = []
queue_length_distributions = []

# Run simulations for different traffic intensities and store metrics
for label, intensity in TRAFFIC_INTENSITIES.items():
    avg_waiting_time, avg_customers_in_system, utilization, wait_times, queue_lengths_data = run_simulation(label, intensity)
    traffic_intensity_vals.append(intensity)
    waiting_times.append(avg_waiting_time)
    customers_in_system_vals.append(avg_customers_in_system)
    utilizations.append(utilization)
    wait_time_distributions.append(wait_times)
    queue_length_distributions.append(queue_lengths_data)

# Create subplots for all the performance metrics
fig, axs = plt.subplots(3, 2, figsize=(12, 12))  # Create a 3x2 grid of subplots

# Plot Average Waiting Time (Wq) vs Traffic Intensity (ρ)
axs[0, 0].plot(traffic_intensity_vals, waiting_times, marker='o', label="Avg Waiting Time (Wq)")
axs[0, 0].set_xlabel('Traffic Intensity (ρ)')
axs[0, 0].set_ylabel('Avg Waiting Time (minutes)')
axs[0, 0].set_title('Avg Waiting Time (Wq) vs Traffic Intensity (ρ)')

# Plot Average Number of Customers in System (L) vs Traffic Intensity (ρ)
axs[0, 1].plot(traffic_intensity_vals, customers_in_system_vals, marker='o', label="Avg Customers in System (L)")
axs[0, 1].set_xlabel('Traffic Intensity (ρ)')
axs[0, 1].set_ylabel('Avg Customers in System')
axs[0, 1].set_title('Avg Customers in System (L) vs Traffic Intensity (ρ)')

# Plot Server Utilization (ρ) vs Traffic Intensity (ρ)
axs[1, 0].plot(traffic_intensity_vals, utilizations, marker='o', label="Server Utilization")
axs[1, 0].set_xlabel('Traffic Intensity (ρ)')
axs[1, 0].set_ylabel('Server Utilization')
axs[1, 0].set_title('Server Utilization vs Traffic Intensity (ρ)')

# Plot Queue Length Distribution for different traffic intensities
for i, label in enumerate(TRAFFIC_INTENSITIES.keys()):
    axs[1, 1].hist(queue_length_distributions[i], bins=20, alpha=0.7, label=f"Queue Length ({label})")
axs[1, 1].set_xlabel('Queue Length')
axs[1, 1].set_ylabel('Frequency')
axs[1, 1].set_title('Queue Length Distribution')
axs[1, 1].legend()

# Plot Waiting Time Distribution for different traffic intensities
for i, label in enumerate(TRAFFIC_INTENSITIES.keys()):
    axs[2, 0].hist(wait_time_distributions[i], bins=20, alpha=0.7, label=f"Waiting Time ({label})")
axs[2, 0].set_xlabel('Waiting Time (minutes)')
axs[2, 0].set_ylabel('Frequency')
axs[2, 0].set_title('Waiting Time Distribution')
axs[2, 0].legend()

# Remove the last empty plot (bottom right)
fig.delaxes(axs[2, 1])

# Adjust layout for better readability
plt.tight_layout()

# Show the plot
plt.show()
