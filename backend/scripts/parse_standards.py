"""
Standards Corpus Parser

Parses regulatory documents from standards/raw/ into markdown files in
standards/parsed/. Uses Docling for PDF parsing when available,
falls back to plain text processing.

Usage:
    cd backend
    python scripts/parse_standards.py

Output:
    standards/parsed/*.md — one markdown file per document

This script is run ONCE and the output is committed to the repository.
The corpus is never rebuilt at request time (API-deletion-proof architecture).
"""
from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).parent.parent
RAW_DIR = BACKEND_ROOT / "standards" / "raw"
PARSED_DIR = BACKEND_ROOT / "standards" / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

# Try to import Docling
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
    logger.info("Docling available — will use for PDF parsing")
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling not installed. Using plain text fallback.")


def parse_with_docling(input_path: Path, output_path: Path) -> bool:
    """Parse a document (PDF, DOCX, etc.) using Docling."""
    try:
        converter = DocumentConverter()
        result = converter.convert(str(input_path))
        markdown_text = result.document.export_to_markdown()
        output_path.write_text(markdown_text, encoding="utf-8")
        logger.info("Docling parsed %s → %s (%d chars)", input_path.name, output_path.name, len(markdown_text))
        return True
    except Exception as exc:
        logger.error("Docling parsing failed for %s: %s", input_path.name, exc)
        return False


def parse_text_file(input_path: Path, output_path: Path) -> bool:
    """Copy/convert a plain text file to markdown."""
    text = input_path.read_text(encoding="utf-8", errors="replace")
    # Basic cleanup
    lines = text.splitlines()
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Copied text file %s → %s", input_path.name, output_path.name)
    return True


def process_all_documents() -> int:
    """Process all documents in the raw/ directory."""
    if not RAW_DIR.exists():
        logger.warning("standards/raw/ does not exist. No documents to parse.")
        return 0

    docs = list(RAW_DIR.iterdir())
    if not docs:
        logger.info("No documents in standards/raw/. Writing built-in standards text.")
        _write_builtin_standards()
        return _count_parsed()

    processed = 0
    for doc_path in docs:
        if doc_path.is_file():
            stem = doc_path.stem
            out_path = PARSED_DIR / f"{stem}.md"

            if doc_path.suffix.lower() in (".pdf", ".docx", ".pptx", ".html"):
                if DOCLING_AVAILABLE:
                    if parse_with_docling(doc_path, out_path):
                        processed += 1
                else:
                    logger.warning("Cannot parse %s without Docling. Skipping.", doc_path.name)
            elif doc_path.suffix.lower() in (".txt", ".md"):
                if parse_text_file(doc_path, out_path):
                    processed += 1

    if processed == 0:
        logger.info("No documents processed. Writing built-in standards text.")
        _write_builtin_standards()

    return _count_parsed()


def _count_parsed() -> int:
    return len(list(PARSED_DIR.glob("*.md")))


def _write_builtin_standards():
    """
    Write built-in regulatory text for all 5 standards bodies.
    These are based on publicly available regulatory text and summaries.
    """
    documents = _get_builtin_standards()
    for filename, content in documents.items():
        path = PARSED_DIR / filename
        path.write_text(content, encoding="utf-8")
        logger.info("Written built-in standard: %s (%d chars)", filename, len(content))


def _get_builtin_standards() -> dict[str, str]:
    """Return built-in standards text for all 5 regulatory bodies."""
    return {
        "fcc_47_cfr_part25.md": _FCC_TEXT,
        "iadc_02_01_rev3.md": _IADC_TEXT,
        "iso_24113_2019.md": _ISO_TEXT,
        "esa_zero_debris_charter.md": _ESA_TEXT,
        "copuos_lts_guidelines.md": _COPUOS_TEXT,
    }


