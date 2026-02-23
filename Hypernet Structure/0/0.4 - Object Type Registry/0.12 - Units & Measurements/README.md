---
ha: "0.4.12"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# 0.12 - Units & Measurements

## Purpose

Defines all units of measurement used in Hypernet - from fundamental physics units to derived digital units. Part of the "explain to aliens" foundation.

**Hypernet Address:** `0.12.*`

---

## Philosophy: Measurement is Comparison

A measurement is comparing something to a standard unit. To explain Hypernet to aliens, we must define what our units ARE.

---

## Unit Categories

### 0.12.1 - SI Base Units
International System fundamental units

### 0.12.2 - Time Units
Seconds, minutes, hours, days, years

### 0.12.3 - Digital Storage Units
Bits, bytes, kilobytes, megabytes, gigabytes

### 0.12.4 - Data Transfer Units
Bits per second, bandwidth

### 0.12.5 - Currency Units
Dollars, euros, and other currencies

### 0.12.6 - Geographic Units
Latitude, longitude, meters, kilometers

### 0.12.7 - Derived Units
Compound units (velocity, frequency, etc.)

---

## 0.12.1 - SI Base Units

### The Seven Fundamental Units

**Second (s) - Time**
```
Definition (2019): The duration of 9,192,631,770 periods of the radiation
corresponding to the transition between two hyperfine levels of the ground
state of the caesium-133 atom.

Practical Meaning: Extremely precise atomic clock standard

Why It Matters: All timing in Hypernet ultimately references this standard
```

**Meter (m) - Length**
```
Definition (2019): The distance traveled by light in vacuum during 1/299,792,458
of a second.

Practical Meaning: Based on speed of light constant

Example Uses:
- Geographic distances (km)
- Altitude (meters above sea level)
- Object dimensions
```

**Kilogram (kg) - Mass**
```
Definition (2019): Based on the Planck constant (h = 6.62607015×10⁻³⁴ J⋅s)

Practical Meaning: Defined by fundamental physics constant

Example Uses:
- Weight of physical objects
- Server hardware mass
- Shipping weight
```

**Ampere (A) - Electric Current**
```
Definition (2019): Based on the elementary charge (e = 1.602176634×10⁻¹⁹ C)

Practical Meaning: Flow of electric charge

Example Uses:
- Power consumption
- Battery capacity
- Electrical systems
```

**Kelvin (K) - Temperature**
```
Definition (2019): Based on the Boltzmann constant (k = 1.380649×10⁻²³ J/K)

Practical Meaning: Absolute temperature scale

Conversions:
Celsius: °C = K - 273.15
Fahrenheit: °F = (9/5)(K - 273.15) + 32

Example Uses:
- CPU temperature
- Data center cooling
- Weather data
```

**Mole (mol) - Amount of Substance**
```
Definition (2019): Exactly 6.02214076×10²³ elementary entities

Practical Meaning: Avogadro's number of particles

Use: Chemistry, materials science
```

**Candela (cd) - Luminous Intensity**
```
Definition (2019): Based on the luminous efficacy of 540 THz radiation

Practical Meaning: Brightness standard

Use: Display brightness, lighting
```

---

## 0.12.2 - Time Units

### Fundamental Time Units

**Second (s)**
```
Base Unit: 1 second

Definition: See SI base units above

Precision in Hypernet:
- Timestamps: Millisecond precision (1/1000 second)
- High-precision: Microsecond (1/1,000,000 second)
- System time: Nanosecond (1/1,000,000,000 second)
```

**Minute**
```
1 minute = 60 seconds

Origin: Ancient Babylonian base-60 number system

Use: Human-scale time intervals
```

**Hour**
```
1 hour = 60 minutes = 3,600 seconds

Use: Work time, scheduling, time zones
```

**Day**
```
1 day = 24 hours = 1,440 minutes = 86,400 seconds

Definition: Time for Earth to rotate once

Variations:
- Solar day: ~86,400 seconds (varies slightly)
- Sidereal day: 86,164.1 seconds (relative to stars)

Use: Calendars, scheduling, billing cycles
```

**Week**
```
1 week = 7 days = 168 hours = 604,800 seconds

Origin: Various cultural and astronomical traditions

Use: Work cycles, scheduling patterns
```

**Month**
```
Variable: 28-31 days

Based on lunar cycles (historical)

Calendar Months:
- January: 31 days
- February: 28 days (29 in leap year)
- March: 31 days
- April: 30 days
- May: 31 days
- June: 30 days
- July: 31 days
- August: 31 days
- September: 30 days
- October: 31 days
- November: 30 days
- December: 31 days

Mnemonic: "30 days hath September, April, June, and November..."
```

