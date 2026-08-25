"""
CelesTrak GP API client.
Fetches satellite orbital data (OMM format) from the public CelesTrak API.
No authentication required.
"""
from __future__ import annotations

import logging
import math
import time
from pathlib import Path

import httpx

from app.models.satellite import OrbitalElements, SatelliteData, SatelliteSearchResult

logger = logging.getLogger(__name__)

CELESTRAK_GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"

# In-memory cache to avoid hammering CelesTrak
_cache: dict[str, tuple[list[dict], float]] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_key(norad_id: int | None = None, group: str | None = None) -> str:
    if norad_id:
        return f"norad:{norad_id}"
    if group:
        return f"group:{group}"
    return "all"


def _get_cached(key: str) -> list[dict] | None:
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cached(key: str, data: list[dict]) -> None:
    _cache[key] = (data, time.time())


async def fetch_satellite_raw(
    norad_id: int | None = None,
    group: str | None = None,
    format: str = "json",
    use_cache: bool = True,
) -> list[dict]:
    """
    Fetch raw satellite OMM records from CelesTrak GP API.

    Parameters
    ----------
    norad_id : int, optional
        Specific satellite NORAD catalog number.
    group : str, optional
        Group name: 'starlink', 'active', 'stations', 'cosmos-2251-debris', etc.
    format : str
        Response format — always 'json' for machine use.
    use_cache : bool
        Whether to use the in-memory cache.

    Returns
    -------
    list[dict]
        List of OMM satellite records.
    """
    key = _cache_key(norad_id=norad_id, group=group)

    if use_cache:
        cached = _get_cached(key)
        if cached is not None:
            logger.debug("CelesTrak cache hit: %s", key)
            return cached

    params: dict[str, str] = {"FORMAT": format}
    if norad_id is not None:
        params["CATNR"] = str(norad_id)
    elif group:
        params["GROUP"] = group

    logger.info("Fetching CelesTrak data: %s", params)
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(CELESTRAK_GP_URL, params=params)
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, list):
        raise ValueError(f"Unexpected CelesTrak response format: {type(data)}")

    _set_cached(key, data)
    return data


def _omm_to_satellite_data(record: dict) -> SatelliteData:
    """Convert a raw OMM JSON record to a SatelliteData model."""
    norad_id = int(record.get("NORAD_CAT_ID", 0))
    mean_motion = float(record.get("MEAN_MOTION", 0.0))
    eccentricity = float(record.get("ECCENTRICITY", 0.0))
    inclination = float(record.get("INCLINATION", 0.0))
    epoch = record.get("EPOCH", "")

    # Compute semi-major axis from mean motion (Kepler's 3rd law)
    # n (rad/s) = 2*pi / T = 2*pi * mean_motion / 86400
    # a^3 = GM / n^2
    MU = 398600.4418  # km^3/s^2
    n_rad_s = mean_motion * 2 * math.pi / 86400.0
    a_km = (MU / (n_rad_s ** 2)) ** (1.0 / 3.0)

    orbital_elements = OrbitalElements(
        semi_major_axis_km=a_km,
        eccentricity=eccentricity,
        inclination_deg=inclination,
        raan_deg=float(record.get("RA_OF_ASC_NODE", 0.0)),
        arg_of_perigee_deg=float(record.get("ARG_OF_PERICENTER", 0.0)),
        mean_anomaly_deg=float(record.get("MEAN_ANOMALY", 0.0)),
        mean_motion_rev_per_day=mean_motion,
        bstar_drag=float(record.get("BSTAR", 0.0)),
        epoch=epoch,
    )

    return SatelliteData(
        norad_cat_id=norad_id,
        object_name=record.get("OBJECT_NAME", "UNKNOWN"),
        object_type=record.get("OBJECT_TYPE", "PAYLOAD"),
        classification_type=record.get("CLASSIFICATION_TYPE", "U"),
        international_designator=record.get("INTLDES"),
        epoch=epoch,
        mean_motion=mean_motion,
        eccentricity=eccentricity,
        inclination=inclination,
        ra_of_asc_node=float(record.get("RA_OF_ASC_NODE", 0.0)),
        arg_of_pericenter=float(record.get("ARG_OF_PERICENTER", 0.0)),
        mean_anomaly=float(record.get("MEAN_ANOMALY", 0.0)),
        bstar=float(record.get("BSTAR", 0.0)),
        mean_motion_dot=float(record.get("MEAN_MOTION_DOT", 0.0)),
        mean_motion_ddot=float(record.get("MEAN_MOTION_DDOT", 0.0)),
        element_set_no=int(record.get("ELEMENT_SET_NO", 0)),
        rev_at_epoch=int(record.get("REV_AT_EPOCH", 0)),
        orbital_elements=orbital_elements,
    )


async def get_satellite_by_norad_id(norad_id: int) -> SatelliteData | None:
    """Fetch and parse a single satellite by NORAD catalog ID."""
    records = await fetch_satellite_raw(norad_id=norad_id)
    if not records:
        return None
    return _omm_to_satellite_data(records[0])


async def search_satellites(query: str, limit: int = 20) -> list[SatelliteSearchResult]:
    """
    Search satellites by name or NORAD ID from the 'active' group.
    Falls back to the demo set if CelesTrak is unreachable.
    """
    query = query.strip().upper()

    # If query is a number, look up by NORAD ID
    if query.isdigit():
        sat = await get_satellite_by_norad_id(int(query))
        if sat and sat.orbital_elements:
            return [SatelliteSearchResult(
                norad_cat_id=sat.norad_cat_id,
                object_name=sat.object_name,
                object_type=sat.object_type,
                epoch=sat.epoch,
                mean_motion=sat.mean_motion,
                eccentricity=sat.eccentricity,
                inclination=sat.inclination,
                mean_altitude_km=sat.orbital_elements.mean_altitude_km,
            )]
        return []

    # Fetch active satellites and search by name
    try:
        records = await fetch_satellite_raw(group="active")
    except Exception as exc:
        logger.warning("CelesTrak fetch failed, returning empty: %s", exc)
        return []

    results: list[SatelliteSearchResult] = []
    for record in records:
        name = record.get("OBJECT_NAME", "").upper()
        if query in name:
            sat = _omm_to_satellite_data(record)
            alt = sat.orbital_elements.mean_altitude_km if sat.orbital_elements else None
            results.append(SatelliteSearchResult(
                norad_cat_id=sat.norad_cat_id,
                object_name=sat.object_name,
                object_type=sat.object_type,
                epoch=sat.epoch,
                mean_motion=sat.mean_motion,
                eccentricity=sat.eccentricity,
                inclination=sat.inclination,
                mean_altitude_km=alt,
            ))
            if len(results) >= limit:
                break

    return results


async def get_satellite_group(group: str) -> list[SatelliteData]:
    """Fetch all satellites in a named group."""
    records = await fetch_satellite_raw(group=group)
    return [_omm_to_satellite_data(r) for r in records]
