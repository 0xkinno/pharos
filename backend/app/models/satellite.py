"""
Pydantic models for satellite orbital data.
"""
from pydantic import BaseModel, Field


class OrbitalElements(BaseModel):
    """Keplerian orbital elements extracted from TLE/OMM data."""
    semi_major_axis_km: float = Field(..., description="Semi-major axis in km")
    eccentricity: float = Field(..., ge=0.0, lt=1.0)
    inclination_deg: float = Field(..., ge=0.0, le=180.0)
    raan_deg: float = Field(..., ge=0.0, lt=360.0, description="Right ascension of ascending node")
    arg_of_perigee_deg: float = Field(..., ge=0.0, lt=360.0)
    mean_anomaly_deg: float = Field(..., ge=0.0, lt=360.0)
    mean_motion_rev_per_day: float = Field(..., gt=0.0)
    bstar_drag: float = Field(default=0.0, description="BSTAR drag term")
    epoch: str = Field(..., description="TLE epoch ISO string")

    @property
    def perigee_km(self) -> float:
        return self.semi_major_axis_km * (1 - self.eccentricity) - 6371.0

    @property
    def apogee_km(self) -> float:
        return self.semi_major_axis_km * (1 + self.eccentricity) - 6371.0

    @property
    def mean_altitude_km(self) -> float:
        return self.semi_major_axis_km - 6371.0

    @property
    def orbital_period_minutes(self) -> float:
        return 1440.0 / self.mean_motion_rev_per_day


class SatelliteData(BaseModel):
    """Full satellite data record from CelesTrak."""
    norad_cat_id: int = Field(..., description="NORAD catalog number")
    object_name: str = Field(..., description="Satellite name")
    object_type: str = Field(default="PAYLOAD", description="PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN")
    classification_type: str = Field(default="U", description="U=Unclassified, C=Classified, S=Secret")
    international_designator: str | None = Field(None, description="COSPAR ID")
    epoch: str = Field(..., description="TLE epoch")
    mean_motion: float = Field(..., description="Mean motion (revs per day)")
    eccentricity: float
    inclination: float
    ra_of_asc_node: float
    arg_of_pericenter: float
    mean_anomaly: float
    ephemeris_type: int = 0
    classification: str = "U"
    element_set_no: int = 0
    rev_at_epoch: int = 0
    bstar: float = 0.0
    mean_motion_dot: float = 0.0
    mean_motion_ddot: float = 0.0
    # Derived orbital elements (computed after fetch)
    orbital_elements: OrbitalElements | None = None

    @property
    def is_leo(self) -> bool:
        """True if satellite is in Low Earth Orbit (below 2000 km)."""
        if self.orbital_elements:
            return self.orbital_elements.mean_altitude_km < 2000.0
        # Approximate from mean motion: LEO has period < ~127 minutes
        return self.mean_motion > 11.25

    @property
    def is_geo(self) -> bool:
        """True if satellite is in Geostationary Orbit (~35786 km)."""
        if self.orbital_elements:
            alt = self.orbital_elements.mean_altitude_km
            return 35500 < alt < 36100
        # GEO mean motion ~1.003 rev/day
        return 0.99 < self.mean_motion < 1.01


class SatelliteSearchResult(BaseModel):
    """Lightweight search result for satellite listing."""
    norad_cat_id: int
    object_name: str
    object_type: str
    epoch: str
    mean_motion: float
    eccentricity: float
    inclination: float
    mean_altitude_km: float | None = None
