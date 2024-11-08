# import libraries
import numpy as np
from scipy import optimize, constants
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from math import pi, sin, cos, pow


# system parameters
g   = constants.g      # gravity
L_p = 0.30              # pendulum length (m)
L_a = 0.38             # arm length (m)
m_p = 0.5              # pendulum mass (kg)
m_a = 0.6              # arm mass
I_a = 0.0025           # Moment of inertia of the arm
I_p = 0.006            # Moment of inertia of the pendulum
mc  = 0.15             # Location of the center of mass of the pendulum

# simulation parameters
dt = 0.05
Tmax = 35
t = np.arange(0.0, Tmax, dt)

# initail condition
theta = pi - 0.1      # pendulum initial angel
dtheta = .0           # pendulum initial speed
alpha = .0            # arm initial angle
x0 = 0                # موقعیت هدف کالسکه
dalpha= -0.05         # arm initial speed
k = 0.4               # energy control gain

# PID controller gains (Based on ACO, beta =1)
Kp_theta = 4.091
Kd_theta = 0.350
Kp_alpha = 0.125
Kd_alpha = 0.281

# creating initial state
state = np.array([theta, dtheta, alpha, dalpha])
stabilizing = False

# saving force control values
u_values = []

# energy calculation
def energy(th, dth): 
    return 0.5 * (I_a * pow(alpha,2) + m_p * pow(m_p,2) + I_p * pow(dtheta,2)) + (m_p * g * L_p * (cos(theta) - 1))

# siwtch for control or swing up mode
def isControllable(th, dth):
    return th < pi/9 and abs(energy(th, dth)) < 0.5


def derivatives(state, t):
    global stabilizing
    ds = np.zeros_like(state) #?
    _theta  = state[0]  # pendulum angle
    _dtheta = state[1]  # pendulum velocity
    _alpha  = state[2]  # arm angle
    _dalpha = state[3]  # arm velovity

    # control switch based on energy
    if stabilizing or isControllable(_theta, _dtheta):
        stabilizing = True
        u = Kp_theta * _theta + Kd_theta * _dtheta + Kp_alpha * (_alpha - x0) + Kd_alpha * _dalpha #?
    else:
        E = energy(_theta, _dtheta)
        u = k * E * _dtheta * cos(_theta)

    u_values.append(u)  

    ds[0] = state[1]
    ds[1] = (g * sin(_theta) - u * cos(_theta)) / L_p
    ds[2] = state[3]
    ds[3] = u

    return ds #?

# simulation
print("Integrating...")
solution = integrate.odeint(derivatives, state, t)
print("Done")

# array size check for solution and u
if len(u_values) > len(t):
    u_values = u_values[:len(t)]
elif len(u_values) < len(t):
    t = t[:len(u_values)]

# state variebles from ODE solution
theta_s  = solution[:, 0]
dtheta_s = solution[:, 1]
alpha_s  = solution[:, 2]
dalpha_s = solution[:, 3]


plt.figure(figsize=(12, 12))

# pendulum angle plot
plt.subplot(3, 2, 1)
plt.plot(t, theta_s, label="Angle (θ)")
plt.xlabel("Time (s)")
plt.ylabel("θ (rad)")
plt.title("Pendulum Angle (θ) over Time")
plt.grid()
plt.legend()

# pendulum velocity plot
plt.subplot(3, 2, 2)
plt.plot(t, dtheta_s, label="Angular Velocity (θ')", color='orange')
plt.xlabel("Time (s)")
plt.ylabel("θ' (rad/s)")
plt.title("Angular Velocity (θ') over Time")
plt.grid()
plt.legend()

# arm position plot
plt.subplot(3, 2, 3)
plt.plot(t, alpha_s, label="Cart Position (x)", color='green')
plt.xlabel("Time (s)")
plt.ylabel("x (m)")
plt.title("Cart Position (x) over Time")
plt.grid()
plt.legend()

# arm velocity 
plt.subplot(3, 2, 4)
plt.plot(t, dalpha_s, label="Cart Velocity (x')", color='red')
plt.xlabel("Time (s)")
plt.ylabel("x' (m/s)")
plt.title("Cart Velocity (x') over Time")
plt.legend()
plt.grid()

# control force plot
plt.subplot(3, 2, 5)
plt.plot(t, u_values, label="Control Force (u)", color='purple')
plt.xlabel("Time (s)")
plt.ylabel("u (N)")
plt.title("Control Force (u) over Time")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()


# پارامترهای شبیه‌سازی گرافیکی پاندول
pxs = L_p * np.sin(theta_s) + alpha_s
pys = L_p * np.cos(theta_s)

fig = plt.figure()
ax = fig.add_subplot(111, autoscale_on=False, xlim=(-1.5, 1.5), ylim=(-1.2, 1.2))
ax.set_aspect('equal')
ax.grid()

patch = ax.add_patch(Rectangle((0, 0), 0, 0, linewidth=1, edgecolor='k', facecolor='g'))
line, = ax.plot([], [], 'o-', lw=2)
time_template = 'time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

energy_template = 'E = %.3f J'
energy_text = ax.text(0.05, 0.85, '', transform=ax.transAxes)

cart_width = 0.3
cart_height = 0.2

def init():
    line.set_data([], [])
    time_text.set_text('')
    energy_text.set_text('')
    patch.set_xy((-cart_width / 2, -cart_height / 2))
    patch.set_width(cart_width)
    patch.set_height(cart_height)
    return line, time_text, energy_text, patch

def animate(i):
    thisx = [alpha_s[i], pxs[i]]
    thisy = [0, pys[i]]
    line.set_data(thisx, thisy)
    time_text.set_text(time_template % (i * dt))
    E = energy(theta_s[i], dtheta_s[i])
    energy_text.set_text(energy_template % (E))
    patch.set_x(alpha_s[i] - cart_width / 2)
    return line, time_text, energy_text, patch

ani = animation.FuncAnimation(fig, animate, np.arange(1, len(solution)), interval=25, blit=True, init_func=init)

plt.show()
