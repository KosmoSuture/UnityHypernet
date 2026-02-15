# 0.9 - Language Definitions

## Purpose

Defines all languages used in Hypernet - human languages, programming languages, markup languages, and encoding systems. Part of the "explain to aliens" foundation.

**Hypernet Address:** `0.9.*`

---

## Philosophy: Define Every Language

To truly be self-defining, Hypernet must explain:
- What IS a language?
- How do humans communicate?
- How do machines communicate?
- How is meaning encoded?

---

## Language Categories

### 0.9.1 - Human Natural Languages
Languages humans use to communicate with each other

### 0.9.2 - Programming Languages
Languages humans use to instruct computers

### 0.9.3 - Markup & Styling Languages
Languages for structuring and styling content

### 0.9.4 - Data Definition Languages
Languages for describing data structures

### 0.9.5 - Query Languages
Languages for requesting data

### 0.9.6 - Encoding Systems
How characters and symbols are represented

---

## 0.9.1 - Human Natural Languages

### What IS Language?

```
Language: A structured system of communication using symbols (sounds, gestures,
written characters) governed by grammatical rules to express meaning.

Components:
1. Phonology: Sound system
2. Morphology: Word structure
3. Syntax: Sentence structure
4. Semantics: Meaning
5. Pragmatics: Context and usage
```

### English

```
Language Family: Indo-European → Germanic → West Germanic

Alphabet: Latin alphabet (26 letters)
- A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
- a b c d e f g h i j k l m n o p q r s t u v w x y z

Basic Grammar:
- Word Order: Subject-Verb-Object (SVO)
  Example: "Matt (S) writes (V) code (O)"

- Articles: a, an, the
  - Definite: "the cat" (specific cat)
  - Indefinite: "a cat" (any cat)

- Verb Tenses:
  - Present: "I write"
  - Past: "I wrote"
  - Future: "I will write"

- Plurals: Usually add -s
  - cat → cats
  - dog → dogs
  - (Irregular: child → children, person → people)

Common Words:
- Pronouns: I, you, he, she, it, we, they
- Prepositions: in, on, at, to, from, with
- Conjunctions: and, or, but, because, if
```

### Character Set

```
English uses UTF-8 encoding:

Basic Latin (U+0020 to U+007E):
- Letters: A-Z, a-z
- Digits: 0-9
- Punctuation: . , ! ? ; : ' "
- Symbols: @ # $ % & * ( ) - + = / \

Common Usage:
"Hello, world!" = H e l l o , [space] w o r l d !
```

### Language Variants

```
British English vs American English:

Spelling:
- colour (UK) vs color (US)
- programme (UK) vs program (US)
- centre (UK) vs center (US)

Vocabulary:
- lift (UK) vs elevator (US)
- lorry (UK) vs truck (US)
- flat (UK) vs apartment (US)
```

---

## 0.9.2 - Programming Languages

### What IS Programming?

```
Programming: Writing instructions for computers in a language they can execute.

Levels:
1. Machine Code: Binary (0s and 1s) - CPU understands directly
2. Assembly: Low-level symbolic (MOV, ADD, JMP)
3. High-level: Human-readable (Python, JavaScript)

Compilation vs Interpretation:
- Compiled: Source → Machine code → Execute (C, Rust)
- Interpreted: Source → Execute directly (Python, JavaScript)
- Hybrid: Source → Bytecode → Virtual Machine (Java, C#)
```

### Python

```
Language Type: High-level, interpreted, dynamically typed

Philosophy: Readable and simple syntax

Example - Hello World:
print("Hello, world!")

Example - Function:
def add(a, b):
    """Add two numbers and return the result"""
    return a + b

result = add(5, 3)  # result = 8

Data Types:
- Integer: 42
- Float: 3.14
- String: "Hello"
- Boolean: True, False
- List: [1, 2, 3]
- Dictionary: {"name": "Matt", "age": 35}
- None: null/nothing

Control Flow:
if condition:
    # do something
elif other_condition:
    # do something else
else:
    # fallback

Loops:
for item in items:
    # process item

while condition:
    # repeat
```

