"""
GEDCOM/PAF Genealogy Importer

Imports genealogy data from GEDCOM (.ged) files into the Hypernet.
GEDCOM (Genealogical Data Communication) is the universal standard for
genealogy data exchange, used by PAF (Personal Ancestral File), Ancestry,
FamilySearch, and every other major genealogy program.

Designed to handle massive databases (millions of records) via streaming
line-by-line parsing. No external dependencies required.

Target categories:
    6.1 — Ancient/Classical (before 500 AD)
    6.2 — Medieval/Renaissance (500-1600)
    6.3 — Early Modern (1600-1900)
    6.4 — 20th Century (1900-2000)
    6.5 — 21st Century Deceased (2000+)
    6.6 — Family Lines/Genealogy (family group records)
    6.7 — Notable Historical Figures
    6.8 — Uncategorized/Unknown (no dates)

Usage:
    importer = GenealogyImporter(archive_root, private_root)
    result = importer.import_gedcom("/path/to/database.ged")
    print(result.summary())
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Generator

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)


# ── GEDCOM Date Parsing ──────────────────────────────────────────────

# GEDCOM month abbreviations
GEDCOM_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

# Date modifiers
DATE_MODIFIER_RE = re.compile(
    r"^(ABT|ABOUT|EST|CAL|CALC|BEF|BEFORE|AFT|AFTER|FROM|TO|INT)\s+",
    re.IGNORECASE,
)
DATE_RANGE_RE = re.compile(
    r"^BET\s+(.+?)\s+AND\s+(.+)$",
    re.IGNORECASE,
)
DATE_PERIOD_RE = re.compile(
    r"^FROM\s+(.+?)\s+TO\s+(.+)$",
    re.IGNORECASE,
)


@dataclass
class GedcomDate:
    """Parsed GEDCOM date with original text preserved."""
    original: str = ""
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    modifier: str = ""          # ABT, BEF, AFT, BET, CAL, EST, etc.
    year_end: Optional[int] = None  # For ranges (BET ... AND ...)
    is_approximate: bool = False
    calendar: str = "GREGORIAN"  # GREGORIAN, JULIAN, HEBREW, etc.

    @property
    def sort_year(self) -> Optional[int]:
        """Best guess year for sorting/classification."""
        return self.year

    def to_iso(self) -> str:
        """Best-effort ISO date string."""
        if self.year is None:
            return ""
        parts = [f"{self.year:04d}"]
        if self.month:
            parts.append(f"{self.month:02d}")
            if self.day:
                parts.append(f"{self.day:02d}")
        return "-".join(parts)

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "modifier": self.modifier,
            "year_end": self.year_end,
            "is_approximate": self.is_approximate,
            "iso": self.to_iso(),
        }


def parse_gedcom_date(raw: str) -> GedcomDate:
    """Parse a GEDCOM date string into a GedcomDate object.

    Handles formats like:
        15 MAR 1850
        MAR 1850
        1850
        ABT 1850
        BEF 1900
        AFT 1800
        BET 1850 AND 1860
        CAL 1850
        FROM 1850 TO 1860
        @#DJULIAN@ 1 JAN 1752
    """
    result = GedcomDate(original=raw.strip())
    text = raw.strip()

    if not text:
        return result

    # Handle calendar escape (e.g., @#DJULIAN@ or @#DHEBREW@)
    cal_match = re.match(r"@#D(\w+)@\s*(.*)", text)
    if cal_match:
        result.calendar = cal_match.group(1).upper()
        text = cal_match.group(2).strip()

    # Handle BET ... AND ... ranges
    range_match = DATE_RANGE_RE.match(text)
    if range_match:
        result.modifier = "BET"
        result.is_approximate = True
        start = parse_gedcom_date(range_match.group(1))
        end = parse_gedcom_date(range_match.group(2))
        result.year = start.year
        result.month = start.month
        result.day = start.day
        result.year_end = end.year
        return result

    # Handle FROM ... TO ... periods
    period_match = DATE_PERIOD_RE.match(text)
    if period_match:
        result.modifier = "FROM/TO"
        result.is_approximate = True
        start = parse_gedcom_date(period_match.group(1))
        end = parse_gedcom_date(period_match.group(2))
        result.year = start.year
        result.month = start.month
        result.day = start.day
        result.year_end = end.year
        return result

    # Handle modifiers (ABT, BEF, AFT, CAL, EST, etc.)
    mod_match = DATE_MODIFIER_RE.match(text)
    if mod_match:
        modifier = mod_match.group(1).upper()
        # Normalize
        modifier_map = {
            "ABOUT": "ABT", "BEFORE": "BEF", "AFTER": "AFT",
            "CALC": "CAL",
        }
        result.modifier = modifier_map.get(modifier, modifier)
        result.is_approximate = result.modifier in ("ABT", "EST", "CAL")
        text = text[mod_match.end():].strip()

    # Now parse the actual date: "DD MMM YYYY", "MMM YYYY", or "YYYY"
    _parse_date_components(text, result)

    return result


def _parse_date_components(text: str, result: GedcomDate) -> None:
    """Parse date components from cleaned text (no modifiers)."""
    parts = text.split()

    if not parts:
        return

    # Try "DD MMM YYYY"
    if len(parts) >= 3:
        try:
            day = int(parts[0])
            month = GEDCOM_MONTHS.get(parts[1].upper())
            year = int(parts[2])
            if month and 1 <= day <= 31:
                result.day = day
                result.month = month
                result.year = year
                return
        except (ValueError, IndexError):
            pass

    # Try "MMM YYYY"
    if len(parts) >= 2:
        month = GEDCOM_MONTHS.get(parts[0].upper())
        if month:
            try:
                result.month = month
                result.year = int(parts[1])
                return
            except ValueError:
                pass

    # Try bare "YYYY"
    if len(parts) >= 1:
        try:
            year = int(parts[0])
            if 0 <= year <= 9999:
                result.year = year
                return
        except ValueError:
            pass

    # Could not parse — year remains None, original is preserved


# ── GEDCOM Name Parsing ──────────────────────────────────────────────

@dataclass
class GedcomName:
    """Parsed GEDCOM name with components."""
    full: str = ""
    given: str = ""          # First/given name(s)
    surname: str = ""        # Family name
    prefix: str = ""         # e.g., "Dr.", "Rev."
    suffix: str = ""         # e.g., "Jr.", "III"
    maiden: str = ""         # Maiden name (via _MARNM or MARR context)
    nickname: str = ""       # NICK tag

    def display_name(self) -> str:
        """Formatted display name."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        if self.given:
            parts.append(self.given)
        if self.surname:
            parts.append(self.surname)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts) if parts else self.full

    def to_dict(self) -> dict:
        d = {}
        for key in ("full", "given", "surname", "prefix", "suffix", "maiden", "nickname"):
            val = getattr(self, key)
            if val:
                d[key] = val
        d["display"] = self.display_name()
        return d


def parse_gedcom_name(raw: str) -> GedcomName:
    """Parse a GEDCOM name string.

    GEDCOM format: "Given Names /Surname/ Suffix"
    Examples:
        "John /Smith/"
        "John William /Smith/ Jr."
        "Mary Elizabeth /Anderson/"
        "/Unknown/"
    """
    result = GedcomName(full=raw.strip())
    text = raw.strip()

    if not text:
        return result

    # Extract surname between slashes
    surname_match = re.search(r"/([^/]*)/", text)
    if surname_match:
        result.surname = surname_match.group(1).strip()

        # Everything before the first slash is given name(s)
        before = text[:surname_match.start()].strip()
        # Everything after the last slash is suffix
        after = text[surname_match.end():].strip()

        result.given = before
        if after:
            result.suffix = after
    else:
        # No slashes — treat entire string as given name
        result.given = text

    return result


# ── GEDCOM Parsed Records ───────────────────────────────────────────

@dataclass
class GedcomIndividual:
    """A parsed INDI record from GEDCOM."""
    xref: str = ""                    # e.g., "@I1@"
    names: list = field(default_factory=list)  # list[GedcomName]
    sex: str = ""                     # M, F, U
    birth_date: Optional[GedcomDate] = None
    birth_place: str = ""
    death_date: Optional[GedcomDate] = None
    death_place: str = ""
    burial_place: str = ""
    baptism_date: Optional[GedcomDate] = None
    baptism_place: str = ""
    # LDS ordinances (PAF-specific)
    lds_baptism: str = ""
    lds_endowment: str = ""
    lds_sealing: str = ""
    occupation: str = ""
    note: str = ""
    family_spouse: list = field(default_factory=list)    # FAMS xrefs
    family_child: list = field(default_factory=list)     # FAMC xrefs
    sources: list = field(default_factory=list)          # SOUR xrefs
    custom_tags: dict = field(default_factory=dict)      # _PAFID, etc.
    change_date: str = ""

    @property
    def primary_name(self) -> GedcomName:
        return self.names[0] if self.names else GedcomName()

    @property
    def is_living(self) -> bool:
        """Heuristic: considered living if no death date and born after ~1900."""
        if self.death_date and self.death_date.year is not None:
            return False
        # If birth year is known and recent, likely living
        if self.birth_date and self.birth_date.year:
            return self.birth_date.year > 1900
        # No dates at all — could be living, flag conservatively
        return True

    @property
    def is_deceased(self) -> bool:
        if self.death_date and self.death_date.year is not None:
            return True
        # Very old birth year implies deceased
        if self.birth_date and self.birth_date.year:
            return self.birth_date.year < 1900
        return False

    def classify_era(self) -> str:
        """Classify this person into an era subcategory.

        Returns:
            "6.1" through "6.8" era code
        """
        year = None
        if self.birth_date and self.birth_date.sort_year is not None:
            year = self.birth_date.sort_year
        elif self.death_date and self.death_date.sort_year is not None:
            # If only death year, estimate birth ~30 years before
            year = self.death_date.sort_year - 30

        if year is None:
            return "6.8"  # Uncategorized/Unknown

        if year < 500:
            return "6.1"  # Ancient/Classical
        elif year < 1600:
            return "6.2"  # Medieval/Renaissance
        elif year < 1900:
            return "6.3"  # Early Modern
        elif year < 2000:
            return "6.4"  # 20th Century
        else:
            return "6.5"  # 21st Century Deceased

    def to_dict(self) -> dict:
        d = {
            "xref": self.xref,
            "names": [n.to_dict() for n in self.names],
            "display_name": self.primary_name.display_name(),
            "sex": self.sex,
            "is_living": self.is_living,
            "is_deceased": self.is_deceased,
            "era": self.classify_era(),
        }
        if self.birth_date:
            d["birth"] = {"date": self.birth_date.to_dict(), "place": self.birth_place}
        if self.death_date:
            d["death"] = {"date": self.death_date.to_dict(), "place": self.death_place}
        if self.burial_place:
            d["burial_place"] = self.burial_place
        if self.baptism_date:
            d["baptism"] = {"date": self.baptism_date.to_dict(), "place": self.baptism_place}
        if self.occupation:
            d["occupation"] = self.occupation
        if self.note:
            d["note"] = self.note
        if self.family_spouse:
            d["family_spouse_xrefs"] = self.family_spouse
        if self.family_child:
            d["family_child_xrefs"] = self.family_child
        if self.sources:
            d["source_xrefs"] = self.sources
        if self.custom_tags:
            d["custom_tags"] = self.custom_tags
        if self.lds_baptism or self.lds_endowment or self.lds_sealing:
            d["lds_ordinances"] = {
                k: v for k, v in [
                    ("baptism", self.lds_baptism),
                    ("endowment", self.lds_endowment),
                    ("sealing", self.lds_sealing),
                ] if v
            }
        return d


@dataclass
class GedcomFamily:
    """A parsed FAM record from GEDCOM."""
    xref: str = ""                    # e.g., "@F1@"
    husband_xref: str = ""            # HUSB
    wife_xref: str = ""               # WIFE
    children_xrefs: list = field(default_factory=list)  # CHIL
    marriage_date: Optional[GedcomDate] = None
    marriage_place: str = ""
    divorce_date: Optional[GedcomDate] = None
    divorce_place: str = ""
    lds_sealing: str = ""
    sources: list = field(default_factory=list)
    note: str = ""
    custom_tags: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "xref": self.xref,
            "husband_xref": self.husband_xref,
            "wife_xref": self.wife_xref,
            "children_xrefs": self.children_xrefs,
        }
        if self.marriage_date:
            d["marriage"] = {"date": self.marriage_date.to_dict(), "place": self.marriage_place}
        if self.divorce_date:
            d["divorce"] = {"date": self.divorce_date.to_dict(), "place": self.divorce_place}
        if self.note:
            d["note"] = self.note
        if self.sources:
            d["source_xrefs"] = self.sources
        if self.lds_sealing:
            d["lds_sealing"] = self.lds_sealing
        if self.custom_tags:
            d["custom_tags"] = self.custom_tags
        return d


@dataclass
class GedcomSource:
    """A parsed SOUR record from GEDCOM."""
    xref: str = ""
    title: str = ""
    author: str = ""
    publisher: str = ""
    text: str = ""
    repository: str = ""
    note: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v}


# ── GEDCOM Streaming Parser ─────────────────────────────────────────

# ANSEL to Unicode mapping for the most common characters.
# Full ANSEL has ~200 code points; this covers the ones most likely
# encountered in genealogy data (diacritics on Latin letters).
_ANSEL_MAP = {
    0xA1: "\u0141",  # L with stroke
    0xA2: "\u00D8",  # O with stroke
    0xA3: "\u0110",  # D with stroke
    0xA4: "\u00DE",  # Thorn
    0xA5: "\u00C6",  # AE ligature
    0xA6: "\u0152",  # OE ligature
    0xA7: "\u02B9",  # Soft sign
    0xA8: "\u00B7",  # Middle dot
    0xA9: "\u266D",  # Flat sign
    0xAA: "\u00AE",  # Registered
    0xAB: "\u00B1",  # Plus-minus
    0xAE: "\u02BC",  # Alif/Hamza
    0xB0: "\u02BB",  # Ayn
    0xB1: "\u0142",  # l with stroke
    0xB2: "\u00F8",  # o with stroke
    0xB3: "\u0111",  # d with stroke
    0xB4: "\u00FE",  # thorn
    0xB5: "\u00E6",  # ae ligature
    0xB6: "\u0153",  # oe ligature
    0xB7: "\u02BA",  # Hard sign
    0xB8: "\u0131",  # Dotless i
    0xB9: "\u00A3",  # Pound sign
    0xBA: "\u00F0",  # Eth
    0xC0: "\u00B0",  # Degree (combining hook above)
    0xC1: "\u2113",  # Script l
    0xC2: "\u2117",  # Sound recording copyright
    0xC3: "\u00A9",  # Copyright
    0xC4: "\u266F",  # Sharp sign
    0xC5: "\u00BF",  # Inverted question mark
    0xC6: "\u00A1",  # Inverted exclamation
    0xCF: "\u00DF",  # Sharp s (Eszett)
    # Combining diacritics (ANSEL uses them in precomposed form, but
    # we map the combining byte to Unicode combining characters)
    0xE0: "\u0309",  # Hook above
    0xE1: "\u0300",  # Grave
    0xE2: "\u0301",  # Acute
    0xE3: "\u0302",  # Circumflex
    0xE4: "\u0303",  # Tilde
    0xE5: "\u0304",  # Macron
    0xE6: "\u0306",  # Breve
    0xE7: "\u0307",  # Dot above
    0xE8: "\u0308",  # Diaeresis/Umlaut
    0xE9: "\u030C",  # Caron/Hacek
    0xEA: "\u030A",  # Ring above
    0xED: "\u0327",  # Cedilla
    0xEE: "\u0328",  # Ogonek
    0xF0: "\u0338",  # Stroke
    0xF1: "\u0332",  # Underline
    0xF2: "\u0323",  # Dot below
    0xF3: "\u0324",  # Diaeresis below
    0xF4: "\u0325",  # Ring below
    0xF6: "\u0333",  # Double underline
    0xFE: "\u0313",  # Comma above (smooth breathing)
}


def _decode_ansel(data: bytes) -> str:
    """Best-effort ANSEL to Unicode conversion.

    ANSEL (ANSI/NISO Z39.47) is the default encoding in older GEDCOM files,
    especially those from PAF. Characters 0x00-0x7F are identical to ASCII.
    Characters 0x80+ are mapped via _ANSEL_MAP. Unknown bytes are replaced
    with the Unicode replacement character.
    """
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        if b < 0x80:
            result.append(chr(b))
        elif b in _ANSEL_MAP:
            result.append(_ANSEL_MAP[b])
        else:
            # Unknown ANSEL byte — use replacement character
            result.append("\uFFFD")
        i += 1
    return "".join(result)


@dataclass
class GedcomLine:
    """A single parsed line from a GEDCOM file."""
    level: int
    xref: str       # e.g., "@I1@" or "" if no xref
    tag: str         # e.g., "INDI", "NAME", "DATE"
    value: str       # Everything after the tag


