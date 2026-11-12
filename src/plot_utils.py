"""
Plotting utilities for consistent, publication-quality figures.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Global style
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "font.size": 12,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 1.8,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
})


def save_fig(fig, name):
    """Save figure to the figures directory."""
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_step_response(t, y, setpoint=1.0, title="Step Response", label="Response",
                       filename=None, extra_lines=None, show_metrics=False, metrics=None):
    """Plot a single step response."""
    fig, ax = plt.subplots()
    ax.plot(t, y, label=label, color="steelblue")
    ax.axhline(setpoint, color="red", linestyle="--", alpha=0.7, label="Setpoint")

    if extra_lines:
        colors = ["darkorange", "green", "purple", "brown", "teal"]
        for i, (t2, y2, lbl) in enumerate(extra_lines):
            ax.plot(t2, y2, label=lbl, color=colors[i % len(colors)])

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (m)")
    ax.set_title(title)
    ax.legend()

    if show_metrics and metrics:
        _annotate_metrics(ax, t, y, setpoint, metrics)

    if filename:
        save_fig(fig, filename)
    return fig, ax


def plot_comparison(results, setpoint=1.0, title="Controller Comparison",
                    filename=None):
    """
    Plot multiple step responses on one figure.

    results: list of (t, y, label) tuples
    """
    fig, ax = plt.subplots()
    colors = ["steelblue", "darkorange", "green", "purple", "brown", "teal", "crimson"]

    for i, (t, y, label) in enumerate(results):
        ax.plot(t, y, label=label, color=colors[i % len(colors)])

    ax.axhline(setpoint, color="red", linestyle="--", alpha=0.5, label="Setpoint")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (m)")
    ax.set_title(title)
    ax.legend()

    if filename:
        save_fig(fig, filename)
    return fig, ax


def plot_with_control(t, y, u, setpoint=1.0, title="Response & Control Signal",
                      filename=None):
    """Plot response and control effort on two subplots."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(t, y, label="Position", color="steelblue")
    ax1.axhline(setpoint, color="red", linestyle="--", alpha=0.7, label="Setpoint")
    ax1.set_ylabel("Position (m)")
    ax1.set_title(title)
    ax1.legend()

    ax2.plot(t, u, label="Control Force", color="darkorange")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Force (N)")
    ax2.legend()

    if filename:
        save_fig(fig, filename)
    return fig, (ax1, ax2)


def _annotate_metrics(ax, t, y, setpoint, metrics):
    """Annotate a step response plot with the four metrics."""
    # Rise time
    if metrics["rise_time"] is not None:
        tr = metrics["rise_time"]
        # Find the index closest to 10% crossing
        idx_10 = np.argmax(y >= 0.1 * setpoint)
        idx_90 = np.argmax(y >= 0.9 * setpoint)
        ax.annotate("", xy=(t[idx_90], 0.9 * setpoint), xytext=(t[idx_10], 0.1 * setpoint),
                     arrowprops=dict(arrowstyle="<->", color="green", lw=1.5))
        ax.text((t[idx_10] + t[idx_90]) / 2, 0.5 * setpoint,
                f"Rise time\n{tr:.3f} s", ha="center", fontsize=9, color="green",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # Overshoot
    peak_idx = np.argmax(y)
    peak_val = y[peak_idx]
    if peak_val > setpoint:
        ax.annotate("", xy=(t[peak_idx], peak_val), xytext=(t[peak_idx], setpoint),
                     arrowprops=dict(arrowstyle="<->", color="red", lw=1.5))
        ax.text(t[peak_idx] + 0.05, (peak_val + setpoint) / 2,
                f"Overshoot\n{metrics['overshoot_pct']:.1f}%", fontsize=9, color="red",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # Settling time
    ts = metrics["settling_time"]
    if ts is not None:
        ax.axvline(ts, color="purple", linestyle=":", alpha=0.7)
        ax.text(ts + 0.02, 0.3 * setpoint, f"Settling\n{ts:.2f} s",
                fontsize=9, color="purple",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # 2% band
    band = 0.02 * setpoint
    ax.axhspan(setpoint - band, setpoint + band, alpha=0.1, color="green", label="±2% band")

    # Steady-state error
    sse = metrics["steady_state_error"]
    ax.text(t[-1] * 0.75, y[-1] - 0.08,
            f"SS Error: {sse:.4f} m", fontsize=9, color="blue",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