### JavaScript

```
Language Type: High-level, interpreted, dynamically typed

Primary Use: Web browsers, Node.js servers

Example - Hello World:
console.log("Hello, world!");

Example - Function:
function add(a, b) {
    // Add two numbers
    return a + b;
}

const result = add(5, 3);  // result = 8

Arrow Functions:
const add = (a, b) => a + b;

Data Types:
- Number: 42, 3.14
- String: "Hello"
- Boolean: true, false
- Array: [1, 2, 3]
- Object: {name: "Matt", age: 35}
- null: intentional absence
- undefined: not yet assigned

Promises (Asynchronous):
async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
}
```

### SQL (Structured Query Language)

```
Language Type: Domain-specific for databases

Purpose: Query and manipulate data in relational databases

Example - Select:
SELECT name, age
FROM users
WHERE age > 30
ORDER BY name;

Example - Insert:
INSERT INTO users (name, age, email)
VALUES ('Matt', 35, 'matt@hypernet.com');

Example - Update:
UPDATE users
SET age = 36
WHERE name = 'Matt';

Example - Delete:
DELETE FROM users
WHERE age < 18;

Example - Join:
SELECT users.name, photos.title
FROM users
JOIN photos ON photos.user_id = users.id
WHERE users.name = 'Matt';
```

---

## 0.9.3 - Markup Languages

### HTML (HyperText Markup Language)

```
Purpose: Structure web content

Basic Structure:
<!DOCTYPE html>
<html>
  <head>
    <title>Page Title</title>
  </head>
  <body>
    <h1>Main Heading</h1>
    <p>This is a paragraph.</p>
    <a href="https://hypernet.com">Link</a>
    <img src="photo.jpg" alt="Description">
  </body>
</html>

Elements:
- <h1> to <h6>: Headings
- <p>: Paragraph
- <a>: Link
- <img>: Image
- <div>: Generic container
- <span>: Inline container
```

### CSS (Cascading Style Sheets)

```
Purpose: Style and layout web content

Example:
body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #333;
    font-size: 24px;
}

.button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
}
```

### Markdown

```
Purpose: Lightweight markup for formatted text

Syntax:
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*
`Code`

- Bullet point
- Another point

1. Numbered list
2. Second item

[Link text](https://url.com)
![Image alt](image.jpg)

> Blockquote

```code block```
```

---

## 0.9.4 - Data Definition Languages

### JSON Schema

```
Purpose: Define structure of JSON data

Example:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "age": {
      "type": "integer",
      "minimum": 0
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  },
  "required": ["name", "email"]
}

Valid Data:
{
  "name": "Matt",
  "age": 35,
  "email": "matt@hypernet.com"
}
```

### XML Schema (XSD)

```
Purpose: Define structure of XML documents

Example:
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="person">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="age" type="xs:integer"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```

---

## 0.9.5 - Query Languages

### GraphQL

```
Purpose: Query language for APIs

Schema Definition:
type User {
  id: ID!
  name: String!
  email: String!
  photos: [Photo!]!
}

type Photo {
  id: ID!
  title: String
  url: String!
  takenAt: DateTime
}

Query:
query {
  user(id: "1.1") {
    name
    photos {
      title
      url
    }
  }
}
```

---

## 0.9.6 - Character Encoding Systems

### ASCII (American Standard Code for Information Interchange)

```
Definition: 7-bit character encoding (128 characters)

Range: 0-127

Common Characters:
0-31: Control characters (not printable)
32: Space
33-47: Punctuation (! " # $ % & ' ( ) * + , - . /)
48-57: Digits (0-9)
58-64: More punctuation (: ; < = > ? @)
65-90: Uppercase letters (A-Z)
91-96: Brackets and symbols ([ \ ] ^ _ `)
97-122: Lowercase letters (a-z)
123-126: More symbols ({ | } ~)
127: DEL (delete)

