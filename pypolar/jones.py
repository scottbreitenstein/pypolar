# pylint: disable=invalid-name
# pylint: disable=bare-except
# pylint: disable=global-statement
# pep257: disable=D401

"""
Useful routines for managing polarization with the Jones calculus.

To Do

* modify interpret() when phase difference differs by more than 2pi
* improve interpret() to give angle for elliptical polarization
* finish Poincaré stuff
* add complex polarization parameter chi
* test everything with non-unity amplitudes
* finish normalize

Scott Prahl
Apr 2020
"""

import numpy as np
import pypolar.fresnel

__all__ = ('use_alternate_convention',
           'op_linear_polarizer',
           'op_retarder',
           'op_attenuator',
           'op_mirror',
           'op_rotation',
           'op_quarter_wave_plate',
           'op_half_wave_plate',
           'op_fresnel_reflection',
           'op_fresnel_transmission',
           'field_linear',
           'field_left_circular',
           'field_right_circular',
           'field_horizontal',
           'field_elliptical',
           'field_vertical',
           'interpret',
           'intensity',
           'phase',
           'ellipse_azimuth',
           'ellipse_axes',
           'ellipticity',
           'ellipticity_angle',
           'amplitude_ratio',
           'amplitude_ratio_angle',
           'jones_op_to_mueller_op')

alternate_sign_convention = False

def use_alternate_convention(state):
    """
    Change sign convention used for Jones calculus.

    Read the documentation about the different conventions possible.

    The default convention is to assume the wave function is
    represented by exp(j*(omega*t-k*z)) and that the perspective
    when viewing a sectional pattern is to look back along the
    optical axis towards the source.  This is the most commonly used
    convention, but there are noteable exceptions (Wikipedia, Fowler, and
    Hecht (sometimes).

    Call this function once at the beginning and everything should
    be just fine.
    """
    global alternate_sign_convention
    alternate_sign_convention = state

def op_linear_polarizer(theta):
    """
    Jones matrix operator for a rotated linear polarizer.

    The polarizer has been rotated around a normal to its surface.

    Args:
        theta: rotation angle measured from the horizontal plane [radians]
    """
    return np.array([[np.cos(theta)**2, np.sin(theta) * np.cos(theta)],
                      [np.sin(theta) * np.cos(theta), np.sin(theta)**2]])


def op_retarder(theta, delta):
    """
    Jones matrix operator for an rotated optical retarder.

    The retarder has been rotated around a normal to its surface.

    Args:
        theta: rotation angle between fast-axis and the horizontal plane [radians]
        delta: phase delay introduced between fast and slow-axes         [radians]
    """
    if alternate_sign_convention:
        theta *= -1
    P = np.exp(+delta / 2 * 1j)
    Q = np.exp(-delta / 2 * 1j)
    D = np.sin(delta / 2) * 2j
    C = np.cos(theta)
    S = np.sin(theta)
    retarder = np.array([[C * C * P + S * S * Q, C * S * D],
                         [C * S * D, C * C * Q + S * S * P]])
    if alternate_sign_convention:
        return np.conjugate(retarder)
    return retarder


def op_attenuator(t):
    """
    Jones matrix operator for an isotropic optical attenuator.

    The transmittance t=I/I_0 is the fraction of light getting
    through the attenuator or absorber.

    Args:
        t: fraction of intensity getting through attenuator  [---]
    """
    f = np.sqrt(t)
    return np.array([[f, 0], [0, f]])


def op_mirror():
    """Jones matrix operator for a perfect mirror."""
    return np.array([[1, 0], [0, -1]])


def op_rotation(theta):
    """
    Jones matrix operator to rotate light around the optical axis.

    Args:
        theta : angle of rotation around optical axis  [radians]
    Returns:
        2x2 matrix of the rotation operator           [-]
    """
    return np.array([[np.cos(theta), np.sin(theta)],
                     [-np.sin(theta), np.cos(theta)]])


def op_quarter_wave_plate(theta):
    """
    Jones matrix operator for an rotated quarter-wave plate.

    The QWP had been rotated around a normal to its surface.

    Args:
        theta : angle from fast-axis to horizontal plane  [radians]
    Returns:
        2x2 matrix of the quarter-wave plate operator     [-]
    """
    return op_retarder(theta, np.pi / 2)


def op_half_wave_plate(theta):
    """
    Jones matrix operator for a rotated half-wave plate.

    The half wave plate has been rotated around a normal to
    the surface of the plate.

    Args:
        theta : angle from fast-axis to horizontal plane  [radians]
    Returns:
        2x2 matrix of the half-wave plate operator     [-]
    """
    return op_retarder(theta, np.pi)


