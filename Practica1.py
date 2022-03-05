from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random

N = 100
K = 10
NPROD = 3
NCONS = 3


def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage, index, data, mutex):
    mutex.acquire()
    try:
        storage[index.value] = data
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()


def get_data(storage, index, mutex):
    mutex.acquire()
    
    try:
        
        data = storage[0]
        index.value = index.value - 1
        delay()
        for i in range(index.value):
            storage[i] = storage[i + 1]
        storage[index.value] = -1

    finally:
        
        mutex.release()
        
    return data


def index_lower(storage):
    
    lower = None
    index = -1
    
    for i in range(NPROD):
        
        if storage[i][0] == -1:
            
            continue

        if index == -1:
            
            index = i
            lower = storage[i][0]

        if storage[i][0] < lower:
            
            lower = storage[i][0]
            index = i
            

    return index


def producer(storage, index, empty, non_empty, mutex):
    
    for v in range(N):
        
        delay(6)
        empty.acquire()
        add_data(storage, index, v, mutex)
        non_empty.release()
        print (f"Productor {current_process().name} almacenado {v}")
        
    empty.acquire()
    add_data(storage, index, -1, mutex)
    non_empty.release()
    print (f"Productor {current_process().name} terminado")


def consumer(storage, index, empty, non_empty, mutex, list_final):
    
    ind = 0
    running = [False for i in range(NPROD)]
    delay(6)
    
    for k in range(N*NPROD):
        
        for j in range(NPROD):
                
            if not running[j]:
                    
                non_empty[j].acquire()
                running[j] = True
                
        
        i = index_lower(storage)
        running[i] = False
        valor_consumido = get_data(storage[i], index[i], mutex[i])
        empty[i].release()
        list_final[ind] = valor_consumido
        ind += 1
        delay(6)
        
        print (f"Consumiendo {valor_consumido} del productor {i}")
        


def main():
    
    storage_list = []
    index = []
    non_empty = []
    empty = []
    mutex = []
    
    final = Array('i', NPROD*N)

    for i in range(NPROD):
        
        storage = Array('i', K)
        
        for i in range(K):
            
            storage[i] = -1
        
        
        storage_list.append(storage)
        
        index.append(Value('i', 0))
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(K))
        mutex.append(Lock())

        
    prodlst = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage_list[i], index[i], empty[i], non_empty[i], mutex[i]))
               for i in range(NPROD)]

    merge = Process(target=consumer,
                      name='merge',
                      args=(storage_list, index, empty, non_empty, mutex, final))

    for p in prodlst:
        p.start()
    merge.start()

    for p in prodlst:
        p.join()
    merge.join()

    print ("Almacen final", final[:])


if __name__ == '__main__':
    main()