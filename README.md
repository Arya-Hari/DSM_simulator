# DSM_simulator
This simulator aims to simulate the working of a Distributed Shared Memory System using socket programming in Python. It implements DSM following the central server DSM algorithm.

This Distributed Shared Memory simulation following the central server algorithm has two major components : 
* A server.py file which acts as the server and is used to handle client requests. It follows certain rules -
  * One client can do only one action (read/write) at a time for one file only
  * Multiple clients can be allowed to read the same file
  * Only one client can write a file at a time, during which, reading and writing by other clients is not allowed.
  * A client whose request to read or write was denied is given the provision to wait until access is granted. If access in such scenarios is not granted within a time limit a time-out condition occurs.
* A client.py file which acts as the client and is used to create client instances and relay information from the server to the client.

This simulation makes use of socket programming for inter-process communication. The ease of use of Python in socket programming is why it was used for the simulation.