**Year**
```
1 year = 365.25 days (average with leap years)

Variations:
- Calendar year: 365 days
- Leap year: 366 days (every 4 years, except century years unless divisible by 400)
- Tropical year: 365.242189 days (Earth orbit around sun)

Leap Year Rules:
- Divisible by 4: Leap year (2024)
- Divisible by 100: Not leap year (2100)
- Divisible by 400: Leap year anyway (2000)

Use: Long-term planning, subscriptions, contracts
```

### Unix Timestamp

```
Definition: Seconds since January 1, 1970 00:00:00 UTC (the "epoch")

Why this date? Arbitrary choice when Unix was developed

Examples:
0 = 1970-01-01 00:00:00
1000000000 = 2001-09-09 01:46:40
1609459200 = 2021-01-01 00:00:00
2147483647 = 2038-01-19 03:14:07 (32-bit int max - "Year 2038 problem")

Use in Hypernet:
All timestamps stored as Unix time (64-bit to avoid 2038 problem)
Converted to ISO 8601 for display
```

---

## 0.12.3 - Digital Storage Units

### Binary Units

**Bit (b)**
```
Definition: Single binary digit (0 or 1)

Fundamental unit of digital information

Example:
1 bit can represent: yes/no, true/false, on/off
```

**Byte (B)**
```
Definition: 8 bits

Historical: Size needed to encode one character

Example:
'A' = 01000001 (binary) = 65 (decimal) = 1 byte
```

**Kilobyte (KB)**
```
Decimal Definition: 1,000 bytes (SI prefix)
Binary Definition (KiB): 1,024 bytes (2¹⁰)

Confusion: Industry often mixes these
- Hard drive makers use 1,000 (decimal)
- Operating systems use 1,024 (binary)

Hypernet Convention:
- KB = 1,000 bytes (decimal)
- KiB = 1,024 bytes (binary) when precision matters
```

**Megabyte (MB)**
```
Decimal: 1,000,000 bytes = 1,000 KB
Binary (MiB): 1,048,576 bytes = 1,024 KiB

Example:
- Photo: ~5 MB
- Song (MP3): ~4 MB
- Document: ~0.1 MB
```

**Gigabyte (GB)**
```
Decimal: 1,000,000,000 bytes = 1,000 MB
Binary (GiB): 1,073,741,824 bytes = 1,024 MiB

Example:
- Movie (HD): ~4 GB
- Operating system: ~20 GB
- User's photo library: ~100 GB
```

**Terabyte (TB)**
```
Decimal: 1,000,000,000,000 bytes = 1,000 GB
Binary (TiB): 1,099,511,627,776 bytes = 1,024 GiB

Example:
- Hard drive: 1-4 TB
- Database: 10-100 TB
- User's total data: ~1 TB
```

**Petabyte (PB)**
```
Decimal: 1,000,000,000,000,000 bytes = 1,000 TB

Example:
- Large company data: ~10 PB
- Google search index: ~hundreds of PB
- Hypernet (eventual): ~PB scale
```

### Context Examples

```
Text:
- Single character: 1 byte
- Tweet (280 chars): ~280 bytes
- This README: ~50 KB
- Novel: ~1 MB

Images:
- Small thumbnail: ~10 KB
- Photo (compressed JPEG): ~3 MB
- Photo (RAW): ~25 MB
- 4K screenshot: ~15 MB

Video:
- 1 minute 1080p: ~150 MB
- 1 hour 1080p: ~9 GB
- 1 hour 4K: ~36 GB

Music:
- 3-minute song (MP3): ~3 MB
- 3-minute song (lossless): ~30 MB
- Album (12 songs, MP3): ~40 MB
```

---

## 0.12.4 - Data Transfer Units

### Bandwidth

**Bits per second (bps)**
```
Definition: Rate of data transfer

Note: Usually bits (b), not bytes (B)
- 8 bits = 1 byte
- 8 Mbps = 1 MB/s

Common Units:
- Kbps (kilobits per second): 1,000 bps
- Mbps (megabits per second): 1,000,000 bps
- Gbps (gigabits per second): 1,000,000,000 bps
```

**Examples**
```
Dial-up modem: 56 Kbps = 7 KB/s
DSL: 1-10 Mbps = 125 KB/s - 1.25 MB/s
Cable: 100-1000 Mbps = 12.5 - 125 MB/s
Fiber: 1-10 Gbps = 125 MB/s - 1.25 GB/s

API Rate Limits:
- 100 requests/minute
- 10 MB/second data transfer
- 1,000 requests/hour
```