def _parse_line(line: str) -> Optional[GedcomLine]:
    """Parse a single GEDCOM line.

    Format: LEVEL [XREF] TAG [VALUE]
    Examples:
        0 @I1@ INDI
        1 NAME John /Smith/
        2 DATE 15 MAR 1850
        1 _PAFID 12345
    """
    line = line.rstrip("\r\n")
    if not line or not line[0].isdigit():
        return None

    # Split into at most 3 parts for level + rest
    parts = line.split(None, 1)
    if len(parts) < 2:
        return None

    try:
        level = int(parts[0])
    except ValueError:
        return None

    rest = parts[1]

    # Check if next token is an xref (@...@)
    xref = ""
    if rest.startswith("@"):
        xref_end = rest.find("@", 1)
        if xref_end > 0:
            xref = rest[:xref_end + 1]
            rest = rest[xref_end + 1:].lstrip()

    # Split tag from value
    tag_parts = rest.split(None, 1)
    tag = tag_parts[0].upper() if tag_parts else ""
    value = tag_parts[1] if len(tag_parts) > 1 else ""

    return GedcomLine(level=level, xref=xref, tag=tag, value=value)


class GedcomParser:
    """Streaming GEDCOM parser.

    Parses .ged files line-by-line, yielding complete records. Handles
    GEDCOM 5.5 and 5.5.1 formats, ANSEL/UTF-8/ASCII encoding, and
    PAF-specific extensions.

    Designed for massive files — no full-file buffering.
    """

    def __init__(self):
        self.individuals: dict[str, GedcomIndividual] = {}
        self.families: dict[str, GedcomFamily] = {}
        self.sources: dict[str, GedcomSource] = {}
        self.header: dict = {}
        self.encoding: str = "UTF-8"
        self.gedcom_version: str = ""
        self.source_program: str = ""
        self._line_count: int = 0
        self._record_count: int = 0
        self._parse_errors: int = 0

    def parse_file(self, filepath: str | Path) -> None:
        """Parse a GEDCOM file.

        Detects encoding from the HEAD record, then re-reads if needed.
        For very large files, this streams line by line.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"GEDCOM file not found: {filepath}")

        file_size = filepath.stat().st_size
        log.info("Parsing GEDCOM file: %s (%.1f MB)", filepath.name,
                 file_size / (1024 * 1024))

        # First pass: detect encoding from HEAD
        encoding = self._detect_encoding(filepath)
        self.encoding = encoding
        log.info("Detected encoding: %s", encoding)

        # Main parse
        lines = self._read_lines(filepath, encoding)
        self._parse_lines(lines)

        log.info(
            "Parsed %d lines, %d records: %d individuals, %d families, "
            "%d sources (%d errors)",
            self._line_count, self._record_count,
            len(self.individuals), len(self.families),
            len(self.sources), self._parse_errors,
        )

    def _detect_encoding(self, filepath: Path) -> str:
        """Detect file encoding from the GEDCOM HEAD record.

        GEDCOM specifies encoding via:
            1 CHAR UTF-8
            1 CHAR ANSEL
            1 CHAR ASCII
            1 CHAR UNICODE (UTF-16)

        Also checks for BOM (Byte Order Mark).
        """
        # Check BOM
        with open(filepath, "rb") as f:
            bom = f.read(4)

        if bom[:3] == b"\xef\xbb\xbf":
            return "utf-8-sig"
        if bom[:2] in (b"\xff\xfe", b"\xfe\xff"):
            return "utf-16"

        # Read first ~50 lines looking for CHAR tag
        try:
            with open(filepath, "r", encoding="ascii", errors="replace") as f:
                for i, line in enumerate(f):
                    if i > 100:
                        break
                    line = line.strip()
                    if line.startswith("1 CHAR"):
                        parts = line.split(None, 2)
                        if len(parts) >= 3:
                            charset = parts[2].upper().strip()
                            if charset in ("UTF-8", "UTF8"):
                                return "utf-8"
                            elif charset == "ANSEL":
                                return "ANSEL"
                            elif charset == "ASCII":
                                return "ascii"
                            elif charset in ("UNICODE", "UTF-16"):
                                return "utf-16"
                            elif charset == "ANSI":
                                return "cp1252"
        except Exception:
            pass

        # Default: try UTF-8, fall back to latin-1
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                f.read(4096)
            return "utf-8"
        except UnicodeDecodeError:
            return "cp1252"

    def _read_lines(self, filepath: Path, encoding: str) -> Generator[str, None, None]:
        """Read lines from a GEDCOM file with encoding handling."""
        if encoding == "ANSEL":
            # Read as bytes and decode via ANSEL mapper
            with open(filepath, "rb") as f:
                buffer = b""
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        if buffer:
                            yield _decode_ansel(buffer)
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line_bytes, buffer = buffer.split(b"\n", 1)
                        yield _decode_ansel(line_bytes)
        else:
            with open(filepath, "r", encoding=encoding, errors="replace") as f:
                for line in f:
                    yield line

    def _parse_lines(self, lines: Generator[str, None, None]) -> None:
        """Parse all lines from the GEDCOM file into records."""
        current_record_lines: list[GedcomLine] = []
        current_level0_tag: str = ""
        current_level0_xref: str = ""

        for raw_line in lines:
            self._line_count += 1

            parsed = _parse_line(raw_line)
            if parsed is None:
                continue

            if parsed.level == 0:
                # Flush previous record
                if current_record_lines:
                    self._process_record(
                        current_level0_xref,
                        current_level0_tag,
                        current_record_lines,
                    )

                current_level0_xref = parsed.xref
                current_level0_tag = parsed.tag if not parsed.xref else parsed.value.split()[0] if parsed.value else parsed.tag
                # For level-0 lines with xref: "0 @I1@ INDI" -> tag is in value
                if parsed.xref:
                    # The tag is actually the value portion
                    current_level0_tag = parsed.tag  # Already parsed correctly
                current_record_lines = [parsed]
                self._record_count += 1
            else:
                current_record_lines.append(parsed)

            # Progress logging for large files
            if self._line_count % 500000 == 0:
                log.info("  ...parsed %d lines (%d individuals, %d families)",
                         self._line_count, len(self.individuals),
                         len(self.families))

        # Flush last record
        if current_record_lines:
            self._process_record(
                current_level0_xref,
                current_level0_tag,
                current_record_lines,
            )

    def _process_record(self, xref: str, tag: str, lines: list[GedcomLine]) -> None:
        """Process a complete level-0 record."""
        try:
            if tag == "INDI":
                indi = self._parse_individual(xref, lines)
                self.individuals[xref] = indi
            elif tag == "FAM":
                fam = self._parse_family(xref, lines)
                self.families[xref] = fam
            elif tag == "SOUR" and xref:
                src = self._parse_source(xref, lines)
                self.sources[xref] = src
            elif tag == "HEAD":
                self._parse_header(lines)
            # TRLR, NOTE, REPO, SUBM, SUBN — skip
        except Exception as e:
            self._parse_errors += 1
            if self._parse_errors <= 20:
                log.warning("Error parsing %s %s at line ~%d: %s",
                            tag, xref, self._line_count, e)

    def _parse_individual(self, xref: str, lines: list[GedcomLine]) -> GedcomIndividual:
        """Parse an INDI record into a GedcomIndividual."""
        indi = GedcomIndividual(xref=xref)
        current_event = ""     # BIRT, DEAT, BAPM, BURI, CHR, etc.
        current_name: Optional[GedcomName] = None
        in_name_block = False

        for gl in lines:
            tag = gl.tag
            val = gl.value.strip()
            level = gl.level

            # Level 1 tags
            if level == 1:
                current_event = ""
                in_name_block = False

                if tag == "NAME":
                    current_name = parse_gedcom_name(val)
                    indi.names.append(current_name)
                    in_name_block = True
                elif tag == "SEX":
                    indi.sex = val.upper()[:1]
                elif tag == "BIRT":
                    current_event = "BIRT"
                elif tag == "DEAT":
                    current_event = "DEAT"
                    # A DEAT tag with no sub-records still means deceased
                    if indi.death_date is None:
                        indi.death_date = GedcomDate(original="Y" if val.upper() == "Y" else "")
                elif tag == "BURI":
                    current_event = "BURI"
                elif tag in ("BAPM", "CHR"):
                    current_event = "BAPM"
                elif tag == "FAMS":
                    indi.family_spouse.append(val)
                elif tag == "FAMC":
                    indi.family_child.append(val)
                elif tag == "SOUR":
                    indi.sources.append(val)
                elif tag == "OCCU":
                    indi.occupation = val
                elif tag == "NOTE":
                    indi.note = val
                elif tag == "CHAN":
                    current_event = "CHAN"
                elif tag == "NICK":
                    if indi.names:
                        indi.names[-1].nickname = val
                # LDS ordinances
                elif tag == "BAPL":
                    current_event = "BAPL"
                elif tag == "ENDL":
                    current_event = "ENDL"
                elif tag == "SLGC":
                    current_event = "SLGC"
                # PAF and custom tags (start with _)
                elif tag.startswith("_"):
                    indi.custom_tags[tag] = val

            # Level 2 tags (sub-records)
            elif level == 2:
                if in_name_block and current_name:
                    if tag == "GIVN":
                        current_name.given = val
                    elif tag == "SURN":
                        current_name.surname = val
                    elif tag == "NPFX":
                        current_name.prefix = val
                    elif tag == "NSFX":
                        current_name.suffix = val
                    elif tag == "NICK":
                        current_name.nickname = val
                    elif tag == "_MARNM":
                        current_name.maiden = current_name.surname
                        current_name.surname = val

                if tag == "DATE":
                    parsed_date = parse_gedcom_date(val)
                    if current_event == "BIRT":
                        indi.birth_date = parsed_date
                    elif current_event == "DEAT":
                        indi.death_date = parsed_date
                    elif current_event == "BAPM":
                        indi.baptism_date = parsed_date
                    elif current_event == "CHAN":
                        indi.change_date = val
                elif tag == "PLAC":
                    if current_event == "BIRT":
                        indi.birth_place = val
                    elif current_event == "DEAT":
                        indi.death_place = val
                    elif current_event == "BURI":
                        indi.burial_place = val
                    elif current_event == "BAPM":
                        indi.baptism_place = val
                elif tag == "STAT":
                    if current_event == "BAPL":
                        indi.lds_baptism = val
                    elif current_event == "ENDL":
                        indi.lds_endowment = val
                    elif current_event == "SLGC":
                        indi.lds_sealing = val
                elif tag == "CONC":
                    # Concatenation (no space)
                    if current_event == "" and indi.note:
                        indi.note += val
                elif tag == "CONT":
                    # Continuation (with newline)
                    if current_event == "" and indi.note:
                        indi.note += "\n" + val
                elif tag.startswith("_"):
                    indi.custom_tags[tag] = val

        return indi

    def _parse_family(self, xref: str, lines: list[GedcomLine]) -> GedcomFamily:
        """Parse a FAM record into a GedcomFamily."""
        fam = GedcomFamily(xref=xref)
        current_event = ""

        for gl in lines:
            tag = gl.tag
            val = gl.value.strip()
            level = gl.level

            if level == 1:
                current_event = ""

                if tag == "HUSB":
                    fam.husband_xref = val
                elif tag == "WIFE":
                    fam.wife_xref = val
                elif tag == "CHIL":
                    fam.children_xrefs.append(val)
                elif tag == "MARR":
                    current_event = "MARR"
                elif tag == "DIV":
                    current_event = "DIV"
                elif tag == "SOUR":
                    fam.sources.append(val)
                elif tag == "NOTE":
                    fam.note = val
                elif tag == "SLGS":
                    current_event = "SLGS"
                elif tag.startswith("_"):
                    fam.custom_tags[tag] = val

            elif level == 2:
                if tag == "DATE":
                    parsed_date = parse_gedcom_date(val)
                    if current_event == "MARR":
                        fam.marriage_date = parsed_date
                    elif current_event == "DIV":
                        fam.divorce_date = parsed_date
                elif tag == "PLAC":
                    if current_event == "MARR":
                        fam.marriage_place = val
                    elif current_event == "DIV":
                        fam.divorce_place = val
                elif tag == "STAT" and current_event == "SLGS":
                    fam.lds_sealing = val
                elif tag.startswith("_"):
                    fam.custom_tags[tag] = val

        return fam

    def _parse_source(self, xref: str, lines: list[GedcomLine]) -> GedcomSource:
        """Parse a SOUR record into a GedcomSource."""
        src = GedcomSource(xref=xref)
        current_tag = ""

        for gl in lines:
            tag = gl.tag
            val = gl.value.strip()
            level = gl.level

            if level == 1:
                current_tag = tag
                if tag == "TITL":
                    src.title = val
                elif tag == "AUTH":
                    src.author = val
                elif tag == "PUBL":
                    src.publisher = val
                elif tag == "TEXT":
                    src.text = val
                elif tag == "REPO":
                    src.repository = val
                elif tag == "NOTE":
                    src.note = val

            elif level == 2:
                if tag == "CONC":
                    if current_tag == "TITL":
                        src.title += val
                    elif current_tag == "TEXT":
                        src.text += val
                elif tag == "CONT":
                    if current_tag == "TITL":
                        src.title += "\n" + val
                    elif current_tag == "TEXT":
                        src.text += "\n" + val

        return src

    def _parse_header(self, lines: list[GedcomLine]) -> None:
        """Parse the HEAD record for metadata."""
        current_sub = ""

        for gl in lines:
            tag = gl.tag
            val = gl.value.strip()
            level = gl.level

            if level == 1:
                current_sub = tag
                if tag == "SOUR":
                    self.source_program = val
                    self.header["source"] = val
                elif tag == "CHAR":
                    self.header["charset"] = val
                elif tag == "GEDC":
                    current_sub = "GEDC"
                elif tag == "FILE":
                    self.header["filename"] = val
                elif tag == "NOTE":
                    self.header["note"] = val
                elif tag == "DEST":
                    self.header["destination"] = val
                elif tag == "DATE":
                    self.header["date"] = val
                elif tag == "SUBM":
                    self.header["submitter"] = val
                elif tag == "LANG":
                    self.header["language"] = val

            elif level == 2:
                if current_sub == "SOUR" and tag == "VERS":
                    self.header["source_version"] = val
                elif current_sub == "SOUR" and tag == "NAME":
                    self.header["source_name"] = val
                elif current_sub == "GEDC" and tag == "VERS":
                    self.gedcom_version = val
                    self.header["gedcom_version"] = val
                elif current_sub == "GEDC" and tag == "FORM":
                    self.header["gedcom_form"] = val


# ── Import Statistics ────────────────────────────────────────────────

@dataclass
class GenealogyStats:
    """Statistics from a genealogy import."""
    total_individuals: int = 0
    total_families: int = 0
    total_sources: int = 0
    living_count: int = 0
    deceased_count: int = 0
    unknown_status_count: int = 0
    era_distribution: dict = field(default_factory=dict)
    sex_distribution: dict = field(default_factory=dict)
    geographic_distribution: dict = field(default_factory=dict)
    largest_families: list = field(default_factory=list)
    date_range: dict = field(default_factory=dict)
    source_program: str = ""
    gedcom_version: str = ""
    encoding: str = ""
    parse_errors: int = 0
    import_duration_seconds: float = 0.0

    def summary(self) -> dict:
        return asdict(self)


def compute_stats(parser: GedcomParser) -> GenealogyStats:
    """Compute comprehensive statistics from parsed GEDCOM data."""
    stats = GenealogyStats(
        total_individuals=len(parser.individuals),
        total_families=len(parser.families),
        total_sources=len(parser.sources),
        source_program=parser.source_program,
        gedcom_version=parser.gedcom_version,
        encoding=parser.encoding,
        parse_errors=parser._parse_errors,
    )

    era_counts = defaultdict(int)
    sex_counts = defaultdict(int)
    place_counts = defaultdict(int)
    min_year = 9999
    max_year = 0

    for indi in parser.individuals.values():
        # Living/deceased classification
        if indi.is_deceased:
            stats.deceased_count += 1
        elif indi.is_living:
            stats.living_count += 1
        else:
            stats.unknown_status_count += 1

        # Era
        era = indi.classify_era()
        era_counts[era] += 1

        # Sex
        sex = indi.sex or "U"
        sex_counts[sex] += 1

        # Geographic distribution (from birth place — use country/state)
        if indi.birth_place:
            parts = [p.strip() for p in indi.birth_place.split(",")]
            if parts:
                # Use last component (usually country or state)
                location = parts[-1] if len(parts) > 1 else parts[0]
                place_counts[location] += 1

        # Date range
        for d in (indi.birth_date, indi.death_date):
            if d and d.sort_year is not None:
                if d.sort_year < min_year:
                    min_year = d.sort_year
                if d.sort_year > max_year:
                    max_year = d.sort_year

    ERA_LABELS = {
        "6.1": "Ancient/Classical (before 500 AD)",
        "6.2": "Medieval/Renaissance (500-1600)",
        "6.3": "Early Modern (1600-1900)",
        "6.4": "20th Century (1900-2000)",
        "6.5": "21st Century Deceased (2000+)",
        "6.6": "Family Lines/Genealogy",
        "6.7": "Notable Historical Figures",
        "6.8": "Uncategorized/Unknown",
    }
    stats.era_distribution = {
        f"{era} ({ERA_LABELS.get(era, era)})": count
        for era, count in sorted(era_counts.items())
    }

    stats.sex_distribution = dict(sorted(sex_counts.items()))

    # Top 20 locations
    stats.geographic_distribution = dict(
        sorted(place_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    )

    # Largest families by number of children
    fam_sizes = []
    for fam in parser.families.values():
        child_count = len(fam.children_xrefs)
        if child_count > 0:
            husb_name = ""
            wife_name = ""
            if fam.husband_xref in parser.individuals:
                husb_name = parser.individuals[fam.husband_xref].primary_name.display_name()
            if fam.wife_xref in parser.individuals:
                wife_name = parser.individuals[fam.wife_xref].primary_name.display_name()
            fam_sizes.append({
                "family": f"{husb_name} & {wife_name}".strip(" &"),
                "xref": fam.xref,
                "children": child_count,
            })
    stats.largest_families = sorted(fam_sizes, key=lambda x: x["children"], reverse=True)[:20]

    if min_year < 9999:
        stats.date_range = {"earliest": min_year, "latest": max_year}

    return stats


# ── Relationship Link Builder ────────────────────────────────────────

@dataclass
class RelationshipLink:
    """A relationship link between two individuals."""
    link_type: str       # parent_of, child_of, spouse_of, sibling_of
    from_xref: str
    to_xref: str
    from_name: str = ""
    to_name: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "type": self.link_type,
            "from_xref": self.from_xref,
            "to_xref": self.to_xref,
        }
        if self.from_name:
            d["from_name"] = self.from_name
        if self.to_name:
            d["to_name"] = self.to_name
        if self.metadata:
            d["metadata"] = self.metadata
        return d


def build_relationship_links(parser: GedcomParser) -> list[RelationshipLink]:
    """Build all relationship links from parsed family records.

    For each family (FAM) record, creates:
    - spouse_of links between husband and wife
    - parent_of links from each parent to each child
    - child_of links from each child to each parent
    - sibling_of links between children in the same family
    """
    links: list[RelationshipLink] = []

    def _name(xref: str) -> str:
        indi = parser.individuals.get(xref)
        return indi.primary_name.display_name() if indi else ""

    for fam in parser.families.values():
        husb = fam.husband_xref
        wife = fam.wife_xref

        # Spouse links
        if husb and wife:
            meta = {}
            if fam.marriage_date:
                meta["marriage_date"] = fam.marriage_date.to_dict()
            if fam.marriage_place:
                meta["marriage_place"] = fam.marriage_place
            if fam.divorce_date:
                meta["divorced"] = True
                meta["divorce_date"] = fam.divorce_date.to_dict()

            links.append(RelationshipLink(
                link_type="spouse_of",
                from_xref=husb, to_xref=wife,
                from_name=_name(husb), to_name=_name(wife),
                metadata=meta,
            ))
            links.append(RelationshipLink(
                link_type="spouse_of",
                from_xref=wife, to_xref=husb,
                from_name=_name(wife), to_name=_name(husb),
                metadata=meta,
            ))

        # Parent-child links
        parents = [x for x in (husb, wife) if x]
        children = fam.children_xrefs

        for parent_xref in parents:
            for child_xref in children:
                links.append(RelationshipLink(
                    link_type="parent_of",
                    from_xref=parent_xref, to_xref=child_xref,
                    from_name=_name(parent_xref), to_name=_name(child_xref),
                    metadata={"family_xref": fam.xref},
                ))
                links.append(RelationshipLink(
                    link_type="child_of",
                    from_xref=child_xref, to_xref=parent_xref,
                    from_name=_name(child_xref), to_name=_name(parent_xref),
                    metadata={"family_xref": fam.xref},
                ))

        # Sibling links (between all children in the family)
        for i, child_a in enumerate(children):
            for child_b in children[i + 1:]:
                links.append(RelationshipLink(
                    link_type="sibling_of",
                    from_xref=child_a, to_xref=child_b,
                    from_name=_name(child_a), to_name=_name(child_b),
                    metadata={"family_xref": fam.xref},
                ))
                links.append(RelationshipLink(
                    link_type="sibling_of",
                    from_xref=child_b, to_xref=child_a,
                    from_name=_name(child_b), to_name=_name(child_a),
                    metadata={"family_xref": fam.xref},
                ))

    return links


# ── Place Parsing ────────────────────────────────────────────────────

@dataclass
class ParsedPlace:
    """A parsed hierarchical place."""
    original: str = ""
    city: str = ""
    county: str = ""
    state: str = ""
    country: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v}


def parse_place(raw: str) -> ParsedPlace:
    """Parse a GEDCOM place string.

    GEDCOM places are comma-separated, typically:
        City, County, State/Province, Country
    But the number of components varies widely.
    """
    result = ParsedPlace(original=raw)
    if not raw:
        return result

    parts = [p.strip() for p in raw.split(",")]
    parts = [p for p in parts if p]  # remove empty

    if len(parts) >= 4:
        result.city = parts[0]
        result.county = parts[1]
        result.state = parts[2]
        result.country = parts[3]
    elif len(parts) == 3:
        result.city = parts[0]
        result.state = parts[1]
        result.country = parts[2]
    elif len(parts) == 2:
        result.city = parts[0]
        result.country = parts[1]
    elif len(parts) == 1:
        result.country = parts[0]

    return result


# ── GenealogyImporter (BaseConnector) ────────────────────────────────

@dataclass
class GenealogyImportResult:
    """Full result of a genealogy import operation."""
    total_individuals: int = 0
    total_families: int = 0
    total_sources: int = 0
    total_links: int = 0
    individuals_imported: int = 0
    families_imported: int = 0
    links_created: int = 0
    living_flagged: int = 0
    errors: list = field(default_factory=list)
    stats: Optional[GenealogyStats] = None
    duration_seconds: float = 0.0

    def summary(self) -> dict:
        return {
            "total_individuals": self.total_individuals,
            "total_families": self.total_families,
            "total_sources": self.total_sources,
            "total_links": self.total_links,
            "individuals_imported": self.individuals_imported,
            "families_imported": self.families_imported,
            "links_created": self.links_created,
            "living_flagged": self.living_flagged,
            "errors": len(self.errors),
            "duration_seconds": round(self.duration_seconds, 2),
        }


class GenealogyImporter(BaseConnector):
    """Imports GEDCOM genealogy data into the Hypernet.

    Parses .ged files (PAF, Ancestry, FamilySearch, etc.) and creates
    Hypernet nodes for each person, organized by era into the
    '6 - People of History' category.

    Living people are flagged for privacy and linked to '1 - People'
    rather than exposed publicly.
    """

    source_type = "genealogy"
    source_name = "GEDCOM/PAF"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._gedcom_path: Optional[Path] = None
        self._parser: Optional[GedcomParser] = None
        self._stats: Optional[GenealogyStats] = None
        self._import_result: Optional[GenealogyImportResult] = None
        self._data_dir = self.staging_dir / "genealogy"
        self._search_index: dict = {}  # surname -> list of xrefs
        # Contribution attribution (defaults per Matt's directive)
        self._contributor_name: str = "Larry Anderson"
        self._source_name: str = "PAF Database"

    def authenticate(self) -> AuthStatus:
        """No auth needed — just check if GEDCOM file exists."""
        if self._gedcom_path and self._gedcom_path.exists():
            return AuthStatus.AUTHENTICATED
        return AuthStatus.NOT_CONFIGURED

    def configure(self, gedcom_path: str) -> None:
        """Set the path to the GEDCOM file."""
        self._gedcom_path = Path(gedcom_path)

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan GEDCOM file and return individual records as RawItems."""
        if not self._gedcom_path or not self._gedcom_path.exists():
            return ScanResult(source_platform="gedcom", errors=1)

        # Parse if not already done
        if self._parser is None:
            self._parser = GedcomParser()
            self._parser.parse_file(self._gedcom_path)

        items: list[RawItem] = []
        total = len(self._parser.individuals)

        for xref, indi in self._parser.individuals.items():
            if len(items) >= max_items:
                break

            name = indi.primary_name.display_name()
            content = json.dumps(indi.to_dict(), indent=2, default=str)

            item = RawItem(
                source_type="genealogy_individual",
                source_id=xref,
                source_platform="gedcom",
                title=name,
                content=content,
                metadata={
                    "sex": indi.sex,
                    "era": indi.classify_era(),
                    "is_living": indi.is_living,
                    "birth_year": indi.birth_date.sort_year if indi.birth_date else None,
                    "death_year": indi.death_date.sort_year if indi.death_date else None,
                },
            )
            item.compute_hash()

            if not self.is_duplicate(item):
                items.append(item)

        return ScanResult(
            source_platform="gedcom",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a single genealogy individual as a Hypernet node."""
        try:
            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "gedcom",
                "content_hash": item.content_hash,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "contributed_by": {
                    "name": self._contributor_name,
                    "source": self._source_name,
                    "imported_at": datetime.now(timezone.utc).isoformat(),
                },
            }

            # Merge in the full individual data
            try:
                indi_data = json.loads(item.content)
                node_data["individual"] = indi_data
            except (json.JSONDecodeError, TypeError):
                node_data["raw_content"] = item.content

            # Add privacy flag for living individuals
            if item.metadata.get("is_living"):
                node_data["privacy"] = {
                    "is_living": True,
                    "consent_required": True,
                    "public_display": False,
                }

            stage_path = self._data_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({"target_address": target_address, "data": node_data}, indent=2),
                encoding="utf-8",
            )

            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.IMPORTED,
                hypernet_address=target_address,
            )
        except Exception as e:
            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.FAILED,
                error=str(e),
            )

    def import_gedcom(
        self,
        path: str,
        max_items: int = 0,
        contributor_name: str = "Larry Anderson",
        source_name: str = "PAF Database",
    ) -> GenealogyImportResult:
        """Main entry point: parse and import a GEDCOM file.

        Args:
            path: Path to .ged file
            max_items: Maximum individuals to import (0 = unlimited)
            contributor_name: Name of the person who contributed this data.
                Default: "Larry Anderson" — Larry gets credit for everything
                imported from the PAF database (Matt's directive).
            source_name: Name of the data source (default: "PAF Database")

        Returns:
            GenealogyImportResult with full statistics
        """
        start_time = time.time()
        result = GenealogyImportResult()

        # Set contributor attribution for all nodes created during this import
        self._contributor_name = contributor_name
        self._source_name = source_name

        self.configure(path)
        if not self._gedcom_path.exists():
            result.errors.append(f"File not found: {path}")
            return result

        # Parse the GEDCOM file
        log.info("Starting GEDCOM import: %s", path)
        self._parser = GedcomParser()
        try:
            self._parser.parse_file(self._gedcom_path)
        except Exception as e:
            result.errors.append(f"Parse error: {e}")
            result.duration_seconds = time.time() - start_time
            return result

        result.total_individuals = len(self._parser.individuals)
        result.total_families = len(self._parser.families)
        result.total_sources = len(self._parser.sources)

        # Build relationship links
        links = build_relationship_links(self._parser)
        result.total_links = len(links)

        # Import individuals
        count = 0
        for xref, indi in self._parser.individuals.items():
            if max_items > 0 and count >= max_items:
                break

            era = indi.classify_era()
            name = indi.primary_name.display_name()
            safe_id = re.sub(r"[^a-zA-Z0-9]", "", xref)

            if indi.is_living:
                # Living people go to private staging, flagged for 1 - People linking
                target = f"1.pending.genealogy.{safe_id}"
                result.living_flagged += 1
            else:
                target = f"{era}.{safe_id}"

            content = json.dumps(indi.to_dict(), indent=2, default=str)
            item = RawItem(
                source_type="genealogy_individual",
                source_id=xref,
                source_platform="gedcom",
                title=name,
                content=content,
                metadata={
                    "sex": indi.sex,
                    "era": era,
                    "is_living": indi.is_living,
                },
            )
            item.compute_hash()

            if self.is_duplicate(item):
                continue

            import_result = self.import_item(item, target)
            if import_result.status == ImportStatus.IMPORTED:
                result.individuals_imported += 1
                self.mark_imported(item)
            elif import_result.status == ImportStatus.FAILED:
                result.errors.append(f"{xref}: {import_result.error}")

            count += 1

            # Save dedup index periodically
            if count % 500 == 0:
                self._save_dedup_index()
                log.info("  ...imported %d/%d individuals", count, result.total_individuals)

        # Import family records
        self._import_families(result)

        # Import relationship links
        self._import_links(links, result)

        # Build search index
        self._build_search_index()

        # Compute stats
        self._stats = compute_stats(self._parser)
        self._stats.import_duration_seconds = time.time() - start_time
        result.stats = self._stats
        result.duration_seconds = time.time() - start_time

        # Save the dedup index
        self._save_dedup_index()

        # Save stats and search index
        self._save_metadata(result)

        self._import_result = result

        log.info(
            "GEDCOM import complete: %d individuals, %d families, %d links "
            "in %.1f seconds (%d living flagged, %d errors)",
            result.individuals_imported, result.families_imported,
            result.links_created, result.duration_seconds,
            result.living_flagged, len(result.errors),
        )

        return result

    def _import_families(self, result: GenealogyImportResult) -> None:
        """Import family group records into 6.6."""
        for xref, fam in self._parser.families.items():
            try:
                safe_id = re.sub(r"[^a-zA-Z0-9]", "", xref)
                target = f"6.6.{safe_id}"

                fam_data = fam.to_dict()

                # Resolve names for readability
                if fam.husband_xref in self._parser.individuals:
                    fam_data["husband_name"] = (
                        self._parser.individuals[fam.husband_xref]
                        .primary_name.display_name()
                    )
                if fam.wife_xref in self._parser.individuals:
                    fam_data["wife_name"] = (
                        self._parser.individuals[fam.wife_xref]
                        .primary_name.display_name()
                    )
                children_names = []
                for child_xref in fam.children_xrefs:
                    if child_xref in self._parser.individuals:
                        children_names.append(
                            self._parser.individuals[child_xref]
                            .primary_name.display_name()
                        )
                if children_names:
                    fam_data["children_names"] = children_names

                node_data = {
                    "title": f"Family: {fam_data.get('husband_name', '?')} & "
                             f"{fam_data.get('wife_name', '?')}",
                    "source_type": "genealogy_family",
                    "source_platform": "gedcom",
                    "family": fam_data,
                    "imported_at": datetime.now(timezone.utc).isoformat(),
                    "contributed_by": {
                        "name": self._contributor_name,
                        "source": self._source_name,
                        "imported_at": datetime.now(timezone.utc).isoformat(),
                    },
                }

                stage_path = self._data_dir / f"fam_{safe_id}.json"
                stage_path.parent.mkdir(parents=True, exist_ok=True)
                stage_path.write_text(
                    json.dumps({"target_address": target, "data": node_data}, indent=2),
                    encoding="utf-8",
                )

                result.families_imported += 1

            except Exception as e:
                result.errors.append(f"Family {xref}: {e}")

    def _import_links(self, links: list[RelationshipLink],
                      result: GenealogyImportResult) -> None:
        """Save relationship links to a JSON file for later indexing."""
        try:
            links_data = [link.to_dict() for link in links]

            links_path = self._data_dir / "relationship_links.json"
            links_path.parent.mkdir(parents=True, exist_ok=True)

            # For very large link sets, write in streaming fashion
            with open(links_path, "w", encoding="utf-8") as f:
                f.write("[\n")
                for i, link_dict in enumerate(links_data):
                    if i > 0:
                        f.write(",\n")
                    json.dump(link_dict, f)
                f.write("\n]")

            result.links_created = len(links)

        except Exception as e:
            result.errors.append(f"Links export: {e}")

    def _build_search_index(self) -> None:
        """Build a surname-based search index for fast lookups."""
        self._search_index = defaultdict(list)

        for xref, indi in self._parser.individuals.items():
            for name in indi.names:
                if name.surname:
                    key = name.surname.upper()
                    self._search_index[key].append(xref)
                if name.given:
                    key = name.given.split()[0].upper() if name.given else ""
                    if key:
                        self._search_index[key].append(xref)

    def _save_metadata(self, result: GenealogyImportResult) -> None:
        """Save import stats, search index, and contribution record to disk."""
        self._data_dir.mkdir(parents=True, exist_ok=True)

        # Stats
        stats_path = self._data_dir / "import_stats.json"
        stats_data = result.stats.summary() if result.stats else {}
        stats_data["import_summary"] = result.summary()
        stats_path.write_text(
            json.dumps(stats_data, indent=2, default=str),
            encoding="utf-8",
        )

        # Search index
        index_path = self._data_dir / "search_index.json"
        index_data = {k: v for k, v in self._search_index.items()}
        index_path.write_text(
            json.dumps(index_data, indent=2),
            encoding="utf-8",
        )

        # Source mapping (xref -> display name + era)
        name_map = {}
        for xref, indi in self._parser.individuals.items():
            name_map[xref] = {
                "name": indi.primary_name.display_name(),
                "era": indi.classify_era(),
                "living": indi.is_living,
            }
        names_path = self._data_dir / "name_index.json"
        names_path.write_text(
            json.dumps(name_map, indent=2),
            encoding="utf-8",
        )

        # Contribution summary record — credits the contributor
        now = datetime.now(timezone.utc)
        date_stamp = now.strftime("%Y%m%d")
        total_records = (
            result.individuals_imported
            + result.families_imported
            + result.links_created
        )
        contribution_record = {
            "ha": f"6.0.contributions.paf-import-{date_stamp}",
            "object_type": "contribution-record",
            "contributor": self._contributor_name,
            "relation_to_owner": "Father of Sarah (1.2)",
            "source": f"Personal Ancestral File ({self._source_name})",
            "records_imported": total_records,
            "individuals_imported": result.individuals_imported,
            "families_imported": result.families_imported,
            "links_created": result.links_created,
            "living_flagged": result.living_flagged,
            "date_imported": now.isoformat(),
            "note": (
                "One of the largest personal ancestral databases, "
                f"compiled by {self._contributor_name} over decades"
            ),
        }
        contrib_path = self._data_dir / f"contribution-record-{date_stamp}.json"
        contrib_path.write_text(
            json.dumps(contribution_record, indent=2),
            encoding="utf-8",
        )
        log.info(
            "Contribution record saved: %s credited with %d records",
            self._contributor_name, total_records,
        )

    def search(self, query: str, max_results: int = 50) -> list[dict]:
        """Search imported individuals by name.

        Args:
            query: Name or partial name to search for
            max_results: Maximum results to return

        Returns:
            List of matching individual summaries
        """
        # Load search index if needed
        if not self._search_index:
            index_path = self._data_dir / "search_index.json"
            if index_path.exists():
                try:
                    self._search_index = json.loads(
                        index_path.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    return []
            else:
                return []

        # Load name index
        names_path = self._data_dir / "name_index.json"
        name_map = {}
        if names_path.exists():
            try:
                name_map = json.loads(names_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Search
        query_upper = query.strip().upper()
        matching_xrefs = set()

        # Exact key match
        if query_upper in self._search_index:
            matching_xrefs.update(self._search_index[query_upper])

        # Partial match on keys
        if len(matching_xrefs) < max_results:
            for key, xrefs in self._search_index.items():
                if query_upper in key or key.startswith(query_upper):
                    matching_xrefs.update(xrefs)
                    if len(matching_xrefs) >= max_results * 2:
                        break

        # Also search through name_map display names for substring match
        if len(matching_xrefs) < max_results:
            for xref, info in name_map.items():
                if query_upper in info.get("name", "").upper():
                    matching_xrefs.add(xref)
                    if len(matching_xrefs) >= max_results * 2:
                        break

        # Build results
        results = []
        for xref in list(matching_xrefs)[:max_results]:
            info = name_map.get(xref, {})
            results.append({
                "xref": xref,
                "name": info.get("name", xref),
                "era": info.get("era", "6.8"),
                "is_living": info.get("living", False),
            })

        # Sort by name
        results.sort(key=lambda x: x["name"])

        return results

    def get_stats(self) -> Optional[dict]:
        """Get import statistics (from last import or from disk)."""
        if self._stats:
            return self._stats.summary()

        stats_path = self._data_dir / "import_stats.json"
        if stats_path.exists():
            try:
                return json.loads(stats_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        return None


# ════════════════════════════════════════════════════════════════════
# MULTI-FORMAT IMPORT & DEDUPLICATION ENGINE
# ════════════════════════════════════════════════════════════════════
#
# Extends the GEDCOM importer with:
#   - PersonRecord: unified internal representation across all formats
#   - AncestryDNAParser: CSV parser for Ancestry.com DNA match exports
#   - FamilySearchParser: GEDCOM 7.0 with JSON-LD extension awareness
#   - GrampsXMLParser: Gramps open-source genealogy XML format
#   - GenericCSVParser: configurable column-mapped CSV import
#   - PersonMatcher: fuzzy deduplication engine
#   - GenealogyStore: central store with incremental dedup and search
#   - API route builders for server_routes.py integration
# ════════════════════════════════════════════════════════════════════


# ── Unified PersonRecord ────────────────────────────────────────────

@dataclass
class SourceAttribution:
    """Tracks which source contributed a piece of data."""
    value: str = ""
    source: str = ""          # e.g., "PAF (Larry Anderson)", "FamilySearch"
    confidence: float = 1.0   # 0.0 to 1.0
    imported_at: str = ""

    def to_dict(self) -> dict:
        d: dict = {"value": self.value, "source": self.source}
        if self.confidence < 1.0:
            d["confidence"] = round(self.confidence, 2)
        if self.imported_at:
            d["imported_at"] = self.imported_at
        return d


@dataclass
class PersonRecord:
    """Unified person record aggregating data from multiple genealogy sources.

    Every field tracks its source provenance so that merges preserve
    attribution and conflicting data can be surfaced for human review.
    """
    record_id: str = ""                      # internal UUID-style ID
    # Primary fields
    given_name: str = ""
    surname: str = ""
    maiden_name: str = ""
    prefix: str = ""
    suffix: str = ""
    nickname: str = ""
    sex: str = ""                            # M, F, U
    # Dates
    birth_date: str = ""                     # ISO-ish or original string
    birth_place: str = ""
    death_date: str = ""
    death_place: str = ""
    burial_place: str = ""
    # Family cross-references (record_ids)
    spouse_ids: list = field(default_factory=list)
    parent_ids: list = field(default_factory=list)
    child_ids: list = field(default_factory=list)
    sibling_ids: list = field(default_factory=list)
    # Provenance
    sources: list = field(default_factory=list)   # list[str] source labels
    source_xrefs: dict = field(default_factory=dict)  # source_label -> original xref
    # Alternatives for conflicting data
    alternatives: dict = field(default_factory=dict)  # field_name -> list[SourceAttribution]
    # Metadata
    era: str = "6.8"
    is_living: bool = False
    occupation: str = ""
    notes: list = field(default_factory=list)
    custom: dict = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        if self.given_name:
            parts.append(self.given_name)
        if self.surname:
            parts.append(self.surname)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts) if parts else "(Unknown)"

    @property
    def birth_year(self) -> Optional[int]:
        return _extract_year(self.birth_date)

    @property
    def death_year(self) -> Optional[int]:
        return _extract_year(self.death_date)

    def to_dict(self) -> dict:
        d: dict = {
            "record_id": self.record_id,
            "display_name": self.display_name,
            "given_name": self.given_name,
            "surname": self.surname,
            "sex": self.sex,
            "era": self.era,
            "is_living": self.is_living,
            "sources": self.sources,
        }
        if self.maiden_name:
            d["maiden_name"] = self.maiden_name
        if self.prefix:
            d["prefix"] = self.prefix
        if self.suffix:
            d["suffix"] = self.suffix
        if self.nickname:
            d["nickname"] = self.nickname
        if self.birth_date:
            d["birth_date"] = self.birth_date
        if self.birth_place:
            d["birth_place"] = self.birth_place
        if self.death_date:
            d["death_date"] = self.death_date
        if self.death_place:
            d["death_place"] = self.death_place
        if self.burial_place:
            d["burial_place"] = self.burial_place
        if self.occupation:
            d["occupation"] = self.occupation
        if self.notes:
            d["notes"] = self.notes
        if self.spouse_ids:
            d["spouse_ids"] = self.spouse_ids
        if self.parent_ids:
            d["parent_ids"] = self.parent_ids
        if self.child_ids:
            d["child_ids"] = self.child_ids
        if self.sibling_ids:
            d["sibling_ids"] = self.sibling_ids
        if self.source_xrefs:
            d["source_xrefs"] = self.source_xrefs
        if self.alternatives:
            d["alternatives"] = {
                k: [a.to_dict() for a in v]
                for k, v in self.alternatives.items()
            }
        if self.custom:
            d["custom"] = self.custom
        return d


def _extract_year(date_str: str) -> Optional[int]:
    """Extract a 4-digit year from various date string formats."""
    if not date_str:
        return None
    m = re.search(r"\b(\d{4})\b", date_str)
    return int(m.group(1)) if m else None


def _generate_record_id(source: str, original_id: str) -> str:
    """Generate a deterministic record ID from source + original ID."""
    h = hashlib.sha256(f"{source}::{original_id}".encode()).hexdigest()[:16]
    return f"gen-{h}"


# ── Convert existing GedcomIndividual to PersonRecord ────────────

def gedcom_individual_to_person(indi: GedcomIndividual,
                                source_label: str = "GEDCOM") -> PersonRecord:
    """Convert a GedcomIndividual (from the existing parser) into a PersonRecord."""
    name = indi.primary_name
    rec = PersonRecord(
        record_id=_generate_record_id(source_label, indi.xref),
        given_name=name.given,
        surname=name.surname,
        maiden_name=name.maiden,
        prefix=name.prefix,
        suffix=name.suffix,
        nickname=name.nickname,
        sex=indi.sex,
        birth_date=indi.birth_date.to_iso() if indi.birth_date else "",
        birth_place=indi.birth_place,
        death_date=indi.death_date.to_iso() if indi.death_date else "",
        death_place=indi.death_place,
        burial_place=indi.burial_place,
        occupation=indi.occupation,
        era=indi.classify_era(),
        is_living=indi.is_living,
        sources=[source_label],
        source_xrefs={source_label: indi.xref},
    )
    if indi.note:
        rec.notes.append(indi.note)
    return rec


# ── Ancestry.com DNA Match CSV Parser ──────────────────────────────

@dataclass
class DNAMatch:
    """A DNA match record from Ancestry.com CSV export."""
    match_name: str = ""
    match_id: str = ""
    shared_cm: float = 0.0
    shared_segments: int = 0
    confidence: str = ""       # "Extremely High", "Very High", "High", "Moderate", etc.
    relationship_range: str = ""
    starred: bool = False
    notes: str = ""
    source: str = "Ancestry.com"

    def to_dict(self) -> dict:
        d: dict = {
            "match_name": self.match_name,
            "shared_cm": self.shared_cm,
            "shared_segments": self.shared_segments,
            "source": self.source,
        }
        if self.match_id:
            d["match_id"] = self.match_id
        if self.confidence:
            d["confidence"] = self.confidence
        if self.relationship_range:
            d["relationship_range"] = self.relationship_range
        if self.starred:
            d["starred"] = True
        if self.notes:
            d["notes"] = self.notes
        return d


class AncestryDNAParser:
    """Parser for Ancestry.com DNA match CSV exports.

    Ancestry exports DNA matches as CSV files with columns like:
        Match Name, Match Test ID, Shared DNA (cM), Shared Segments,
        Confidence, Relationship Range, Starred, Notes, etc.

    Column names vary slightly between export versions, so we auto-detect
    by fuzzy-matching header names.
    """

    # Map of canonical field -> possible CSV header names
    COLUMN_ALIASES: dict[str, list[str]] = {
        "match_name": ["match name", "name", "match", "matchname"],
        "match_id": ["match test id", "testid", "match id", "id"],
        "shared_cm": ["shared dna", "shared cm", "shareddna", "cm", "centimorgans",
                       "shared dna (cm)", "shared centimorgans"],
        "shared_segments": ["shared segments", "segments", "num segments",
                            "number of segments"],
        "confidence": ["confidence", "confidence level"],
        "relationship_range": ["relationship range", "relationship", "predicted relationship",
                               "estimated relationship"],
        "starred": ["starred", "star", "favorite"],
        "notes": ["notes", "note", "user notes"],
    }

    def __init__(self):
        self.matches: list[DNAMatch] = []
        self._column_map: dict[str, int] = {}

    def parse_file(self, filepath: str | Path) -> list[DNAMatch]:
        """Parse an Ancestry DNA match CSV file.

        Handles both UTF-8 and UTF-8-BOM encodings. Streams line by line
        for large match lists.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DNA match CSV not found: {filepath}")

        self.matches = []

        # Try UTF-8-BOM first, fall back to UTF-8, then cp1252
        for enc in ("utf-8-sig", "utf-8", "cp1252"):
            try:
                with open(filepath, "r", encoding=enc, newline="") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header is None:
                        return self.matches

                    self._map_columns(header)

                    for row in reader:
                        match = self._parse_row(row)
                        if match:
                            self.matches.append(match)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        log.info("Parsed %d DNA matches from %s", len(self.matches), filepath.name)
        return self.matches

    def _map_columns(self, header: list[str]) -> None:
        """Auto-detect column positions by fuzzy-matching header names."""
        self._column_map = {}
        normalized = [h.strip().lower() for h in header]

        for field_name, aliases in self.COLUMN_ALIASES.items():
            for i, col_name in enumerate(normalized):
                if col_name in aliases:
                    self._column_map[field_name] = i
                    break
            else:
                # Try fuzzy matching
                for i, col_name in enumerate(normalized):
                    for alias in aliases:
                        if (difflib.SequenceMatcher(None, col_name, alias).ratio() > 0.8):
                            self._column_map[field_name] = i
                            break
                    if field_name in self._column_map:
                        break

    def _parse_row(self, row: list[str]) -> Optional[DNAMatch]:
        """Parse a single CSV row into a DNAMatch."""
        if not row or all(not c.strip() for c in row):
            return None

        def _get(field_key: str) -> str:
            idx = self._column_map.get(field_key)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return ""

        name = _get("match_name")
        if not name:
            return None

        match = DNAMatch(match_name=name)
        match.match_id = _get("match_id")
        match.confidence = _get("confidence")
        match.relationship_range = _get("relationship_range")
        match.notes = _get("notes")

        cm_str = _get("shared_cm")
        if cm_str:
            # Remove non-numeric chars except decimal point
            cm_clean = re.sub(r"[^\d.]", "", cm_str)
            try:
                match.shared_cm = float(cm_clean)
            except ValueError:
                pass

        seg_str = _get("shared_segments")
        if seg_str:
            try:
                match.shared_segments = int(re.sub(r"[^\d]", "", seg_str))
            except ValueError:
                pass

        starred = _get("starred").lower()
        match.starred = starred in ("yes", "true", "1", "y")

        return match


# ── FamilySearch GEDCOM 7.0 Parser ─────────────────────────────────

class FamilySearchParser(GedcomParser):
    """Extended GEDCOM parser with FamilySearch GEDCOM 7.0 awareness.

    GEDCOM 7.0 (FamilySearch GEDCOM) adds:
    - JSON-LD extension URIs in the header (SCHMA / TAG)
    - @VOID@ sentinel for missing references
    - EXID (external identifier) tags with type URIs
    - MIME-type media references
    - Enum values for many tags
    - No CONC (concatenation is gone — lines can be any length)

    This parser handles the standard GEDCOM parts via the parent class
    and additionally notes any 7.0 extensions found during parsing.
    """

    def __init__(self):
        super().__init__()
        self.extensions: dict[str, str] = {}  # tag -> URI
        self.external_ids: dict[str, list[dict]] = {}  # xref -> [{type, id}]
        self.is_gedcom7: bool = False

    def _parse_header(self, lines: list[GedcomLine]) -> None:
        """Parse HEAD, noting any GEDCOM 7.0 schema extensions."""
        super()._parse_header(lines)

        # Check for GEDCOM 7.x version
        if self.gedcom_version.startswith("7"):
            self.is_gedcom7 = True
            log.info("Detected FamilySearch GEDCOM 7.0 format (version %s)",
                     self.gedcom_version)

        # Parse SCHMA / TAG extension definitions
        # GEDCOM 7.0: 1 SCHMA / 2 TAG _SOMETAG http://example.com/ext
        in_schema = False
        for gl in lines:
            if gl.level == 1 and gl.tag == "SCHMA":
                in_schema = True
            elif gl.level == 1 and gl.tag != "SCHMA":
                in_schema = False
            elif in_schema and gl.level == 2 and gl.tag == "TAG":
                # value is "_TAGNAME URI"
                parts = gl.value.strip().split(None, 1)
                if len(parts) == 2:
                    tag_name, uri = parts
                    self.extensions[tag_name] = uri
                    log.debug("GEDCOM 7.0 extension: %s -> %s", tag_name, uri)

    def _parse_individual(self, xref: str, lines: list[GedcomLine]) -> GedcomIndividual:
        """Parse INDI record, capturing EXID and 7.0-specific tags."""
        indi = super()._parse_individual(xref, lines)

        # Capture EXID (external identifiers) — GEDCOM 7.0 feature
        exids: list[dict] = []
        current_exid_value = ""
        for gl in lines:
            if gl.level == 1 and gl.tag == "EXID":
                current_exid_value = gl.value.strip()
            elif gl.level == 2 and gl.tag == "TYPE" and current_exid_value:
                exids.append({"type": gl.value.strip(), "id": current_exid_value})
                current_exid_value = ""
            elif gl.level == 1:
                if current_exid_value:
                    exids.append({"type": "", "id": current_exid_value})
                current_exid_value = ""

        # Catch trailing EXID without TYPE sub-tag
        if current_exid_value:
            exids.append({"type": "", "id": current_exid_value})

        if exids:
            self.external_ids[xref] = exids
            indi.custom_tags["_EXID"] = json.dumps(exids)

        # Handle @VOID@ references (GEDCOM 7.0 sentinel for missing data)
        if indi.family_spouse:
            indi.family_spouse = [f for f in indi.family_spouse if f != "@VOID@"]
        if indi.family_child:
            indi.family_child = [f for f in indi.family_child if f != "@VOID@"]

        return indi

    def to_person_records(self, source_label: str = "FamilySearch") -> list[PersonRecord]:
        """Convert all parsed individuals to PersonRecord objects."""
        records = []
        for indi in self.individuals.values():
            rec = gedcom_individual_to_person(indi, source_label)
            # Attach external IDs if present
            if indi.xref in self.external_ids:
                rec.custom["external_ids"] = self.external_ids[indi.xref]
            records.append(rec)
        return records


# ── Gramps XML Parser ──────────────────────────────────────────────

class GrampsXMLParser:
    """Parser for Gramps XML genealogy export files.

    Gramps (https://gramps-project.org) is the most popular open-source
    genealogy application. It exports to XML with elements:
        <person>, <family>, <event>, <place>, <source>, <citation>,
        <repository>, <media>, <note>

    This parser extracts person and family records, converting them to
    PersonRecord objects for integration with the deduplication engine.
    Designed for streaming via iterparse for large exports.
    """

    # Gramps XML namespace
    GRAMPS_NS = "http://gramps-project.org/xml/1.7.1/"

    def __init__(self):
        self.persons: dict[str, PersonRecord] = {}
        self.families: dict[str, dict] = {}
        self.events: dict[str, dict] = {}
        self.places: dict[str, dict] = {}
        self.sources: dict[str, dict] = {}
        self._parse_errors: int = 0

    def _ns(self, tag: str) -> str:
        """Wrap a tag with the Gramps namespace."""
        return f"{{{self.GRAMPS_NS}}}{tag}"

    def _detect_namespace(self, filepath: Path) -> str:
        """Detect the actual namespace from the file, since versions vary."""
        try:
            for _event, elem in ET.iterparse(str(filepath), events=("start",)):
                tag = elem.tag
                if tag.startswith("{"):
                    ns_end = tag.index("}")
                    return tag[1:ns_end]
                # If no namespace found in first element, bail
                break
        except ET.ParseError:
            pass
        return self.GRAMPS_NS

    def parse_file(self, filepath: str | Path) -> None:
        """Parse a Gramps XML export file.

        Uses iterparse for memory-efficient processing of large files.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Gramps XML file not found: {filepath}")

        log.info("Parsing Gramps XML: %s (%.1f MB)",
                 filepath.name, filepath.stat().st_size / (1024 * 1024))

        # Detect namespace
        ns = self._detect_namespace(filepath)
        if ns != self.GRAMPS_NS:
            log.info("Using detected Gramps namespace: %s", ns)
            self.GRAMPS_NS = ns

        # Parse in two passes: first events/places (needed to resolve
        # person/family references), then persons/families.
        self._parse_events_and_places(filepath)
        self._parse_persons_and_families(filepath)

        log.info(
            "Gramps XML parsed: %d persons, %d families, %d events, "
            "%d places, %d sources (%d errors)",
            len(self.persons), len(self.families), len(self.events),
            len(self.places), len(self.sources), self._parse_errors,
        )

    def _parse_events_and_places(self, filepath: Path) -> None:
        """First pass: parse events, places, and sources."""
        try:
            tree = ET.parse(str(filepath))
            root = tree.getroot()
        except ET.ParseError as e:
            log.error("Gramps XML parse error: %s", e)
            self._parse_errors += 1
            return

        ns = self.GRAMPS_NS

        # Events
        for ev_elem in root.iter(f"{{{ns}}}event"):
            try:
                handle = ev_elem.get("handle", "")
                ev: dict = {"handle": handle}

                type_el = ev_elem.find(f"{{{ns}}}type")
                if type_el is not None and type_el.text:
                    ev["type"] = type_el.text

                dateval = ev_elem.find(f"{{{ns}}}dateval")
                if dateval is not None:
                    ev["date"] = dateval.get("val", "")
                    ev["date_type"] = dateval.get("type", "")
                datestr = ev_elem.find(f"{{{ns}}}datestr")
                if datestr is not None:
                    ev["date"] = datestr.get("val", "")
                daterange = ev_elem.find(f"{{{ns}}}daterange")
                if daterange is not None:
                    ev["date"] = f"{daterange.get('start', '')}/{daterange.get('stop', '')}"
                    ev["date_type"] = "range"

                place_ref = ev_elem.find(f"{{{ns}}}place")
                if place_ref is not None:
                    ev["place_handle"] = place_ref.get("hlink", "")

                desc = ev_elem.find(f"{{{ns}}}description")
                if desc is not None and desc.text:
                    ev["description"] = desc.text

                if handle:
                    self.events[handle] = ev
            except Exception as e:
                self._parse_errors += 1
                if self._parse_errors <= 20:
                    log.warning("Error parsing Gramps event: %s", e)

        # Places
        for pl_elem in root.iter(f"{{{ns}}}placeobj"):
            try:
                handle = pl_elem.get("handle", "")
                pl: dict = {"handle": handle}

                pname = pl_elem.find(f"{{{ns}}}pname")
                if pname is not None:
                    pl["name"] = pname.get("value", "")

                # Hierarchical place references
                placeref = pl_elem.find(f"{{{ns}}}placeref")
                if placeref is not None:
                    pl["parent_handle"] = placeref.get("hlink", "")

                coord = pl_elem.find(f"{{{ns}}}coord")
                if coord is not None:
                    pl["lat"] = coord.get("lat", "")
                    pl["long"] = coord.get("long", "")

                if handle:
                    self.places[handle] = pl
            except Exception as e:
                self._parse_errors += 1

        # Sources
        for src_elem in root.iter(f"{{{ns}}}source"):
            try:
                handle = src_elem.get("handle", "")
                src: dict = {"handle": handle}
                stitle = src_elem.find(f"{{{ns}}}stitle")
                if stitle is not None and stitle.text:
                    src["title"] = stitle.text
                sauthor = src_elem.find(f"{{{ns}}}sauthor")
                if sauthor is not None and sauthor.text:
                    src["author"] = sauthor.text
                spubinfo = src_elem.find(f"{{{ns}}}spubinfo")
                if spubinfo is not None and spubinfo.text:
                    src["pubinfo"] = spubinfo.text
                if handle:
                    self.sources[handle] = src
            except Exception as e:
                self._parse_errors += 1

    def _resolve_place(self, place_handle: str) -> str:
        """Resolve a place handle to a full place name, walking up the hierarchy."""
        parts = []
        visited: set[str] = set()
        current = place_handle

        while current and current not in visited:
            visited.add(current)
            place = self.places.get(current)
            if not place:
                break
            name = place.get("name", "")
            if name:
                parts.append(name)
            current = place.get("parent_handle", "")

        return ", ".join(parts)

    def _parse_persons_and_families(self, filepath: Path) -> None:
        """Second pass: parse person and family records."""
        try:
            tree = ET.parse(str(filepath))
            root = tree.getroot()
        except ET.ParseError:
            return

        ns = self.GRAMPS_NS

        # Persons
        for p_elem in root.iter(f"{{{ns}}}person"):
            try:
                self._parse_gramps_person(p_elem, ns)
            except Exception as e:
                self._parse_errors += 1
                if self._parse_errors <= 20:
                    log.warning("Error parsing Gramps person: %s", e)

        # Families
        for f_elem in root.iter(f"{{{ns}}}family"):
            try:
                self._parse_gramps_family(f_elem, ns)
            except Exception as e:
                self._parse_errors += 1

        # Wire up family relationships into PersonRecords
        self._resolve_family_links()

    def _parse_gramps_person(self, elem, ns: str) -> None:
        """Parse a single <person> element into a PersonRecord."""
        handle = elem.get("handle", "")
        gramps_id = elem.get("id", handle)

        rec = PersonRecord(
            record_id=_generate_record_id("Gramps", gramps_id),
            sources=["Gramps"],
            source_xrefs={"Gramps": gramps_id},
        )

        # Gender
        gender_el = elem.find(f"{{{ns}}}gender")
        if gender_el is not None and gender_el.text:
            g = gender_el.text.strip().upper()
            if g == "M" or g == "MALE":
                rec.sex = "M"
            elif g == "F" or g == "FEMALE":
                rec.sex = "F"
            else:
                rec.sex = "U"

        # Name
        name_el = elem.find(f"{{{ns}}}name")
        if name_el is not None:
            first = name_el.find(f"{{{ns}}}first")
            if first is not None and first.text:
                rec.given_name = first.text.strip()
            surname_el = name_el.find(f"{{{ns}}}surname")
            if surname_el is not None and surname_el.text:
                rec.surname = surname_el.text.strip()
                # Check for maiden name via prim attribute
                if surname_el.get("prim", "1") == "0":
                    rec.maiden_name = surname_el.text.strip()
            suffix_el = name_el.find(f"{{{ns}}}suffix")
            if suffix_el is not None and suffix_el.text:
                rec.suffix = suffix_el.text.strip()
            title_el = name_el.find(f"{{{ns}}}title")
            if title_el is not None and title_el.text:
                rec.prefix = title_el.text.strip()
            nick_el = name_el.find(f"{{{ns}}}nick")
            if nick_el is not None and nick_el.text:
                rec.nickname = nick_el.text.strip()

        # Event references
        for evref in elem.iter(f"{{{ns}}}eventref"):
            ev_handle = evref.get("hlink", "")
            role = evref.get("role", "Primary")
            if role.lower() != "primary":
                continue
            ev = self.events.get(ev_handle, {})
            ev_type = ev.get("type", "").lower()
            ev_date = ev.get("date", "")
            ev_place_handle = ev.get("place_handle", "")
            ev_place = self._resolve_place(ev_place_handle) if ev_place_handle else ""

            if ev_type == "birth":
                rec.birth_date = ev_date
                rec.birth_place = ev_place
            elif ev_type == "death":
                rec.death_date = ev_date
                rec.death_place = ev_place
            elif ev_type == "burial":
                rec.burial_place = ev_place
            elif ev_type == "occupation":
                rec.occupation = ev.get("description", ev_date)

        # Notes
        for noteref in elem.iter(f"{{{ns}}}noteref"):
            # Gramps stores notes separately; we just track the handle
            rec.notes.append(f"[gramps-note:{noteref.get('hlink', '')}]")

        # Classify era
        rec.era = _classify_era_from_year(rec.birth_year)

        # Living heuristic
        if not rec.death_date:
            by = rec.birth_year
            if by and by > 1900:
                rec.is_living = True
        else:
            rec.is_living = False

        self.persons[handle] = rec

    def _parse_gramps_family(self, elem, ns: str) -> None:
        """Parse a single <family> element."""
        handle = elem.get("handle", "")
        gramps_id = elem.get("id", handle)

        fam: dict = {
            "handle": handle,
            "id": gramps_id,
            "father_handle": "",
            "mother_handle": "",
            "child_handles": [],
        }

        father = elem.find(f"{{{ns}}}father")
        if father is not None:
            fam["father_handle"] = father.get("hlink", "")
        mother = elem.find(f"{{{ns}}}mother")
        if mother is not None:
            fam["mother_handle"] = mother.get("hlink", "")
        for childref in elem.iter(f"{{{ns}}}childref"):
            fam["child_handles"].append(childref.get("hlink", ""))

        # Marriage event
        for evref in elem.iter(f"{{{ns}}}eventref"):
            ev_handle = evref.get("hlink", "")
            ev = self.events.get(ev_handle, {})
            if ev.get("type", "").lower() == "marriage":
                fam["marriage_date"] = ev.get("date", "")
                ph = ev.get("place_handle", "")
                fam["marriage_place"] = self._resolve_place(ph) if ph else ""

        self.families[handle] = fam

    def _resolve_family_links(self) -> None:
        """Wire up spouse/parent/child/sibling links on PersonRecords."""
        for fam in self.families.values():
            father_h = fam.get("father_handle", "")
            mother_h = fam.get("mother_handle", "")
            child_handles = fam.get("child_handles", [])

            father = self.persons.get(father_h)
            mother = self.persons.get(mother_h)

            # Spouse links
            if father and mother:
                if mother.record_id not in father.spouse_ids:
                    father.spouse_ids.append(mother.record_id)
                if father.record_id not in mother.spouse_ids:
                    mother.spouse_ids.append(father.record_id)

            # Parent-child links
            child_records = [self.persons[h] for h in child_handles if h in self.persons]
            for child in child_records:
                for parent in (father, mother):
                    if parent:
                        if child.record_id not in parent.child_ids:
                            parent.child_ids.append(child.record_id)
                        if parent.record_id not in child.parent_ids:
                            child.parent_ids.append(parent.record_id)

            # Sibling links
            for i, child_a in enumerate(child_records):
                for child_b in child_records[i + 1:]:
                    if child_b.record_id not in child_a.sibling_ids:
                        child_a.sibling_ids.append(child_b.record_id)
                    if child_a.record_id not in child_b.sibling_ids:
                        child_b.sibling_ids.append(child_a.record_id)


def _classify_era_from_year(year: Optional[int]) -> str:
    """Classify a year into a Hypernet era code."""
    if year is None:
        return "6.8"
    if year < 500:
        return "6.1"
    elif year < 1600:
        return "6.2"
    elif year < 1900:
        return "6.3"
    elif year < 2000:
        return "6.4"
    else:
        return "6.5"


# ── Generic CSV Parser ─────────────────────────────────────────────

# Standard column name aliases for auto-detection
_CSV_COLUMN_ALIASES: dict[str, list[str]] = {
    "first_name": [
        "first_name", "firstname", "first name", "given_name", "givenname",
        "given name", "given", "first", "forename",
    ],
    "last_name": [
        "last_name", "lastname", "last name", "surname", "family_name",
        "familyname", "family name", "last",
    ],
    "birth_date": [
        "birth_date", "birthdate", "birth date", "born", "date_of_birth",
        "dob", "b_date", "bdate",
    ],
    "birth_place": [
        "birth_place", "birthplace", "birth place", "born_at", "place_of_birth",
        "b_place", "bplace",
    ],
    "death_date": [
        "death_date", "deathdate", "death date", "died", "date_of_death",
        "dod", "d_date", "ddate",
    ],
    "death_place": [
        "death_place", "deathplace", "death place", "died_at",
        "place_of_death", "d_place",
    ],
    "sex": [
        "sex", "gender",
    ],
    "father": [
        "father", "father_name", "dad", "father name",
    ],
    "mother": [
        "mother", "mother_name", "mom", "mother name",
    ],
    "spouse": [
        "spouse", "spouse_name", "husband", "wife", "partner",
        "spouse name", "married_to",
    ],
    "maiden_name": [
        "maiden_name", "maidenname", "maiden name", "birth_surname",
        "nee",
    ],
    "middle_name": [
        "middle_name", "middlename", "middle name", "middle",
    ],
    "suffix": [
        "suffix", "name_suffix", "jr", "sr",
    ],
    "prefix": [
        "prefix", "title", "name_prefix", "honorific",
    ],
    "nickname": [
        "nickname", "nick", "alias", "aka", "also_known_as",
    ],
    "occupation": [
        "occupation", "job", "profession", "work",
    ],
    "notes": [
        "notes", "note", "comments", "remarks",
    ],
    "id": [
        "id", "person_id", "record_id", "individual_id", "uid",
    ],
}


class GenericCSVParser:
    """Configurable CSV importer with auto-detection of column names.

    Supports importing genealogy data from any CSV file. Columns are
    auto-detected by matching header names against common aliases, or
    can be manually mapped via the ``column_map`` parameter.

    Usage:
        parser = GenericCSVParser()
        records = parser.parse_file("family_data.csv")

        # Or with custom mapping:
        parser = GenericCSVParser(column_map={
            "first_name": 0, "last_name": 1, "birth_date": 3
        })
        records = parser.parse_file("custom_export.csv")
    """

    def __init__(self, column_map: Optional[dict[str, int]] = None,
                 source_label: str = "CSV Import",
                 delimiter: str = ","):
        self.column_map: dict[str, int] = column_map or {}
        self.source_label = source_label
        self.delimiter = delimiter
        self.records: list[PersonRecord] = []
        self._warnings: list[str] = []
        self._raw_headers: list[str] = []

    @property
    def warnings(self) -> list[str]:
        return self._warnings

    @property
    def detected_columns(self) -> dict[str, int]:
        """Return the column mapping (auto-detected or user-supplied)."""
        return dict(self.column_map)

    def parse_file(self, filepath: str | Path,
                   max_rows: int = 0) -> list[PersonRecord]:
        """Parse a CSV file into PersonRecord objects.

        Args:
            filepath: Path to the CSV file
            max_rows: Maximum rows to parse (0 = unlimited)

        Returns:
            List of PersonRecord objects
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        self.records = []
        self._warnings = []

        # Auto-detect delimiter if not specified
        if self.delimiter == ",":
            self.delimiter = self._detect_delimiter(filepath)

        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                with open(filepath, "r", encoding=enc, newline="") as f:
                    reader = csv.reader(f, delimiter=self.delimiter)
                    header = next(reader, None)
                    if header is None:
                        return self.records

                    self._raw_headers = [h.strip() for h in header]

                    # Auto-detect columns if no manual map provided
                    if not self.column_map:
                        self.column_map = self._auto_detect_columns(header)

                    mapped_fields = list(self.column_map.keys())
                    if not mapped_fields:
                        self._warnings.append(
                            "No columns could be mapped. Headers found: "
                            + str(self._raw_headers)
                        )
                        return self.records

                    log.info("CSV column mapping: %s", self.column_map)

                    row_num = 0
                    for row in reader:
                        row_num += 1
                        if max_rows > 0 and row_num > max_rows:
                            break
                        rec = self._parse_row(row, row_num)
                        if rec:
                            self.records.append(rec)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        log.info("Parsed %d person records from CSV: %s",
                 len(self.records), filepath.name)
        return self.records

    def _detect_delimiter(self, filepath: Path) -> str:
        """Auto-detect CSV delimiter by examining the first few lines."""
        try:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                sample = f.read(4096)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=",;\t|")
            return dialect.delimiter
        except (csv.Error, Exception):
            return ","

    def _auto_detect_columns(self, header: list[str]) -> dict[str, int]:
        """Auto-detect column mapping from header names."""
        mapping: dict[str, int] = {}
        normalized = [h.strip().lower().replace("-", "_") for h in header]

        for field_name, aliases in _CSV_COLUMN_ALIASES.items():
            # Exact match
            for i, col in enumerate(normalized):
                if col in aliases:
                    mapping[field_name] = i
                    break
            else:
                # Fuzzy match
                for i, col in enumerate(normalized):
                    for alias in aliases:
                        ratio = difflib.SequenceMatcher(None, col, alias).ratio()
                        if ratio > 0.85:
                            mapping[field_name] = i
                            break
                    if field_name in mapping:
                        break

        return mapping

    def _parse_row(self, row: list[str], row_num: int) -> Optional[PersonRecord]:
        """Parse a single CSV row into a PersonRecord."""
        if not row or all(not c.strip() for c in row):
            return None

        def _get(field_key: str) -> str:
            idx = self.column_map.get(field_key)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return ""

        first = _get("first_name")
        last = _get("last_name")

        if not first and not last:
            return None

        # Build middle + given
        middle = _get("middle_name")
        given = f"{first} {middle}".strip() if middle else first

        original_id = _get("id") or f"row-{row_num}"

        rec = PersonRecord(
            record_id=_generate_record_id(self.source_label, original_id),
            given_name=given,
            surname=last,
            maiden_name=_get("maiden_name"),
            prefix=_get("prefix"),
            suffix=_get("suffix"),
            nickname=_get("nickname"),
            sex=_normalize_sex(_get("sex")),
            birth_date=_get("birth_date"),
            birth_place=_get("birth_place"),
            death_date=_get("death_date"),
            death_place=_get("death_place"),
            occupation=_get("occupation"),
            sources=[self.source_label],
            source_xrefs={self.source_label: original_id},
        )

        notes = _get("notes")
        if notes:
            rec.notes.append(notes)

        # Store father/mother/spouse as custom fields for later linking
        father = _get("father")
        mother = _get("mother")
        spouse = _get("spouse")
        if father:
            rec.custom["father_name"] = father
        if mother:
            rec.custom["mother_name"] = mother
        if spouse:
            rec.custom["spouse_name"] = spouse

        # Classify era
        rec.era = _classify_era_from_year(rec.birth_year)
        # Living heuristic
        if not rec.death_date:
            by = rec.birth_year
            rec.is_living = bool(by and by > 1900)

        return rec


def _normalize_sex(raw: str) -> str:
    """Normalize sex/gender field to M/F/U."""
    if not raw:
        return "U"
    r = raw.strip().upper()
    if r in ("M", "MALE", "MAN", "BOY"):
        return "M"
    if r in ("F", "FEMALE", "WOMAN", "GIRL"):
        return "F"
    return "U"


# ════════════════════════════════════════════════════════════════════
# DEDUPLICATION ENGINE
# ════════════════════════════════════════════════════════════════════

# Nickname equivalences — common English name variants
_NICKNAME_MAP: dict[str, list[str]] = {
    "william": ["bill", "will", "willy", "billy", "liam", "willie"],
    "elizabeth": ["beth", "liz", "lizzy", "eliza", "liza", "betty", "betsy",
                  "bess", "bessie", "libby", "lisa", "ellie"],
    "robert": ["bob", "bobby", "rob", "robbie", "bert", "robby"],
    "james": ["jim", "jimmy", "jamie", "jem"],
    "john": ["jack", "johnny", "jon"],
    "richard": ["dick", "rick", "rich", "ricky"],
    "thomas": ["tom", "tommy"],
    "margaret": ["maggie", "meg", "peggy", "marge", "margie", "madge", "greta",
                 "rita"],
    "catherine": ["kate", "kathy", "cathy", "katie", "kitty", "kay", "cat"],
    "katherine": ["kate", "kathy", "cathy", "katie", "kitty", "kay", "cat"],
    "joseph": ["joe", "joey"],
    "charles": ["charlie", "chuck", "chas"],
    "edward": ["ed", "eddie", "ted", "teddy", "ned"],
    "michael": ["mike", "mikey", "mick"],
    "daniel": ["dan", "danny"],
    "david": ["dave", "davey"],
    "benjamin": ["ben", "benny"],
    "samuel": ["sam", "sammy"],
    "andrew": ["andy", "drew"],
    "alexander": ["alex", "sandy", "alec"],
    "nicholas": ["nick", "nicky"],
    "matthew": ["matt", "matty"],
    "patrick": ["pat", "paddy"],
    "francis": ["frank", "fran"],
    "stephen": ["steve", "stevie"],
    "steven": ["steve", "stevie"],
    "peter": ["pete"],
    "anthony": ["tony"],
    "timothy": ["tim", "timmy"],
    "christopher": ["chris", "kit"],
    "jonathan": ["jon", "jonny"],
    "nathaniel": ["nate", "nat", "nathan"],
    "theodore": ["ted", "teddy", "theo"],
    "frederick": ["fred", "freddy", "fritz"],
    "henry": ["harry", "hal", "hank"],
    "arthur": ["art"],
    "albert": ["al", "bert", "bertie"],
    "dorothy": ["dot", "dolly", "dottie"],
    "mary": ["molly", "polly", "mae", "mamie", "may"],
    "sarah": ["sally", "sadie"],
    "patricia": ["pat", "patty", "trish"],
    "barbara": ["barb", "babs"],
    "jennifer": ["jenny", "jen"],
    "jessica": ["jess", "jessie"],
    "virginia": ["ginny", "ginger"],
    "rebecca": ["becky", "becca"],
    "deborah": ["debbie", "deb"],
    "ann": ["annie", "anna", "nan", "nancy"],
    "anne": ["annie", "anna", "nan", "nancy"],
    "susanna": ["susan", "sue", "susie", "suzy"],
    "susan": ["sue", "susie", "suzy"],
    "helen": ["nell", "nellie", "ellie"],
    "eleanor": ["nell", "nellie", "ellie", "nora"],
    "caroline": ["carrie"],
    "abigail": ["abby", "gail"],
    "harriet": ["hattie"],
    "louisa": ["lou", "lulu"],
    "agnes": ["aggie", "nessie"],
}

# Build reverse lookup: nickname -> set of canonical names
_NICKNAME_REVERSE: dict[str, set[str]] = {}
for _canonical, _nicks in _NICKNAME_MAP.items():
    for _n in _nicks:
        _NICKNAME_REVERSE.setdefault(_n, set()).add(_canonical)
    # Also add canonical to its own group
    _NICKNAME_REVERSE.setdefault(_canonical, set()).add(_canonical)


def _are_name_variants(name_a: str, name_b: str) -> bool:
    """Check if two first names are known nickname variants of each other."""
    a = name_a.strip().lower()
    b = name_b.strip().lower()
    if a == b:
        return True

    # Direct lookup
    if a in _NICKNAME_MAP and b in _NICKNAME_MAP[a]:
        return True
    if b in _NICKNAME_MAP and a in _NICKNAME_MAP[b]:
        return True

    # Check if they share a canonical name
    groups_a = _NICKNAME_REVERSE.get(a, set())
    groups_b = _NICKNAME_REVERSE.get(b, set())
    return bool(groups_a & groups_b)


# ── US State Abbreviation Normalization ────────────────────────────

_US_STATE_ABBREV: dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC",
}
# Build reverse (abbrev -> full) for flexible matching
_US_STATE_FULL: dict[str, str] = {v.lower(): k for k, v in _US_STATE_ABBREV.items()}


