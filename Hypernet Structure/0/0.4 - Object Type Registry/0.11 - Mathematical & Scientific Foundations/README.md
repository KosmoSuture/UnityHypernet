---
ha: "0.4.11"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# 0.11 - Mathematical & Scientific Foundations

## Purpose

Defines the mathematical and scientific concepts that Hypernet relies on. Part of the "explain to aliens" foundation - explaining from absolute first principles.

**Hypernet Address:** `0.11.*`

---

## Philosophy: Build From Axioms

To truly explain Hypernet to an alien civilization, we must define:
- What IS a number?
- What IS arithmetic?
- What IS geometry?
- What IS physics?

---

## Foundation Categories

### 0.11.1 - Number Systems
Counting, integers, decimals, binary

### 0.11.2 - Arithmetic
Addition, subtraction, multiplication, division

### 0.11.3 - Algebra
Variables, equations, functions

### 0.11.4 - Geometry
Points, lines, shapes, space

### 0.11.5 - Calculus
Change, rates, optimization

### 0.11.6 - Statistics & Probability
Randomness, distributions, inference

### 0.11.7 - Logic
Boolean logic, set theory, proofs

### 0.11.8 - Physics
Time, space, energy, information

---

## 0.11.1 - Number Systems

### Natural Numbers (ℕ)

```
Definition: Counting numbers

Set: {0, 1, 2, 3, 4, 5, ...}

Purpose: Counting discrete things
- 0 apples
- 1 person
- 42 photos

Operations:
- Addition: 3 + 2 = 5
- Multiplication: 3 × 2 = 6
- Subtraction: 5 - 2 = 3 (only if result ≥ 0)
```

### Integers (ℤ)

```
Definition: Whole numbers (positive, negative, zero)

Set: {..., -3, -2, -1, 0, 1, 2, 3, ...}

Purpose: Represent differences and debts
- Temperature: -10°C
- Elevation: -50m (below sea level)
- Account balance: -$100 (overdrawn)

Operations:
- Addition: -3 + 5 = 2
- Subtraction: 5 - 8 = -3
- Multiplication: -3 × -2 = 6
```

### Rational Numbers (ℚ)

```
Definition: Numbers expressible as fractions

Format: p/q where p, q are integers, q ≠ 0

Examples:
- 1/2 = 0.5
- 3/4 = 0.75
- 22/7 ≈ π (approximation)

Purpose: Precise division
- 1/3 of something
- 0.25 (quarter)
- 2.5 (two and a half)
```

### Real Numbers (ℝ)

```
Definition: All numbers on number line

Includes:
- Rationals: 1/2, 0.5
- Irrationals: π, √2, e

Cannot be expressed as fractions:
- π = 3.14159265358979...
- e = 2.71828182845904...
- √2 = 1.41421356237309...

Purpose: Continuous quantities
- Distance: 3.7 meters
- Time: 5.238 seconds
- Probability: 0.73
```

### Binary (Base-2)

```
Definition: Number system using only 0 and 1

Purpose: How computers represent all numbers

Place Values:
... 128  64  32  16  8  4  2  1
... 2⁷   2⁶  2⁵  2⁴  2³ 2² 2¹ 2⁰

Examples:
Decimal → Binary
0 → 0
1 → 1
2 → 10
3 → 11
4 → 100
5 → 101
10 → 1010
42 → 101010

Calculation for 42:
42 = 32 + 8 + 2
   = 2⁵ + 2³ + 2¹
   = 101010₂
```

### Hexadecimal (Base-16)

```
Definition: Number system using 0-9 and A-F

Digits: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F
Where: A=10, B=11, C=12, D=13, E=14, F=15

Purpose: Compact representation of binary
- 1 hex digit = 4 binary digits
- 2 hex digits = 1 byte

Examples:
Decimal → Hex
15 → F
16 → 10
255 → FF
4096 → 1000

Color in web (RGB):
Red = #FF0000 = 255,0,0
Blue = #0000FF = 0,0,255
White = #FFFFFF = 255,255,255
```

---

## 0.11.2 - Arithmetic

### Addition

