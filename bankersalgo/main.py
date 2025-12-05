import multiprocessing as mp
import time
import ctypes
import numpy as np

from shared_state import initialize_shared_state, get_numpy_views, n, r
from deadlock_detector import deadlock_detector_process

def handle_request(lock, A_view, C_view, R_view, pid, r_id, count):
    """function to satisfy a request."""
    
    lock.acquire()
    try:
        print(f"P{pid}: REQUESTING {count} of R{r_id}...")
        
        if A_view[r_id] >= count:
            # since we only do detection we assume that resource granted
            A_view[r_id] -= count
            C_view[pid, r_id] += count
            print(f"P{pid}: GRANTED {count} of R{r_id}. Available R{r_id}: {A_view[r_id]}")
            return "GRANTED"
        else:
            # request cannot be granted then place in wait 
            R_view[pid, r_id] += count
            print(f"P{pid}: WAITING for {count} of R{r_id}. Added to Request Matrix.")
            return "WAITING"
    finally:
        lock.release()

def handle_release(lock, A_view, C_view, pid, r_id, count):
    """function to resource release once done"""
    
    lock.acquire()
    try:
        if C_view[pid, r_id] >= count:
            C_view[pid, r_id] -= count
            A_view[r_id] += count
            print(f"P{pid}: RELEASED {count} of R{r_id}. Available R{r_id}: {A_view[r_id]}")
        else:
            print(f"P{pid}: ERROR, tried to release more R{r_id} than held.")
    finally:
        lock.release()

# --- Client Process Simulation (Designed to create a Deadlock) ---

def client_process(pid, lock, available_raw, allocation_raw, request_raw):
    """
    Simulates a process making requests and releases using a dictionary schedule.
    """
    A, C, R = get_numpy_views(available_raw, allocation_raw, request_raw)
    
    print(f"P{pid} started.")

    # dictionary defining the resource request schedules based on PID
    
  
    REQUEST_SCHEDULE = {
        0: [(0, 1), (1, 1)],  # P0 needs 1 R0, then 1 R1
        1: [(1, 1), (2, 1)],  # P1 needs 1 R1, then 1 R2
        2: [(2, 1), (0, 1)],  # P2 needs 1 R2, then 1 R0
    }

    if pid in REQUEST_SCHEDULE:
        schedule = REQUEST_SCHEDULE[pid]
        
        # Iterate through the sequential requests
        for i, (r_id, count) in enumerate(schedule):
            
            # Execute the request
            handle_request(lock, A, C, R, pid, r_id=r_id, count=count)
            
            # Preserve the original time delay that separated the acquire/wait calls
            if i == 0:
                time.sleep(1)
                
    elif pid == 3:
        # P3: Idle process that doesn't participate in the deadlock
        print(f"P{pid}: Idle, won't create a deadlock.")

    # Keep processes alive so the deadlock state persists for the detector
    while True:
        time.sleep(10)
        
# main function

if __name__ == "__main__":
    # initialize shared State and lock
    lock, available_raw, allocation_raw, request_raw = initialize_shared_state()
    
    # create detector process
    detector_proc = mp.Process(target=deadlock_detector_process, 
                               args=(lock, available_raw, allocation_raw, request_raw))
    detector_proc.start()
    
    # create client processes
    client_procs = []
    for i in range(n):
        p = mp.Process(target=client_process, 
                       args=(i, lock, available_raw, allocation_raw, request_raw))
        client_procs.append(p)
        p.start()
       #run the algorithm for 20 seconds  
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        print("\nTermination signal received.")
    finally:
        # Clean up processes
        detector_proc.terminate()
        for p in client_procs:
            p.terminate()
        
        print("\nSimulation ended.")