def _normalize_place(raw: str) -> str:
    """Normalize a place string for comparison.

    Lowercases, removes extra whitespace, standardizes US state names.
    """
    if not raw:
        return ""
    text = raw.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.replace(".", "")

    # Try to normalize US state abbreviations in the last component
    parts = [p.strip() for p in text.split(",")]
    for i, part in enumerate(parts):
        if part in _US_STATE_ABBREV:
            parts[i] = _US_STATE_ABBREV[part]
        elif part in _US_STATE_FULL:
            parts[i] = _US_STATE_FULL[part]

    return ", ".join(p for p in parts if p)


# ── Matching Score Components ──────────────────────────────────────

def _name_similarity(a: PersonRecord, b: PersonRecord) -> float:
    """Compute name similarity score (0.0 - 1.0).

    Considers given name, surname, maiden name, and nickname variants.
    """
    scores: list[float] = []

    # Surname comparison (most important within name matching)
    sur_a = a.surname.strip().lower()
    sur_b = b.surname.strip().lower()
    if sur_a and sur_b:
        if sur_a == sur_b:
            scores.append(1.0)
        else:
            # Check maiden name
            maiden_a = a.maiden_name.strip().lower()
            maiden_b = b.maiden_name.strip().lower()
            if maiden_a and maiden_a == sur_b:
                scores.append(0.95)
            elif maiden_b and maiden_b == sur_a:
                scores.append(0.95)
            else:
                ratio = difflib.SequenceMatcher(None, sur_a, sur_b).ratio()
                scores.append(ratio)
    elif sur_a or sur_b:
        scores.append(0.0)
    # If neither has a surname, skip this component

    # Given name comparison
    given_a = a.given_name.strip().lower().split()[0] if a.given_name.strip() else ""
    given_b = b.given_name.strip().lower().split()[0] if b.given_name.strip() else ""
    if given_a and given_b:
        if given_a == given_b:
            scores.append(1.0)
        elif _are_name_variants(given_a, given_b):
            scores.append(0.9)
        else:
            ratio = difflib.SequenceMatcher(None, given_a, given_b).ratio()
            scores.append(ratio)
    elif given_a or given_b:
        scores.append(0.0)

    # Middle name / full given name comparison (bonus)
    full_given_a = a.given_name.strip().lower()
    full_given_b = b.given_name.strip().lower()
    if " " in full_given_a and " " in full_given_b:
        ratio = difflib.SequenceMatcher(None, full_given_a, full_given_b).ratio()
        scores.append(ratio)

    # Nickname check (bonus)
    if a.nickname and b.nickname:
        if a.nickname.strip().lower() == b.nickname.strip().lower():
            scores.append(1.0)

    return sum(scores) / len(scores) if scores else 0.0