Example:
'A' = 65 = 0x41 = 01000001 binary
'a' = 97 = 0x61 = 01100001 binary
'0' = 48 = 0x30 = 00110000 binary
```

### Unicode

```
Definition: Universal character encoding standard

Goal: Represent every character from every writing system

Code Points: U+0000 to U+10FFFF (1,114,112 possible characters)

Planes:
- Basic Multilingual Plane (BMP): U+0000 to U+FFFF
  - Most common characters
  - Latin, Greek, Cyrillic, Arabic, Chinese, Japanese, Korean, etc.

- Supplementary Planes: U+10000 to U+10FFFF
  - Historical scripts
  - Emoji
  - Rare characters

Examples:
U+0041: A (Latin capital letter A)
U+4E00: 一 (Chinese character one)
U+1F600: 😀 (grinning face emoji)
```

### UTF-8

```
Definition: Variable-length encoding of Unicode

Advantages:
- Backward compatible with ASCII
- Space-efficient for Latin text
- Self-synchronizing (can find character boundaries)

Encoding:
1 byte: U+0000 to U+007F (ASCII compatible)
  0xxxxxxx

2 bytes: U+0080 to U+07FF
  110xxxxx 10xxxxxx

3 bytes: U+0800 to U+FFFF
  1110xxxx 10xxxxxx 10xxxxxx

4 bytes: U+10000 to U+10FFFF
  11110xxx 10xxxxxx 10xxxxxx 10xxxxxx

Examples:
'A' (U+0041) = 0x41 = 01000001 (1 byte)
'©' (U+00A9) = 0xC2A9 = 11000010 10101001 (2 bytes)
'你' (U+4F60) = 0xE4BDA0 = 11100100 10111101 10100000 (3 bytes)
'😀' (U+1F600) = 0xF09F9880 = 11110000 10011111 10011000 10000000 (4 bytes)
```

### UTF-16

```
Definition: Variable-length encoding using 16-bit units

1 unit (2 bytes): U+0000 to U+FFFF (BMP)
2 units (4 bytes): U+10000 to U+10FFFF (surrogate pairs)

Used by: Windows, Java, JavaScript internally
```

---

## Regular Expressions

```
Definition: Pattern matching language for strings

Common Patterns:
.       Any character
\d      Digit (0-9)
\w      Word character (a-z, A-Z, 0-9, _)
\s      Whitespace (space, tab, newline)
+       One or more
*       Zero or more
?       Zero or one
{n,m}   Between n and m repetitions
^       Start of string
$       End of string
[]      Character class
|       Or

Examples:
Email: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
Phone: ^\d{3}-\d{3}-\d{4}$
URL: ^https?://[^\s]+$
```

---

## Why Language Definitions Matter

### 1. Complete Communication
Hypernet can explain how humans and machines communicate.

### 2. Multilingual Support
Understanding language structures enables proper support for all human languages.

### 3. Code Understanding
AI entities can reason about code by understanding programming languages.

### 4. Translation
Language definitions enable translation between languages.

### 5. Encoding Correctness
Proper character encoding prevents data corruption.

---

## Language Statistics in Hypernet

### Human Languages
- Primary: English (documentation, UI)
- Supported: All major languages (user content)
- Encoding: UTF-8 (universal support)

### Programming Languages
- Backend: Python (FastAPI, services)
- Frontend: JavaScript/TypeScript (React)
- Database: SQL (PostgreSQL)
- Configuration: YAML, JSON

### Markup Languages
- Documentation: Markdown
- Web: HTML, CSS
- Data: JSON, XML

---

**Status:** Active - Core Languages Defined
**Created:** February 10, 2026
**Purpose:** Define all languages from first principles
**Owner:** Hypernet Core Team
**Philosophy:** "Language is how meaning moves between minds."

---

*"A language is just an agreement about how to encode thought."*
— Hypernet Language Philosophy