def op_fresnel_reflection(m, theta):
    """
    Jones matrix operator for Fresnel reflection at angle theta.

    Args:
        m :     complex index of refraction   [-]
        theta : angle from normal to surface  [radians]
    Returns:
        2x2 matrix of the Fresnel transmission operator     [-]
    """
    return np.array([[pypolar.fresnel.r_par(m, theta), 0],
                     [0, pypolar.fresnel.r_per(m, theta)]])


def op_fresnel_transmission(m, theta):
    """
    Jones matrix operator for Fresnel transmission at angle theta.

    *** THIS IS ALMOST CERTAINLY WRONG ***

    Args:
        m :     complex index of refraction       [-]
        theta : angle from normal to surface      [radians]
    Returns:
        2x2 Fresnel transmission operator           [-]
    """
    c = np.cos(theta)
    d = np.sqrt(m * m - np.sin(theta)**2, dtype=np.complex)
    if m.imag == 0:
        d = np.conjugate(d)
    a = np.sqrt(d/c)
    return a*np.array([[pypolar.fresnel.t_par(m, theta), 0], [0, pypolar.fresnel.t_per(m, theta)]])


def field_linear(theta):
    """Jones vector for linear polarized light at angle theta from horizontal plane."""
    return np.array([np.cos(theta), np.sin(theta)])


def field_right_circular():
    """Jones Vector for right circular polarized light."""
    J = 1 / np.sqrt(2) * np.array([1, 1j])
    if alternate_sign_convention:
        return np.conjugate(J)
    return J


def field_left_circular():
    """Jones Vector for left circular polarized light."""
    J = 1 / np.sqrt(2) * np.array([1, -1j])
    if alternate_sign_convention:
        return np.conjugate(J)
    return J


def field_horizontal():
    """Jones Vector for horizontal polarized light."""
    return np.array([1, 0])


def field_vertical():
    """Jones Vector for vertical polarized light."""
    return np.array([0, 1])


def field_elliptical(azimuth, elliptic_angle, phi_x=0, E_0=1):
    """
    Jones vector for elliptically polarized light.

    Uses Azzam's equation 1.75

    Args:
        azimuth: tilt angle of ellipse from x-axis        [radians]
        ellipticity_angle: arctan(minor-axis/major-axis)  [radians]
        phi_x: phase for E field in x-direction           [radians]
        E_0: amplitude of field
    Returns:
        Jones vector with specified characteristics
    """
    ce = np.cos(elliptic_angle)
    se = np.sin(elliptic_angle)
    ca = np.cos(azimuth)
    sa = np.sin(azimuth)

    J = E_0 * np.array([ca*ce-sa*se*1j, sa*ce+ca*se*1j])

    J *= np.exp(1j * (phi_x-np.angle(J[0])))

    if alternate_sign_convention:
        return np.conjugate(J)
    return J

def interpret(J):
    """
    Interpret a Jones vector.

    arg:
        J: A Jones vector (2x1) which may have complex entries

    Examples
    -------
    interpret([1, -1j]) --> "Right circular polarization"

    interpret([0.5, 0.5]) -->
                      "Linear polarization at 45.000000 degrees CCW from x-axis"

    interpret( np.array([exp(-1j*pi), exp(-1j*pi/3)]) ) -->
                "Left elliptical polarization, rotated with respect to the axes"
    """
    try:
        j1, j2 = J
    except:
        print("Jones vector must have two elements")
        return 0

    eps = 1e-12
    mag1, p1 = abs(j1), np.angle(j1)
    mag2, p2 = abs(j2), np.angle(j2)

    JJ = np.array([j1, j2])
    inten = intensity(JJ)
    phaze = np.degrees(phase(JJ))
    azi = np.degrees(ellipse_azimuth(JJ))
    ell = ellipticity(JJ)

    s = "Intensity is %.3f\n" % inten
    s += "Phase is %.1f°\n" % phaze

    if np.remainder(p1 - p2, np.pi) < eps:
        ang = np.arctan2(mag2, mag1) * 180 / np.pi
        return s + "Linear polarization at %f degrees CCW from x-axis" % ang

    if abs(mag1 - mag2) < eps:
        if abs(p1 - p2 - np.pi / 2) < eps:
            s += "Right circular polarization"
        elif p1 > p2:
            s += "Right elliptical polarization\n"
            s += "    ellipticity is %.1f°\n" % ell
            s += "    rotated %.1f° respect to the axes" % azi
        if (p1 - p2 + np.pi / 2) < eps:
            s += "Left circular polarization"
        elif p1 < p2:
            s += "Left elliptical polarization\n"
            s += "    ellipticity is %.1f°\n" % ell
            s += "    rotated %.1f° respect to the axes" % azi
    else:
        if p1 - p2 == np.pi / 2:
            s += "Right elliptical polarization, non-rotated"
        elif p1 > p2:
            s += "Right elliptical polarization\n"
            s += "    ellipticity is %.1f°\n" % ell
            s += "    rotated %.1f° respect to the axes" % azi
        if p1 - p2 == -np.pi / 2:
            s += "Left circular polarization, non-rotated"
        elif p1 < p2:
            s += "Left elliptical polarization\n"
            s += "    ellipticity is %.1f°\n" % ell
            s += "    rotated %.1f° respect to the axes" % azi
    return s