def _date_similarity(date_a: str, date_b: str) -> float:
    """Compute date similarity (0.0 - 1.0).

    Handles exact match, year-only, and approximate dates.
    Within 2 years = strong match, up to 5 years = partial.
    """
    if not date_a or not date_b:
        return 0.0  # Cannot compare — no penalty, no reward

    year_a = _extract_year(date_a)
    year_b = _extract_year(date_b)

    if year_a is None or year_b is None:
        return 0.0

    diff = abs(year_a - year_b)
    if diff == 0:
        # Same year — bonus if month/day also match
        if date_a == date_b:
            return 1.0
        return 0.95
    elif diff <= 1:
        return 0.85
    elif diff <= 2:
        return 0.7
    elif diff <= 5:
        return 0.3
    else:
        return 0.0


def _place_similarity(place_a: str, place_b: str) -> float:
    """Compute place similarity (0.0 - 1.0).

    Hierarchical: exact match > same state > same country.
    """
    if not place_a or not place_b:
        return 0.0

    norm_a = _normalize_place(place_a)
    norm_b = _normalize_place(place_b)

    if norm_a == norm_b:
        return 1.0

    parts_a = [p.strip() for p in norm_a.split(",")]
    parts_b = [p.strip() for p in norm_b.split(",")]

    # Check city match
    if parts_a and parts_b and parts_a[0] == parts_b[0] and parts_a[0]:
        return 0.9

    # Check state/region match (second-to-last or last component)
    if len(parts_a) >= 2 and len(parts_b) >= 2:
        if parts_a[-2] == parts_b[-2] and parts_a[-2]:
            return 0.6
        if parts_a[-1] == parts_b[-1] and parts_a[-1]:
            return 0.4

    # Just last component (country)
    if parts_a and parts_b and parts_a[-1] == parts_b[-1] and parts_a[-1]:
        return 0.3

    # Fuzzy overall
    ratio = difflib.SequenceMatcher(None, norm_a, norm_b).ratio()
    return ratio * 0.5  # Scale down fuzzy place matching


