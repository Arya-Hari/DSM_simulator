# DSM_simulator
The key features of a Distributed Shared Memory system that we have aimed to emulate/simulate are - 
(i) Memory Manager - It manages the allocation and deallocation of memory in the local address space of each machine
(ii) Page Table - It maintains a mapping between virtual and physical addresses for each process and contains information about each page's location (local or remote).
(iii) Coherence Protocol - It ensures that changes made to shared data by one processor are reflected in the copies held by other processors.
(iv) Thread Scheduler - It coordinates the execution of threads on each machine. Ensures synchronization and consistency in the execution of parallel programs.