```
Definition: Combining quantities

Notation: a + b = c

Properties:
- Commutative: a + b = b + a
  (Order doesn't matter: 3 + 5 = 5 + 3)

- Associative: (a + b) + c = a + (b + c)
  (Grouping doesn't matter: (2 + 3) + 4 = 2 + (3 + 4))

- Identity: a + 0 = a
  (Adding zero doesn't change value)
```

### Multiplication

```
Definition: Repeated addition

Notation: a × b = c (also a·b or ab)

Properties:
- Commutative: a × b = b × a
- Associative: (a × b) × c = a × (b × c)
- Distributive: a × (b + c) = a×b + a×c
- Identity: a × 1 = a
- Zero: a × 0 = 0

Example:
3 × 4 = 3 + 3 + 3 + 3 = 12
```

### Division

```
Definition: Inverse of multiplication

Notation: a ÷ b = c (also a/b)

Special Cases:
- Division by zero: UNDEFINED
  (Cannot divide by zero)

- Division by one: a ÷ 1 = a

Example:
12 ÷ 4 = 3 (because 3 × 4 = 12)
```

### Exponentiation

```
Definition: Repeated multiplication

Notation: aⁿ (a to the power of n)

Examples:
2³ = 2 × 2 × 2 = 8
10⁴ = 10 × 10 × 10 × 10 = 10,000

Special Cases:
a⁰ = 1 (anything to power 0 is 1)
a¹ = a
a⁻¹ = 1/a (negative exponent = reciprocal)

Computer Use:
2⁸ = 256 (1 byte can represent 256 values)
2³² = 4,294,967,296 (32-bit integer range)
```

---

## 0.11.3 - Algebra

### Variables

```
Definition: Symbols representing unknown or changeable values

Notation: Usually letters (x, y, z, a, b, c)

Example:
x + 5 = 10

Solving:
x + 5 = 10
x + 5 - 5 = 10 - 5
x = 5
```

### Functions

```
Definition: Relationship between inputs and outputs

Notation: f(x) = expression

Examples:
f(x) = x + 1
  Input: 5 → Output: 6
  Input: 10 → Output: 11

f(x) = x²
  Input: 3 → Output: 9
  Input: 5 → Output: 25

f(x) = 2x
  Input: 4 → Output: 8
```

### Linear Functions

```
Format: y = mx + b

Where:
- m = slope (rate of change)
- b = y-intercept (starting value)

Example: Storage cost
y = 0.10x + 5
  x = gigabytes stored
  y = monthly cost in dollars
  0.10 = $0.10 per GB
  5 = $5 base fee

If x = 100 GB:
y = 0.10(100) + 5 = 10 + 5 = $15/month
```

---

## 0.11.4 - Geometry

### Points & Coordinates

```
2D Coordinate System:
Point: (x, y)
  x = horizontal position
  y = vertical position

Example: (3, 4)
  3 units right, 4 units up

3D Coordinate System:
Point: (x, y, z)
  x = horizontal
  y = vertical
  z = depth

GPS Coordinates:
(latitude, longitude)
(40.7128, -74.0060) = New York City
```

### Distance

```
Distance between two points in 2D:

d = √[(x₂-x₁)² + (y₂-y₁)²]

Example:
Point A: (1, 2)
Point B: (4, 6)

d = √[(4-1)² + (6-2)²]
  = √[3² + 4²]
  = √[9 + 16]
  = √25
  = 5
```

### Haversine Formula

```
Purpose: Distance between two points on Earth's surface

Given:
- Point 1: (lat₁, lon₁)
- Point 2: (lat₂, lon₂)
- R = Earth's radius ≈ 6,371 km

Formula:
a = sin²(Δlat/2) + cos(lat₁) × cos(lat₂) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1-a))
d = R × c

Use in Hypernet:
Location.nearby(lat, lon, radius_km) uses Haversine to find
nearby locations within radius.
```

---

## 0.11.5 - Calculus

### Derivatives

```
Definition: Rate of change

Notation: f'(x) or df/dx

Example:
f(x) = x² (position)
f'(x) = 2x (velocity)

At x = 3:
f'(3) = 2(3) = 6 (changing at rate of 6)

Use in Hypernet:
- Growth rate of data storage
- Change in API usage over time
- Optimization (finding minimum/maximum)
```

### Integrals

