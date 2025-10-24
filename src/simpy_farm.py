import simpy
import random
import statistics 

class EggFarmSimulation:
    def __init__(self, belt_capacity, hen_count=10000, simulation_time=720):
        
        self.belt_capacity = belt_capacity
        self.hen_count = hen_count
        self.simulation_time = simulation_time  # in minutes

        # environment
        self.env = simpy.Environment()
        self.collection_belt = simpy.Resource(self.env, capacity=belt_capacity)

        # variables
        self.eggs_laid = 0
        self.eggs_collected = 0
        self.eggs_broken = 0
        self.queue_history = []
        self.utilization_history = []
        self.queue_time_series = []
        self.utilization_time_series = []

    # laying probability
    def laying_probability(self, current_time):
        hour = current_time / 60  
        if 6 <= hour < 10:  # morning
            return 0.03
        elif 10 <= hour < 14:  # mid-day
            return 0.02
        else:  # other times
            return 0.01

    # breakage probability 
    def breakage_probability(self, queue_length):
        base_rate = 0.01
        congestion_factor = queue_length / 1000.0
        if congestion_factor > 0.5:
            congestion_factor = 0.5
        return base_rate + congestion_factor

    # Generate eggs each minute
    def egg_generator(self):
        while True:
            prob = self.laying_probability(self.env.now)

            # Count new eggs this minute
            new_eggs = 0
            for _ in range(self.hen_count):
                if random.random() < prob:
                    new_eggs += 1

            # Update total laid eggs 
            self.eggs_laid += new_eggs

            # Start a collect_egg process
            for _ in range(new_eggs):
                self.env.process(self.collect_egg())

            # Wait 1 minute
            yield self.env.timeout(1)

    # egg collect process 
    def collect_egg(self):
        arrival_time = self.env.now

        # Observe queue length at arrival
        queue_length = len(self.collection_belt.queue)
        self.queue_history.append((arrival_time, queue_length))

        # egg breaks while waiting
        if queue_length > 0:
            prob_break = self.breakage_probability(queue_length)
            if random.random() < prob_break:
                self.eggs_broken += 1
                return  

        # Request one unit of the belt 
        with self.collection_belt.request() as req:
            yield req  

            users = len(self.collection_belt.users)
            capacity = self.collection_belt.capacity
            if capacity > 0:
                utilization = users / capacity
            else:
                utilization = 0
            self.utilization_history.append((self.env.now, utilization))

            # short transport time
            yield self.env.timeout(0.1)

            # Egg successfully collected
            self.eggs_collected += 1

    # Record queue and utilization
    def metrics_collector(self):
        while True:
            current_queue = len(self.collection_belt.queue)
            users = len(self.collection_belt.users)
            capacity = self.collection_belt.capacity
            if capacity > 0:
                current_util = users / capacity
            else:
                current_util = 0

            self.queue_history.append((self.env.now, current_queue))
            self.utilization_history.append((self.env.now, current_util))

            yield self.env.timeout(1)

    # Start generator and metrics processes and run the simulation
    def run(self):
        self.env.process(self.egg_generator())
        self.env.process(self.metrics_collector())

        self.env.run(until=self.simulation_time)

        self._process_history_data()

    # Convert recorded lists into per-minute averages
    def _process_history_data(self):
        queue_by_minute = {}
        for t, q in self.queue_history:
            minute = int(t)
            if minute not in queue_by_minute:
                queue_by_minute[minute] = []
            queue_by_minute[minute].append(q)

        util_by_minute = {}
        for t, u in self.utilization_history:
            minute = int(t)
            if minute not in util_by_minute:
                util_by_minute[minute] = []
            util_by_minute[minute].append(u)

        self.queue_time_series = []
        self.utilization_time_series = []
        for minute in range(self.simulation_time):
            if minute in queue_by_minute and len(queue_by_minute[minute]) > 0:
                avg_q = sum(queue_by_minute[minute]) / len(queue_by_minute[minute])
            else:
                avg_q = 0
            self.queue_time_series.append(avg_q)

            if minute in util_by_minute and len(util_by_minute[minute]) > 0:
                avg_u = sum(util_by_minute[minute]) / len(util_by_minute[minute])
            else:
                avg_u = 0
            self.utilization_time_series.append(avg_u)


    # Calculate and return performance metrics
    def get_metrics(self):
        # Breakage rate 
        if self.eggs_laid > 0:
            breakage_rate = self.eggs_broken / self.eggs_laid
        else:
            breakage_rate = 0

        # Average utilization and queue 
        if len(self.utilization_time_series) > 0:
            avg_util = statistics.mean(self.utilization_time_series)
        else:
            avg_util = 0

        if len(self.queue_time_series) > 0:
            avg_queue = statistics.mean(self.queue_time_series)
            max_queue = max(self.queue_time_series)
        else:
            avg_queue = 0
            max_queue = 0

        return {
            'eggs_laid': self.eggs_laid,
            'eggs_collected': self.eggs_collected,
            'eggs_broken': self.eggs_broken,
            'breakage_rate': breakage_rate,
            'utilization': avg_util,
            'max_queue': max_queue,
            'avg_queue': avg_queue,
            'belt_capacity': self.belt_capacity
        }
