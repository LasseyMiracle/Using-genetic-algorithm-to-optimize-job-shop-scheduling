import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

mutation_rate = 0.01
#selection_rate = 0.2

Population_Size = int(input("Enter the population size: "))
Number_of_Generations = int(input("Enter the number of generations: "))
num_machines = int(input("Enter the number of machines: "))
list_of_jobs = []


def initialize_jobs_from_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # ... rest of your code ...

    for line in lines:
        job_id = int(line.split(":")[0].split("_")[1])
        data = line.split(":")[1].strip().split("->")
        num_operations = 0
        operations = []
        for op_data in data:
            machine, processing_time = int(op_data.split("M")[1].split("[")[0]), int(
                op_data.split("[")[1].split("]")[0])
            operations.append({'machine': machine, 'processing_time': processing_time})
            num_operations += 1
        list_of_jobs.append({'job_id': job_id, 'num_operations': num_operations, 'operations': operations})
    # print(list_of_jobs)


def initialize_jobs():
    num_jobs = int(input("Enter the number of jobs: "))
    for i in range(num_jobs):
        job_id = i + 1
        num_operations = int(input(f"Enter the number of operations for Job {i + 1}: "))
        operations = []
        for j in range(num_operations):
            while True:
                machine = int(input(f"Enter machine for operation {j + 1} of Job {i + 1}: "))
                if machine > num_machines:
                    print(f"Invalid machine number. Please enter a valid machine number (1 to {num_machines}).")
                else:
                    break
            processing_time = int(input(f"Enter processing time for operation {j + 1} of Job {i + 1}: "))
            operations.append({'machine': machine, 'processing_time': processing_time})

        list_of_jobs.append({'job_id': job_id, 'num_operations': num_operations, 'operations': operations})


def initialize_chromosome():
    chromosome = []
    for job in list_of_jobs:
        job_id = job['job_id']
        for operation in range(job['num_operations']):
            chromosome.append(job_id)
    return chromosome


def initialize_population():
    initial_chromosome = initialize_chromosome()
    population = []
    for i in range(Population_Size):
        chromosome_copy = initial_chromosome[:]
        random.shuffle(chromosome_copy)
        population.append(chromosome_copy)
    return population


def fitness_func(chromosome):
    machine_avail_time = {machine: 0 for machine in range(1, num_machines + 1)}
    job_completion_time = {job['job_id']: 0 for job in list_of_jobs}
    job_operation_index = {job['job_id']: 0 for job in list_of_jobs}
    schedule = []

    for job_id in chromosome:
        job = list_of_jobs[job_id - 1]
        operations = job['operations']
        op_index = job_operation_index[job_id]

        # Ensure the operation index is within the bounds
        if op_index >= len(operations):
            continue

        operation = operations[op_index]
        machine = operation['machine']
        processing_time = operation['processing_time']
        start_time = max(machine_avail_time[machine], job_completion_time[job_id])
        completion_time = start_time + processing_time
        machine_avail_time[machine] = completion_time
        job_completion_time[job_id] = completion_time
        job_operation_index[job_id] += 1

        schedule.append((job_id, machine, start_time, completion_time))

    makespan = max(job_completion_time.values())
    return makespan, schedule


def select_parents(population):
    parents = []
    for _ in range(2):
        tournament = random.sample(population, k=3)
        parents.append(min(tournament, key=lambda x: fitness_func(x)[0]))
    return parents


def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    child1 = validate_and_repair(child1)
    child2 = validate_and_repair(child2)

    return child1, child2


def validate_and_repair(child):
    job_operation_counts = {job['job_id']: job['num_operations'] for job in list_of_jobs}
    child_counts = {job_id: child.count(job_id) for job_id in job_operation_counts}

    for job_id, expected_count in job_operation_counts.items():
        if child_counts[job_id] != expected_count:
            current_count = child_counts[job_id]
            if current_count < expected_count:
                missing_count = expected_count - current_count
                for _ in range(missing_count):
                    child.append(job_id)
            elif current_count > expected_count:
                excess_count = current_count - expected_count
                indices_to_remove = [i for i, x in enumerate(child) if x == job_id][:excess_count]
                for index in sorted(indices_to_remove, reverse=True):
                    child.pop(index)

    return child


def mutation(chromosome):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(chromosome)), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]


def genetic_algorithm():
    population = initialize_population()
    best_schedule_overall = None  # Store the best schedule overall
    best_fitness_overall = float('inf')  # Initialize with a very large value
    best_chromosome_overall = None  # Store the best chromosome overall

    for generation in range(Number_of_Generations):
        new_population = []
        for _ in range(Population_Size // 2):
            parents = select_parents(population)
            child1, child2 = crossover(parents[0], parents[1])
            mutation(child1)
            mutation(child2)
            new_population.extend([child1, child2])

        population = sorted(new_population, key=lambda x: fitness_func(x)[0])[:Population_Size]
        best_chromosome = min(population, key=lambda x: fitness_func(x)[0]) # Get the best chromosome
        BF, BS = fitness_func(best_chromosome)

        # Update best_schedule_overall if a better schedule is found
        if BF < best_fitness_overall:
            best_fitness_overall = BF
            best_schedule_overall = BS
            best_chromosome_overall = best_chromosome # Store the best chromosome

        print(f"Generation {generation}: Best fitness = {BF} -> Schedule = {BS}")

    return best_chromosome_overall  # Return the overall best chromosome


def plot_gantt_chart(schedule):
    fig, ax = plt.subplots()
    cmap = ListedColormap(
        ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
         'tab:olive', 'tab:cyan'])

    # Create job ID mapping (J1 to A, J2 to B, ..., J10 to J)
    job_id_mapping = {i + 1: chr(ord('A') + i) for i in range(10)}  # Mapping for J1 to J10
    
    # In case you have more than 10 Jobs and you want to display the Numerical Job Ids > 10
    # job_id_mapping.update({i + 1: str(i+1) for i in range(10,len(list_of_jobs))})

    for job_id, machine, start_time, end_time in schedule:
        # Get job label from mapping or use the original Job ID if it is greater than 10
        job_label = job_id_mapping.get(job_id, job_id)  
        ax.barh(machine, end_time - start_time, left=start_time, height=0.6, color=cmap(job_id % 10),
                edgecolor='black')
        ax.text(start_time + (end_time - start_time) / 2, machine, job_label, color='black', ha='center',
                va='center')

    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_title('Job Shop Schedule')
    plt.yticks(range(1, num_machines + 1), [f'M{i}' for i in range(1, num_machines + 1)])

    # Add job ID key at the top right corner
#    key_text = "\n".join([f"{job_id_mapping[i + 1]}" for i in range(len(job_id_mapping))])
#    ax.text(0.95, 0.95, key_text, transform=ax.transAxes, ha='right', va='top',
#            bbox=dict(facecolor='white', alpha=0.8))

    plt.show()



# initialize_jobs()
initialize_jobs_from_file("input_file.txt")
Population = initialize_population()

best_chromosome = genetic_algorithm()
makespan, best_schedule = fitness_func(best_chromosome)
print("Best Schedule:", best_schedule)

plot_gantt_chart(best_schedule)