"""
Generate the feedback loop block diagram for the report.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")


def draw_feedback_loop():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1.5, 2.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Box style
    box_style = dict(boxstyle="round,pad=0.4", facecolor="lightblue", edgecolor="black", linewidth=1.5)
    sum_style = dict(boxstyle="circle,pad=0.2", facecolor="lightyellow", edgecolor="black", linewidth=1.5)

    # Summing junction
    ax.text(2, 1, "Σ", fontsize=14, ha="center", va="center",
            bbox=sum_style, fontweight="bold")

    # Controller
    ax.text(4.5, 1, "PID\nController", fontsize=11, ha="center", va="center",
            bbox=box_style)

    # Plant
    ax.text(7, 1, "Plant\n(System)", fontsize=11, ha="center", va="center",
            bbox=box_style)

    # Sensor
    ax.text(5.5, -0.5, "Sensor", fontsize=11, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgreen", edgecolor="black", linewidth=1.5))

    # Arrows
    arrow_props = dict(arrowstyle="-|>", color="black", lw=1.5)

    # Setpoint -> summing junction
    ax.annotate("", xy=(1.6, 1), xytext=(0, 1), arrowprops=arrow_props)
    ax.text(0.8, 1.35, "Setpoint\n(target)", fontsize=9, ha="center", color="darkblue")

    # Summing junction -> Controller
    ax.annotate("", xy=(3.6, 1), xytext=(2.4, 1), arrowprops=arrow_props)
    ax.text(3, 1.35, "Error", fontsize=9, ha="center", color="red")

    # Controller -> Plant
    ax.annotate("", xy=(6.1, 1), xytext=(5.4, 1), arrowprops=arrow_props)
    ax.text(5.75, 1.35, "u(t)", fontsize=9, ha="center", color="darkblue")

    # Plant -> Output
    ax.annotate("", xy=(9.5, 1), xytext=(7.9, 1), arrowprops=arrow_props)
    ax.text(9, 1.35, "Output\n(actual)", fontsize=9, ha="center", color="darkblue")

    # Output -> Sensor (down)
    ax.annotate("", xy=(8.5, -0.5), xytext=(8.5, 0.6),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5, connectionstyle="arc3"))

    # Sensor -> Summing junction (left, below)
    ax.annotate("", xy=(2, 0.6), xytext=(4.6, -0.5),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))
    ax.text(3, -0.3, "Measurement", fontsize=9, ha="center", color="darkgreen")

    # + and - signs at summing junction
    ax.text(1.7, 1.3, "+", fontsize=10, ha="center", color="blue", fontweight="bold")
    ax.text(1.7, 0.6, "−", fontsize=12, ha="center", color="red", fontweight="bold")

    fig.suptitle("Closed-Loop Feedback Control System", fontsize=13, fontweight="bold")
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, "feedback_loop.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


if __name__ == "__main__":
    draw_feedback_loop()

