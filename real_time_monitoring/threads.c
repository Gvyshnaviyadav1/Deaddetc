#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h> // For sleep

// Define two mutexes (locks)
pthread_mutex_t mutex1;
pthread_mutex_t mutex2;

// --- Thread 1 Function ---
void *thread_func_1(void *arg) {
    printf("Thread 1: Trying to lock Mutex 1...\n");
    // Thread 1 locks Mutex 1
    pthread_mutex_lock(&mutex1);
    printf("Thread 1: Locked Mutex 1. Waiting for Mutex 2...\n");

    // Introduce a delay to increase the chance of the other thread locking mutex2
    sleep(1);

    // Thread 1 tries to lock Mutex 2 (This is where the deadlock occurs)
    printf("Thread 1: Trying to lock Mutex 2...\n");
    pthread_mutex_lock(&mutex2);

    // This part will not be reached in the deadlock scenario
    printf("Thread 1: Locked Mutex 2. Releasing both...\n");
    pthread_mutex_unlock(&mutex2);
    pthread_mutex_unlock(&mutex1);
    printf("Thread 1: Finished.\n");

    return NULL;
}

// --- Thread 2 Function ---
void *thread_func_2(void *arg) {
    printf("Thread 2: Trying to lock Mutex 2...\n");
    // Thread 2 locks Mutex 2
    pthread_mutex_lock(&mutex2);
    printf("Thread 2: Locked Mutex 2. Waiting for Mutex 1...\n");

    // Introduce a delay to ensure thread 1 has already locked mutex1
    sleep(1);

    // Thread 2 tries to lock Mutex 1 (This is where the deadlock occurs)
    printf("Thread 2: Trying to lock Mutex 1...\n");
    pthread_mutex_lock(&mutex1);

    // This part will not be reached in the deadlock scenario
    printf("Thread 2: Locked Mutex 1. Releasing both...\n");
    pthread_mutex_unlock(&mutex1);
    pthread_mutex_unlock(&mutex2);
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

    printf("Starting threads...\n");

    // Create the two threads
    pthread_create(&t1, NULL, thread_func_1, NULL);
    pthread_create(&t2, NULL, thread_func_2, NULL);

    // The threads will enter a deadlock, so we don't expect join to finish normally.
    // In a real scenario, you might have a timeout or monitoring logic.
    // For this demonstration, we'll let the program run in the deadlocked state.
    printf("Main thread is sleeping for 10 seconds to allow deadlock to form...\n");
    sleep(10); 
    printf("Main thread: Program is likely deadlocked. Press Ctrl+C to stop.\n");

    // Clean up (though these lines won't be reached if the program is stopped by Ctrl+C)
     pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    //pthread_mutex_destroy(&mutex1);
    //pthread_mutex_destroy(&mutex2);

    return 0;
}
