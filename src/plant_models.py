"""
Plant models and simulation utilities.

System 1: Mass-spring-damper
    m*x'' + c*x' + k*x = u(t)
    With m=1 kg, c=10 N.s/m, k=20 N/m

System 2: Third-order system  G(s) = 1/(s+1)^3
    Expanded: s^3 + 3s^2 + 3s + 1  =>  y''' + 3y'' + 3y' + y = u
"""

import numpy as np


def simulate_mass_spring_damper(
    pid_controller,
    m=1.0,
    c=10.0,
    k=20.0,
    x0=0.0,
    v0=0.0,
    t_end=5.0,
    dt=0.001,
    noise_std=0.0,
):
    """
    Simulate the mass-spring-damper with a PID controller.

    State: [x, v]
    Equation:  m*x'' = u - c*x' - k*x
               x'' = (u - c*v - k*x) / m

    Returns:
        t_arr, x_arr, u_arr, u_unsat_arr, error_arr
    """
    n_steps = int(t_end / dt)
    t_arr = np.linspace(0, t_end, n_steps + 1)
    x_arr = np.zeros(n_steps + 1)
    v_arr = np.zeros(n_steps + 1)
    u_arr = np.zeros(n_steps + 1)
    u_unsat_arr = np.zeros(n_steps + 1)
    error_arr = np.zeros(n_steps + 1)

    x_arr[0] = x0
    v_arr[0] = v0

    rng = np.random.default_rng(42)

    for i in range(n_steps):
        # Measurement with optional noise
        measurement = x_arr[i]
        if noise_std > 0:
            measurement += rng.normal(0, noise_std)

        u, u_unsat, error = pid_controller.compute(measurement)
        u_arr[i] = u
        u_unsat_arr[i] = u_unsat
        error_arr[i] = error

        # Semi-implicit Euler integration of  m*x'' = u - c*v - k*x
        acc = (u - c * v_arr[i] - k * x_arr[i]) / m
        v_arr[i + 1] = v_arr[i] + acc * dt
        x_arr[i + 1] = x_arr[i] + v_arr[i + 1] * dt  # use updated velocity

    # Fill last control values
    u_arr[-1] = u_arr[-2]
    u_unsat_arr[-1] = u_unsat_arr[-2]
    error_arr[-1] = error_arr[-2]

    return t_arr, x_arr, u_arr, u_unsat_arr, error_arr


def simulate_third_order(
    pid_controller,
    t_end=30.0,
    dt=0.001,
):
    """
    Simulate G(s) = 1/(s+1)^3 with PID control.

    State-space form (controllable canonical):
        y''' + 3y'' + 3y' + y = u

    Let x1=y, x2=y', x3=y''
        x1' = x2
        x2' = x3
        x3' = -x1 - 3*x2 - 3*x3 + u

    Returns:
        t_arr, y_arr, u_arr
    """
    n_steps = int(t_end / dt)
    t_arr = np.linspace(0, t_end, n_steps + 1)
    y_arr = np.zeros(n_steps + 1)
    u_arr = np.zeros(n_steps + 1)

    x1, x2, x3 = 0.0, 0.0, 0.0

    for i in range(n_steps):
        u, _, _ = pid_controller.compute(x1)
        u_arr[i] = u

        # Euler integration
        dx1 = x2
        dx2 = x3
        dx3 = -x1 - 3 * x2 - 3 * x3 + u

        x1 += dx1 * dt
        x2 += dx2 * dt
        x3 += dx3 * dt

        y_arr[i + 1] = x1

    u_arr[-1] = u_arr[-2]
    return t_arr, y_arr, u_arr


def compute_metrics(t_arr, y_arr, setpoint=1.0, settling_pct=0.02):
    """
    Compute standard step-response performance metrics.

    Returns dict with:
        rise_time       : time from first 10% to first 90% crossing of setpoint
                          (None if 90% is never reached)
        overshoot_pct   : peak overshoot as percentage of setpoint
        settling_time   : time after which |y - setpoint| < settling_pct * setpoint
                          (None if it never settles, e.g. due to SS error)
        steady_state_error : |setpoint - y_final|  (averaged over last 10%)
        settled         : whether the response actually settled within the band
    """
    y_final = y_arr[-1]

    # Rise time: 10% to 90% of setpoint
    y10 = 0.1 * setpoint
    y90 = 0.9 * setpoint

    t_10 = None
    t_90 = None
    for i in range(len(y_arr)):
        if t_10 is None and y_arr[i] >= y10:
            t_10 = t_arr[i]
        if t_90 is None and y_arr[i] >= y90:
            t_90 = t_arr[i]

    rise_time = (t_90 - t_10) if (t_10 is not None and t_90 is not None) else None

    # Overshoot
    peak = np.max(y_arr)
    if peak > setpoint:
        overshoot_pct = (peak - setpoint) / setpoint * 100
    else:
        overshoot_pct = 0.0

    # Settling time (last time |y - setpoint| exceeds threshold)
    band = settling_pct * setpoint
    settling_time = None
    settled = True
    for i in range(len(y_arr) - 1, -1, -1):
        if abs(y_arr[i] - setpoint) > band:
            settling_time = t_arr[i]
            break
    if settling_time is None:
        settling_time = 0.0
    elif settling_time >= t_arr[-1] - 0.01:
        # Response never actually settled — still outside band at end
        settled = False

    # Steady-state error
    # Average over last 10% of simulation
    tail = int(0.9 * len(y_arr))
    ss_error = abs(setpoint - np.mean(y_arr[tail:]))

    return {
        "rise_time": rise_time,
        "overshoot_pct": overshoot_pct,
        "settling_time": settling_time,
        "steady_state_error": ss_error,
        "settled": settled,
    }