def _family_similarity(a: PersonRecord, b: PersonRecord,
                       store: Optional[dict] = None) -> float:
    """Compute family relationship similarity (0.0 - 1.0).

    Checks if two people share spouse names, children names, or parent names.
    ``store`` is a dict of record_id -> PersonRecord for looking up names.
    """
    if store is None:
        store = {}

    signals: list[float] = []

    # Check for shared spouse names
    spouse_names_a = _get_related_names(a.spouse_ids, store)
    spouse_names_b = _get_related_names(b.spouse_ids, store)
    if spouse_names_a or spouse_names_b:
        # Also check custom spouse_name field (from CSV imports)
        sp_custom_a = a.custom.get("spouse_name", "").strip().lower()
        sp_custom_b = b.custom.get("spouse_name", "").strip().lower()
        if sp_custom_a:
            spouse_names_a.add(sp_custom_a)
        if sp_custom_b:
            spouse_names_b.add(sp_custom_b)

        if spouse_names_a and spouse_names_b:
            overlap = _fuzzy_set_overlap(spouse_names_a, spouse_names_b)
            if overlap > 0:
                signals.append(min(overlap, 1.0))

    # Check for shared children names
    child_names_a = _get_related_names(a.child_ids, store)
    child_names_b = _get_related_names(b.child_ids, store)
    if child_names_a and child_names_b:
        overlap = _fuzzy_set_overlap(child_names_a, child_names_b)
        if overlap > 0:
            signals.append(min(overlap, 1.0))

    # Check parent names
    parent_names_a = _get_related_names(a.parent_ids, store)
    parent_names_b = _get_related_names(b.parent_ids, store)
    if not parent_names_a:
        fa = a.custom.get("father_name", "").strip().lower()
        ma = a.custom.get("mother_name", "").strip().lower()
        if fa:
            parent_names_a.add(fa)
        if ma:
            parent_names_a.add(ma)
    if not parent_names_b:
        fb = b.custom.get("father_name", "").strip().lower()
        mb = b.custom.get("mother_name", "").strip().lower()
        if fb:
            parent_names_b.add(fb)
        if mb:
            parent_names_b.add(mb)

    if parent_names_a and parent_names_b:
        overlap = _fuzzy_set_overlap(parent_names_a, parent_names_b)
        if overlap > 0:
            signals.append(min(overlap, 1.0))

    return sum(signals) / len(signals) if signals else 0.0