_FCC_TEXT = """# FCC 47 CFR Part 25 — Satellite Disposal Requirements

## FCC 47 CFR Part 25.114(d)(14) — Post-Mission Disposal Requirements

### Adopted Rule (September 2022, FCC 22-74)

For non-geostationary orbit (NGSO) space stations operating in low Earth orbit (LEO)
at or below 2000 km altitude, the space station shall be disposed of within five (5)
years following the end of the space station's mission.

This rule was adopted in the Report and Order FCC 22-74, "Mitigation of Orbital Debris
in the New Space Age," on September 29, 2022. It became effective for new satellite
applications filed after September 29, 2024.

The rule reduces the previous 25-year guideline to 5 years, reflecting the significant
increase in LEO satellite traffic and the need for faster orbital clearance to prevent
the accumulation of debris in heavily-used orbital shells.

### Casualty Risk Assessment Requirement

For uncontrolled atmospheric reentries, the probability of human casualty must not
exceed 1 in 10,000 (1×10⁻⁴). The expected number of casualties from a reentry event,
calculated as the product of the effective casualty area and the world population
density, must satisfy E(c) < 1×10⁻⁴.

Operators must demonstrate compliance with the casualty risk threshold in their
satellite license applications. For satellites that cannot meet this threshold with
uncontrolled reentry, a controlled reentry targeting an uninhabited area must be
planned and executed.

### LEO Definition for Disposal Rules

For purposes of the post-mission disposal rules, LEO is defined as orbital altitudes
at or below 2000 km above the Earth's surface. Non-geostationary orbit space stations
operating above 2000 km are subject to different disposal requirements.

### Enforcement

The FCC has authority to impose forfeitures of up to $100,000 per day per violation
for non-compliance with satellite disposition requirements. The Commission can also
deny license renewals, revoke operating licenses, and initiate proceedings against
operators who fail to dispose of satellites as required.

Source: Federal Communications Commission, 47 CFR Part 25.114(d)(14)
FCC 22-74 (2022), https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites
"""

_IADC_TEXT = """# IADC Space Debris Mitigation Guidelines (IADC-02-01 Rev 3, 2021)

## Inter-Agency Space Debris Coordination Committee

Members: ASI (Italy), CNES (France), CNSA (China), CSA (Canada), DLR (Germany),
ESA (Europe), ISRO (India), JAXA (Japan), KARI (South Korea), NASA (USA),
ROSCOSMOS (Russia), SSA (South Korea), UKSA (United Kingdom)

## Section 5.2.3 — Passivation

To avoid on-orbit break-ups, spacecraft and orbital stages should be passivated
at the end of their operational life. Passivation means the depletion of residual
stored energy sources by:

- Releasing or burning remaining propellants
- Venting all pressurants and pressurized gases
- Discharging all batteries to a safe level
- Spinning down flywheels and momentum wheels

Historical break-up events demonstrate the debris-generation consequences of
non-passivation. The Ariane 44L upper stage explosion in 1986 created more than
500 trackable fragments. The DMSP F-13 satellite battery explosion in 2015 created
a debris cloud of over 100 trackable fragments.

Passivation is one of the most effective mitigation measures for preventing on-orbit
explosions. All operators are strongly encouraged to implement passivation procedures
as a standard end-of-mission practice.

## Section 5.3.1 — Collision Probability During Disposal

During the disposal phase, spacecraft and launch vehicle orbital stages shall be
designed and operated to limit the probability of accidental collision with known
trackable objects. The probability of collision during the disposal maneuver should
not exceed 0.001 (1 in 1,000).

The disposal trajectory should be designed to minimize the crossing of orbital shells
with high concentrations of space objects. Conjunction screening should be performed
before executing disposal maneuvers, and the maneuver should be delayed or modified
if the collision probability exceeds the threshold.

## Section 5.3.2 — Orbital Lifetime Limit (25-Year Rule)

The orbital lifetime after the end of operational life should be limited to 25 years
for objects in the LEO protected region (below 2000 km altitude). This guideline
represents the international consensus of all IADC member agencies on the maximum
acceptable post-mission orbital lifetime for LEO satellites.

The 25-year rule was established to balance the need for orbital clearance against
the practical constraints of natural atmospheric drag. At LEO altitudes below
approximately 600 km, natural atmospheric drag will bring satellites down within
25 years even without active deorbit maneuvers. Above this altitude, active
deorbit maneuvers or disposal to lower orbits are required to meet the guideline.

Note: The US FCC's 5-year rule (47 CFR Part 25.114(d)(14)) is more stringent than
the IADC 25-year guideline for US-licensed operators.

## Section 5.4 — Controlled Atmospheric Reentry

When a controlled atmospheric reentry is required (typically due to casualty risk
from uncontrolled reentry exceeding acceptable thresholds), the disposal maneuver
should target an uninhabited ocean area.

The South Pacific Oceanic Uninhabited Area (SPOUA), also known as Point Nemo, at
approximately 48°52.6′S 123°23.6′W, is the preferred target zone. This location is
the most remote point in the world's oceans, at least 2,688 km from the nearest land.

Operators planning controlled reentries should perform trajectory analysis to verify
that the impact zone falls within the designated target area with high probability,
accounting for orbit determination uncertainty and atmospheric drag variability.

Source: IADC-02-01, Revision 3 (2021), https://www.iadc-home.org/documents_public/
"""

