"""
main.py — Solar System Simulation entry point.

States
------
CONFIG  : Planets orbit, sidebar fully active, dotted trajectory preview shown.
          Camera is locked to the launch planet — it follows the planet as it
          orbits the Sun.  Click LAUNCH → FLYING.
FLYING  : Camera follows the rocket, angle slider hidden.
          Click RESET → CONFIG.

Controls
--------
  Scroll wheel       Zoom in / out (over the sim area)
  ESC or close       Quit

Usage
-----
  python3 main.py
"""

from __future__ import annotations
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pygame

from simulation.bodies  import Star, Planet, Rocket
from simulation.physics import Physics
from visuals.renderer   import Renderer
from visuals.ui         import ConfigPanel

# ── constants ─────────────────────────────────────────────────────────────────
WIN_W, WIN_H   = 1280, 860
DATA_PATH      = os.path.join(os.path.dirname(__file__), "data", "planets.json")
EARTH_DAY_S    = 86_400.0        # seconds in one Earth day
PREVIEW_STEPS  = 600             # ghost-sim steps for trajectory preview
PREVIEW_DT     = 1_800.0         # 30 minutes per ghost step  (~12.5 days forward)
TRAIL_CAP      = 4_000           # max recorded rocket positions
PLANET_VIEW_RADII = 35.0         # zoom radius (planet radii) for default view


# ── helpers ───────────────────────────────────────────────────────────────────

def load_planets_data() -> tuple:
    """Return (raw star dict, raw planets list) from JSON."""
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data["star"], data["planets"]


def build_system(raw_star: dict, raw_planets: list,
                 cfg: dict) -> tuple:
    """
    Construct live Star and Planet objects from raw data + current panel config.
    Only enabled planets are included.  NASA reference values are passed
    through so the HUD can show the real-world numbers.
    """
    star = Star(
        name   = raw_star["name"],
        mass   = raw_star["mass_kg"],
        radius = raw_star["radius_m"],
        color  = raw_star["color"],
    )
    planets = []
    for idx in cfg["enabled"]:
        pd = raw_planets[idx]
        planets.append(Planet(
            name             = pd["name"],
            mass             = pd["mass_kg"] * cfg["masses"][idx],
            radius           = pd["radius_m"],
            orbital_radius   = pd["orbital_radius_m"],
            orbital_period   = pd["orbital_period_s"],
            color            = pd["color"],
            surface_gravity  = pd["surface_gravity_ms2"],
            escape_velocity       = pd.get("escape_velocity_ms",       0.0),
            low_orbit_velocity    = pd.get("low_orbit_velocity_ms",    0.0),
            heliocentric_velocity = pd.get("heliocentric_velocity_ms", 0.0),
            delta_v_solar_escape  = pd.get("delta_v_solar_escape_ms",  0.0),
        ))
    return star, planets


def get_launch_planet(cfg: dict, planets: list):
    """Return the Planet object the rocket would launch from, or None."""
    if not planets:
        return None
    enabled = cfg["enabled"]
    try:
        local_idx = enabled.index(cfg["launch_idx"])
    except ValueError:
        local_idx = 0
    return planets[local_idx] if 0 <= local_idx < len(planets) else None


def make_preview_rocket(cfg: dict, planets: list) -> Rocket:
    """
    Create a Rocket ready for trajectory prediction — not the live rocket.
    Returns None if no planets are enabled.
    """
    launch_planet = get_launch_planet(cfg, planets)
    if launch_planet is None:
        return None

    r = Rocket()
    r.thrust    = cfg["thrust"]
    r.burn_time = cfg["fuel"]
    r.launch(launch_planet, angle_deg=cfg["angle"])
    return r


def compute_preview(cfg: dict, star, planets: list, physics: Physics) -> list:
    """Return list of [x, y] positions for the dotted preview."""
    ghost = make_preview_rocket(cfg, planets)
    if ghost is None:
        return []
    return physics.predict_trajectory(ghost, star, planets,
                                      n_steps=PREVIEW_STEPS,
                                      dt=PREVIEW_DT)