def _get_related_names(record_ids: list[str],
                       store: dict) -> set[str]:
    """Look up display names for a list of record IDs."""
    names: set[str] = set()
    for rid in record_ids:
        rec = store.get(rid)
        if rec:
            dn = rec.display_name.strip().lower()
            if dn and dn != "(unknown)":
                names.add(dn)
    return names


def _fuzzy_set_overlap(set_a: set[str], set_b: set[str]) -> float:
    """Count fuzzy matches between two sets of names.

    Returns a score: number of fuzzy matches / max(len(set_a), len(set_b)).
    """
    if not set_a or not set_b:
        return 0.0

    matches = 0
    for name_a in set_a:
        for name_b in set_b:
            if name_a == name_b:
                matches += 1
                break
            ratio = difflib.SequenceMatcher(None, name_a, name_b).ratio()
            if ratio > 0.8:
                matches += 1
                break

    return matches / max(len(set_a), len(set_b))


# ── PersonMatcher (Deduplication Engine) ───────────────────────────

@dataclass
class MatchResult:
    """Result of comparing two person records for potential duplication."""
    record_id_a: str
    record_id_b: str
    name_a: str = ""
    name_b: str = ""
    score: float = 0.0
    name_score: float = 0.0
    date_score: float = 0.0
    place_score: float = 0.0
    family_score: float = 0.0
    decision: str = ""       # "auto_merge", "suggest_merge", "different"
    decided_by: str = ""     # "algorithm", "human"
    decided_at: str = ""

    def to_dict(self) -> dict:
        return {
            "record_id_a": self.record_id_a,
            "record_id_b": self.record_id_b,
            "name_a": self.name_a,
            "name_b": self.name_b,
            "score": round(self.score, 1),
            "components": {
                "name": round(self.name_score, 2),
                "date": round(self.date_score, 2),
                "place": round(self.place_score, 2),
                "family": round(self.family_score, 2),
            },
            "decision": self.decision,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
        }


