"""
Experiment 3: Real-world problems and their fixes.

Section 7 of the assignment:
  (a) Actuator saturation & integral windup (max 30 N)
  (b) Noisy sensor (±1 mm) making D jumpy
  (c) Setpoint kick (derivative spike on step change)
  (d) Effect of slow update rate
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from pid_controller import PIDController
from plant_models import simulate_mass_spring_damper, compute_metrics
from plot_utils import save_fig, FIGURES_DIR
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run():
    dt = 0.001
    t_end = 8.0
    setpoint = 1.0

    print("=" * 60)
    print("EXPERIMENT 3: Real-world problems and fixes")
    print("=" * 60)

    # ---- (a) Actuator saturation & integral windup ----
    print("\n--- (a) Actuator saturation & integral windup ---")

    # Without saturation (unlimited)
    pid_unlimited = PIDController(Kp=100, Ki=80, Kd=5, dt=dt, setpoint=setpoint)
    t1, x1, u1, _, _ = simulate_mass_spring_damper(pid_unlimited, dt=dt, t_end=t_end)

    # With saturation, NO anti-windup
    pid_sat_no_aw = PIDController(Kp=100, Ki=80, Kd=5, dt=dt, setpoint=setpoint,
                                   output_limits=(-30, 30), anti_windup=False)
    t2, x2, u2, u2_unsat, _ = simulate_mass_spring_damper(pid_sat_no_aw, dt=dt, t_end=t_end)

    # With saturation AND anti-windup
    pid_sat_aw = PIDController(Kp=100, Ki=80, Kd=5, dt=dt, setpoint=setpoint,
                                output_limits=(-30, 30), anti_windup=True)
    t3, x3, u3, _, _ = simulate_mass_spring_damper(pid_sat_aw, dt=dt, t_end=t_end)

    m1 = compute_metrics(t1, x1, setpoint)
    m2 = compute_metrics(t2, x2, setpoint)
    m3 = compute_metrics(t3, x3, setpoint)
    print(f"  Unlimited:           Overshoot={m1['overshoot_pct']:.1f}%, Settling={m1['settling_time']:.3f}s")
    print(f"  Saturated, no AW:    Overshoot={m2['overshoot_pct']:.1f}%, Settling={m2['settling_time']:.3f}s")
    print(f"  Saturated, with AW:  Overshoot={m3['overshoot_pct']:.1f}%, Settling={m3['settling_time']:.3f}s")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(t1, x1, label="Unlimited force", color="steelblue")
    ax1.plot(t2, x2, label="Saturated ±30N, no anti-windup", color="darkorange")
    ax1.plot(t3, x3, label="Saturated ±30N, with anti-windup", color="green")
    ax1.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax1.set_ylabel("Position (m)")
    ax1.set_title("Actuator Saturation & Integral Windup")
    ax1.legend(fontsize=9)

    ax2.plot(t1, u1, label="Unlimited", color="steelblue", alpha=0.7)
    ax2.plot(t2, u2, label="Saturated, no AW", color="darkorange", alpha=0.7)
    ax2.plot(t3, u3, label="Saturated, with AW", color="green", alpha=0.7)
    ax2.axhline(30, color="gray", linestyle=":", alpha=0.5)
    ax2.axhline(-30, color="gray", linestyle=":", alpha=0.5)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Control Force (N)")
    ax2.legend(fontsize=9)
    save_fig(fig, "windup_problem.png")

    # ---- (b) Noisy sensor making D jumpy ----
    print("\n--- (b) Noisy sensor ±1mm ---")

    # Without noise
    pid_clean = PIDController(Kp=100, Ki=50, Kd=5, dt=dt, setpoint=setpoint)
    t_c, x_c, u_c, _, _ = simulate_mass_spring_damper(pid_clean, dt=dt, t_end=t_end, noise_std=0.0)

    # With noise, no filter
    pid_noisy = PIDController(Kp=100, Ki=50, Kd=5, dt=dt, setpoint=setpoint)
    t_n, x_n, u_n, _, _ = simulate_mass_spring_damper(pid_noisy, dt=dt, t_end=t_end, noise_std=0.001)

    # With noise AND derivative filter
    pid_filtered = PIDController(Kp=100, Ki=50, Kd=5, dt=dt, setpoint=setpoint,
                                  derivative_filter_coeff=20)
    t_f, x_f, u_f, _, _ = simulate_mass_spring_damper(pid_filtered, dt=dt, t_end=t_end, noise_std=0.001)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(t_c, x_c, label="Clean sensor", color="steelblue")
    ax1.plot(t_n, x_n, label="Noisy sensor (±1mm)", color="darkorange", alpha=0.7)
    ax1.plot(t_f, x_f, label="Noisy + D filter (N=20)", color="green")
    ax1.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax1.set_ylabel("Position (m)")
    ax1.set_title("Sensor Noise & Derivative Filtering")
    ax1.legend(fontsize=9)

    ax2.plot(t_c, u_c, label="Clean", color="steelblue", alpha=0.5)
    ax2.plot(t_n, u_n, label="Noisy, no filter", color="darkorange", alpha=0.3)
    ax2.plot(t_f, u_f, label="Noisy + filtered", color="green", alpha=0.7)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Control Force (N)")
    ax2.legend(fontsize=9)
    save_fig(fig, "noise_problem.png")

    # ---- (c) Derivative kick ----
    print("\n--- (c) Derivative kick (setpoint step) ---")

    # Standard derivative on error
    pid_kick = PIDController(Kp=100, Ki=50, Kd=10, dt=dt, setpoint=setpoint,
                              derivative_on_measurement=False)
    t_k, x_k, u_k, _, _ = simulate_mass_spring_damper(pid_kick, dt=dt, t_end=t_end)

    # Derivative on measurement
    pid_no_kick = PIDController(Kp=100, Ki=50, Kd=10, dt=dt, setpoint=setpoint,
                                 derivative_on_measurement=True)
    t_nk, x_nk, u_nk, _, _ = simulate_mass_spring_damper(pid_no_kick, dt=dt, t_end=t_end)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(t_k, x_k, label="D on error (kick)", color="darkorange")
    ax1.plot(t_nk, x_nk, label="D on measurement (no kick)", color="green")
    ax1.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax1.set_ylabel("Position (m)")
    ax1.set_title("Derivative Kick: D on Error vs D on Measurement")
    ax1.legend(fontsize=9)

    # Focus on the control signal in the first 0.05s
    ax2.plot(t_k, u_k, label="D on error", color="darkorange")
    ax2.plot(t_nk, u_nk, label="D on measurement", color="green")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Control Force (N)")
    ax2.set_xlim(0, 0.5)
    ax2.legend(fontsize=9)
    ax2.set_title("Control Signal Detail (first 0.5s)")
    save_fig(fig, "derivative_kick.png")

    # ---- (d) Slow update rate ----
    print("\n--- (d) Effect of slow update rate ---")

    dt_values = [0.001, 0.01, 0.05, 0.1]
    results = []

    for dt_val in dt_values:
        pid = PIDController(Kp=100, Ki=50, Kd=5, dt=dt_val, setpoint=setpoint)
        t, x, u, _, _ = simulate_mass_spring_damper(pid, dt=dt_val, t_end=t_end)
        metrics = compute_metrics(t, x, setpoint)
        results.append((t, x, f"dt={dt_val}s ({int(1/dt_val)} Hz)"))
        print(f"  dt={dt_val}s: Overshoot={metrics['overshoot_pct']:.1f}%, "
              f"Settling={metrics['settling_time']:.3f}s, "
              f"SS_Error={metrics['steady_state_error']:.4f}m")

    fig, ax = plt.subplots()
    colors = ["steelblue", "darkorange", "green", "purple"]
    for i, (t, x, label) in enumerate(results):
        ax.plot(t, x, label=label, color=colors[i])
    ax.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (m)")
    ax.set_title("Effect of Update Rate on PID Performance")
    ax.legend()
    ax.set_ylim(-0.5, 2.5)  # Clip to show the instability without ruining scale
    save_fig(fig, "update_rate.png")

    print("\nExperiment 3 complete.")


if __name__ == "__main__":
    run()
