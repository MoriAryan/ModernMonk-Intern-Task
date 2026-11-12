"""
Experiment 1: Demonstrate individual P, I, D effects on the mass-spring-damper.

Section 5 of the assignment:
  - P-only with at least 4 gain values
  - Show why P alone always has steady-state error (with calculation)
  - PI controller
  - PD controller
  - Show how D reduces overshoot/oscillation
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from pid_controller import PIDController
from plant_models import simulate_mass_spring_damper, compute_metrics
from plot_utils import plot_comparison, plot_step_response, save_fig, FIGURES_DIR
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run():
    dt = 0.001
    t_end = 8.0
    setpoint = 1.0

    print("=" * 60)
    print("EXPERIMENT 1: Individual P, I, D effects")
    print("=" * 60)

    # ---- P-only with varying gains ----
    print("\n--- P-only controller with varying Kp ---")
    kp_values = [10, 50, 100, 200]
    results = []

    for kp in kp_values:
        pid = PIDController(Kp=kp, Ki=0, Kd=0, dt=dt, setpoint=setpoint)
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
        metrics = compute_metrics(t, x, setpoint)
        results.append((t, x, f"Kp={kp}"))

        # Theoretical steady-state error for P-only:
        #   At steady state: u = Kp * e = k * x_ss
        #   x_ss = Kp * setpoint / (Kp + k)
        #   e_ss = setpoint - x_ss = k * setpoint / (Kp + k)
        k_spring = 20.0
        e_ss_theory = k_spring * setpoint / (kp + k_spring)
        x_ss_theory = kp * setpoint / (kp + k_spring)

        rt_str = f"{metrics['rise_time']:.4f}" if metrics['rise_time'] is not None else "N/A"
        print(f"  Kp={kp:4d}: Rise={rt_str}s, "
              f"Overshoot={metrics['overshoot_pct']:.1f}%, "
              f"Settling={metrics['settling_time']:.3f}s, "
              f"SS_Error={metrics['steady_state_error']:.4f}m "
              f"(theory: {e_ss_theory:.4f}m, x_ss_theory: {x_ss_theory:.4f}m)")

    plot_comparison(results, setpoint=setpoint,
                    title="P-only Controller: Effect of Varying Kp",
                    filename="p_only_varying_kp.png")

    # --- Annotated metrics graph for Section 4 ---
    # Use gains that produce visible overshoot to show all four metrics clearly
    print("\n--- Annotated metrics graph (Section 4) ---")
    pid = PIDController(Kp=200, Ki=80, Kd=2, dt=dt, setpoint=setpoint)
    t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
    metrics = compute_metrics(t, x, setpoint)
    print(f"  PID (Kp=200, Ki=80, Kd=2) metrics: {metrics}")

    plot_step_response(t, x, setpoint=setpoint,
                       title="Step Response with Performance Metrics",
                       label="PID (Kp=200, Ki=80, Kd=2)",
                       filename="metrics_annotated.png",
                       show_metrics=True,
                       metrics=metrics)

    # ---- PI controller ----
    print("\n--- PI controller ---")
    pi_results = []
    pi_configs = [
        (50, 10),
        (50, 30),
        (50, 60),
        (100, 30),
    ]
    for kp, ki in pi_configs:
        pid = PIDController(Kp=kp, Ki=ki, Kd=0, dt=dt, setpoint=setpoint)
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
        metrics = compute_metrics(t, x, setpoint)
        pi_results.append((t, x, f"Kp={kp}, Ki={ki}"))
        rt_str = f"{metrics['rise_time']:.4f}" if metrics['rise_time'] is not None else "N/A"
        print(f"  Kp={kp}, Ki={ki}: Rise={rt_str}s, "
              f"Overshoot={metrics['overshoot_pct']:.1f}%, "
              f"Settling={metrics['settling_time']:.3f}s, "
              f"SS_Error={metrics['steady_state_error']:.6f}m")

    plot_comparison(pi_results, setpoint=setpoint,
                    title="PI Controller: Effect of Integral Gain",
                    filename="pi_controller.png")

    # ---- PD controller ----
    print("\n--- PD controller ---")
    pd_results = []
    pd_configs = [
        (200, 0),     # P-only baseline (high Kp shows overshoot)
        (200, 2),
        (200, 5),
        (200, 10),
    ]
    for kp, kd in pd_configs:
        pid = PIDController(Kp=kp, Ki=0, Kd=kd, dt=dt, setpoint=setpoint)
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
        metrics = compute_metrics(t, x, setpoint)
        pd_results.append((t, x, f"Kp={kp}, Kd={kd}"))
        rt_str = f"{metrics['rise_time']:.4f}" if metrics['rise_time'] is not None else "N/A"
        print(f"  Kp={kp}, Kd={kd}: Rise={rt_str}s, "
              f"Overshoot={metrics['overshoot_pct']:.1f}%, "
              f"Settling={metrics['settling_time']:.3f}s, "
              f"SS_Error={metrics['steady_state_error']:.4f}m")

    plot_comparison(pd_results, setpoint=setpoint,
                    title="PD Controller: D Reduces Overshoot",
                    filename="pd_controller.png")

    print("\nExperiment 1 complete.")


if __name__ == "__main__":
    run()