def normalize_vector(J):
    """
    Normalize a vector by dividing each part by common number.

    After normalization the magnitude should be equal to ~1.
    """
    norm = np.linalg.norm(J)
    if norm == 0:
        return J
    return J / norm


def normalize(J):
    """Normalize a vector."""
#    alpha = ellipse_azimuth(J)
#    gamma = phase(J)
    return J
#    return np.array([np.cos(R)*np.exp(-0.5j*gamma),np.cos(R)*np.exp(0.5j*gamma)])


def intensity(J):
    """Return the intensity."""
    inten = abs(J[0])**2 + abs(J[1])**2
    return inten


def phase(J):
    """Return the phase."""
    gamma = np.angle(J[1]) - np.angle(J[0])
    return gamma


def ellipse_azimuth(J):
    """
    Return the angle between the major semi-axis and the x-axis.

    The polarization ellipse is rotated by this angle (called
    the azimuth) relative to the laboratory frame.
    """
    Ex0, Ey0 = np.abs(J)
    delta = phase(J)
    numer = 2 * Ex0 * Ey0 * np.cos(delta)
    denom = Ex0**2 - Ey0**2
    psi = 0.5 * np.arctan2(numer, denom)
    return psi


def ellipse_azimuth2(J):
    """
    Return the angle between the major semi-axis and the x-axis.

    How does this differ from orientation above?
    """
    delta = phase(J)
    psi = ellipse_azimuth(J)
    chi = 0.5 * np.arcsin(np.sin(2 * psi) * np.sin(delta))
    return chi


def ellipse_axes(J):
    """
    Return the semi-major and semi-minor radii of the ellipse.

    Twice these values will be the semi-major or semi-minor diameters.
    """
    Ex0, Ey0 = np.abs(J)
    alpha = ellipse_azimuth(J)
    delta = phase(J)
    C = np.cos(alpha)
    S = np.sin(alpha)
    asqr = (Ex0 * C)**2 + (Ey0 * S)**2 + 2 * Ex0 * Ey0 * C * S * np.cos(delta)
    bsqr = (Ex0 * S)**2 + (Ey0 * C)**2 - 2 * Ex0 * Ey0 * C * S * np.cos(delta)
    a = np.sqrt(abs(asqr))
    b = np.sqrt(abs(bsqr))
    if a < b:
        return b, a
    return a, b


def ellipticity(J):
    """
    Return the ellipticity of the polarization ellipse.

    This is the ratio of semi-minor to semi-major radii.
    The ellipticity is a measure of the fatness of the ellipse.
    The ellipticity can be defined to always be positive.  However
    negative values can be used to indicate left-handed polarization.
    Thus the ellipticity will range from -1 to 0 to 1 as light moves from
    LCP to Linear Polarization to RCP.
    """
    a, b = ellipse_axes(J)
    if phase(J) < 0:
        return -b/a
    return b/a


def ellipticity_angle(J):
    """
    Return the ellipticity angle of the polarization ellipse.

    The tangent of this angle is the ratio of semi-minor:semi-major
    radii.  It is between -pi/4 ≤ angle ≤ pi/4.  Positive values
    are for right–handed ellipticity.  Negative values for left-handed
    ellipticity.
    """
    a, b = ellipse_axes(J)
    if abs(a) >= abs(b):
        epsilon = np.arctan2(b, a)
    else:
        epsilon = np.arctan2(a, b)

    if phase(J) < 0:
        return -epsilon
    return epsilon