```
Definition: Accumulation over time

Notation: ∫f(x)dx

Example:
f(x) = 2 (constant rate)
∫₀¹⁰ 2 dx = 2 × 10 = 20 (total accumulation)

Use in Hypernet:
- Total data transferred over period
- Cumulative API calls
- Total value created
```

---

## 0.11.6 - Statistics & Probability

### Mean (Average)

```
Definition: Sum divided by count

Formula: μ = (x₁ + x₂ + ... + xₙ) / n

Example:
Photos per day: [5, 3, 8, 4, 5]
Mean = (5 + 3 + 8 + 4 + 5) / 5 = 25 / 5 = 5
```

### Median

```
Definition: Middle value when sorted

Example:
[1, 3, 5, 7, 9] → Median = 5

[1, 2, 3, 4, 5, 6] → Median = (3 + 4) / 2 = 3.5
```

### Standard Deviation

```
Definition: Measure of spread

Formula: σ = √[Σ(x - μ)² / n]

Use: Understanding variability
- Low σ: Data clustered near mean
- High σ: Data spread out
```

### Probability

```
Definition: Likelihood of event

Range: 0 (impossible) to 1 (certain)

Example:
Fair coin flip:
P(heads) = 0.5 = 50%
P(tails) = 0.5 = 50%

Rolling die:
P(six) = 1/6 ≈ 0.167 ≈ 16.7%
```

---

## 0.11.7 - Logic

### Boolean Logic

```
Definition: Logic with two values: True and False

Operations:

AND (∧):
True AND True = True
True AND False = False
False AND True = False
False AND False = False

OR (∨):
True OR True = True
True OR False = True
False OR True = True
False OR False = False

NOT (¬):
NOT True = False
NOT False = True

XOR (exclusive or):
True XOR True = False
True XOR False = True
False XOR True = True
False XOR False = False
```

### Set Theory

```
Set: Collection of distinct objects

Notation: {1, 2, 3}

Operations:
Union (∪): All elements from both sets
  {1, 2} ∪ {2, 3} = {1, 2, 3}

Intersection (∩): Elements in both sets
  {1, 2} ∩ {2, 3} = {2}

Difference (-): Elements in first but not second
  {1, 2, 3} - {2} = {1, 3}
```

---

## 0.11.8 - Physics

### Time

```
Definition: Dimension in which events occur in sequence

Units:
- Second (s): Base unit
- Minute: 60 seconds
- Hour: 3,600 seconds
- Day: 86,400 seconds

Unix Timestamp:
Seconds since January 1, 1970 00:00:00 UTC

Example:
1,709,251,200 = February 29, 2024 12:00:00 UTC

Use in Hypernet:
- All timestamps stored as Unix time
- Human-readable via ISO 8601
```

### Information

```
Definition: Reduction of uncertainty

Units:
- Bit: Single binary digit (0 or 1)
- Byte: 8 bits
- Kilobyte (KB): 1,024 bytes
- Megabyte (MB): 1,024 KB = 1,048,576 bytes
- Gigabyte (GB): 1,024 MB
- Terabyte (TB): 1,024 GB

Information Entropy:
H = -Σ p(x) log₂ p(x)

Measures surprise/uncertainty in data
```

### Speed of Light

```
c = 299,792,458 meters/second

Implications:
- Nothing can travel faster
- Information has maximum speed
- Latency is unavoidable across distance

Example:
New York to London: ~5,585 km
Minimum latency: 5,585,000 / 299,792,458 ≈ 0.0186 seconds = 18.6 ms

(Real latency is higher due to routing, processing, etc.)
```

---

## Why Mathematics Matters

### 1. Computation Foundation
All computing is mathematics - bits, logic, arithmetic.

### 2. Data Analysis
Statistics enable understanding of patterns in data.

### 3. Optimization
Calculus allows finding best solutions.

### 4. Encryption
Number theory enables cryptography and security.

### 5. Geometry
Spatial operations (distance, location, mapping).

### 6. Universal Language
Mathematics transcends human languages - truly universal.

---

**Status:** Active - Core Mathematics Defined
**Created:** February 10, 2026
**Purpose:** Define mathematical foundations from first principles
**Owner:** Hypernet Core Team
**Philosophy:** "Mathematics is the language of the universe - and of computation."

---

*"An alien civilization might not understand English, but they would understand mathematics."*
— Hypernet Mathematics Philosophy
