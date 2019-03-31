# pylint: disable=invalid-name
"""
Useful basic routines for managing polarization using the Stokes/Mueller calculus

Todo:
    * tests and documentation

Scott Prahl
April 2019
"""

import sympy
import pypolar.sym_fresnel as sym_fresnel

__all__ = ['op_linear_polarizer',
           'op_retarder',
           'op_attenuator',
           'op_mirror',
           'op_rotation',
           'op_quarter_wave_plate',
           'op_half_wave_plate',
           'op_fresnel_reflection',
           'op_fresnel_transmission',
           'stokes_linear',
           'stokes_left_circular',
           'stokes_right_circular',
           'stokes_horizontal',
           'stokes_vertical',
           'stokes_to_jones',
           'mueller_to_jones']


def op_linear_polarizer(theta):
    """
    Mueller matrix operator for a linear polarizer rotated about a normal to
    the surface of the polarizer.

    theta: rotation angle measured from the horizontal plane [radians]
    """

    C2 = sympy.cos(2 * theta)
    S2 = sympy.sin(2 * theta)
    lp = sympy.Matrix([[1, C2, S2, 0],
                   [C2, C2**2, C2 * S2, 0],
                   [S2, C2 * S2, S2 * S2, 0],
                   [0, 0, 0, 0]])
    return 0.5 * lp


def op_retarder(theta, delta):
    """
    Mueller matrix operator for an optical retarder rotated about a normal to
    the surface of the retarder.

    theta: rotation angle between fast-axis and the horizontal plane [radians]
    delta: phase delay introduced between fast and slow-axes         [radians]
    """

    C2 = sympy.cos(2 * theta)
    S2 = sympy.sin(2 * theta)
    C = sympy.cos(delta)
    S = sympy.sin(delta)
    ret = sympy.Matrix([[1, 0, 0, 0],
                    [0, C2**2 + C * S2**2, (1 - C) * S2 * C2, -S * S2],
                    [0, (1 - C) * C2 * S2, S2**2 + C * C2**2, S * C2],
                    [0, S * S2, -S * C2, C]])
    return ret


def op_attenuator(od):
    """
    Mueller matrix operator for an optical attenuator.

    od: base ten optical density  [---]
    """
    k = 10**(-od)
    att = sympy.Matrix([[k, 0, 0, 0],
                    [0, k, 0, 0],
                    [0, 0, k, 0],
                    [0, 0, 0, k]])
    return att


def op_mirror():
    """
    Mueller matrix operator for a perfect mirror.
    """

    mir = sympy.Matrix([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, -1, 0],
                    [0, 0, 0, -1]])
    return mir


def op_rotation(theta):
    """
    Mueller matrix operator to rotate light about the optical axis.

    theta: rotation angle  [radians]
    """

    C2 = sympy.cos(2 * theta)
    S2 = sympy.sin(2 * theta)
    rot = sympy.Matrix([[1, 0, 0, 0],
                    [0, C2, S2, 0],
                    [0, -S2, C2, 0],
                    [0, 0, 0, 1]])
    return rot


def op_quarter_wave_plate(theta):
    """
    Mueller matrix operator for an quarter-wave plate rotated about a normal to
    the surface of the plate.

    theta: rotation angle between fast-axis and the horizontal plane [radians]
    """

    C2 = sympy.cos(2 * theta)
    S2 = sympy.sin(2 * theta)
    qwp = sympy.Matrix([[1, 0, 0, 0],
                    [0, C2**2, C2 * S2, -S2],
                    [0, C2 * S2, S2 * S2, C2],
                    [0, S2, -C2, 0]])
    return qwp


def op_half_wave_plate(theta):
    """
    Mueller matrix operator for an half-wave plate rotated about a normal to
    the surface of the plate.

    theta: rotation angle between fast-axis and the horizontal plane [radians]
    """

    C2 = sympy.cos(2 * theta)
    S2 = sympy.sin(2 * theta)
    qwp = sympy.Matrix([[1, 0, 0, 0],
                    [0, C2**2 - S2**2, 2 * C2 * S2, 0],
                    [0, 2 * C2 * S2, S2 * S2 - C2**2, 0],
                    [0, 0, 0, -1]])
    return qwp


def op_fresnel_reflection(m, theta):
    """
    Mueller matrix operator for Fresnel reflection at angle theta

    Convert from the Jones operator to ensure that phase change are
    handled properly
    Args:
        m :     complex index of refraction   [-]
        theta : angle from normal to surface  [radians]
    Returns:
        4x4 Fresnel reflection operator       [-]
    """
    J = pypolar.jones.op_fresnel_reflection(m, theta)
    R = pypolar.jones.jones_op_to_mueller_op(J)
    return R


