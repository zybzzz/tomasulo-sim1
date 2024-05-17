# tomasulo-sim1

This is the tomasulo simulator for the IBM 360/91.

Based on _Modern processor design: fundamentals of superscalar processors_.

## environment

python version: 3.12

## feature

1. Examining the internal state of the processor at each cycle, this simulator is designed to aid in the understanding of the tomasulo algorithm.

## The simulation environment makes the following agreements

- It simply simulates memory behavior, generating **random numbers** from data loaded from memory, with **no effect** on writes to memory, and **the addresses of load and store cannot be the same**.
- This is a simulation of an IBM 360/91 FPU that **sequentially issues** two instructions per cycle.
- Only **ADD and MUL** are simulated, with ADD consuming 2 clock cycles and MUL consuming 3 clock cycles.
- Distributed reserved station design with **three** reserved station units for ADD and **two** reserved station units for MUL.
- The last cycle of instruction execution can send the execution result of the instruction to the CDB **at the same time** as the instruction execution is completed.