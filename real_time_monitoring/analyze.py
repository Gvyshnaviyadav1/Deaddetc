import re
import subprocess
import os
import sys
#dictionary to run deadlock and no deadlock file
CONFIGURATIONS = [
    {
        'process_name': 'nodeadlock',      #executable files and output files of strace
         'strace_file': 'out1.txt'
    },
    {
        'process_name': 'threads',        
        'strace_file': 'out2.txt'
    },
]

def check_deadlock_from_strace(filename):
    """
    analyze the strace output to confirm if threads 
    were permanently blocked 
    
    returns if processes are deadlocked or not
    """
    print(f"\n Analyzing {filename} for permanent blocking signs...")

    last_action = {}
    total_syscalls = 0
    
    # map the last line of action for every TID
    try:
        with open(filename, 'r') as f:
            for line in f:
                total_syscalls += 1
                match = re.match(r"^\s*(\d+)\s+.*$", line)
                if match:
                    tid = match.group(1)
                    last_action[tid] = line.strip()

        print(f"   -> Analyzed {total_syscalls} syscall lines.") #checking total no of syscalls
        if not last_action:
            print("Error: strace output is empty or unreadable.")  #if there is error then give execption
            return False, set()
            
    except FileNotFoundError:  #remove exceptions
        print(f"Error: strace output file '{filename}' not found. Skipping analysis for this file.")
        return None, set()  
    except Exception as e:
        print(f"An error occurred during strace file parsing: {e}. Skipping analysis.")
        return None, set()



    # check for clean exit similar which means no dead lock the program was sucessfull 
    clean_exit = any("exit_group(" in action and " = 0" in action for action in last_action.values())
    
    if clean_exit:
        print("   -> Found 'exit_group(0)' or successful termination. The program completed cleanly.")
        return False, set()

    # if it has exited cleanly
    
    # system calls (futex) that have no return value or end with ? showing blocked 
    blocking_pattern = r"\b(futex\(.*FUTEX_WAIT.*)\b(?![^=]*=\s*[-0-9]+)"
    
    permanently_blocked_tids = set()
    
    for tid, action_line in last_action.items():
        if re.search(blocking_pattern, action_line) or action_line.endswith("?"):
            permanently_blocked_tids.add(tid)

    # deadlock is confirmed if >= 2 TIDs were permanently blocked 
    if len(permanently_blocked_tids) >= 2:
        print(f"✅ DEADLOCK DETECTED! Found {len(permanently_blocked_tids)} TIDs permanently blocked.")
        return True, permanently_blocked_tids
    else:
        print("❌ No evidence of permanent deadlock found.")
        return False, set()

def get_process_info(pid):
    """
    retrieves and displays memory information for the process using /proc.
    """
    status_file_path = f"/proc/{pid}/status"
    task_dir = f"/proc/{pid}/task"
    memory_stats = {}
    
    try:
        # for getting memory /proc/<PID>/status 
        with open(status_file_path, 'r') as f:
            for line in f:
                if line.startswith("VmSize:") or line.startswith("VmRSS:"):
                    key, value, unit = line.split()
                    memory_stats[key.strip(':')] = f"{value} {unit}"
        
        # thread IDs (TIDs) from /proc/<PID>/task
        all_tids = [d for d in os.listdir(task_dir) if d.isdigit()]
        
        print("\n--- Process Information (Live) ---")
        print(f"**PID (Main Process ID):** {pid}")
        print(f"**All Threads (TIDs):** {', '.join(all_tids)}")
        
    
        print("\n**Memory Usage (Total Process):**")
        for k, v in memory_stats.items():
            print(f"   - {k}: {v}")
            
        print("\n*Note: All threads within a process share the same VmSize and VmRSS.*")

    except FileNotFoundError:
        print(f"Error: Could not access process info for PID {pid}. The process likely terminated.")
    except Exception as e:
        print(f"An unexpected error occurred during info retrieval: {e}")


def find_pid_and_analyze_live(process_name, is_deadlocked):
    """finds the PID of the currently running process and initiates the detailed analysis."""
    print(f"\n🔍 Searching for PID of running process '{process_name}'...")
    
    try:
        pgrep_command = f"pgrep -x {process_name}"
        pid_output = subprocess.run(pgrep_command, shell=True, capture_output=True, text=True, check=True)
        pids = pid_output.stdout.strip().split('\n')
        
        if not pids or pids == ['']:
            raise subprocess.CalledProcessError(1, pgrep_command, stderr="No process found.")

        main_pid = pids[0]
        print(f"   -> Main Process PID found: {main_pid}")

        get_process_info(main_pid)

    except subprocess.CalledProcessError:
        print(f"   -> Error: pgrep command failed or process '{process_name}' not running.")
        if is_deadlocked is True:
             print("      (Expected, as the deadlocked process was terminated to create the strace file.)")
        elif is_deadlocked is False:
             print("      (Expected, as the non-deadlocked program completed successfully.)")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    
    for config in CONFIGURATIONS:
        p_name = config['process_name']
        f_name = config['strace_file']
        
        print("\n" + "#" * 70)
        print(f"## Analyzing Scenario:{p_name.upper()}(File: {f_name})")
        print("#" * 70)

        # check for deadlock using strace output
        is_deadlocked, blocked_tids = check_deadlock_from_strace(f_name)
        
        if is_deadlocked is None:
            print(f"Analysis for {p_name} skipped due to file error.")
            continue
        
        # analyze process status and memory
        if is_deadlocked:
            print("\n--- DETAILED ANALYSIS: DEADLOCK STATE ---")  #if system is in deadlocked state we find how much memory it is using and what all procesess are invlovled in that program 
            find_pid_and_analyze_live(p_name, is_deadlocked)

        else:
            print("\n--- DETAILED ANALYSIS: NO DEADLOCK STATE ---")
            
        
        print("\n" + "=" * 50)
        if is_deadlocked:
            print(f"SUMMARY for {p_name.upper()}: 🔴 DEADLOCK CONFIRMED")
        else:
            print(f"SUMMARY for {p_name.upper()}: 🟢 NO DEADLOCK CONFIRMED. Program completed cleanly.")
        print("=" * 50)
