import multiprocessing as mp
from multiprocessing.sharedctypes import RawArray
import ctypes
import numpy as np

# parameters
n= 4  
r= 3  

#available resources in matrix
INIT_AVAILABLE = np.array([1, 1, 1], dtype=ctypes.c_int)

def initialize_shared_state():     #function to intialize all the required matrices  and store them in shared memory 
    
  
    # lock protects access to shared memory
    lock = mp.Lock()

    
   #available instances intially
    available = RawArray(ctypes.c_int, INIT_AVAILABLE)
    
    #allocation matrix
    allocation = RawArray(ctypes.c_int, n * r)
    
    # request Matrix (n *r)
   
    request = RawArray(ctypes.c_int, n * r)

    print("Shared state initialized")
    
    return lock, available, allocation, request
    
def get_numpy_views(available, allocation, request):
    A = np.frombuffer(available, dtype=ctypes.c_int)
    C = np.frombuffer(allocation, dtype=ctypes.c_int).reshape(n,r)
    R = np.frombuffer(request, dtype=ctypes.c_int).reshape(n,r)
    
    return A, C, R