_ISO_TEXT = """# ISO 24113:2019 — Space Systems: Space Debris Mitigation Requirements

## International Organization for Standardization
## Technical Committee ISO/TC 20/SC 14 (Space systems and operations)

## Overview

ISO 24113:2019 specifies the space debris mitigation requirements applicable to
spacecraft and launch vehicle orbital stages to limit the generation of space debris
in Earth orbit. It replaces ISO 24113:2011.

## Section 6.2.2 — Protected Region A (LEO)

The LEO protected orbital region is defined as the spherical shell below an altitude
of 2000 km above the Earth's surface. This region is designated as Protected Region A.

Spacecraft and orbital stages that have completed their operational mission shall not
remain in Protected Region A (below 2000 km altitude) for more than 25 years after
the end of the operational mission. Compliance with this requirement shall be
demonstrated by either:

a) Natural orbital decay within 25 years, verified by orbital lifetime estimation;
b) Active disposal maneuver to either lower the orbit (for natural decay) or to
   perform a controlled atmospheric reentry within the 25-year window.

Orbital lifetime estimation shall account for solar activity variations, atmospheric
density model uncertainty, and satellite area-to-mass ratio.

## Section 6.2.3 — Protected Region B (GEO)

The GEO protected orbital region is defined as the orbital shell within 200 km above
and 200 km below the geostationary orbit altitude of approximately 35,786 km.
This region is designated as Protected Region B.

Spacecraft operated in or near geostationary orbit shall, at the end of the
operational mission, be transferred to a disposal orbit with a perigee no less than
200 km above the GEO protected region. The disposal orbit perigee shall be at a
minimum altitude of 35,786 + 200 + 200 = 36,186 km above the Earth's surface.

The disposal maneuver shall be executed using the remaining propellant in the
onboard propulsion system. Operators shall maintain sufficient propellant reserves
throughout the operational lifetime to perform this final disposal maneuver.

## Section 6.3 — Debris Generation During Operations

Operations in protected orbital regions shall be designed so that they do not
create new debris. In particular:

a) No intentional release of objects in protected orbital regions shall be
   performed unless the released objects can be demonstrated to reenter
   naturally within the 25-year requirement period.

b) The probability of accidental collision during normal operations shall be
   kept below acceptable levels through orbital design, conjunction assessment,
   and collision avoidance maneuvers.

c) On-board stored energy sources shall be passivated at end of operational
   mission to prevent accidental explosions.

Source: ISO 24113:2019 (E), Second Edition, 2019-07
https://www.iso.org/standard/72383.html
"""

