"""
Experiment 4: Ziegler-Nichols tuning on G(s) = 1/(s+1)^3

Section 8 of the assignment:
  - Describe manual tuning steps
  - Find ultimate gain Ku and ultimate period Tu
  - Apply ZN recipe table
  - Plot result and improve
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from pid_controller import PIDController
from plant_models import simulate_third_order, compute_metrics
from plot_utils import save_fig, FIGURES_DIR
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_ultimate_gain(dt=0.001, t_end=60.0):
    """
    Find the ultimate gain Ku for G(s)=1/(s+1)^3.

    Theoretical: The system 1/(s+1)^3 has phase = -180° at w where
    3*arctan(w) = pi, so w = tan(pi/3) = sqrt(3).
    |G(jw)| = 1/|jw+1|^3 = 1/(1+w^2)^(3/2) = 1/(1+3)^(3/2) = 1/8
    So Ku = 8, Tu = 2*pi/sqrt(3) ≈ 3.628 s
    """
    Ku_theory = 8.0
    Tu_theory = 2 * np.pi / np.sqrt(3)

    print(f"  Theoretical: Ku = {Ku_theory:.1f}, Tu = {Tu_theory:.3f} s")

    # Verify by simulation: use P-only with increasing gain
    print("\n  Searching for sustained oscillation...")
    print("  (Comparing oscillation amplitude in early vs late portion of simulation)")
    kp_test_values = [2, 4, 6, 7, 7.5, 7.9, 8.0, 8.1, 8.5]
    oscillation_results = []

    for kp in kp_test_values:
        pid = PIDController(Kp=kp, Ki=0, Kd=0, dt=dt, setpoint=1.0)
        t, y, u = simulate_third_order(pid, t_end=t_end, dt=dt)

        # Compare amplitude in two windows to determine growth/decay
        mid = len(y) // 2
        quarter3 = 3 * len(y) // 4

        y_early = y[mid:quarter3]
        y_late = y[quarter3:]
        amp_early = (np.max(y_early) - np.min(y_early)) / 2
        amp_late = (np.max(y_late) - np.min(y_late)) / 2

        oscillation_results.append((kp, amp_late, amp_early))

        if amp_late < 0.005:
            status = "decaying (settled)"
        elif amp_late > amp_early * 1.05:
            status = "growing"
        elif amp_late < amp_early * 0.95:
            status = "slowly decaying"
        else:
            status = "~sustained (marginal)"

        print(f"    Kp={kp:.1f}: early amp={amp_early:.4f}, late amp={amp_late:.4f} ({status})")

    # Plot the search
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True)
    for i, kp in enumerate(kp_test_values):
        ax = axes[i // 3][i % 3]
        pid = PIDController(Kp=kp, Ki=0, Kd=0, dt=dt, setpoint=1.0)
        t, y, u = simulate_third_order(pid, t_end=t_end, dt=dt)
        ax.plot(t, y, linewidth=0.8)
        ax.axhline(1.0, color="red", linestyle="--", alpha=0.3)
        ax.set_title(f"Kp={kp}", fontsize=10)
        ax.set_ylim(-0.5, 2.5)
        if i // 3 == 2:
            ax.set_xlabel("Time (s)")
        if i % 3 == 0:
            ax.set_ylabel("Output")

    fig.suptitle("Finding Ultimate Gain Ku: P-only on 1/(s+1)³", fontsize=13)
    plt.tight_layout()
    save_fig(fig, "zn_ultimate_search.png")

    return Ku_theory, Tu_theory


def run():
    dt = 0.001
    t_end = 40.0
    setpoint = 1.0

    print("=" * 60)
    print("EXPERIMENT 4: Ziegler-Nichols tuning")
    print("=" * 60)

    # Step 1: Find Ku and Tu
    Ku, Tu = find_ultimate_gain(dt=dt)

    # Step 2: Apply ZN recipe
    print(f"\n--- Ziegler-Nichols recipe (Ku={Ku}, Tu={Tu:.3f}s) ---")

    zn_configs = {
        "P":   {"Kp": 0.5 * Ku, "Ki": 0.0, "Kd": 0.0},
        "PI":  {"Kp": 0.45 * Ku, "Ki": 0.45 * Ku / (Tu / 1.2), "Kd": 0.0},
        "PID": {"Kp": 0.6 * Ku, "Ki": 0.6 * Ku / (Tu / 2), "Kd": 0.6 * Ku * Tu / 8},
    }

    # Ti = Tu/2, Td = Tu/8 for PID
    Ti = Tu / 2
    Td = Tu / 8
    print(f"  PID: Kp = 0.6*Ku = {0.6*Ku:.2f}")
    print(f"       Ti = Tu/2 = {Ti:.3f} s  =>  Ki = Kp/Ti = {0.6*Ku/Ti:.2f}")
    print(f"       Td = Tu/8 = {Td:.3f} s  =>  Kd = Kp*Td = {0.6*Ku*Td:.2f}")

    for name, gains in zn_configs.items():
        print(f"  ZN-{name}: Kp={gains['Kp']:.2f}, Ki={gains['Ki']:.2f}, Kd={gains['Kd']:.2f}")

    # Step 3: Simulate all ZN configs
    results = []
    all_metrics = {}

    for name, gains in zn_configs.items():
        pid = PIDController(
            Kp=gains["Kp"], Ki=gains["Ki"], Kd=gains["Kd"],
            dt=dt, setpoint=setpoint
        )
        t, y, u = simulate_third_order(pid, t_end=t_end, dt=dt)
        metrics = compute_metrics(t, y, setpoint)
        results.append((t, y, f"ZN-{name}"))
        all_metrics[f"ZN-{name}"] = metrics

    # Plot ZN results
    fig, ax = plt.subplots()
    colors = ["steelblue", "darkorange", "green"]
    for i, (t, y, label) in enumerate(results):
        ax.plot(t, y, label=label, color=colors[i])
    ax.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Output")
    ax.set_title("Ziegler-Nichols Tuned Controllers on 1/(s+1)³")
    ax.legend()
    save_fig(fig, "zn_tuned.png")

    # Print table
    print(f"\n{'Controller':<15} {'Rise Time (s)':>13} {'Overshoot (%)':>14} "
          f"{'Settling (s)':>13} {'SS Error':>13}")
    print("-" * 72)
    for name in all_metrics:
        m = all_metrics[name]
        rt = f"{m['rise_time']:.3f}" if m['rise_time'] else "N/A"
        print(f"{name:<15} {rt:>13} {m['overshoot_pct']:>14.2f} "
              f"{m['settling_time']:>13.3f} {m['steady_state_error']:>13.6f}")

    # Step 4: Improve the ZN-PID result
    print("\n--- Improving ZN-PID ---")

    # ZN-PID typically gives ~25% overshoot. Reduce it.
    zn_pid = zn_configs["PID"]
    improved_configs = {
        "ZN-PID (original)": zn_pid.copy(),
        "Improved: lower Ki": {"Kp": zn_pid["Kp"], "Ki": zn_pid["Ki"] * 0.5, "Kd": zn_pid["Kd"]},
        "Improved: more Kd":  {"Kp": zn_pid["Kp"], "Ki": zn_pid["Ki"] * 0.5, "Kd": zn_pid["Kd"] * 2},
        "Improved: balanced":  {"Kp": zn_pid["Kp"] * 0.8, "Ki": zn_pid["Ki"] * 0.4, "Kd": zn_pid["Kd"] * 2.5},
    }

    improved_results = []
    improved_metrics = {}

    for name, gains in improved_configs.items():
        pid = PIDController(
            Kp=gains["Kp"], Ki=gains["Ki"], Kd=gains["Kd"],
            dt=dt, setpoint=setpoint
        )
        t, y, u = simulate_third_order(pid, t_end=t_end, dt=dt)
        metrics = compute_metrics(t, y, setpoint)
        improved_results.append((t, y, name))
        improved_metrics[name] = metrics
        print(f"  {name}: Kp={gains['Kp']:.2f}, Ki={gains['Ki']:.2f}, Kd={gains['Kd']:.2f} "
              f"=> OS={metrics['overshoot_pct']:.1f}%, Ts={metrics['settling_time']:.2f}s")

    # Plot improved
    fig, ax = plt.subplots()
    colors = ["steelblue", "darkorange", "green", "purple"]
    for i, (t, y, label) in enumerate(improved_results):
        ax.plot(t, y, label=label, color=colors[i])
    ax.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Output")
    ax.set_title("Improving the Ziegler-Nichols PID on 1/(s+1)³")
    ax.legend(fontsize=9)
    save_fig(fig, "zn_improved.png")

    print("\nExperiment 4 complete.")


if __name__ == "__main__":
    run()

