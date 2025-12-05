# Concurrent System Analysis: Deadlock Detection & Simulation

This repository contains two parts designed to explore concurrent
systems: 1. **Deadlock Detection:** Analyzing C programs
(`nodeadlock.c`, `threads.c`) using the Linux `strace` utility. 2.
**Deadlock Simulation:** A Python multi-process simulation based on the
Banker's Algorithm resource model.

------------------------------------------------------------------------

## Part 1: Deadlock Detection using `strace` Analysis

This part requires compiling C programs and running the Python analysis
script (`analyze.py`) **concurrently** in separate terminals to
correctly capture the state of the deadlocked program.

### 1. Compilation

Compile both the non-deadlock and the deadlock programs.

``` bash
# Compile the non-deadlock program
gcc nodeadlock.c -o nodeadlock -pthread

# Compile the deadlock program
gcc threads.c -o threads -pthread
```

### 2. Execution and Tracing (Terminal 1)

``` bash
# Run the non-deadlock program
strace -f -o out1.txt ./nodeadlock

# Run the deadlock program
strace -f -o out2.txt ./threads
```

⚠️ The `threads` program is expected to block due to deadlock. Continue
without terminating it.

### 3. Run Analysis (Terminal 2)

``` bash
python3 analyze.py
```

The script checks out1.txt and analyzes the live `threads` process using
`/proc`.

------------------------------------------------------------------------

## Part 2: Deadlock Simulation (Banker's Algorithm Model)

### 1. Setup

``` bash
cd bankersalgo
```

### 2. Execution

``` bash
python3 main.py
```

The simulation: - Initializes shared memory matrices\
- Runs multiple client processes\
- Triggers circular wait\
- Detector identifies deadlock every few seconds\
- Runs for \~20 seconds then terminates
