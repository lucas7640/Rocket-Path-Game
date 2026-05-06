# 🚀 Rocket Path — Solar System Simulation

A solar system simulation where you can build your own system, watch planets orbit, launch a rocket from any planet, and experiment with different trajectories.

**▶ [Play it in your browser](https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/)** — no install needed.

---

## Play Online (GitHub Pages)

1. Push this repository to GitHub
2. Go to **Settings → Pages**
3. Under *Source*, choose **Deploy from a branch → main → / (root)**
4. Click Save — your game will be live at `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/` within a minute

The simulation runs entirely in the browser. No Python, no installs.

---

## Run Locally (Python / Pygame)

```bash
# Install the only dependency
pip3 install pygame

# Run the simulation (launches from Earth by default)
python3 main.py
```

## Quick Start

```bash
# Install the only dependency
pip3 install pygame

# Run the simulation (launches from Earth by default)
python3 main.py

# Launch from Mars at a 45° angle
python3 main.py --planet Mars --angle 45

# Just watch the planets orbit (no rocket)
python3 main.py --no-rocket

# Speed up time (1 million× real time)
python3 main.py --speed 1000000
```

---

## Project Structure

```
Solar System Simulation/
│
├── main.py                  ← Entry point, CLI flags, simulation loop
│
├── simulation/
│   ├── bodies.py            ← Star, Planet, Rocket classes
│   └── physics.py           ← Gravity engine & integrators (Euler, RK4 stub)
│
├── visuals/
│   └── renderer.py          ← Pygame renderer, coordinate scaling, HUD
│
├── data/
│   └── planets.json         ← Real solar system data (masses, radii, orbits)
│
├── notes/
│   └── physics_notes.md     ← Key formulas: gravity, orbits, trajectories
│
└── assets/                  ← Images, sounds (add here as needed)
```

---

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--planet NAME` | `Earth` | Planet to launch from |
| `--angle DEG` | `0` | Launch angle in degrees (0 = straight up/radial, 90 = prograde) |
| `--no-rocket` | off | Disable rocket, just view the solar system |
| `--speed N` | `86400` | Simulation speed multiplier (86400 = 1 day per second) |

---

## How It Works

**Planets** orbit the star using analytical circular equations — no numerical drift.

**The Rocket** is governed by full N-body Newtonian gravity from every body in the system. The engine applies thrust for a configurable burn time, then the rocket coasts under gravity alone.

**Physics engine:** Forward Euler integration (see `simulation/physics.py`). A Velocity Verlet or RK4 upgrade is stubbed out for higher-accuracy long-duration trajectories.

**Renderer:** Pygame window with auto-scaling so the whole system fits on screen. Rocket trajectory is drawn as a red trail.

---

## Customise Your Solar System

Edit `data/planets.json` to:
- Add or remove planets
- Change masses, orbital radii, or periods
- Adjust colors
- Create entirely fictional systems

---

## Roadmap

- [ ] Custom planet creator (interactive UI)
- [ ] Gravity-assist / slingshot manoeuvres
- [ ] Multiple rockets with different trajectories
- [ ] Velocity Verlet / RK4 integrator
- [ ] Save & replay trajectory
- [ ] Sound effects on launch

---

## Development Resources

The `Resources/` folder contains useful Claude skills for development:

- `skills/code-review.md` — review simulation code
- `skills/debug.md` — debug physics issues
- `skills/test-writer.md` — generate unit tests for the physics engine
- `agents/code-reviewer.md` — automated code review agent

---

## Physics Reference

See [`notes/physics_notes.md`](notes/physics_notes.md) for all key formulas:
gravitational force, orbital velocity, escape velocity, trajectory types, and integrator equations.
