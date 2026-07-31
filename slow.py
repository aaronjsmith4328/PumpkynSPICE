####################################################################################
#
#        ____                        __              _____ ____  ________________
#       / __ \__  ______ ___  ____  / /____  ______ / ___// __ \/  _/ ____/ ____/
#      / /_/ / / / / __ `__ \/ __ \/ //_/ / / / __ \\__ \/ /_/ // // /   / __/   
#     / ____/ /_/ / / / / / / /_/ / ,< / /_/ / / / /__/ / ____// // /___/ /___   
#    /_/    \__,_/_/ /_/ /_/ .___/_/|_|\__, /_/ /_/____/_/   /___/\____/_____/   
#                         /_/         /____/                                     
#
#
#
#                      R
#         Vs(+) ---/\/\/\/\---+---> Vout
#                             |
#                            ===  C
#                             |
#                            GND
#
#
#
#####################################################################################
"""
slow.py -- pumpkynspice RC circuit simulator (pure-Python reference implementation)
 
Simulates the step response of a simple first-order RC low-pass circuit driven
by a trapezoidal pulse (rise -> high -> fall -> low). The source voltage Vs(t)
is generated sample-by-sample, and Vout(t) is integrated with a basic backward-
Euler update of the capacitor voltage:
 
    i_R(t)   = (Vs(t) - Vout(t)) / R
    Vout(t+dt) = Vout(t) + i_R(t) * dt / C
 
This module is intentionally implemented with plain Python lists and loops
(no numpy) as a baseline for later performance comparisons. A future
numpy-vectorized version is planned to benchmark against this one -- see
"slow" in the filename as a hint that a "fast" sibling is coming.
 
Circuit:
    Vs(+) --- R ---+---> Vout
                   |
                  === C
                   |
                  GND
 
Parameters (see main()):
    R        : Resistance in Ohms
    C        : Capacitance in Farads
    Vs_max   : Peak/high-level source voltage in Volts
    dt       : Simulation time step in seconds
    t_start  : Initial low period before the pulse begins, in seconds
    t_ramp   : Rise/fall time of the pulse edges, in seconds
    t_high   : Duration the source stays high, in seconds
    t_low    : Duration the source stays low after the pulse, in seconds
 
Output:
    Saves a plot of Vsource and Vout vs. time to 'output.png' in the
    current working directory.
 
Usage:
    uv run slow.py
"""
import matplotlib.pyplot as plt

def make_ramp(v_from, v_to, duration, dt):
    n_steps = int(duration / dt)
    if n_steps <= 0:
        return []
    return [v_from + (v_to - v_from) * (i / n_steps) for i in range(n_steps + 1)]

def main():
    print("Hello from pumpkynspice!")
    R = 10e3       # Ohms
    C = 100e-6     # Farads
    Vs_max = 3.3  # Volts
    dt = 0.001    # seconds

    t_start = 5.0   # seconds low, before ramp
    t_ramp  = 0.05  # seconds to ramp up/down -- tweak this to taste
    t_high  = 5.0   # seconds high
    t_low   = 10.0  # seconds low at the end

    v_start     = [0] * int(t_start / dt)
    v_ramp_up   = make_ramp(0, Vs_max, t_ramp, dt)
    v_high      = [Vs_max] * int(t_high / dt)
    v_ramp_down = make_ramp(Vs_max, 0, t_ramp, dt)
    v_low       = [0] * int(t_low / dt)

    v = v_start + v_ramp_up + v_high + v_ramp_down + v_low
    t = [i * dt for i in range(len(v))]

    # Initial value
    Vout_list = []
    Vout = 0
    for voltage in v:
        RC = R*C
        Vout = (RC/(RC+dt)) * Vout + (dt/(RC+dt)) * voltage
        Vout_list.append(Vout)

    # Now lets plot
    plt.plot(t, v, label="Vsource", color="blue")
    plt.plot(t, Vout_list, label="Vout", color="red")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Voltage (Volts)")
    plt.title("Vout vs Vsource in a simple RC circuit from a pulse")
    plt.legend()  # Displays the labels
    plt.savefig('output.png')

if __name__ == "__main__":
    main()
