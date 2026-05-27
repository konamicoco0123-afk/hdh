from copy import deepcopy


def fcfs_scheduling(processes):
    """First-Come First-Serve scheduling.

    Args:
        processes (list[dict]): List of processes with keys pid, arrival, burst.

    Returns:
        dict: schedule history and average times.
    """
    jobs = deepcopy(processes)
    jobs.sort(key=lambda item: (item["arrival"], item["pid"]))

    time = 0
    history = []
    waiting_times = []
    turnaround_times = []

    for job in jobs:
        arrival = job["arrival"]
        burst = job["burst"]
        pid = job["pid"]

        if time < arrival:
            time = arrival

        start = time
        end = time + burst
        waiting = start - arrival
        turnaround = end - arrival

        history.append({"pid": pid, "start": start, "end": end})
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)
        time = end

    average_waiting = sum(waiting_times) / len(waiting_times) if waiting_times else 0.0
    average_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0.0

    return {
        "algorithm": "FCFS",
        "history": history,
        "average_waiting_time": round(average_waiting, 2),
        "average_turnaround_time": round(average_turnaround, 2),
    }


def sjf_scheduling(processes):
    """Non-preemptive Shortest Job First scheduling.

    Args:
        processes (list[dict]): List of processes with keys pid, arrival, burst.

    Returns:
        dict: schedule history and average times.
    """
    jobs = deepcopy(processes)
    remaining = sorted(jobs, key=lambda item: (item["arrival"], item["burst"], item["pid"]))

    time = 0
    history = []
    waiting_times = []
    turnaround_times = []
    completed = []

    while remaining:
        available = [job for job in remaining if job["arrival"] <= time]
        if not available:
            time = remaining[0]["arrival"]
            available = [job for job in remaining if job["arrival"] <= time]

        available.sort(key=lambda item: (item["burst"], item["arrival"], item["pid"]))
        job = available[0]
        remaining.remove(job)

        start = max(time, job["arrival"])
        end = start + job["burst"]
        waiting = start - job["arrival"]
        turnaround = end - job["arrival"]

        history.append({"pid": job["pid"], "start": start, "end": end})
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)
        time = end
        completed.append(job)

    average_waiting = sum(waiting_times) / len(waiting_times) if waiting_times else 0.0
    average_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0.0

    return {
        "algorithm": "SJF",
        "history": history,
        "average_waiting_time": round(average_waiting, 2),
        "average_turnaround_time": round(average_turnaround, 2),
    }


def rr_scheduling(processes, quantum=2):
    """Round Robin scheduling with fixed time quantum.

    Args:
        processes (list[dict]): List of processes with keys pid, arrival, burst.
        quantum (int): Time quantum.

    Returns:
        dict: schedule history and average times.
    """
    jobs = deepcopy(processes)
    jobs.sort(key=lambda item: (item["arrival"], item["pid"]))

    remaining = [{"pid": job["pid"], "arrival": job["arrival"], "burst": job["burst"], "remaining": job["burst"]} for job in jobs]
    time = 0
    history = []
    completed = {}
    waiting_times = []
    turnaround_times = []
    ready_queue = []
    next_index = 0

    def enqueue_arrivals(current_time):
        nonlocal next_index
        while next_index < len(remaining) and remaining[next_index]["arrival"] <= current_time:
            ready_queue.append(remaining[next_index])
            next_index += 1

    enqueue_arrivals(time)

    while ready_queue or next_index < len(remaining):
        if not ready_queue:
            time = remaining[next_index]["arrival"]
            enqueue_arrivals(time)
            continue

        proc = ready_queue.pop(0)
        start = max(time, proc["arrival"])
        run_time = min(quantum, proc["remaining"])
        end = start + run_time

        history.append({"pid": proc["pid"], "start": start, "end": end})
        proc["remaining"] -= run_time
        time = end
        enqueue_arrivals(time)

        if proc["remaining"] > 0:
            ready_queue.append(proc)
        else:
            completion = time
            turnaround = completion - proc["arrival"]
            waiting = turnaround - proc["burst"]
            turnaround_times.append(turnaround)
            waiting_times.append(waiting)
            completed[proc["pid"]] = proc

    average_waiting = sum(waiting_times) / len(waiting_times) if waiting_times else 0.0
    average_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0.0

    return {
        "algorithm": "Round Robin",
        "history": history,
        "average_waiting_time": round(average_waiting, 2),
        "average_turnaround_time": round(average_turnaround, 2),
        "quantum": quantum,
    }
