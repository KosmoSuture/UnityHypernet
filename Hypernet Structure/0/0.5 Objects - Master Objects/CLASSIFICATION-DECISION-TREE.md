---
ha: "0.5"
object_type: "0.5.3.1"
creator: "2.1.adversary"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# Object Classification Decision Tree

**Author:** The Adversary (Audit Swarm Node 4)
**Date:** 2026-02-22
**Companion to:** TAXONOMY-PROPOSAL.md
**Purpose:** Given any real-world object, determine its 0.5.x type in 5 questions or fewer.
**Status:** PROPOSAL — supplements the Architect's taxonomy

---

## How to Use This

Start at Question 1. Follow the path. You'll reach a 0.5.x category in 3-5 steps. If you reach a dead end, use `0.5.0.1 Generic Object` and flag it for taxonomy review.

**Rule:** Always choose the PRIMARY type — what the object IS, not what it RELATES TO. A medical image is an Image (what it is) that relates to health (what it's about). Use links and flags for the "about" part.

---

## The Decision Tree

### Question 1: Is it a BEING with identity and agency?

**Yes → Is it an individual or a group?**
- Individual (human, AI instance, fictional character) → **0.5.1 Person**
- Group (company, government, team, community) → **0.5.2 Organization**

**No → Question 2**

---

### Question 2: Is it primarily TEXT or STRUCTURED DATA meant to be read/processed?

**Yes → Does it have a sender and recipient (directional communication)?**
- Yes (email, chat message, social post, notification, call) → **0.5.14 Communication**
- No → Is it a creative/cultural work with artistic intent?
  - Yes (novel, essay, poem, play, lyrics) → **0.5.15 Creative Work** (literary subcategory)
  - No → **0.5.3 Document**

**No → Question 3**

---

### Question 3: Is it SENSORY content (visual, auditory, spatial) stored as a file?

**Yes → What kind?**
- Image, video, audio, 3D model, map, chart → **0.5.4 Media**
- But wait: is it the FILE or the CULTURAL WORK?
  - The file (JPEG, MP4, MP3) → **0.5.4 Media**
  - The work itself (the painting, the song as composition, the film as art) → **0.5.15 Creative Work**
  - When in doubt, choose Media (the file) and link to Creative Work (the meaning)

**No → Question 4**

---

### Question 4: Is it a PHYSICAL THING that exists in the real world?

**Yes →**
- Computing/electronic device → **0.5.5.1 Device**
- Tool, instrument → **0.5.5.2 Tool**
- Vehicle → **0.5.5.3 Vehicle**
- Furniture → **0.5.5.4 Furniture**
- Clothing, wearable → **0.5.5.5 Clothing & Wearable**
- Food, drink, medication, supply → **0.5.5.6 Consumable**
- Building, bridge, infrastructure → **0.5.5.7 Structure**
- Raw material, component, chemical → **0.5.5.8 Material**
- None of the above → **0.5.5 Artifact** (general)

All physical objects → **0.5.5 Artifact**

**No → Question 5**

---

### Question 5: Which of these best describes it?

| Description | Category |
|---|---|
| A place (physical address, building, city, virtual world, website) | **0.5.6 Location** |
| Something that happens at a specific time (meeting, birthday, earthquake, deployment) | **0.5.7 Event** |
| An abstract idea, theory, category, symbol, or method | **0.5.8 Concept** |
| Work to be done: a task, project, workflow, goal, or experiment | **0.5.9 Action** |
| Executable code, an application, API, dataset, or AI model | **0.5.10 Software** |
| Money, a financial account, transaction, investment, or invoice | **0.5.11 Financial** |
| A living thing, health record, genetic data, recipe, or ecological data | **0.5.12 Biological** |
| A contract, law, regulation, patent, license, or identity document | **0.5.13 Legal** |
| A single data point: temperature, metric, rating, sensor reading | **0.5.16 Measurement** |
| None of the above | **0.5.0.1 Generic Object** |

---

## Quick-Reference: Common Ambiguities

These objects commonly cause classification confusion. Here's the canonical answer:

| Object | Common Confusion | Correct Type | Why |
|---|---|---|---|
| Email | Document or Communication? | **0.5.14.1.1** Communication | Has sender, recipient, delivery status |
| Social media post | Document or Communication? | **0.5.14.1.4** Communication | Has author, audience, threading, engagement |
| Blog post | Document or Communication? | **0.5.3.7.3** Document | Published text, no specific recipient |
| Chat message | Document or Communication? | **0.5.14.1.3** Communication | Real-time, threaded, delivery status |
| Newsletter | Communication or Document? | **0.5.14.4.1** Communication | Broadcast to subscribers |
| Book | Document or Creative Work? | **0.5.3.7.1** Document (for the text); **0.5.15.2.1** Creative Work (for the literary work) | Create both, link them |
| Photograph (file) | Media or Creative Work? | **0.5.4.1** Media | It's a file with dimensions, encoding |
| Photograph (art) | Media or Creative Work? | **0.5.15.1.3** Creative Work | It's a work with artist, style, meaning |
| Song (audio file) | Media or Creative Work? | **0.5.4.3** Media | It's a file with duration, bit rate |
| Song (composition) | Media or Creative Work? | **0.5.15.3.2** Creative Work | It's a work with composer, genre |
| Smart contract | Software or Legal or Financial? | **0.5.10.1** Software | It's code. Link to Legal + Financial for context |
| Recipe | Document or Biological? | **0.5.12.5.1** Biological (Recipe) | It has ingredients, nutrition, cooking method |
| Medical image | Media or Biological? | **0.5.4.1** Media | It's an image file. Flag `0.8.2.medical`, link to Health Record |
| Podcast episode | Media or Communication or Creative Work? | **0.5.4.3** Media (the audio file) | It's an audio file. Link to Creative Work if it's a produced show |
| Playlist | Media or Creative Work? | Use links-based Collection pattern | A playlist is a set of `contains` links from a parent object. See COLLECTION-PATTERN.md |
| Transaction record | Event or Financial? | **0.5.11.2** Financial | It has amount, currency, counterparty — Financial's structural signature |
| Calendar event | Event or Action? | **0.5.7.1** Event | It happens at a time. A task to prepare for it is a separate 0.5.9 Action |
| Bug report | Document or Action? | **0.5.9.1.2** Action (Bug Report) | It has status, assignee, priority — Action's structural signature |
| Meme | Media or Communication or Creative Work? | **0.5.4.1** Media (the image file) | Flag: `cultural_meme`. Link to Creative Work if notable |
| NFT | Financial or Media or Legal? | **0.5.11.3.4** Financial (Token) | The token is financial. What it points to is a separate linked object |
| QR code | Media or Data? | **0.5.4.1** Media (Image) | It's an image. What it encodes is a separate linked object |
| Booking/Reservation | Event or Action? | **0.5.9.1** Action (Task) | It's an intent/commitment with status. The event it reserves is a separate linked Event |

---

## The One Rule

**When in doubt: choose the type whose STRUCTURAL SIGNATURE matches best, not whose TOPIC matches best.**

Structural signature = the fields that are ESSENTIAL to the object:
- If it has sender + recipient + delivery status → Communication
- If it has amount + currency + counterparty → Financial
- If it has dimensions + encoding + file size → Media
- If it has status + assignee + dependencies → Action
- If it has start time + end time + participants → Event

Topic is expressed through LINKS and FLAGS, not through type. A medical document is `type: Document` with `flag: medical` and `link: health_record`.

---

*This decision tree is designed to reduce classification ambiguity to near zero. If an object genuinely cannot be classified using this tree, that's a signal the taxonomy needs a new type — file a governance proposal.*
