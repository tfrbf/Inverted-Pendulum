import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from math import pi, sin, cos, pow

# SYSTEM PARAMETERS
g = 9.8   # GRAVITY
L_p = 1.0   # PENDULUM LENGTH (m)
L_a = 1.0   # ARM LENGTH (m)
m1 = 0.5   # PENDULUM MASS (kg)
I_a = 0     # Moment of inertia of the arm
I_p = 0     # Moment of inertia of the PENDULUM
mc = 0           # Location of the center of mass of the pendulum

# SIMULATION PARAMETERS
dt = 0.05
Tmax = 35
t = np.arange(0.0, Tmax, dt)

# INITIAL CONDITIONS
dtheta = .0      # PENDULUM ANGULAR VELOCITY
theta = pi - 0.1   # PWNDULUM INITIAL ANGEL
alpha = .0      # ARM INITIAL ANGEL
x0 = 0          # موقعیت هدف کالسکه
dalpha= -0.05   # ARM INITIAL SPEED
k = 0.08        # ENERGY CONTROL GAIN

# CONTROLLER GAINS
Kp_theta = 50
Kd_theta = 15
Kp_alpha = 3.1
Kd_alpha = 4.8

# وضعیت اولیه
state = np.array([theta, dtheta, alpha, dalpha])
stabilizing = False

# متغیر برای ذخیره نیروی کنترلی
u_values = []

def energy(th, dth):
    return 0.5 * (I_a * pow(alpha,2) + m1 * pow(m1,2) + I_p * pow(dtheta,2)) + (m1 * g * L_p * (cos(theta) - 1))

def isControllable(th, dth):
    return th < pi/9 and abs(energy(th, dth)) < 0.5

def derivatives(state, t):
    global stabilizing
    ds = np.zeros_like(state)
    _theta = state[0]
    _dtheta = state[1]  # سرعت زاویه‌ای
    _alpha = state[2]
    _dalpha = state[3]  # سرعت کالسکه

    # کنترل با توجه به وضعیت پایدارسازی
    if stabilizing or isControllable(_theta, _dtheta):
        stabilizing = True
        u = Kp_theta * _theta + Kd_theta * _dtheta + Kp_alpha * (_alpha - x0) + Kd_alpha * _dalpha
    else:
        E = energy(_theta, _dtheta)
        u = k * E * _dtheta * cos(_theta)

    u_values.append(u)  # ذخیره نیروی کنترلی

    ds[0] = state[1]
    ds[1] = (g * sin(_theta) - u * cos(_theta)) / L_p
    ds[2] = state[3]
    ds[3] = u

    return ds

# شبیه‌سازی
# شبیه‌سازی
print("Integrating...")
solution = integrate.odeint(derivatives, state, t)
print("Done")

# بررسی و تطبیق اندازه u_values و solution
if len(u_values) > len(t):
    u_values = u_values[:len(t)]
elif len(u_values) < len(t):
    t = t[:len(u_values)]

# استخراج مقادیر حالت‌ها از solution
ths = solution[:, 0]
Ys = solution[:, 1]
xs = solution[:, 2]
Zs = solution[:, 3]

# رسم نمودارهای پارامترهای کنترلی
plt.figure(figsize=(12, 10))

# نمودار زاویه پاندول
plt.subplot(3, 2, 1)
plt.plot(t, ths, label="Angle (θ)")
plt.xlabel("Time (s)")
plt.ylabel("θ (rad)")
plt.title("Pendulum Angle (θ) over Time")
plt.legend()

# نمودار سرعت زاویه‌ای
plt.subplot(3, 2, 2)
plt.plot(t, Ys, label="Angular Velocity (θ')", color='orange')
plt.xlabel("Time (s)")
plt.ylabel("θ' (rad/s)")
plt.title("Angular Velocity (θ') over Time")
plt.legend()

# نمودار موقعیت کالسکه
plt.subplot(3, 2, 3)
plt.plot(t, xs, label="Cart Position (x)", color='green')
plt.xlabel("Time (s)")
plt.ylabel("x (m)")
plt.title("Cart Position (x) over Time")
plt.legend()

# نمودار سرعت کالسکه
plt.subplot(3, 2, 4)
plt.plot(t, Zs, label="Cart Velocity (x')", color='red')
plt.xlabel("Time (s)")
plt.ylabel("x' (m/s)")
plt.title("Cart Velocity (x') over Time")
plt.legend()

# نمودار نیروی کنترلی
plt.subplot(3, 2, 5)
plt.plot(t, u_values, label="Control Force (u)", color='purple')
plt.xlabel("Time (s)")
plt.ylabel("u (N)")
plt.title("Control Force (u) over Time")
plt.legend()

plt.tight_layout()
plt.show()


# پارامترهای شبیه‌سازی گرافیکی پاندول
pxs = L_p * np.sin(ths) + xs
pys = L_p * np.cos(ths)

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
    thisx = [xs[i], pxs[i]]
    thisy = [0, pys[i]]
    line.set_data(thisx, thisy)
    time_text.set_text(time_template % (i * dt))
    E = energy(ths[i], Ys[i])
    energy_text.set_text(energy_template % (E))
    patch.set_x(xs[i] - cart_width / 2)
    return line, time_text, energy_text, patch

ani = animation.FuncAnimation(fig, animate, np.arange(1, len(solution)), interval=25, blit=True, init_func=init)

plt.show()