class PersonMatcher:
    """Identifies duplicate people across multiple genealogy sources.

    Uses fuzzy matching on names, dates, places, and family relationships
    to score potential matches. Merges confirmed matches into a single
    unified record while preserving source provenance.

    Weights:
        - Name similarity:   30%
        - Date matching:     25%
        - Place matching:    20%
        - Family relations:  25%

    Score interpretation:
        - 80-100: Auto-merge (high confidence)
        - 60-79:  Suggest merge (human review recommended)
        - 0-59:   Different people

    The matcher is incremental: new imports are compared against existing
    data, and match decisions are saved to avoid re-confirmation.
    """

    # Tunable weights (must sum to 1.0)
    WEIGHT_NAME = 0.30
    WEIGHT_DATE = 0.25
    WEIGHT_PLACE = 0.20
    WEIGHT_FAMILY = 0.25

    # Thresholds
    AUTO_MERGE_THRESHOLD = 80.0
    SUGGEST_MERGE_THRESHOLD = 60.0

    def __init__(self, store: Optional[dict[str, PersonRecord]] = None):
        self._store: dict[str, PersonRecord] = store or {}
        self._matches: list[MatchResult] = []
        self._decisions: dict[str, MatchResult] = {}  # "idA::idB" -> MatchResult
        # Surname index for blocking (avoid O(n^2) on entire dataset)
        self._surname_index: dict[str, list[str]] = defaultdict(list)

    @property
    def matches(self) -> list[MatchResult]:
        return self._matches

    @property
    def pending_matches(self) -> list[MatchResult]:
        """Return matches that need human review."""
        return [m for m in self._matches if m.decision == "suggest_merge"]

    @property
    def auto_merged(self) -> list[MatchResult]:
        """Return matches that were auto-merged."""
        return [m for m in self._matches if m.decision == "auto_merge"]

    def set_store(self, store: dict[str, PersonRecord]) -> None:
        """Set the record store and rebuild indexes."""
        self._store = store
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild the surname blocking index."""
        self._surname_index = defaultdict(list)
        for rid, rec in self._store.items():
            key = rec.surname.strip().upper()
            if key:
                self._surname_index[key].append(rid)
            # Also index maiden name
            if rec.maiden_name:
                mk = rec.maiden_name.strip().upper()
                if mk:
                    self._surname_index[mk].append(rid)

    def compare(self, a: PersonRecord, b: PersonRecord) -> MatchResult:
        """Compare two person records and return a match result.

        Computes weighted score from name, date, place, and family components.
        """
        # Check if we already have a decision for this pair
        pair_key = _pair_key(a.record_id, b.record_id)
        if pair_key in self._decisions:
            return self._decisions[pair_key]

        name_score = _name_similarity(a, b)
        # Combine birth and death date scores
        birth_sim = _date_similarity(a.birth_date, b.birth_date)
        death_sim = _date_similarity(a.death_date, b.death_date)
        date_parts = [s for s in (birth_sim, death_sim) if s > 0]
        date_score = sum(date_parts) / len(date_parts) if date_parts else 0.0

        # Combine birth and death place scores
        birth_place_sim = _place_similarity(a.birth_place, b.birth_place)
        death_place_sim = _place_similarity(a.death_place, b.death_place)
        place_parts = [s for s in (birth_place_sim, death_place_sim) if s > 0]
        place_score = sum(place_parts) / len(place_parts) if place_parts else 0.0

        family_score = _family_similarity(a, b, self._store)

        # Weighted total (scale to 0-100)
        total = (
            name_score * self.WEIGHT_NAME
            + date_score * self.WEIGHT_DATE
            + place_score * self.WEIGHT_PLACE
            + family_score * self.WEIGHT_FAMILY
        ) * 100.0

        # Determine decision
        if total >= self.AUTO_MERGE_THRESHOLD:
            decision = "auto_merge"
        elif total >= self.SUGGEST_MERGE_THRESHOLD:
            decision = "suggest_merge"
        else:
            decision = "different"

        result = MatchResult(
            record_id_a=a.record_id,
            record_id_b=b.record_id,
            name_a=a.display_name,
            name_b=b.display_name,
            score=total,
            name_score=name_score,
            date_score=date_score,
            place_score=place_score,
            family_score=family_score,
            decision=decision,
            decided_by="algorithm",
            decided_at=datetime.now(timezone.utc).isoformat(),
        )

        return result

    def find_matches_for(self, record: PersonRecord,
                         max_candidates: int = 100) -> list[MatchResult]:
        """Find potential duplicates for a single record using blocking.

        Uses surname blocking to avoid comparing against every record
        in the store. Returns matches sorted by score descending.
        """
        candidates: set[str] = set()

        # Block by surname
        key = record.surname.strip().upper()
        if key:
            candidates.update(self._surname_index.get(key, []))
        # Also check maiden name
        if record.maiden_name:
            mk = record.maiden_name.strip().upper()
            if mk:
                candidates.update(self._surname_index.get(mk, []))

        # Remove self
        candidates.discard(record.record_id)

        # Limit candidates
        candidate_list = list(candidates)[:max_candidates]

        results: list[MatchResult] = []
        for rid in candidate_list:
            other = self._store.get(rid)
            if not other:
                continue
            match = self.compare(record, other)
            if match.score >= self.SUGGEST_MERGE_THRESHOLD:
                results.append(match)

        results.sort(key=lambda m: m.score, reverse=True)
        return results

    def find_all_matches(self,
                         records: Optional[list[PersonRecord]] = None,
                         chunk_size: int = 500) -> list[MatchResult]:
        """Run deduplication across all records or a subset.

        If ``records`` is provided, each record is compared against the
        existing store. Otherwise, the entire store is compared internally.
        This uses surname-based blocking to keep performance manageable.

        Args:
            records: New records to check against existing store.
                     If None, checks the entire store against itself.
            chunk_size: Process in chunks for progress logging.

        Returns:
            List of MatchResult objects above the suggest threshold.
        """
        self._matches = []

        if records is None:
            # Internal dedup: compare store against itself
            all_rids = list(self._store.keys())
            processed = 0
            for rid in all_rids:
                rec = self._store[rid]
                found = self.find_matches_for(rec)
                for m in found:
                    pk = _pair_key(m.record_id_a, m.record_id_b)
                    if pk not in self._decisions:
                        self._decisions[pk] = m
                        self._matches.append(m)

                processed += 1
                if processed % chunk_size == 0:
                    log.info("  ...dedup progress: %d/%d records checked, "
                             "%d potential matches found",
                             processed, len(all_rids), len(self._matches))
        else:
            # Incremental: compare new records against store
            for i, rec in enumerate(records):
                found = self.find_matches_for(rec)
                for m in found:
                    pk = _pair_key(m.record_id_a, m.record_id_b)
                    if pk not in self._decisions:
                        self._decisions[pk] = m
                        self._matches.append(m)

                if (i + 1) % chunk_size == 0:
                    log.info("  ...dedup progress: %d/%d new records checked, "
                             "%d potential matches found",
                             i + 1, len(records), len(self._matches))

        log.info("Deduplication complete: %d potential matches "
                 "(%d auto-merge, %d suggest)",
                 len(self._matches),
                 len(self.auto_merged),
                 len(self.pending_matches))

        return self._matches

    def confirm_merge(self, record_id_a: str, record_id_b: str) -> Optional[MatchResult]:
        """Confirm a merge between two records (human decision)."""
        pk = _pair_key(record_id_a, record_id_b)
        match = self._decisions.get(pk)
        if match:
            match.decision = "auto_merge"  # Upgrade to confirmed merge
            match.decided_by = "human"
            match.decided_at = datetime.now(timezone.utc).isoformat()
        return match

    def reject_merge(self, record_id_a: str, record_id_b: str) -> Optional[MatchResult]:
        """Reject a potential merge between two records (human decision)."""
        pk = _pair_key(record_id_a, record_id_b)
        match = self._decisions.get(pk)
        if match:
            match.decision = "different"
            match.decided_by = "human"
            match.decided_at = datetime.now(timezone.utc).isoformat()
        else:
            # Create a decision even if not in matches
            match = MatchResult(
                record_id_a=record_id_a,
                record_id_b=record_id_b,
                decision="different",
                decided_by="human",
                decided_at=datetime.now(timezone.utc).isoformat(),
            )
            self._decisions[pk] = match
        return match

    def save_decisions(self, filepath: str | Path) -> None:
        """Save match decisions to JSON for persistence."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "decisions": [m.to_dict() for m in self._decisions.values()],
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "total": len(self._decisions),
        }
        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_decisions(self, filepath: str | Path) -> int:
        """Load saved match decisions. Returns number of decisions loaded."""
        filepath = Path(filepath)
        if not filepath.exists():
            return 0
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            count = 0
            for d in data.get("decisions", []):
                pk = _pair_key(d["record_id_a"], d["record_id_b"])
                mr = MatchResult(
                    record_id_a=d["record_id_a"],
                    record_id_b=d["record_id_b"],
                    name_a=d.get("name_a", ""),
                    name_b=d.get("name_b", ""),
                    score=d.get("score", 0),
                    name_score=d.get("components", {}).get("name", 0),
                    date_score=d.get("components", {}).get("date", 0),
                    place_score=d.get("components", {}).get("place", 0),
                    family_score=d.get("components", {}).get("family", 0),
                    decision=d.get("decision", ""),
                    decided_by=d.get("decided_by", ""),
                    decided_at=d.get("decided_at", ""),
                )
                self._decisions[pk] = mr
                count += 1
            return count
        except (json.JSONDecodeError, KeyError, OSError) as e:
            log.warning("Failed to load decisions from %s: %s", filepath, e)
            return 0


def _pair_key(id_a: str, id_b: str) -> str:
    """Canonical pair key (order-independent)."""
    return "::".join(sorted([id_a, id_b]))


# ── Merge Logic ────────────────────────────────────────────────────

def merge_persons(primary: PersonRecord,
                  secondary: PersonRecord) -> PersonRecord:
    """Merge two person records, keeping the most complete data from each.

    - Keeps all source references (provenance)
    - For conflicting data (e.g. different birth dates), the primary
      record's value is kept as the main value and the secondary's is
      stored as an alternative with its source attribution
    - Primary record's data takes precedence when equal quality

    Args:
        primary: The record whose data takes precedence
        secondary: The record being merged into primary

    Returns:
        A new PersonRecord with merged data
    """
    now = datetime.now(timezone.utc).isoformat()

    merged = PersonRecord(
        record_id=primary.record_id,
        sources=list(set(primary.sources + secondary.sources)),
        source_xrefs={**secondary.source_xrefs, **primary.source_xrefs},
        alternatives=dict(primary.alternatives),  # copy
    )

    # Helper to merge a simple string field with provenance tracking
    def _merge_field(field_name: str) -> str:
        val_a = getattr(primary, field_name, "").strip()
        val_b = getattr(secondary, field_name, "").strip()

        if val_a and val_b and val_a.lower() != val_b.lower():
            # Conflict: keep primary, record secondary as alternative
            alts = merged.alternatives.setdefault(field_name, [])
            alts.append(SourceAttribution(
                value=val_b,
                source=", ".join(secondary.sources),
                confidence=0.6,
                imported_at=now,
            ))
            return val_a
        elif val_a:
            return val_a
        elif val_b:
            return val_b
        return ""

    merged.given_name = _merge_field("given_name")
    merged.surname = _merge_field("surname")
    merged.maiden_name = _merge_field("maiden_name")
    merged.prefix = _merge_field("prefix")
    merged.suffix = _merge_field("suffix")
    merged.nickname = _merge_field("nickname")
    merged.birth_date = _merge_field("birth_date")
    merged.birth_place = _merge_field("birth_place")
    merged.death_date = _merge_field("death_date")
    merged.death_place = _merge_field("death_place")
    merged.burial_place = _merge_field("burial_place")
    merged.occupation = _merge_field("occupation")

    # Sex: prefer non-U value
    if primary.sex and primary.sex != "U":
        merged.sex = primary.sex
    elif secondary.sex and secondary.sex != "U":
        merged.sex = secondary.sex
    else:
        merged.sex = primary.sex or secondary.sex or "U"

    # Merge list fields (deduped)
    merged.spouse_ids = list(set(primary.spouse_ids + secondary.spouse_ids))
    merged.parent_ids = list(set(primary.parent_ids + secondary.parent_ids))
    merged.child_ids = list(set(primary.child_ids + secondary.child_ids))
    merged.sibling_ids = list(set(primary.sibling_ids + secondary.sibling_ids))
    merged.notes = list(set(primary.notes + secondary.notes))

    # Merge custom fields
    merged.custom = {**secondary.custom, **primary.custom}

    # Recompute derived fields
    merged.era = _classify_era_from_year(merged.birth_year)
    merged.is_living = primary.is_living or secondary.is_living

    return merged


# ── GenealogyStore (Central Store) ──────────────────────────────────

