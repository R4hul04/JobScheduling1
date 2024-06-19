import matplotlib.pyplot as plt

class Job:
    def __init__(self, job_id, arrival_time, burst_time, priority=0):
        self.job_id = job_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.original_burst_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None

class Scheduler:
    def __init__(self, jobs):
        self.jobs = jobs

    def schedule(self):
        raise NotImplementedError

class FCFS(Scheduler):
    def schedule(self):
        self.jobs.sort(key=lambda x: x.arrival_time)
        current_time = 0
        for job in self.jobs:
            job.start_time = max(current_time, job.arrival_time)
            job.completion_time = job.start_time + job.burst_time
            job.turnaround_time = job.completion_time - job.arrival_time
            job.waiting_time = job.start_time - job.arrival_time
            current_time = job.completion_time

class SJN(Scheduler):
    def schedule(self):
        self.jobs.sort(key=lambda x: x.arrival_time)
        current_time = 0
        ready_queue = []
        completed_jobs = []

        while self.jobs or ready_queue:
            while self.jobs and self.jobs[0].arrival_time <= current_time:
                ready_queue.append(self.jobs.pop(0))
            if ready_queue:
                ready_queue.sort(key=lambda x: x.burst_time)
                job = ready_queue.pop(0)
                job.start_time = current_time
                job.completion_time = job.start_time + job.burst_time
                job.turnaround_time = job.completion_time - job.arrival_time
                job.waiting_time = job.start_time - job.arrival_time
                current_time = job.completion_time
                completed_jobs.append(job)
                print(f"Scheduled {job.job_id} from {job.start_time} to {job.completion_time}")
            else:
                current_time += 1
                print(f"No job ready at time {current_time}, incrementing time")
        
        self.jobs = completed_jobs

class RR(Scheduler):
    def __init__(self, jobs, time_quantum):
        super().__init__(jobs)
        self.time_quantum = time_quantum

    def schedule(self):
        current_time = 0
        queue = self.jobs[:]
        while queue:
            job = queue.pop(0)
            if job.start_time is None:
                job.start_time = current_time

            if job.burst_time <= self.time_quantum:
                current_time += job.burst_time
                job.completion_time = current_time
                job.turnaround_time = job.completion_time - job.arrival_time
                job.waiting_time = job.turnaround_time - job.original_burst_time
                job.burst_time = 0  # Job is fully executed
            else:
                current_time += self.time_quantum
                job.burst_time -= self.time_quantum
                queue.append(job)

class PriorityScheduler(Scheduler):
    def schedule(self):
        self.jobs.sort(key=lambda x: (x.arrival_time, x.priority))
        current_time = 0
        ready_queue = []
        completed_jobs = []

        while self.jobs or ready_queue:
            while self.jobs and self.jobs[0].arrival_time <= current_time:
                ready_queue.append(self.jobs.pop(0))
            if ready_queue:
                ready_queue.sort(key=lambda x: x.priority)
                job = ready_queue.pop(0)
                job.start_time = current_time
                job.completion_time = job.start_time + job.burst_time
                job.turnaround_time = job.completion_time - job.arrival_time
                job.waiting_time = job.start_time - job.arrival_time
                current_time = job.completion_time
                completed_jobs.append(job)
                print(f"Scheduled {job.job_id} from {job.start_time} to {job.completion_time} with priority {job.priority}")
            else:
                current_time += 1
                print(f"No job ready at time {current_time}, incrementing time")
        
        self.jobs = completed_jobs

class SimulationEngine:
    def __init__(self, jobs, scheduler_class):
        self.jobs = jobs
        self.scheduler = scheduler_class(jobs)
    
    def run(self):
        self.scheduler.schedule()
        self.display_results()
        if self.jobs:  # Check if there are jobs to plot
            plot_gantt_chart(self.jobs)
    
    def display_results(self):
        print(f"{'Job ID':<10}{'Arrival':<10}{'Burst':<10}{'Start':<10}{'Completion':<15}{'Waiting':<10}{'Turnaround':<15}")
        for job in self.jobs:
            print(f"{job.job_id:<10}{job.arrival_time:<10}{job.original_burst_time:<10}{job.start_time:<10}{job.completion_time:<15}{job.waiting_time:<10}{job.turnaround_time:<15}")

def plot_gantt_chart(jobs):
    fig, gnt = plt.subplots()
    gnt.set_ylim(0, 50)
    gnt.set_xlim(0, max(job.completion_time for job in jobs) + 10)
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Job ID')

    gnt.set_yticks([15 + 10*i for i in range(len(jobs))])
    gnt.set_yticklabels([job.job_id for job in jobs])

    for i, job in enumerate(jobs):
        gnt.broken_barh([(job.start_time, job.completion_time - job.start_time)], (10 + 10*i, 9), facecolors=('tab:blue'))
        gnt.text(job.start_time + (job.completion_time - job.start_time) / 2, 15 + 10*i, f"{job.start_time}-{job.completion_time}", 
                 va='center', ha='center', color='white', fontweight='bold')

    plt.show()

def create_jobs():
    return [
        Job(1, 0, 5),
        Job(2, 1, 3),
        Job(3, 2, 8),
        Job(4, 3, 6)
    ]

def test_scheduler():
    print("Testing FCFS Scheduler")
    jobs = create_jobs()
    engine = SimulationEngine(jobs, FCFS)
    engine.run()
    
    print("Testing SJN Scheduler")
    jobs = create_jobs()
    engine = SimulationEngine(jobs, SJN)
    engine.run()
    
    print("Testing RR Scheduler with time quantum 2")
    jobs = create_jobs()
    engine = SimulationEngine(jobs, lambda jobs: RR(jobs, 2))
    engine.run()
    
    print("Testing Priority Scheduler")
    jobs_with_priority = [
        Job(1, 0, 5, 2),
        Job(2, 1, 3, 1),
        Job(3, 2, 8, 4),
        Job(4, 3, 6, 3)
    ]
    engine = SimulationEngine(jobs_with_priority, PriorityScheduler)
    engine.run()

# Run the test function
test_scheduler()
