"""
Useful basic routines for managing polarization using the Mueller calculus

Todo:
    * add jupyter notebook for documentation
    * test routines
    * improve internal documentation
    * figure out

Scott Prahl
Apr 2018
"""

import numpy as np
import pypolar.jones as jones
import pypolar.fresnel as fresnel

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
           'draw_stokes_ellipse',
           'draw_field',
           'draw_stokes_animated']


def op_linear_polarizer(theta):
    """
    Mueller matrix operator for a linear polarizer rotated about a normal to
    the surface of the polarizer.

    theta: rotation angle measured from the horizontal plane [radians]
    """

    C2 = np.cos(2 * theta)
    S2 = np.sin(2 * theta)
    lp = np.array([[1, C2, S2, 0],
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

    C2 = np.cos(2 * theta)
    S2 = np.sin(2 * theta)
    C = np.cos(delta)
    S = np.sin(delta)
    ret = np.array([[1, 0, 0, 0],
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
    att = np.array([[k, 0, 0, 0],
                    [0, k, 0, 0],
                    [0, 0, k, 0],
                    [0, 0, 0, k]])
    return att


def op_mirror():
    """
    Mueller matrix operator for a perfect mirror.
    """

    mir = np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, -1, 0],
                    [0, 0, 0, -1]])
    return mir


def op_rotation(theta):
    """
    Mueller matrix operator to rotate light about the optical axis.

    theta: rotation angle  [radians]
    """

    C2 = np.cos(2 * theta)
    S2 = np.sin(2 * theta)
    rot = np.array([[1, 0, 0, 0],
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

    C2 = np.cos(2 * theta)
    S2 = np.sin(2 * theta)
    qwp = np.array([[1, 0, 0, 0],
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

    C2 = np.cos(2 * theta)
    S2 = np.sin(2 * theta)
    qwp = np.array([[1, 0, 0, 0],
                    [0, C2**2 - S2**2, 2 * C2 * S2, 0],
                    [0, 2 * C2 * S2, S2 * S2 - C2**2, 0],
                    [0, 0, 0, -1]])
    return qwp


def op_fresnel_reflection(m, theta):
    """
    Mueller matrix operator for Fresnel reflection at angle theta

    Args:
        m :     complex index of refraction   [-]
        theta : angle from normal to surface  [radians]
    Returns:
        4x4 Fresnel reflection operator       [-]
    """
    p = fresnel.R_par(m, theta)
    s = fresnel.R_per(m, theta)
    ps = 2*np.sqrt(p*s)
    ref = np.array([[p+s, s-p, 0, 0],
                    [s-p, p+s, 0, 0],
                    [0, 0, ps, 0],
                    [0, 0, 0, ps]])
    return 0.5*ref


def op_fresnel_transmission(m, theta):
    """
    Mueller matrix operator for Fresnel transmission at angle theta

    Args:
        m :     complex index of refraction       [-]
        theta : angle from normal to surface      [radians]
    Returns:
        4x4 Fresnel transmission operator         [-]
    """
    p = fresnel.T_par(m, theta)
    s = fresnel.T_per(m, theta)
    ps = 2*np.sqrt(p*s)
    tra = np.array([[s+p, s-p, 0, 0],
                    [s-p, s+p, 0, 0],
                    [0, 0, ps, 0],
                    [0, 0, 0, ps]])
    return 0.5*tra


def stokes_linear(theta):
    """Stokes vector for linear polarized light at angle theta from
       horizontal plane"""

    return np.array([1, np.cos(2*theta), np.sin(2*theta), 0])


def stokes_right_circular():
    """Stokes vector corresponding to right circular polarized light"""

    return np.array([1, 0, 0, 1])


def stokes_left_circular():
    """Stokes vector corresponding to left circular polarized light"""

    return np.array([1, 0, 0, -1])


def stokes_horizontal():
    """Stokes vector corresponding to horizontal polarized light"""

    return np.array([1, 1, 0, 0])


def stokes_vertical():
    """Stokes vector corresponding to vertical polarized light"""

    return np.array([1, -1, 0, 0])


def stokes_to_jones(S):
    """
    Convert a Stokes vector to a Jones vector

    The Jones vector only has the polarized part of the intensity, of course.
    Also, since the Jones vector can differ by an arbitrary phase, the phase
    is chosen which makes the horizontal component purely real.

    Inputs:
        S : a Stokes vector

    Returns:
         the Jones vector corresponding to
    """

    # Calculate the degree of polarization
    p = np.sqrt(S[1]**2 + S[2]**2 + S[3]**2) / S[0]

    # Normalize the Stokes parameters (first one will be 1, of course)
    Q = S[1] / (S[0] * p)
    U = S[2] / (S[0] * p)
    V = S[3] / (S[0] * p)

    # the Jones components
    A = np.sqrt((1 + Q) / 2)
    if A == 0:
        B = 1
    else:
        B = complex(U, -V) / (2 * A)

    # put them together in a vector with the amplitude of the polarized part
    return np.sqrt(S[0] * p) * np.array([A, B])


def draw_stokes_ellipse(S):
    """
    Draw a 2D representation of the polarization state of S

    Args:
        S:      Stokes vector
        offset: starting point
    Returns:
        a matplotlib object with the graph
    """
    J = stokes_to_jones(S)
    plt = jones.draw_stokes_ellipse(J)
    return plt


def draw_field(S, offset=0):
    """
    Draw a 2D and 3D representation of the polarization

    Args:
        S:      Stokes vector
        offset: starting point
    """
    J = stokes_to_jones(S)
    plt = jones.draw_field(J, offset)
    return plt


def draw_stokes_animated(S):
    """
    Draw animated 2D and 3D representations of the polarization

    Args:
        S:      Stokes vector
    """
    J = stokes_to_jones(S)
    ani = jones.draw_stokes_animated(J)
    return ani