def amplitude_ratio(J):
    """
    Return the ratio of electric fields.

    This is the amplitude of the vibrations along x measured
    relative to the amplitude along y.
    """
    Ex0, Ey0 = np.abs(J)
    if Ex0 == 0:
        return np.inf
    return Ey0/Ex0


def amplitude_ratio_angle(J):
    """
    Return the ratio of electric fields.

    The tangent of this angle is the ratio of electric fields in
    the y and x directions.
    """
    Ex0, Ey0 = np.abs(J)
    psi = np.arctan2(Ey0, Ex0)
    return psi


def poincare_point(J):
    """Return the point on the Poincaré sphere."""
    longitude = 2 * ellipse_azimuth(J)
    a, b = ellipse_axes(J)
    latitude = 2 * np.arctan2(b, a)
    return latitude, longitude


def jones_op_to_mueller_op(JJ):
    """
    Convert a complex 2x2 Jones matrix to a real 4x4 Mueller matrix.

    Hauge, Muller, and Smith, "Conventions and Formulas for Using the Mueller-
    Stokes Calculus in Ellipsometry," Surface Science, 96, 81-107 (1980)
    Args:
        J:      Jones matrix
    Returns:
        equivalent 4x4 Mueller matrix
    """
    if alternate_sign_convention:
        J = np.conjugate(JJ)
    else:
        J = JJ
    M = np.zeros(shape=[4, 4], dtype=np.complex)
    C = np.conjugate(J)
    M[0, 0] = J[0, 0] * C[0, 0] + J[0, 1] * C[0, 1] + \
        J[1, 0] * C[1, 0] + J[1, 1] * C[1, 1]
    M[0, 1] = J[0, 0] * C[0, 0] + J[1, 0] * C[1, 0] - \
        J[0, 1] * C[0, 1] - J[1, 1] * C[1, 1]
    M[0, 2] = J[0, 1] * C[0, 0] + J[1, 1] * C[1, 0] + \
        J[0, 0] * C[0, 1] + J[1, 0] * C[1, 1]
    M[0, 3] = 1j * (J[0, 1] * C[0, 0] + J[1, 1] * C[1, 0] -
                    J[0, 0] * C[0, 1] - J[1, 0] * C[1, 1])
    M[1, 0] = J[0, 0] * C[0, 0] + J[0, 1] * C[0, 1] - \
        J[1, 0] * C[1, 0] - J[1, 1] * C[1, 1]
    M[1, 1] = J[0, 0] * C[0, 0] - J[1, 0] * C[1, 0] - \
        J[0, 1] * C[0, 1] + J[1, 1] * C[1, 1]
    M[1, 2] = J[0, 0] * C[0, 1] + J[0, 1] * C[0, 0] - \
        J[1, 0] * C[1, 1] - J[1, 1] * C[1, 0]
    M[1, 3] = 1j * (J[0, 1] * C[0, 0] + J[1, 0] * C[1, 1] -
                    J[1, 1] * C[1, 0] - J[0, 0] * C[0, 1])
    M[2, 0] = J[0, 0] * C[1, 0] + J[1, 0] * C[0, 0] + \
        J[0, 1] * C[1, 1] + J[1, 1] * C[0, 1]
    M[2, 1] = J[0, 0] * C[1, 0] + J[1, 0] * C[0, 0] - \
        J[0, 1] * C[1, 1] - J[1, 1] * C[0, 1]
    M[2, 2] = J[0, 0] * C[1, 1] + J[0, 1] * C[1, 0] + \
        J[1, 0] * C[0, 1] + J[1, 1] * C[0, 0]
    M[2, 3] = 1j * (-J[0, 0] * C[1, 1] + J[0, 1] * C[1, 0] -
                    J[1, 0] * C[0, 1] + J[1, 1] * C[0, 0])
    M[3, 0] = 1j * (J[0, 0] * C[1, 0] + J[0, 1] * C[1, 1] -
                    J[1, 0] * C[0, 0] - J[1, 1] * C[0, 1])
    M[3, 1] = 1j * (J[0, 0] * C[1, 0] - J[0, 1] * C[1, 1] -
                    J[1, 0] * C[0, 0] + J[1, 1] * C[0, 1])
    M[3, 2] = 1j * (J[0, 0] * C[1, 1] + J[0, 1] * C[1, 0] -
                    J[1, 0] * C[0, 1] - J[1, 1] * C[0, 0])
    M[3, 3] = J[0, 0] * C[1, 1] - J[0, 1] * C[1, 0] - \
        J[1, 0] * C[0, 1] + J[1, 1] * C[0, 0]
    MM = M.real / 2
    return MM