def snap_camera_to_planet(renderer: Renderer, planet) -> None:
    """Lock zoom + camera onto a planet (used on system / launch-planet change)."""
    if planet is None:
        renderer.snap_camera(0.0, 0.0)
        return
    renderer.fit_to_planet(planet, n_radii=PLANET_VIEW_RADII)
    renderer.snap_camera(planet.position[0], planet.position[1])


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    raw_star, raw_planets = load_planets_data()

    renderer = Renderer(width=WIN_W, height=WIN_H)
    panel    = ConfigPanel(planets_data=raw_planets, screen_h=WIN_H)

    # ── initial build ─────────────────────────────────────────────────
    cfg             = panel.get_config()
    star, planets   = build_system(raw_star, raw_planets, cfg)
    physics         = Physics([star] + planets)

    launch_planet = get_launch_planet(cfg, planets)
    snap_camera_to_planet(renderer, launch_planet)

    preview_pts: list = compute_preview(cfg, star, planets, physics)

    # ── simulation state ──────────────────────────────────────────────
    state         = "CONFIG"   # "CONFIG" or "FLYING"
    rocket: Rocket = None
    sim_days       = 0.0

    # preview is recomputed every N frames so it tracks planet movement
    preview_frame  = 0
    PREVIEW_EVERY  = 20   # frames between preview recomputes in CONFIG

    print("Solar System Simulation running.")
    print("  Scroll over the sim to zoom  |  ESC to quit")
    print("  Configure your system in the left panel, then click LAUNCH.")

    running = True
    while running:
        # ── time step ──────────────────────────────────────────────
        cfg       = panel.get_config()
        dt_real   = renderer.clock.get_time() / 1000.0    # actual frame time (s)
        dt_real   = min(dt_real, 0.05)                    # cap at 50 ms
        dt_sim    = dt_real * cfg["days_per_sec"] * EARTH_DAY_S

        # ── events ─────────────────────────────────────────────────
        events = pygame.event.get()
        for event in events:
            r_actions = renderer.process_event(event)
            if "quit" in r_actions:
                running = False

            prev_launch_idx = cfg["launch_idx"]
            p_changes = panel.handle_event(event, launched=(state == "FLYING"))

            if "rebuild" in p_changes:
                cfg           = panel.get_config()
                star, planets = build_system(raw_star, raw_planets, cfg)
                physics       = Physics([star] + planets)
                # re-lock camera to (possibly new) launch planet
                snap_camera_to_planet(renderer, get_launch_planet(cfg, planets))
                preview_pts   = compute_preview(cfg, star, planets, physics)

            if "trajectory" in p_changes:
                cfg = panel.get_config()
                # if launch planet changed, also re-snap the camera/zoom
                if cfg["launch_idx"] != prev_launch_idx and state == "CONFIG":
                    snap_camera_to_planet(renderer,
                                          get_launch_planet(cfg, planets))
                preview_pts = compute_preview(cfg, star, planets, physics)

            if "launch" in p_changes and state == "CONFIG":
                cfg    = panel.get_config()
                rocket = Rocket()
                rocket.thrust    = cfg["thrust"]
                rocket.burn_time = cfg["fuel"]

                launch_planet = get_launch_planet(cfg, planets)
                if launch_planet is None:
                    continue

                rocket.launch(launch_planet, angle_deg=cfg["angle"])
                v_esc  = physics.escape_velocity(launch_planet)
                cap    = physics.delta_v_capacity(rocket.thrust,
                                                  rocket.burn_time,
                                                  rocket.mass)
                tclass = physics.classify_launch(rocket, launch_planet, star)
                print(f"Launched from {launch_planet.name} at {cfg['angle']:.0f}°")
                print(f"  Escape velocity: {v_esc/1000:.2f} km/s")
                print(f"  Δv capacity:     {cap/1000:.2f} km/s")
                print(f"  Trajectory:      {tclass}")
                state = "FLYING"

            if "reset" in p_changes:
                rocket    = None
                sim_days  = 0.0
                state     = "CONFIG"
                cfg           = panel.get_config()
                star, planets = build_system(raw_star, raw_planets, cfg)
                physics       = Physics([star] + planets)
                snap_camera_to_planet(renderer, get_launch_planet(cfg, planets))
                preview_pts = compute_preview(cfg, star, planets, physics)
                print("Simulation reset.")

        # ── physics step ───────────────────────────────────────────
        physics.step_euler(dt_sim, star, planets,
                           rocket if state == "FLYING" else None)
        sim_days += dt_sim / EARTH_DAY_S

        # cap trajectory trail length
        if rocket and len(rocket.trajectory) > TRAIL_CAP:
            rocket.trajectory = rocket.trajectory[::2]

        # ── camera ─────────────────────────────────────────────────
        if state == "FLYING" and rocket:
            renderer.set_camera_target(rocket.position[0], rocket.position[1])
        elif state == "CONFIG":
            lp = get_launch_planet(cfg, planets)
            if lp is not None:
                renderer.set_camera_target(lp.position[0], lp.position[1])
            else:
                renderer.set_camera_target(0.0, 0.0)
        else:
            renderer.set_camera_target(0.0, 0.0)

        # ── preview recompute (CONFIG, periodic) ────────────────────
        if state == "CONFIG":
            preview_frame += 1
            if preview_frame >= PREVIEW_EVERY:
                preview_frame = 0
                cfg         = panel.get_config()
                preview_pts = compute_preview(cfg, star, planets, physics)

        # ── draw ───────────────────────────────────────────────────
        renderer.clear()

        # orbit rings
        for planet in planets:
            renderer.draw_orbit_ring(planet)

        # star
        renderer.draw_body(star, min_r_px=8)

        # planets
        for planet in planets:
            renderer.draw_body(planet)

        # trajectory preview (CONFIG only)
        if state == "CONFIG" and preview_pts:
            renderer.draw_trajectory_preview(preview_pts)

        # rocket + trail (FLYING only)
        if state == "FLYING" and rocket:
            renderer.draw_trajectory(rocket)
            renderer.draw_body(rocket, min_r_px=4)
            launch_planet = next(
                (p for p in planets if p.name == rocket.launch_planet_name), None
            )
            tclass = (physics.classify_launch(rocket, launch_planet, star)
                      if launch_planet else "")
            renderer.draw_rocket_hud(rocket,
                                     planet=launch_planet,
                                     star=star,
                                     physics=physics,
                                     trajectory_class=tclass)

        # NASA-reference launch HUD (CONFIG only)
        if state == "CONFIG":
            lp = get_launch_planet(cfg, planets)
            if lp is not None:
                # ghost rocket for classification
                rcfg = make_preview_rocket(cfg, planets)
                tclass = (physics.classify_launch(rcfg, lp, star)
                          if rcfg is not None else "")
                renderer.draw_launch_hud(lp, star, physics, cfg, tclass)

        # speed label (top-right)
        speed_label = f"{cfg['days_per_sec']:.1f} days/s"
        renderer.draw_speed_overlay(speed_label)

        # panel (draws itself over the left 280 px)
        panel.draw(renderer.screen, renderer.font,
                   elapsed_days=sim_days,
                   launched=(state == "FLYING"))

        renderer.flip(fps=60)

    renderer.quit_pygame()
    print(f"Simulation ended.  Elapsed: {sim_days:.1f} Earth days.")


if __name__ == "__main__":
    main()
