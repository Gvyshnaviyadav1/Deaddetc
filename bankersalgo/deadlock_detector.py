import time
import numpy as np
import ctypes
from shared_state import n, r

def build_wait_for_graph(available_snap, allocation_snap, request_snap):
    """
    a function that creates the graph with all the required resources and processes
    """
    WFG = {i: set() for i in range(n)}
    
    for p_i in range(n):
        # resources requesting
        for r_j in range(r):
            if request_snap[p_i, r_j] > 0:
                # P_i  waiting  R_j
                # check if resouce is available
                if available_snap[r_j] < request_snap[p_i, r_j]:
                    # if  request cannot be immediately satisfied;
                    for p_k in range(n):
                        if allocation_snap[p_k, r_j] > 0:
                            # P_i is waiting for R_j, and P_k is holding some R_j.
                            WFG[p_i].add(p_k)
                            
    return WFG

def dfs_cycle_detection(graph):
    """
    function to run a dfs  to detect a cycle
    Returns the cycle path if found, otherwise None.
    """
    visited = [False] * n   #visited nodes
    recursion_stack = [False] * r
    path = []  #path

    def dfs(u):
        visited[u] = True
        recursion_stack[u] = True
        path.append(u)

        for v in graph[u]:
            if not visited[v]:
                # 
                cycle = dfs(v)
                if cycle:
                    return cycle
            elif recursion_stack[v]:
                # if cycle found
                cycle_start_index = path.index(v)
                return path[cycle_start_index:]
        
        # pop them and go back
        path.pop()
        recursion_stack[u] = False
        return None

    for i in range(n):
        if not visited[i]:
            cycle_found = dfs(i)
            if cycle_found:
                return cycle_found
    
    return None

def deadlock_detector_process(lock, available_raw, allocation_raw, request_raw):
    """
    function to detect the deadlock it checks every 5 seconds
    """
    while True:
        time.sleep(5)  # check every 5 seconds

        # enter the critical section
        lock.acquire()
        try:
            # get the reources
            A_view, C_view, R_view = get_numpy_views(available_raw, allocation_raw, request_raw)
            
            # copy them from shared memory
            A_snap = A_view.copy()
            C_snap = C_view.copy()
            R_snap = R_view.copy()
        finally:
            lock.release() 
            
        # construct the graph and detect cycle 
        WFG = build_wait_for_graph(A_snap, C_snap, R_snap)
        deadlocked_cycle = dfs_cycle_detection(WFG)

        # if deadlock detected print detected
        if deadlocked_cycle:
            cycle_str = " -> P".join(map(str, deadlocked_cycle))
            print("\n" + "="*50)
            print(f"DEADLOCK DETECTED at {time.strftime('%H:%M:%S')}")
            print(f"  Cycle: P{cycle_str} -> P{deadlocked_cycle[0]}")
            print(f"  Involved Processes: {['P'+str(p) for p in deadlocked_cycle]}")
            print(f"  Snapshot of Request Matrix:\n{R_snap}")
            print("="*50 + "\n")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] system is currently SAFE STATE")

def get_numpy_views(*args):
    """ function to reuse views from shared_state"""
    return np.frombuffer(args[0], dtype=ctypes.c_int), \
           np.frombuffer(args[1], dtype=ctypes.c_int).reshape(n,r), \
           np.frombuffer(args[2], dtype=ctypes.c_int).reshape(n,r)