_ESA_TEXT = """# ESA Zero Debris Charter (November 2023)

## European Space Agency — Zero Debris Approach

The ESA Zero Debris Charter was adopted at the ESA Space Summit in Seville,
Spain, on November 6, 2023. The charter commits signatories to achieving
near-zero new debris creation by 2030 for missions operating in Earth orbit.

## Commitment 1 — Assessment and Planning

Signatories commit to performing debris mitigation assessments for all missions,
including assessment of collision probability, reentry casualty risk, passivation
requirements, and post-mission disposal options.

## Commitment 2 — No Intentional Debris Release

Signatories commit to ensuring that no intentional debris is released in orbit.
This commitment applies to all orbital altitudes, not just the LEO and GEO
protected regions defined by IADC and ISO standards.

The commitment recognizes that any object released intentionally in orbit becomes
a tracking concern and potential collision hazard. Mission designs shall minimize
or eliminate intentional debris creation, including lens caps, protective covers,
and other ejected hardware.

The target is near-zero intentional debris creation across all orbital regimes
by 2030, consistent with the broader Zero Debris approach adopted by ESA for all
its missions.

## Commitment 3 — Post-Mission Disposal Probability ≥ 90%

Signatories commit to ensuring that the probability of successful post-mission
disposal for all new missions is at least 0.9 (90%). This requirement is more
stringent than the basic IADC and ISO guidelines, which specify post-mission
lifetime but do not mandate a specific reliability threshold for the disposal
operation itself.

The 90% probability threshold shall be demonstrated through:
- Reliability analysis of the disposal propulsion system
- Failure mode and effects analysis (FMEA) for the disposal sequence
- Redundancy analysis for critical disposal system components
- Contingency disposal plans for propulsion system failures

## Commitment 4 — Debris-Free Operations

Signatories commit to debris-free operations throughout the mission lifetime:

a) Collision avoidance capability: All missions shall have the capability to
   perform collision avoidance maneuvers when conjunction data indicates a
   significant collision risk.

b) Space situational awareness data sharing: Operators shall share orbital
   element data with space traffic management providers to support global
   conjunction screening.

c) Zero debris creation during normal operations: Mission design shall
   minimize or eliminate any inadvertent debris creation.

## Signatories (as of 2024)

ESA and all major European national space agencies, as well as commercial
operators including many satellite manufacturers and operators across Europe
and internationally.

Source: ESA Zero Debris Charter, November 2023
https://www.esa.int/Space_Safety/Space_Debris/ESA_s_Zero_Debris_charter
"""

_COPUOS_TEXT = """# UN COPUOS Guidelines for the Long-Term Sustainability of Outer Space Activities
## A/74/20, Annex II (2019)
## United Nations Committee on the Peaceful Uses of Outer Space

The 21 Guidelines for the Long-Term Sustainability of Outer Space Activities were
adopted by the UN Committee on the Peaceful Uses of Outer Space (COPUOS) in June 2019
and endorsed by the UN General Assembly in Resolution 74/82.

## Guideline B.1 — Registration of Space Objects

States and international intergovernmental organizations conducting space activities
should register their space objects with the United Nations Registry of Objects
Launched into Outer Space in accordance with the Convention on Registration of
Objects Launched into Outer Space (1975).

Registration provides: national catalog number, international designator (COSPAR ID),
launching State(s), date and territory of launch, basic orbital parameters, and
general function of the space object.

Timely and complete registration is fundamental to space traffic management.
Unregistered objects cannot be tracked or coordinated with other operators,
increasing the risk of undetected conjunctions and collisions.

The UN Register is maintained by the UN Office for Outer Space Affairs (UNOOSA)
and is publicly accessible at https://www.unoosa.org/oosa/en/spaceobjectregister/

## Guideline B.2 — Sharing of Space Situational Awareness Information

States, international intergovernmental organizations, and operators are encouraged
to share orbital element data and to coordinate conjunction assessments with space
traffic management providers. Sharing of orbital data supports the following:

a) Global conjunction screening to identify potential collisions before they occur;
b) Space traffic management coordination for maneuver planning;
c) Post-event analysis of close approaches and collisions;
d) Development of space traffic management standards and procedures.

Recommended data sharing venues include:
- US Space-Track.org (operated by the 18th Space Defense Squadron)
- EU Space Surveillance and Tracking (EU SST)
- Commercial SSA providers (e.g., LeoLabs, ExoAnalytic)

## Guideline C.1 — Conducting Maneuver Notification

States, international intergovernmental organizations, and operators conducting
maneuvers that would significantly alter conjunction assessment predictions are
encouraged to notify other operators and space traffic management providers.

Best practice guidelines include:
- Providing at least 24 hours advance notice for maneuvers that significantly
  alter orbit predictions
- Coordinating with space traffic management providers before executing
  maneuvers in crowded orbital regions
- Sharing post-maneuver orbital element updates promptly

The notification practice enables other operators to update their conjunction
screening analyses and avoid false-alarm avoidance maneuvers triggered by
the unannounced orbital change.

Source: UN COPUOS LTS Guidelines (A/74/20, Annex II, 2019)
https://www.unoosa.org/oosa/en/ourwork/topics/long-term-sustainability-of-outer-space-activities.html
"""


if __name__ == "__main__":
    count = process_all_documents()
    print(f"Standards corpus ready: {count} documents in standards/parsed/")
