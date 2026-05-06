# Solar System Simulation — Claude Project Memory

This file is loaded automatically at the start of every session in this project. Keep additions tight and relevant.

---

## What this codebase does

A Python simulation of a customisable solar system where planets orbit a central star and a rocket can be launched from any planet with a configurable angle. The user can experiment with trajectories, observe gravitational effects, and eventually build entirely fictional solar systems.

---

## Architecture

```
main.py  (entry point + simulation loop)
    │
    ├── simulation/
    │       ├── bodies.py     ← Star, Planet, Rocket classes (state + physics props)
    │       └── physics.py    ← Newtonian gravity engine, Euler integrator, RK4 stub
    │
    ├── visuals/
    │       └── renderer.py   ← Pygame window, coordinate scaling, trajectory trail, HUD
    │
    └── data/
            └── planets.json  ← Real solar system data (masses, radii, orbital params, colors)
```

---

## Conventions we actually enforce

- Planets use **analytical circular orbits** (`update_orbit`), not N-body integration — avoids drift
- The **rocket** uses full N-body gravity (attracted by star + all planets)
- All distances in **metres**, velocities in **m/s** — no mixed units anywhere
- Simulation origin is always (0, 0) = centre of the star
- y-axis flipped in renderer (screen y increases downward, simulation y increases upward)
- `bodies.py` owns state; `physics.py` mutates it; `renderer.py` only reads it

---

## Common gotchas

- `python` and `pip` are not available on Lucas's Mac — always use `python3` and `pip3`
- Python version is **3.8** — use `from __future__ import annotations` at the top of any file with modern type hint syntax (`list[x]`, `tuple[x, y]`, etc.)
- The renderer auto-scales to the outermost planet; adding a very distant body will shrink everything else
- Rocket `launch_angle` is relative to the planet's local radial direction, not the global x-axis
- `step_rk4` is a stub — it raises `NotImplementedError`; don't call it yet

---

## Commands that matter

| Command | What it does |
|---|---|
| `python3 main.py` | Run with defaults (launch from Earth, 1 day/sec) |
| `python3 main.py --planet Mars --angle 45` | Launch from Mars at 45° |
| `python3 main.py --no-rocket --speed 1000000` | Just watch orbits, very fast |
| `pip3 install pygame` | Install the only dependency |

---

## Testing strategy

- No formal tests yet — physics formulas can be verified against `notes/physics_notes.md`
- To add tests: use `pytest`, place in a `tests/` folder
- Key things worth unit testing: `gravitational_force`, `escape_velocity`, `orbital_velocity`, `sim_to_px` coordinate conversion

---

## Roadmap (don't implement unless asked)

- Interactive planet creator UI
- Velocity Verlet / RK4 integrator for rocket
- Gravity-assist / slingshot manoeuvres
- Multiple simultaneous rockets
- Save & replay trajectory
- Custom fictional solar systems via JSON

---

## When working on this codebase

- **Plan first.** For physics changes especially, confirm the approach before editing.
- **Keep units consistent.** Everything is SI (metres, kg, seconds). Convert only at the renderer boundary.
- **Don't break the analytical orbit.** Planets must never switch to N-body integration without discussion.
- **Test visually.** Run `main.py` and eyeball the result — that's the primary feedback loop right now.

---

## Out of scope

- Relativistic effects
- 3D rendering (simulation is 2D)
- Real-time multiplayer

---

## Last updated: 2026-05-05 · Maintainer: Lucas
