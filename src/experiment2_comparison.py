"""
Experiment 2: Compare P, PI, PD, PID on one graph and table.

Section 6 of the assignment.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from pid_controller import PIDController
from plant_models import simulate_mass_spring_damper, compute_metrics
from plot_utils import plot_comparison, save_fig, FIGURES_DIR
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run():
    dt = 0.001
    t_end = 8.0
    setpoint = 1.0

    print("=" * 60)
    print("EXPERIMENT 2: P vs PI vs PD vs PID comparison")
    print("=" * 60)

    # Chosen gains (justified in the report)
    configs = {
        "P-only (Kp=100)":   {"Kp": 100, "Ki": 0,   "Kd": 0},
        "PI (Kp=100, Ki=80)": {"Kp": 100, "Ki": 80,  "Kd": 0},
        "PD (Kp=100, Kd=5)": {"Kp": 100, "Ki": 0,   "Kd": 5},
        "PID (Kp=100, Ki=80, Kd=5)": {"Kp": 100, "Ki": 80, "Kd": 5},
    }

    results = []
    all_metrics = {}

    for name, gains in configs.items():
        pid = PIDController(
            Kp=gains["Kp"], Ki=gains["Ki"], Kd=gains["Kd"],
            dt=dt, setpoint=setpoint
        )
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
        metrics = compute_metrics(t, x, setpoint)
        results.append((t, x, name))
        all_metrics[name] = metrics

    # Print table
    print(f"\n{'Controller':<35} {'Rise Time (s)':>13} {'Overshoot (%)':>14} "
          f"{'Settling (s)':>13} {'SS Error (m)':>13}")
    print("-" * 92)
    for name in configs:
        m = all_metrics[name]
        rt = f"{m['rise_time']:.4f}" if m['rise_time'] else "N/A"
        print(f"{name:<35} {rt:>13} {m['overshoot_pct']:>14.2f} "
              f"{m['settling_time']:>13.3f} {m['steady_state_error']:>13.6f}")

    # Comparison plot
    plot_comparison(results, setpoint=setpoint,
                    title="P vs PI vs PD vs PID Controller Comparison",
                    filename="controller_comparison.png")

    # Also make a plot with control effort
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    colors = ["steelblue", "darkorange", "green", "purple"]

    for i, (name, gains) in enumerate(configs.items()):
        pid = PIDController(
            Kp=gains["Kp"], Ki=gains["Ki"], Kd=gains["Kd"],
            dt=dt, setpoint=setpoint
        )
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt, t_end=t_end)
        ax1.plot(t, x, label=name, color=colors[i])
        ax2.plot(t, u, label=name, color=colors[i])

    ax1.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax1.set_ylabel("Position (m)")
    ax1.set_title("Controller Comparison: Response & Control Effort")
    ax1.legend(fontsize=9)

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Control Force (N)")
    ax2.legend(fontsize=9)

    save_fig(fig, "comparison_with_control.png")

    print("\nExperiment 2 complete.")
    return all_metrics


if __name__ == "__main__":
    run()