class GenealogyStore:
    """Central store for unified genealogy records with dedup and search.

    Manages PersonRecords from all sources, supports incremental import
    with automatic deduplication, and provides search and statistics.

    Data is persisted as JSON files in the staging directory, chunked
    for efficient loading of large datasets.
    """

    CHUNK_SIZE = 5000  # Records per file for chunked storage

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.records: dict[str, PersonRecord] = {}
        self.matcher = PersonMatcher()
        self._import_sources: dict[str, dict] = {}  # source_label -> metadata
        self._dirty = False

    @property
    def total_records(self) -> int:
        return len(self.records)

    def load(self) -> int:
        """Load all records from disk. Returns number loaded."""
        self.records = {}
        records_dir = self.data_dir / "records"
        if not records_dir.exists():
            return 0

        count = 0
        for chunk_file in sorted(records_dir.glob("chunk_*.json")):
            try:
                data = json.loads(chunk_file.read_text(encoding="utf-8"))
                for rd in data.get("records", []):
                    rec = self._dict_to_record(rd)
                    self.records[rec.record_id] = rec
                    count += 1
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Failed to load chunk %s: %s", chunk_file.name, e)

        # Load sources metadata
        sources_file = self.data_dir / "sources_metadata.json"
        if sources_file.exists():
            try:
                self._import_sources = json.loads(
                    sources_file.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                pass

        # Load match decisions
        decisions_file = self.data_dir / "match_decisions.json"
        self.matcher.load_decisions(decisions_file)

        # Set up matcher
        self.matcher.set_store(self.records)

        log.info("GenealogyStore loaded: %d records from %s",
                 count, self.data_dir)
        return count

    def save(self) -> None:
        """Save all records to disk in chunks."""
        records_dir = self.data_dir / "records"
        records_dir.mkdir(parents=True, exist_ok=True)

        # Clear old chunks
        for old in records_dir.glob("chunk_*.json"):
            old.unlink()

        # Write new chunks
        all_records = list(self.records.values())
        for i in range(0, len(all_records), self.CHUNK_SIZE):
            chunk = all_records[i:i + self.CHUNK_SIZE]
            chunk_num = i // self.CHUNK_SIZE
            chunk_file = records_dir / f"chunk_{chunk_num:04d}.json"
            data = {
                "records": [r.to_dict() for r in chunk],
                "chunk": chunk_num,
                "count": len(chunk),
            }
            chunk_file.write_text(
                json.dumps(data, indent=1, default=str),
                encoding="utf-8",
            )

        # Save sources metadata
        sources_file = self.data_dir / "sources_metadata.json"
        sources_file.write_text(
            json.dumps(self._import_sources, indent=2, default=str),
            encoding="utf-8",
        )

        # Save match decisions
        decisions_file = self.data_dir / "match_decisions.json"
        self.matcher.save_decisions(decisions_file)

        self._dirty = False
        log.info("GenealogyStore saved: %d records in %d chunks",
                 len(self.records),
                 (len(self.records) + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE)

    def add_records(self, records: list[PersonRecord],
                    source_label: str = "",
                    auto_dedup: bool = True) -> dict:
        """Add records to the store, optionally running deduplication.

        Args:
            records: List of PersonRecord objects to add
            source_label: Label for this import source
            auto_dedup: Whether to run dedup against existing records

        Returns:
            Summary dict with counts of added, merged, suggested
        """
        added = 0
        merged = 0
        suggested = 0
        skipped = 0

        # Track this import source
        if source_label:
            self._import_sources[source_label] = {
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "record_count": len(records),
            }

        for rec in records:
            if rec.record_id in self.records:
                skipped += 1
                continue

            if auto_dedup and self.records:
                # Rebuild indexes to include previously added records in this batch
                if added > 0 and added % 200 == 0:
                    self.matcher.set_store(self.records)

                found = self.matcher.find_matches_for(rec)
                if found:
                    best = found[0]
                    if best.decision == "auto_merge":
                        # Merge into existing record
                        existing = self.records[best.record_id_a
                                                if best.record_id_a != rec.record_id
                                                else best.record_id_b]
                        merged_rec = merge_persons(existing, rec)
                        self.records[existing.record_id] = merged_rec
                        merged += 1
                        continue
                    elif best.decision == "suggest_merge":
                        suggested += 1
                        # Still add — human will decide later

            self.records[rec.record_id] = rec
            added += 1

        # Final index rebuild
        self.matcher.set_store(self.records)
        self._dirty = True

        summary = {
            "added": added,
            "merged": merged,
            "suggested_review": suggested,
            "skipped_existing": skipped,
            "total_in_store": len(self.records),
            "source": source_label,
        }
        log.info("GenealogyStore import: %s", summary)
        return summary

    def run_dedup(self) -> list[MatchResult]:
        """Run full deduplication across all records in the store."""
        self.matcher.set_store(self.records)
        return self.matcher.find_all_matches()

    def confirm_merge(self, record_id_a: str, record_id_b: str) -> dict:
        """Confirm and execute a merge between two records."""
        rec_a = self.records.get(record_id_a)
        rec_b = self.records.get(record_id_b)
        if not rec_a or not rec_b:
            return {"error": "One or both records not found"}

        # Execute merge (first record is primary)
        merged = merge_persons(rec_a, rec_b)
        self.records[merged.record_id] = merged

        # Remove the secondary record
        secondary_id = record_id_b if merged.record_id == record_id_a else record_id_a
        if secondary_id in self.records:
            del self.records[secondary_id]

        # Record decision
        self.matcher.confirm_merge(record_id_a, record_id_b)
        self._dirty = True

        return {
            "merged_id": merged.record_id,
            "removed_id": secondary_id,
            "display_name": merged.display_name,
            "sources": merged.sources,
        }

    def reject_merge(self, record_id_a: str, record_id_b: str) -> dict:
        """Reject a potential merge (mark as different people)."""
        self.matcher.reject_merge(record_id_a, record_id_b)
        return {"status": "rejected", "record_id_a": record_id_a,
                "record_id_b": record_id_b}

    def search(self, name: Optional[str] = None,
               birth_year: Optional[int] = None,
               death_year: Optional[int] = None,
               place: Optional[str] = None,
               source: Optional[str] = None,
               max_results: int = 50) -> list[dict]:
        """Search records by name, dates, place, and/or source.

        All parameters are optional; results match ALL specified criteria.
        """
        results: list[dict] = []
        name_upper = name.strip().upper() if name else ""
        place_norm = _normalize_place(place) if place else ""

        for rec in self.records.values():
            # Name filter
            if name_upper:
                full = rec.display_name.upper()
                surname = rec.surname.upper()
                given = rec.given_name.upper()
                maiden = rec.maiden_name.upper()
                if not (name_upper in full or name_upper in surname
                        or name_upper in given or name_upper in maiden):
                    continue

            # Birth year filter
            if birth_year is not None:
                ry = rec.birth_year
                if ry is None or abs(ry - birth_year) > 2:
                    continue

            # Death year filter
            if death_year is not None:
                ry = rec.death_year
                if ry is None or abs(ry - death_year) > 2:
                    continue

            # Place filter
            if place_norm:
                bp = _normalize_place(rec.birth_place)
                dp = _normalize_place(rec.death_place)
                if place_norm not in bp and place_norm not in dp:
                    continue

            # Source filter
            if source:
                if source not in rec.sources:
                    continue

            results.append(rec.to_dict())
            if len(results) >= max_results:
                break

        return results

    def get_stats(self) -> dict:
        """Compute statistics about the current store."""
        era_counts: dict[str, int] = defaultdict(int)
        sex_counts: dict[str, int] = defaultdict(int)
        source_counts: dict[str, int] = defaultdict(int)
        living = 0
        deceased = 0

        for rec in self.records.values():
            era_counts[rec.era] += 1
            sex_counts[rec.sex or "U"] += 1
            for s in rec.sources:
                source_counts[s] += 1
            if rec.is_living:
                living += 1
            else:
                deceased += 1

        return {
            "total_records": len(self.records),
            "living": living,
            "deceased": deceased,
            "by_era": dict(sorted(era_counts.items())),
            "by_sex": dict(sorted(sex_counts.items())),
            "by_source": dict(sorted(source_counts.items(),
                                      key=lambda x: x[1], reverse=True)),
            "import_sources": self._import_sources,
            "pending_matches": len(self.matcher.pending_matches),
        }

    def get_sources(self) -> list[dict]:
        """List all import sources with contributor credits."""
        result = []
        for label, meta in self._import_sources.items():
            count = sum(1 for r in self.records.values() if label in r.sources)
            result.append({
                "source": label,
                "imported_at": meta.get("imported_at", ""),
                "original_count": meta.get("record_count", 0),
                "current_count": count,
            })
        return result

    @staticmethod
    def _dict_to_record(d: dict) -> PersonRecord:
        """Reconstruct a PersonRecord from a dict (loaded from JSON)."""
        rec = PersonRecord(
            record_id=d.get("record_id", ""),
            given_name=d.get("given_name", ""),
            surname=d.get("surname", ""),
            maiden_name=d.get("maiden_name", ""),
            prefix=d.get("prefix", ""),
            suffix=d.get("suffix", ""),
            nickname=d.get("nickname", ""),
            sex=d.get("sex", "U"),
            birth_date=d.get("birth_date", ""),
            birth_place=d.get("birth_place", ""),
            death_date=d.get("death_date", ""),
            death_place=d.get("death_place", ""),
            burial_place=d.get("burial_place", ""),
            occupation=d.get("occupation", ""),
            era=d.get("era", "6.8"),
            is_living=d.get("is_living", False),
            sources=d.get("sources", []),
            source_xrefs=d.get("source_xrefs", {}),
            spouse_ids=d.get("spouse_ids", []),
            parent_ids=d.get("parent_ids", []),
            child_ids=d.get("child_ids", []),
            sibling_ids=d.get("sibling_ids", []),
            notes=d.get("notes", []),
            custom=d.get("custom", {}),
        )
        # Reconstruct alternatives
        for field_name, alt_list in d.get("alternatives", {}).items():
            rec.alternatives[field_name] = [
                SourceAttribution(
                    value=a.get("value", ""),
                    source=a.get("source", ""),
                    confidence=a.get("confidence", 1.0),
                    imported_at=a.get("imported_at", ""),
                )
                for a in alt_list
            ]
        return rec


# ── Format Auto-Detection ──────────────────────────────────────────

def detect_genealogy_format(filepath: str | Path) -> str:
    """Auto-detect the genealogy file format.

    Returns one of:
        "gedcom"     — Standard GEDCOM 5.x
        "gedcom7"    — FamilySearch GEDCOM 7.0
        "gramps_xml" — Gramps XML export
        "csv"        — Generic CSV
        "dna_csv"    — Ancestry DNA match CSV
        "unknown"    — Unrecognized format
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return "unknown"

    suffix = filepath.suffix.lower()

    # Check file extension first
    if suffix == ".ged":
        # Check for GEDCOM 7.0 vs 5.x
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                head = f.read(4096)
            if "2 VERS 7" in head or "GEDC\n2 VERS 7" in head:
                return "gedcom7"
            return "gedcom"
        except OSError:
            return "gedcom"

    if suffix in (".gramps", ".xml"):
        # Check for Gramps XML namespace
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                head = f.read(2048)
            if "gramps-project.org" in head or "<database" in head:
                return "gramps_xml"
        except OSError:
            pass
        if suffix == ".gramps":
            return "gramps_xml"

    if suffix == ".csv":
        # Check if it looks like DNA match data
        try:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                header_line = f.readline().lower()
            if any(kw in header_line for kw in
                   ("shared dna", "shared cm", "centimorgans", "dna match",
                    "match name", "shared segments")):
                return "dna_csv"
            return "csv"
        except OSError:
            return "csv"

    if suffix == ".tsv":
        return "csv"  # TSV is handled by GenericCSVParser with tab delimiter

    return "unknown"


# ── Unified Import Function ────────────────────────────────────────

def import_genealogy_file(filepath: str | Path,
                          store: GenealogyStore,
                          source_label: str = "",
                          auto_dedup: bool = True,
                          max_records: int = 0) -> dict:
    """Import any supported genealogy file into the store.

    Auto-detects format and delegates to the appropriate parser.
    Returns a summary dict with import statistics.

    Args:
        filepath: Path to the genealogy file
        store: GenealogyStore to import into
        source_label: Human-readable label for this source
        auto_dedup: Whether to run deduplication during import
        max_records: Maximum records to import (0 = unlimited)

    Returns:
        Summary dict with format, counts, and any warnings
    """
    filepath = Path(filepath)
    fmt = detect_genealogy_format(filepath)

    if not source_label:
        source_label = f"{fmt}:{filepath.stem}"

    log.info("Importing genealogy file: %s (format: %s, source: %s)",
             filepath.name, fmt, source_label)

    records: list[PersonRecord] = []
    warnings: list[str] = []
    extra: dict = {}

    if fmt == "gedcom":
        parser = GedcomParser()
        parser.parse_file(filepath)
        for indi in parser.individuals.values():
            records.append(gedcom_individual_to_person(indi, source_label))
            if max_records > 0 and len(records) >= max_records:
                break
        extra["gedcom_version"] = parser.gedcom_version
        extra["source_program"] = parser.source_program
        extra["families"] = len(parser.families)
        extra["sources"] = len(parser.sources)
        extra["parse_errors"] = parser._parse_errors

    elif fmt == "gedcom7":
        parser7 = FamilySearchParser()
        parser7.parse_file(filepath)
        records = parser7.to_person_records(source_label)
        if max_records > 0:
            records = records[:max_records]
        extra["gedcom_version"] = parser7.gedcom_version
        extra["is_gedcom7"] = parser7.is_gedcom7
        extra["extensions"] = parser7.extensions
        extra["external_ids_count"] = len(parser7.external_ids)
        extra["families"] = len(parser7.families)

    elif fmt == "gramps_xml":
        gparser = GrampsXMLParser()
        gparser.parse_file(filepath)
        records = list(gparser.persons.values())
        if max_records > 0:
            records = records[:max_records]
        extra["families"] = len(gparser.families)
        extra["events"] = len(gparser.events)
        extra["places"] = len(gparser.places)
        extra["gramps_sources"] = len(gparser.sources)
        extra["parse_errors"] = gparser._parse_errors

    elif fmt in ("csv", "dna_csv"):
        if fmt == "dna_csv":
            dna_parser = AncestryDNAParser()
            dna_matches = dna_parser.parse_file(filepath)
            extra["dna_matches"] = len(dna_matches)
            extra["dna_data"] = [m.to_dict() for m in dna_matches[:20]]
            warnings.append(
                "DNA match CSV imported as match data, not person records. "
                "Use GEDCOM export for family tree data."
            )
            # DNA matches don't produce PersonRecords
        else:
            csv_parser = GenericCSVParser(source_label=source_label)
            records = csv_parser.parse_file(filepath,
                                            max_rows=max_records if max_records > 0 else 0)
            warnings.extend(csv_parser.warnings)
            extra["detected_columns"] = csv_parser.detected_columns
            extra["raw_headers"] = csv_parser._raw_headers

    else:
        return {
            "success": False,
            "error": f"Unrecognized format: {fmt}",
            "filepath": str(filepath),
        }

    # Add records to store
    import_summary = {}
    if records:
        import_summary = store.add_records(records, source_label, auto_dedup)

    return {
        "success": True,
        "format": fmt,
        "source_label": source_label,
        "records_parsed": len(records),
        "import_summary": import_summary,
        "warnings": warnings,
        "details": extra,
        "filepath": str(filepath),
    }


# ── API Route Builders ─────────────────────────────────────────────

def build_genealogy_routes(router, get_store_fn):
    """Register genealogy API endpoints on the given FastAPI router.

    Call this from server_routes.py with::

        from .genealogy_importer import build_genealogy_routes, GenealogyStore
        _store = None
        def _get_store():
            global _store
            if _store is None:
                _store = GenealogyStore(PRIVATE_ROOT / "genealogy")
                _store.load()
            return _store
        build_genealogy_routes(router, _get_store)

    Args:
        router: FastAPI APIRouter instance
        get_store_fn: Callable returning a GenealogyStore instance
    """
    try:
        from pydantic import BaseModel
    except ImportError:
        log.warning("pydantic not available — genealogy API routes not registered")
        return

    class GenealogyImportRequest(BaseModel):
        path: str
        source_label: str = ""
        auto_dedup: bool = True
        max_records: int = 0

    class GenealogyMergeRequest(BaseModel):
        record_id_a: str
        record_id_b: str

    @router.post("/genealogy/import")
    async def genealogy_import(req: GenealogyImportRequest):
        """Import any genealogy format (auto-detected)."""
        store = get_store_fn()
        try:
            result = import_genealogy_file(
                req.path, store,
                source_label=req.source_label,
                auto_dedup=req.auto_dedup,
                max_records=req.max_records,
            )
            if result.get("success"):
                store.save()
            return result
        except FileNotFoundError as e:
            from fastapi import HTTPException
            raise HTTPException(404, str(e))
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(500, f"Import failed: {e}")

    @router.post("/genealogy/deduplicate")
    async def genealogy_deduplicate():
        """Run deduplication on all imported genealogy data."""
        store = get_store_fn()
        dedup_matches = store.run_dedup()
        store.save()
        return {
            "total_matches": len(dedup_matches),
            "auto_merge": len([m for m in dedup_matches if m.decision == "auto_merge"]),
            "suggest_merge": len([m for m in dedup_matches if m.decision == "suggest_merge"]),
            "matches": [m.to_dict() for m in dedup_matches[:100]],
        }

    @router.get("/genealogy/matches")
    async def genealogy_matches():
        """Get potential duplicate matches for human review."""
        store = get_store_fn()
        pending = store.matcher.pending_matches
        return {
            "total_pending": len(pending),
            "matches": [m.to_dict() for m in pending[:100]],
        }

    @router.post("/genealogy/merge")
    async def genealogy_merge(req: GenealogyMergeRequest):
        """Confirm a merge between two records."""
        store = get_store_fn()
        result = store.confirm_merge(req.record_id_a, req.record_id_b)
        if "error" not in result:
            store.save()
        return result

    @router.get("/genealogy/search")
    async def genealogy_search(
        name: str = "",
        birth_year: Optional[int] = None,
        death_year: Optional[int] = None,
        place: str = "",
        source: str = "",
        max_results: int = 50,
    ):
        """Search imported genealogy records."""
        store = get_store_fn()
        results = store.search(
            name=name or None,
            birth_year=birth_year,
            death_year=death_year,
            place=place or None,
            source=source or None,
            max_results=max_results,
        )
        return {"total": len(results), "results": results}

    @router.get("/genealogy/stats")
    async def genealogy_stats():
        """Get genealogy import statistics."""
        store = get_store_fn()
        return store.get_stats()

    @router.get("/genealogy/sources")
    async def genealogy_sources():
        """List all import sources with contributor credits."""
        store = get_store_fn()
        return {"sources": store.get_sources()}
