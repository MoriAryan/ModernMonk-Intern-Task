# Project Write-Up

### Approach

I started with the mass-spring-damper system and implemented a PID controller to understand how each term affects its response. I then ran separate experiments for P, PI, PD and PID control, compared their performance, and explored practical issues such as actuator saturation, sensor noise, derivative kick and sampling rate.

I also tested Ziegler–Nichols tuning on a separate system and adjusted the resulting gains to improve the response.

### What worked and what needed improvement

The P-only experiment was a useful starting point. The block consistently stopped short of the target, and the simulated steady-state error matched the value from the theoretical calculation. This helped validate the system model.

The PI and PID experiments showed how integral control removes steady-state error, while derivative control helps reduce overshoot. The Ziegler–Nichols method also gave a reasonable starting point, although manual tuning improved its response further.

A few things needed extra attention. The P-only response made some performance metrics difficult to interpret, so I used a separate PID configuration for the annotated metrics graph. The low sampling-rate experiment also became unstable with the selected gains and Euler integration method. I had to distinguish this numerical issue from a general limitation of PID control.

### What I would explore next

With more time, I would try a Runge–Kutta integration method, test how the controller handles external disturbances, and implement gain scheduling for changing operating conditions. I would also compare different anti-windup methods and study how time delays affect PID performance.