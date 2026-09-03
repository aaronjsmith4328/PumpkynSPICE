<p align="center">
  <img src="pumpkyn_spice_logo.png" alt="pumpkynspice logo" width="260"/>
</p>

<h1 align="center">pumpkynspice</h1>

<p align="center">
  A tiny, from-scratch circuit simulator for learning, tinkering, and benchmarking pure Python vs. NumPy.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.14-blue.svg">
  <img alt="uv" src="https://img.shields.io/badge/managed%20with-uv-6C4EE0.svg">
  <img alt="Status" src="https://img.shields.io/badge/status-experimental-orange.svg">
</p>

---

## What is this?

**pumpkynspice** is a toy SPICE simulator written in Python, built incrementally toward a limited but real netlist-driven circuit solver. The goal is not to replicate a full commercial SPICE — it's to understand how one works by building the pieces from scratch.

The current focus is the netlist parser: reading a `.sp` file with PySpice and building a circuit object that can eventually be stamped into an MNA matrix and solved. Each layer builds on the last — parser → MNA stamping → linear solve → nonlinear elements.

The current files in the project are:

| File | Description |
| --- | --- |
| `Spice.py` | Entry point. Instantiates `NetlistParser` on `netlist.sp` and runs it. |
| `NetlistParser.py` | Wraps PySpice's `SpiceParser` to read a `.sp` file and build a circuit object. |
| `netlist.sp` | Example SPICE netlist: an RLC ladder driven by a 1 kHz sine, used for testing the parser. |
| `slow.py` | *(Deprecated)* Initial proof-of-concept RC simulator. Will be removed once the netlist-driven solver is in place. |

---

## The netlist

`netlist.sp` is an AI-generated RLC ladder network for parser testing. A 1 kHz sine drives a series of resistors and inductors, with capacitors shunting to ground at each node:

```spice
* RLC Ladder Network - Transient
* Driving with a 1kHz sine, watching the network ring and settle

Vin 1 0 SIN(0 1 1000)

* Series path (top rail)
R1 1 2 100
L1 2 3 10m
R2 3 4 47
L2 4 5 4.7m

* Shunt elements to ground
C1 2 0 100n
C2 3 0 47n
R3 3 0 10k
C3 4 0 22n
C4 5 0 10n

* Termination
R4 5 0 1k

.TRAN 1u 10m
.END
```

---

## Definition of Done

**You have a circuit simulator when:** it parses a netlist of resistors and independent sources, stamps a Modified Nodal Analysis (MNA) matrix, and solves `G·v = i` for the node voltages.

The core idea: Kirchhoff's current law at each node becomes one linear equation, the conductances form a matrix, and the whole circuit collapses into a single linear solve. Voltage sources are the "modified" part — each adds an extra unknown (its branch current) plus a row and column. If a resistor divider prints the voltages you can check by hand, you have it: everything else in SPICE is a loop wrapped around this solve.

- **Floor:** resistors + current sources only — plain nodal analysis, no augmentation.
- **Stretch:** add a diode solved with Newton-Raphson — the leap from linear to nonlinear.

---

## Getting started

### Requirements

- Python 3.14 (uv's default on this machine — no need to pin it explicitly)
- [uv](https://docs.astral.sh/uv/) for environment/dependency management
- [PySpice](https://pyspice.fabrice-salvaire.fr/) for netlist parsing
- [matplotlib](https://matplotlib.org/) (used by `slow.py`)

### Setup

```
uv sync
```

This installs all dependencies from `uv.lock`, including `PySpice` and `matplotlib`.

To add a new dependency manually:

```
uv add <package>
```

### Run it

```
uv run Spice.py
```

This reads `netlist.sp`, parses it with PySpice, builds a circuit object, and prints `"Main all done!"`.

---

## Roadmap

- [x] Initial proof of concept (`slow.py` — RC simulator)
- [x] Netlist parser (PySpice-backed `NetlistParser`)
- [x] Example SPICE netlist (`netlist.sp`)
- [ ] Remove `slow.py`
- [ ] Stamp MNA matrix from parsed netlist elements
- [ ] Solve `G·v = i` for DC operating point
- [ ] Add Non-Linear Elements (diodes, transistors via Newton-Raphson)
- [ ] Transient analysis
