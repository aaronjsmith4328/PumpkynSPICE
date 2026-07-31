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
import math
import random
import matplotlib.pyplot as plt

def make_ramp(v_from, v_to, duration, dt,
              n_sine=3, n_tri=5, n_saw=7, ripple=0.15):
    """Transition from v_from to v_to over `duration`, but instead of a plain
    linear ramp, ride a composite ripple (sine + triangle + sawtooth) on top of
    the linear trend.
 
    The ripple is windowed (sin(pi*frac)) so it fades to zero at both ends,
    which keeps the endpoints exactly at v_from / v_to -- so this drops straight
    into main()'s pulse assembly with no jump at the seams. The sawtooth's sharp
    resets still land mid-ramp, so the transition stays genuinely busy.
 
    n_sine / n_tri / n_saw : number of full cycles of each component across the
                             ramp.
    ripple                 : combined ripple amplitude as a fraction of the
                             transition height |v_to - v_from|.
    """
    n_steps = int(duration / dt)
    if n_steps <= 0:
        return []
 
    span = v_to - v_from
    amp = ripple * abs(span) if span else ripple   # fall back if flat
 
    out = []
    for i in range(n_steps + 1):
        frac = i / n_steps                          # 0 .. 1 across the ramp
        base = v_from + span * frac                 # linear trend
 
        # sine component, in [-1, 1]
        s = math.sin(2 * math.pi * n_sine * frac)
 
        # triangle component, in [-1, 1] (corners at peaks)
        tf = (n_tri * frac) % 1.0
        tri = 1.0 - 4.0 * abs(tf - 0.5)
 
        # sawtooth component, in [-1, 1] (sharp reset each cycle)
        sf = (n_saw * frac) % 1.0
        saw = 2.0 * sf - 1.0
 
        # window: 0 at both ends, 1 in the middle -> endpoints stay clean
        window = math.sin(math.pi * frac)
 
        ripple_val = amp * window * (s + tri + saw) / 3.0
        out.append(base + ripple_val)
 
    return out
 
 
def build_source(dt, Vs_max, total_time, seed=42,
                 hold_range=(2.0, 8.0), ramp_range=(0.5, 3.0),
                 min_delta_frac=0.3):
    """Build a randomized source-voltage list: a train of composite ramps to
    random levels, each separated by a random hold.
 
    Starts at 0 V, then repeatedly picks a new random target level (each ramp is
    the composite make_ramp shape), ramps to it over a random duration, and
    holds there for a random duration -- until total_time is reached. Because
    each target is drawn independently, the ramps go up and down "randomly."
 
    seed           : fixes the RNG so runs are reproducible.
    hold_range     : (min, max) seconds to sit at a level between ramps.
    ramp_range     : (min, max) seconds for each ramp edge.
    min_delta_frac : each new target must differ from the current level by at
                     least this fraction of Vs_max, so every ramp is visible.
    """
    rng = random.Random(seed)
    v = []
    level = 0.0
 
    # initial hold at 0 before anything happens
    v += [level] * int(rng.uniform(*hold_range) / dt)
 
    while len(v) * dt < total_time:
        # pick a new target that's meaningfully different from where we are
        target = rng.uniform(0, Vs_max)
        while abs(target - level) < min_delta_frac * Vs_max:
            target = rng.uniform(0, Vs_max)
 
        ramp_dur = rng.uniform(*ramp_range)
        v += make_ramp(level, target, ramp_dur, dt)
        level = target
 
        v += [level] * int(rng.uniform(*hold_range) / dt)
 
    return v

def main():
    print("Hello from pumpkynspice!")
    R = 10e3       # Ohms
    C = 100e-6     # Farads
    Vs_max = 3.3  # Volts
    dt = 0.001    # seconds

    total_time = 100.0  # seconds -- ~5x the original single-pulse run
    # A randomized train of composite ramps up and down (reproducible via seed).
    v = build_source(dt, Vs_max, total_time, seed=42)
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
