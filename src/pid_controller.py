"""
PID Controller — written from scratch.

Features:
  - Proportional, Integral, Derivative control
  - Actuator saturation (output clamping)
  - Anti-windup (clamping + back-calculation)
  - Derivative filtering (low-pass on d_term)
  - Derivative-on-measurement (avoids setpoint kick)
"""

import numpy as np


class PIDController:
    """A discrete-time PID controller with practical fixes."""

    def __init__(
        self,
        Kp=1.0,
        Ki=0.0,
        Kd=0.0,
        dt=0.001,
        setpoint=0.0,
        output_limits=(None, None),       # (u_min, u_max) for saturation
        anti_windup=True,
        derivative_filter_coeff=0.0,      # N: filter bandwidth  (0 = no filter)
        derivative_on_measurement=False,
    ):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.setpoint = setpoint

        self.output_min, self.output_max = output_limits
        self.anti_windup = anti_windup
        self.N = derivative_filter_coeff
        self.derivative_on_measurement = derivative_on_measurement

        # Internal state
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_measurement = 0.0
        self.prev_derivative = 0.0   # filtered derivative term

    def reset(self):
        """Reset internal state."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_measurement = 0.0
        self.prev_derivative = 0.0

    def compute(self, measurement):
        """
        Compute the control output given the current measurement.

        Returns:
            u         : control output (possibly clamped)
            u_unsat   : control output before saturation
            error     : current error
        """
        error = self.setpoint - measurement

        # --- Proportional term ---
        P = self.Kp * error

        # --- Integral term ---
        self.integral += error * self.dt
        I = self.Ki * self.integral

        # --- Derivative term ---
        if self.derivative_on_measurement:
            # Derivative on measurement avoids setpoint kick
            raw_derivative = -(measurement - self.prev_measurement) / self.dt
        else:
            raw_derivative = (error - self.prev_error) / self.dt

        # Optional first-order low-pass filter on derivative
        if self.N > 0:
            alpha = self.dt * self.N / (1.0 + self.dt * self.N)
            self.prev_derivative = alpha * raw_derivative + (1 - alpha) * self.prev_derivative
            D = self.Kd * self.prev_derivative
        else:
            D = self.Kd * raw_derivative

        # --- Total output ---
        u_unsat = P + I + D

        # --- Actuator saturation ---
        u = u_unsat
        if self.output_max is not None and u > self.output_max:
            u = self.output_max
        if self.output_min is not None and u < self.output_min:
            u = self.output_min

        # --- Anti-windup (back-calculation / clamping) ---
        if self.anti_windup and (u != u_unsat):
            # Undo the last integration step that caused saturation
            self.integral -= error * self.dt

        # --- Update stored states ---
        self.prev_error = error
        self.prev_measurement = measurement

        return u, u_unsat, error

