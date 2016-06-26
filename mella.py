from dolfin import *

# Form compiler options
parameters["form_compiler"]["cpp_optimize"] = True
parameters["form_compiler"]["optimize"] = True

def update(u, u0, v0, a0, beta, gamma, dt):
    """Update fields at the end of each time step."""

    # Get vectors (references)
    u_vec, u0_vec  = u.vector(), u0.vector()
    v0_vec, a0_vec = v0.vector(), a0.vector()

    # Update acceleration and velocity

    # a = 1/(2*beta)*((u - u0 - v0*dt)/(0.5*dt*dt) - (1-2*beta)*a0)
    a_vec = (1.0/(2.0*beta))*( (u_vec - u0_vec - v0_vec*dt)/(0.5*dt*dt) - (1.0-2.0*beta)*a0_vec )

    # v = dt * ((1-gamma)*a0 + gamma*a) + v0
    v_vec = dt*((1.0-gamma)*a0_vec + gamma*a_vec) + v0_vec

    # Update (u0 <- u0)
    v0.vector()[:], a0.vector()[:] = v_vec, a_vec
    u0.vector()[:] = u.vector()


# Define Mesh
n  = 100
mesh = UnitSquareMesh(n, n, "crossed")

# Function space, Test and Trial functions
V = FunctionSpace(mesh, "CG", 1)
u = TrialFunction(V)
w = TestFunction(V)

# Functions from previous time step (displacement, velocity, acceleration)
u0 = Function(V)
v0 = Function(V)
a0 = Function(V)

# Newmark scheme parameters and time-step
beta  = 0.25
gamma = 0.50
t  = 0.0
dt = 1.0/64.0
T  = 364.0*dt

# Elasticity parameters
E   = 2.50
rho = 1.00               
nu  = 0.25
mu    = E / (2.0*(1.0 + nu))
lmbda = E*nu / ((1.0 + nu)*(1.0 - 2.0*nu))          
c     = pow(mu/rho, 0.5)                                


# Aceleration
def ddot_u(u):
  return ((u - u0 - dt*v0)/(beta*dt*dt) - a0*(1 - 2*beta)/(2*beta))

# Initial conditions (this can be calculated using the Newmar scheme!) and excitation
zeros = Expression('0.0')
ui = Expression('-40.*sin(pi*x[0])*sin(pi*x[1])*exp(-1000.*(pow(x[0]-0.5,2)+pow(x[1]-0.5,2) - c*t))', c=c, t=0.0)
u0 = interpolate(ui, V)
v0 = interpolate(zeros, V)
a0 = interpolate(zeros, V)

# Boundary conditions
def boundaries(x, on_boundary):
    return on_boundary

bc = DirichletBC(V, Constant(0.0), boundaries)

# Define variational problem
F = ddot_u(u)*w*dx + c**2*inner(grad(u), grad(w))*dx
a = lhs(F)
L = rhs(F)

# Time-stepping
u = Function(V)
vtk_file = File("results2/wave.pvd")
while t <= T:

    t += dt
    print("Time: ", t)

    solve(a == L, u, bc)
    update(u, u0, v0, a0, beta, gamma, dt)

    # Save solution to VTK format
vtk_file << u