### Latency

**Milliseconds (ms)**
```
Definition: 1/1000 of a second

Network Latency:
- LAN: <1 ms
- Same city: 5-10 ms
- Cross-country: 50-100 ms
- Transatlantic: 100-150 ms
- Satellite: 500-700 ms

Human Perception:
- <10 ms: Instant
- 10-100 ms: Noticeable
- 100-300 ms: Slight lag
- >300 ms: Annoying
- >1000 ms: Unacceptable for real-time
```

---

## 0.12.5 - Currency Units

### Major Currencies

**US Dollar (USD, $)**
```
Symbol: $
Code: USD
Subdivisions: 100 cents

Use: Primary currency for Hypernet business operations
```

**Euro (EUR, €)**
```
Symbol: €
Code: EUR
Subdivisions: 100 cents

Use: European market transactions
```

**British Pound (GBP, £)**
```
Symbol: £
Code: GBP
Subdivisions: 100 pence
```

### Storage Format

```
Hypernet stores currency as:
- Integer (cents): 1099 = $10.99
  (Avoids floating-point precision issues)

- Decimal with precision: DECIMAL(19,4)
  (For exact monetary calculations)

Example:
$10.99 stored as: 1099 cents or 10.9900
```

---

## 0.12.6 - Geographic Units

### Latitude & Longitude

**Latitude**
```
Range: -90° to +90°

0° = Equator
+90° = North Pole
-90° = South Pole

Format: Decimal degrees
Example: 40.7128° N (New York)
```

**Longitude**
```
Range: -180° to +180°

0° = Prime Meridian (Greenwich)
+180° = International Date Line (East)
-180° = International Date Line (West)

Format: Decimal degrees
Example: -74.0060° W (New York)
```

**Combined**
```
Format: (latitude, longitude)

Examples:
New York: (40.7128, -74.0060)
London: (51.5074, -0.1278)
Tokyo: (35.6762, 139.6503)
Sydney: (-33.8688, 151.2093)

Precision:
- 1 decimal place: ~11 km
- 2 decimal places: ~1.1 km
- 3 decimal places: ~110 m
- 4 decimal places: ~11 m
- 5 decimal places: ~1.1 m
- 6 decimal places: ~0.11 m (11 cm)
```

### Distance

**Kilometer (km)**
```
1 km = 1,000 meters

Earth circumference: ~40,075 km
Earth radius: ~6,371 km

Use: Geographic distances
```

**Mile**
```
1 mile = 1.60934 kilometers
1 mile = 5,280 feet

Use: United States distances
```

---

## 0.12.7 - Derived Units

### Frequency

**Hertz (Hz)**
```
Definition: Cycles per second

Units:
- Hz: 1 cycle/second
- KHz: 1,000 Hz
- MHz: 1,000,000 Hz
- GHz: 1,000,000,000 Hz

Examples:
- CPU: 3.5 GHz (3.5 billion cycles per second)
- WiFi: 2.4 GHz or 5 GHz
- Refresh rate: 60 Hz
```

### Velocity

**Meters per second (m/s)**
```
Definition: Distance traveled per unit time

Example:
- Walking: ~1.4 m/s
- Running: ~5 m/s
- Car: ~25 m/s (90 km/h)
- Speed of light: 299,792,458 m/s
```

---

## Unit Conversions

### Common Conversions

```
Time:
1 day = 24 hours
1 hour = 60 minutes
1 minute = 60 seconds

Data:
1 byte = 8 bits
1 KB = 1,000 bytes (or 1,024 bytes)
1 MB = 1,000 KB
1 GB = 1,000 MB

Distance:
1 km = 1,000 meters
1 mile = 1.609 km
1 meter = 3.281 feet

Temperature:
°C = K - 273.15
°F = (9/5)°C + 32
```

---

## Why Units Matter

### 1. Precision
Exact definitions prevent ambiguity and errors.

### 2. Interoperability
Standard units enable data exchange between systems.

### 3. Human Understanding
Appropriate units make data comprehensible.

### 4. Scientific Accuracy
Proper units ensure correct calculations.

### 5. Universal Communication
Units are language-independent concepts.

---

**Status:** Active - Core Units Defined
**Created:** February 10, 2026
**Purpose:** Define all measurement units from first principles
**Owner:** Hypernet Core Team
**Philosophy:** "To measure is to know."

---

*"Without standard units, every measurement is meaningless. With them, we can compare observations across all of space and time."*
— Hypernet Measurement Philosophy
