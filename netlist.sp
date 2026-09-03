* AI Generated
* RLC Ladder Network - Transient
* Driving with a 1kHz sine, watching the network ring and settle

Vin  1 0 SIN(0 1 1000)

* Series path (top rail)
R1   1 2 100
L1   2 3 10m
R2   3 4 47
L2   4 5 4.7m

* Shunt elements to ground
C1   2 0 100n
C2   3 0 47n
R3   3 0 10k
C3   4 0 22n
C4   5 0 10n

* Termination
R4   5 0 1k

.TRAN 1u 10m
.END