def op_fresnel_transmission(m, theta):
    """
    Mueller matrix operator for Fresnel transmission at angle theta

    Unclear if phase changes are handled properly.  See Collett, "Mueller-Stokes
    Matrix Formulation of Fresnel's Equations," Am. J. Phys. 39, 517 (1971).

    Args:
        m :     complex index of refraction       [-]
        theta : angle from normal to surface      [radians]
    Returns:
        4x4 Fresnel transmission operator         [-]
    """
    tau_p = sym_fresnel.T_par(m, theta)
    tau_s = sym_fresnel.T_per(m, theta)
    a = tau_s + tau_p
    b = tau_s - tau_p
    c = 2 * sympy.sqrt(tau_s*tau_p)
    mat = sympy.Matrix([[a, b, 0, 0],
                    [b, a, 0, 0],
                    [0, 0, c, 0],
                    [0, 0, 0, c]])
    return 0.5 * mat


def stokes_linear(theta):
    """Stokes vector for linear polarized light at angle theta from
       horizontal plane"""

    return sympy.Matrix([1, sympy.cos(2*theta), sympy.sin(2*theta), 0])


def stokes_right_circular():
    """Stokes vector corresponding to right circular polarized light"""

    return sympy.Matrix([1, 0, 0, 1])


def stokes_left_circular():
    """Stokes vector corresponding to left circular polarized light"""

    return sympy.Matrix([1, 0, 0, -1])


def stokes_horizontal():
    """Stokes vector corresponding to horizontal polarized light"""

    return sympy.Matrix([1, 1, 0, 0])


def stokes_unpolarized():
    """Stokes vector corresponding to unpolarized light"""

    return sympy.Matrix([1, 0, 0, 0])

def stokes_vertical():
    """Stokes vector corresponding to vertical polarized light"""

    return sympy.Matrix([1, -1, 0, 0])

def stokes_to_jones(S):
    """
    Convert a Stokes vector to a Jones vector

    The Jones vector only has the polarized part of the intensity, of course.
    Also, since the Jones vector can differ by an arbitrary phase, the phase
    is chosen which makes the horizontal component purely real.

    Isympyuts:
        S : a Stokes vector

    Returns:
         the Jones vector corresponding to
    """

    # Calculate the degree of polarization
    p = sympy.sqrt(S[1]**2 + S[2]**2 + S[3]**2) / S[0]

    # Normalize the Stokes parameters (first one will be 1, of course)
    Q = S[1] / (S[0] * p)
    U = S[2] / (S[0] * p)
    V = S[3] / (S[0] * p)

    # the Jones components
    A = sympy.sqrt((1 + Q) / 2)
    if A == 0:
        B = 1
    else:
        B = sympy.complex(U, -V) / (2 * A)

    # put them together in a vector with the amplitude of the polarized part
    return sympy.sqrt(S[0] * p) * sympy.Matrix([A, B])


def mueller_to_jones(M):
    """
    Convert a Mueller matrix to a Jones matrix

    Theocaris, Matrix Theory of Photoelasticity, eqns 4.70-4.76, 1979

    Isympyuts:
        M : a 4x4 Mueller matrix

    Returns:
         the corresponding 2x2 Jones matrix
    """
    A = sympy.empty((2, 2))
    A[0, 0] = sympy.sqrt((M[0, 0]+M[0, 1]+M[1, 0]+M[1, 1])/2)
    A[0, 1] = sympy.sqrt((M[0, 0]+M[0, 1]-M[1, 0]-M[1, 1])/2)
    A[1, 0] = sympy.sqrt((M[0, 0]-M[0, 1]+M[1, 0]-M[1, 1])/2)
    A[1, 1] = sympy.sqrt((M[0, 0]-M[0, 1]-M[1, 0]+M[1, 1])/2)

    theta = sympy.empty((2, 2))
    theta[0, 0] = 0
    theta[0, 1] = -sympy.arctan2(M[0, 3]+M[1, 3], M[0, 2]+M[1, 2])
    theta[1, 0] = sympy.arctan2(M[3, 0]+M[3, 1], M[2, 0]+M[2, 1])
    theta[1, 1] = sympy.arctan2(M[3, 2]-M[2, 3], M[2, 2]+M[3, 3])

    return A*sympy.exp(1j*theta)


