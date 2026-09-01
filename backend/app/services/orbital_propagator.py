"""
SGP4 Orbital Propagation Service.
Uses the python-sgp4 library (Vallado et al.) to propagate TLE/OMM records.
Produces position vectors, velocity vectors, and derived orbital parameters.
"""
from __future__ import annotations

import logging
import math
from datetime import UTC, datetime

from sgp4.api import WGS84, Satrec
from sgp4.conveniences import jday_datetime

from app.models.satellite import OrbitalElements, SatelliteData

logger = logging.getLogger(__name__)

# Earth constants (WGS84)
R_EARTH_KM = 6371.0
MU_EARTH = 398600.4418  # km^3/s^2


class PropagationResult:
    """Result from SGP4 propagation at a given epoch."""
    __slots__ = (
        "altitude_km",
        "error_code",
        "error_message",
        "latitude_deg",
        "longitude_deg",
        "position_km",
        "success",
        "velocity_km_s",
    )

    def __init__(
        self,
        success: bool,
        position_km: tuple[float, float, float] = (0.0, 0.0, 0.0),
        velocity_km_s: tuple[float, float, float] = (0.0, 0.0, 0.0),
        altitude_km: float = 0.0,
        latitude_deg: float = 0.0,
        longitude_deg: float = 0.0,
        error_code: int = 0,
        error_message: str = "",
    ) -> None:
        self.success = success
        self.position_km = position_km
        self.velocity_km_s = velocity_km_s
        self.altitude_km = altitude_km
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.error_code = error_code
        self.error_message = error_message


def build_satrec_from_satellite(sat: SatelliteData) -> Satrec | None:
    """
    Build an sgp4.Satrec object from a SatelliteData model.
    Uses the OMM data fields directly.
    """
    try:
        satrec = Satrec()
        satrec.sgp4init(
            WGS84,
            "i",  # initialization mode (improved)
            sat.norad_cat_id,
            _epoch_to_jd_fraction(sat.epoch),  # epoch as Julian day + fraction
            sat.bstar,
            sat.mean_motion_dot / (2 * 1440),  # convert to rad/min^2
            sat.mean_motion_ddot / (6 * 1440**2),  # convert to rad/min^3
            sat.eccentricity,
            math.radians(sat.arg_of_pericenter),
            math.radians(sat.inclination),
            math.radians(sat.mean_anomaly),
            sat.mean_motion * (2 * math.pi / 1440),  # rev/day → rad/min
            math.radians(sat.ra_of_asc_node),
        )
        return satrec
    except Exception as exc:
        logger.error("Failed to build Satrec for %d: %s", sat.norad_cat_id, exc)
        return None


def _epoch_to_jd_fraction(epoch_str: str) -> float:
    """
    Convert a TLE epoch string (ISO format) to Julian Day Number.
    Returns the Julian day as a single float (jd + fr combined).
    sgp4init expects: epoch in days since 1949-12-31 00:00 UTC
    """
    try:
        dt = datetime.fromisoformat(epoch_str.replace("Z", "+00:00"))
    except ValueError:
        # Try alternate TLE epoch format
        dt = datetime.now(UTC)

    # sgp4 uses epoch in Julian days since 1949-12-31 00:00 UTC
    # Reference: JD of 1949-12-31 00:00 UTC = 2433281.5
    jd, fr = jday_datetime(dt)
    return jd + fr - 2433281.5  # Days since 1949-12-31


def propagate_to_epoch(sat: SatelliteData, target_dt: datetime | None = None) -> PropagationResult:
    """
    Propagate a satellite to a given time (or current UTC if not specified).

    Returns position (km, TEME frame) and velocity (km/s, TEME frame).
    """
    if target_dt is None:
        target_dt = datetime.now(UTC)

    satrec = build_satrec_from_satellite(sat)
    if satrec is None:
        return PropagationResult(
            success=False,
            error_code=-1,
            error_message="Failed to initialize SGP4 record",
        )

    jd, fr = jday_datetime(target_dt)
    e, r, v = satrec.sgp4(jd, fr)

    if e != 0:
        error_messages = {
            1: "Mean eccentricity not in [0, 1)",
            2: "Mean motion less than 0",
            3: "Perturbed eccentricity not in [0, 1)",
            4: "Semi-latus rectum < 0",
            5: "Epoch elements are sub-orbital",
            6: "Satellite has decayed",
        }
        msg = error_messages.get(e, f"SGP4 propagation error code {e}")
        return PropagationResult(success=False, error_code=e, error_message=msg)

    # r = [x, y, z] in km (TEME frame)
    position_km = tuple(r)  # type: ignore[arg-type]
    velocity_km_s = tuple(v)  # type: ignore[arg-type]

    # Altitude from ECI position vector
    r_magnitude = math.sqrt(sum(x**2 for x in r))
    altitude_km = r_magnitude - R_EARTH_KM

    return PropagationResult(
        success=True,
        position_km=position_km,
        velocity_km_s=velocity_km_s,
        altitude_km=max(altitude_km, 0.0),
    )


def compute_orbital_elements_from_sgp4(sat: SatelliteData) -> OrbitalElements | None:
    """
    Re-derive orbital elements using mean motion from the OMM record.
    This is essentially what's already in the OMM but validated through sgp4.
    """
    n_rev_day = sat.mean_motion
    if n_rev_day <= 0:
        return None

    n_rad_s = n_rev_day * 2 * math.pi / 86400.0
    a_km = (MU_EARTH / (n_rad_s ** 2)) ** (1.0 / 3.0)

    return OrbitalElements(
        semi_major_axis_km=a_km,
        eccentricity=sat.eccentricity,
        inclination_deg=sat.inclination,
        raan_deg=sat.ra_of_asc_node,
        arg_of_perigee_deg=sat.arg_of_pericenter,
        mean_anomaly_deg=sat.mean_anomaly,
        mean_motion_rev_per_day=n_rev_day,
        bstar_drag=sat.bstar,
        epoch=sat.epoch,
    )


def classify_orbit(altitude_km: float, inclination_deg: float) -> str:
    """
    Classify orbit type based on altitude.

    LEO: 160–2000 km
    MEO: 2000–35786 km
    GEO: ~35786 km (geosynchronous)
    HEO: Highly Elliptical Orbit (perigee < 2000 km, apogee > 35786 km)
    GTO: Geostationary Transfer Orbit
    """
    if altitude_km < 2000:
        return "LEO"
    elif altitude_km < 35500:
        return "MEO"
    elif altitude_km <= 36100:
        return "GEO"
    else:
        return "HEO"
