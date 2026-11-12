"""
Run all experiments and generate all figures.
Master script for reproducibility.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("PID Control Assignment - Generating All Figures")
print("=" * 60)

# Import and run all experiments
import experiment1_individual
import experiment2_comparison
import experiment3_problems
import experiment4_ziegler_nichols

print("\n\n")
experiment1_individual.run()

print("\n\n")
experiment2_comparison.run()

print("\n\n")
experiment3_problems.run()

print("\n\n")
experiment4_ziegler_nichols.run()

# List all generated figures
figures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
print("\n\n" + "=" * 60)
print("ALL GENERATED FIGURES:")
print("=" * 60)
for f in sorted(os.listdir(figures_dir)):
    if f.endswith(".png"):
        fpath = os.path.join(figures_dir, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  {f} ({size_kb:.0f} KB)")

print("\nAll experiments complete!")

