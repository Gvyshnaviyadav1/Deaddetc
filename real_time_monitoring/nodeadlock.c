#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h> // For sleep

// Define two mutexes (locks)
pthread_mutex_t mutex1;
pthread_mutex_t mutex2;

// --- Thread 1 Function ---
void *thread_func_1(void *arg) {
    printf("Thread 1: Establishing lock order: M1 then M2.\n");
    
    // 1. Lock Mutex 1
    printf("Thread 1: Trying to lock Mutex 1...\n");
    pthread_mutex_lock(&mutex1);
    printf("Thread 1: Locked Mutex 1.\n");

    // Introduce a delay to allow the other thread to start and potentially block
    sleep(1); 

    // 2. Lock Mutex 2
    printf("Thread 1: Trying to lock Mutex 2...\n");
    pthread_mutex_lock(&mutex2);
    printf("Thread 1: Locked Mutex 2. Critical Section Entered.\n");

    // Critical Section
    printf("Thread 1: Executing critical section (5 seconds)...\n");
    sleep(5); 

    // Release locks in reverse order
    printf("Thread 1: Releasing Mutex 2.\n");
    pthread_mutex_unlock(&mutex2);
    printf("Thread 1: Releasing Mutex 1.\n");
    pthread_mutex_unlock(&mutex1);
    
    printf("Thread 1: Finished.\n");
    return NULL;
}

// --- Thread 2 Function ---
void *thread_func_2(void *arg) {
    printf("Thread 2: Establishing lock order: M1 then M2.\n");
    
    // 1. Lock Mutex 1 (must wait if Thread 1 holds it)
    printf("Thread 2: Trying to lock Mutex 1...\n");
    pthread_mutex_lock(&mutex1);
    printf("Thread 2: Locked Mutex 1.\n");

    // Introduce a delay to ensure the consistent locking is followed
    sleep(1); 

    // 2. Lock Mutex 2 (must wait if Thread 1 holds it)
    printf("Thread 2: Trying to lock Mutex 2...\n");
    pthread_mutex_lock(&mutex2);
    printf("Thread 2: Locked Mutex 2. Critical Section Entered.\n");

    // Critical Section
    printf("Thread 2: Executing critical section (5 seconds)...\n");
    sleep(5); 

    // Release locks in reverse order
    printf("Thread 2: Releasing Mutex 2.\n");
    pthread_mutex_unlock(&mutex2);
    printf("Thread 2: Releasing Mutex 1.\n");
    pthread_mutex_unlock(&mutex1);
    
    printf("Thread 2: Finished.\n");
    return NULL;
}

// --- Main Function ---
int main() {
    pthread_t t1, t2;

    // Initialize the mutexes
    if (pthread_mutex_init(&mutex1, NULL) != 0 || pthread_mutex_init(&mutex2, NULL) != 0) {
        perror("Mutex initialization failed");
        return 1;
    }

    printf("Starting threads. Both will follow the lock order M1 -> M2.\n");

    // Create the two threads
    pthread_create(&t1, NULL, thread_func_1, NULL);
    pthread_create(&t2, NULL, thread_func_2, NULL);

    // Wait for both threads to complete (they should now successfully finish)
    pthread_join(t1, NULL);
    printf("Main thread: Thread 1 has completed.\n");
    
    pthread_join(t2, NULL);
    printf("Main thread: Thread 2 has completed.\n");

    // Clean up
    pthread_mutex_destroy(&mutex1);
    pthread_mutex_destroy(&mutex2);

    printf("Program finished successfully and deadlock-free.\n");

    return 0;
}
