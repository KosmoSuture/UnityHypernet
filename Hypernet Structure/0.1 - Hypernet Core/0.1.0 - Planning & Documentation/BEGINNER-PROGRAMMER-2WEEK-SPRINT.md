# Beginner Programmer 2-Week Sprint
## Clear, Achievable Tasks for Junior Developer

**Goal:** Contribute meaningfully while learning real development skills

---

## Week 1: Foundation & Setup

### Monday: Environment Setup (4 hours)

**Task 1.1: Install Development Tools**
- [ ] Install Python 3.10+ from python.org
- [ ] Install Visual Studio Code
- [ ] Install Git for Windows
- [ ] Test installations (run `python --version`, `git --version`)

**Task 1.2: Set Up Project**
```bash
cd "C:\Hypernet\Hypernet Structure\0.1 - Hypernet Core\0.1.1 - Core System"
pip install -r requirements.txt
```

Create `requirements.txt` if it doesn't exist:
```
fastapi==0.104.1
uvicorn==0.24.0
pillow==10.1.0
pydantic==2.5.0
python-multipart==0.0.6
```

**Task 1.3: Run the API**
```bash
python api.py
```
- Open browser: http://localhost:8000
- Take screenshot showing it works
- Put screenshot in: `0.1.0 - Planning & Documentation/screenshots/api-working.png`

**Deliverable:** Screenshot showing API running + health check response

**How to succeed:**
- Follow instructions exactly
- Google error messages if stuck
- Take notes of what you learn
- Ask for help if stuck > 30 minutes

---

### Tuesday: Test Data Creation (4 hours)

**Task 2.1: Create Test Photos**

Create file: `create_test_data.py`

```python
"""
Create fake but realistic test photos for development
"""
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime, timedelta
import os

def create_test_photo(index, date, location, people):
    """Create a test photo with metadata"""

    # Create image (1920x1080)
    img = Image.new('RGB', (1920, 1080), color=(
        random.randint(100, 200),
        random.randint(100, 200),
        random.randint(100, 200)
    ))

    draw = ImageDraw.Draw(img)

    # Add text overlay
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()

    text = f"Test Photo #{index}\n{date}\n{location}\n{people}"
    draw.text((50, 50), text, fill=(255, 255, 255), font=font)

    # Save
    filename = f"test_photo_{index:04d}.jpg"
    filepath = os.path.join("test_data", "photos", filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, quality=85)

    print(f"Created: {filename}")
    return filepath

# Create 20 test photos
dates = [
    datetime.now() - timedelta(days=random.randint(0, 365))
    for _ in range(20)
]

locations = [
    "Seattle, WA", "New York, NY", "San Francisco, CA",
    "Paris, France", "London, UK", "Tokyo, Japan"
]

people_options = [
    "Matt", "Sarah", "John", "Bridget",
    "Mark", "Richard", "Ollie"
]

for i in range(1, 21):
    date = dates[i-1].strftime("%Y-%m-%d")
    location = random.choice(locations)
    people = ", ".join(random.sample(people_options, random.randint(1, 3)))

    create_test_photo(i, date, location, people)

print("\nDone! Created 20 test photos in test_data/photos/")
```

**Run it:**
```bash
python create_test_data.py
```

**Deliverable:** 20 test photos in `test_data/photos/` folder

---

### Wednesday: Data Validation Functions (4 hours)

**Task 3.1: Write Hypernet Address Validator**

Create file: `validators.py`

```python
"""
Validation functions for Hypernet data
"""
import re
from datetime import datetime

def validate_hypernet_address(address: str) -> tuple[bool, str]:
    """
    Validate a Hypernet Address

    Returns: (is_valid, error_message)

    Examples:
        "1.1" -> (True, "")
        "1.1.8.0.00001" -> (True, "")
        "invalid" -> (False, "Invalid format")
    """

    # Short form (person): 1.1
    short_pattern = r'^\d+\.\d+$'

    # Full form: 1.1.8.0.00001
    full_pattern = r'^\d+\.\d+\.\d+\.\d+\.\d{5}$'

    if re.match(short_pattern, address):
        return (True, "")

    if re.match(full_pattern, address):
        return (True, "")

    return (False, "Invalid Hypernet Address format")


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address"""

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return (True, "")

    return (False, "Invalid email format")


def validate_date(date_str: str) -> tuple[bool, str]:
    """Validate ISO date format (YYYY-MM-DD)"""

    try:
        datetime.fromisoformat(date_str)
        return (True, "")
    except ValueError:
        return (False, "Invalid date format. Use YYYY-MM-DD")


def validate_privacy_level(level: str) -> tuple[bool, str]:
    """Validate privacy level"""

    valid_levels = ['private', 'family', 'friends', 'professional', 'public', 'ai_access', 'legacy']

    if level in valid_levels:
        return (True, "")

    return (False, f"Invalid privacy level. Must be one of: {', '.join(valid_levels)}")


# Tests (run these to verify your functions work)
if __name__ == "__main__":
    print("Testing validators...")

    # Test Hypernet Address
    tests = [
        ("1.1", True),
        ("1.1.8.0.00001", True),
        ("invalid", False),
        ("1.1.8", False)
    ]

    print("\nHypernet Address Validator:")
    for address, should_be_valid in tests:
        is_valid, error = validate_hypernet_address(address)
        status = "✓" if is_valid == should_be_valid else "✗"
        print(f"  {status} {address} -> {is_valid} {error}")

    # Test Email
    email_tests = [
        ("test@example.com", True),
        ("invalid", False),
        ("user@domain.co.uk", True)
    ]

    print("\nEmail Validator:")
    for email, should_be_valid in email_tests:
        is_valid, error = validate_email(email)
        status = "✓" if is_valid == should_be_valid else "✗"
        print(f"  {status} {email} -> {is_valid} {error}")

    # Test Date
    date_tests = [
        ("2024-01-15", True),
        ("2024-1-1", False),
        ("invalid", False)
    ]

    print("\nDate Validator:")
    for date, should_be_valid in date_tests:
        is_valid, error = validate_date(date)
        status = "✓" if is_valid == should_be_valid else "✗"
        print(f"  {status} {date} -> {is_valid} {error}")

    print("\nAll tests complete!")
```

**Run tests:**
```bash
python validators.py
```

**Deliverable:** All tests should print ✓ (checkmarks)

---

### Thursday: Database Inspection Tool (4 hours)

**Task 4.1: Create Database Inspector**

Create file: `inspect_db.py`

```python
"""
Database inspection tool
Shows what's in the Hypernet database
"""
import sqlite3
from datetime import datetime

DB_PATH = "hypernet.db"

def inspect_database():
    """Print summary of database contents"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("HYPERNET DATABASE INSPECTION")
    print("=" * 80)
    print()

    # Objects count by type
    print("OBJECTS BY TYPE:")
    cursor.execute("""
        SELECT object_type, COUNT(*) as count
        FROM objects
        WHERE status = 'active'
        GROUP BY object_type
        ORDER BY count DESC
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:20s} {row[1]:5d}")

    print()

    # Recent photos
    print("RECENT PHOTOS (Last 10):")
    cursor.execute("""
        SELECT
            o.hypernet_address,
            o.title,
            p.taken_at,
            p.location_name
        FROM objects o
        JOIN photos p ON o.id = p.object_id
        WHERE o.status = 'active'
        ORDER BY p.taken_at DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:20s} {row[1]:30s} {row[2]:20s} {row[3] or 'Unknown'}")

    print()

    # People
    print("PEOPLE:")
    cursor.execute("""
        SELECT
            p.hypernet_address,
            p.first_name,
            p.last_name,
            p.relationship_to_owner
        FROM people p
        JOIN objects o ON p.object_id = o.id
        WHERE o.status = 'active'
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:10s} {row[1]} {row[2]:20s} ({row[3]})")

    print()

    # Links
    print("LINKS:")
    cursor.execute("""
        SELECT
            link_type,
            COUNT(*) as count
        FROM links
        WHERE status = 'active'
        GROUP BY link_type
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:20s} {row[1]:5d}")

    print()

    # Database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    size = cursor.fetchone()[0]
    print(f"DATABASE SIZE: {size:,} bytes ({size/1024/1024:.2f} MB)")

    print()
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    inspect_database()
```

**Run it:**
```bash
python inspect_db.py
```

**Deliverable:** Screenshot of database inspection output

---

### Friday: Documentation (4 hours)

**Task 5.1: Document API Endpoints**

Create file: `API-DOCUMENTATION.md` in `0.1.0 - Planning & Documentation/`

```markdown
# Hypernet API Documentation
For VR Developers

## Base URL
http://localhost:8000

## Authentication
None (for MVP demo)

---

## Endpoints

### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "stats": {
    "total_objects": 150,
    "total_photos": 120,
    "total_links": 45
  }
}
```

### GET /photos
Get list of photos

**Parameters:**
- `owner` (string) - Owner Hypernet Address (default: "1.1")
- `limit` (int) - Max results (default: 50, max: 1000)
- `offset` (int) - Pagination offset (default: 0)
- `start_date` (string) - Filter by date (YYYY-MM-DD)
- `end_date` (string) - Filter by date (YYYY-MM-DD)

**Example:**
```
GET /photos?owner=1.1&limit=10
```

**Response:**
```json
{
  "count": 10,
  "photos": [
    {
      "hypernet_address": "1.1.8.0.00001",
      "title": "Family Christmas 2023",
      "taken_at": "2023-12-25T18:30:00",
      "latitude": 47.6062,
      "longitude": -122.3321,
      "location_name": "Seattle, WA"
    }
  ]
}
```

[Continue documenting all endpoints...]
```

**Deliverable:** Complete API documentation with examples for all endpoints

**Task 5.2: Create Setup Guide**

Create `SETUP-GUIDE.md`:
- How to install Python, dependencies
- How to initialize database
- How to import first photos
- How to run API
- Common troubleshooting

---

## Week 2: Testing & Quality Assurance

### Monday: Manual Testing (4 hours)

**Task 6.1: Create Test Checklist**

Create file: `TEST-CHECKLIST.md`

```markdown
# Hypernet API Test Checklist

## Setup Tests
- [ ] Python installed correctly
- [ ] Dependencies install without errors
- [ ] Database initializes with schema
- [ ] API starts without errors

## API Endpoint Tests

### Health Check
- [ ] GET /health returns 200
- [ ] Response includes database stats
- [ ] Stats show correct counts

### Photos
- [ ] GET /photos returns photos
- [ ] Pagination works (limit, offset)
- [ ] Date filtering works (start_date, end_date)
- [ ] GET /photos/{address} returns single photo
- [ ] GET /photos/{address}/file serves image file

### Search
- [ ] POST /search with simple query works
- [ ] Search returns relevant results
- [ ] Results are ranked by relevance

### Timeline
- [ ] POST /timeline returns items in date order
- [ ] Date range filtering works
- [ ] Object type filtering works

### People
- [ ] GET /people returns all people
- [ ] GET /people/{address} returns single person
- [ ] living_only filter works

### AI
- [ ] POST /ai/query returns answer
- [ ] Sources are included
- [ ] Execution time is reasonable (< 1 second)

## Error Handling
- [ ] Invalid Hypernet Address returns 404
- [ ] Malformed requests return 400
- [ ] Server errors return 500 with details

## Performance
- [ ] Queries return in < 100ms (most)
- [ ] Can handle 10 simultaneous requests
- [ ] No memory leaks over time

## Documentation
- [ ] API docs match actual behavior
- [ ] All examples work as written
- [ ] Setup guide is accurate
```

**Task 6.2: Execute Tests**

Go through checklist, test every endpoint:

1. Use browser for GET requests
2. Use Thunder Client (VS Code extension) or Postman for POST requests
3. Mark each item as pass/fail
4. Document any bugs found

**Deliverable:** Completed checklist + bug report (if any bugs found)

---

### Tuesday: Bug Fixes & Improvements (4 hours)

**Task 7.1: Fix Simple Bugs**

If you found bugs yesterday, try to fix them. Focus on:
- Typos in code
- Missing error messages
- Incorrect documentation

**Task 7.2: Add Input Validation**

Add validation to API endpoints. Example:

```python
@app.get("/photos")
def get_photos(
    owner: str = Query("1.1"),
    limit: int = Query(50, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset"),
    conn: sqlite3.Connection = Depends(get_db)
):
    # Add validation
    is_valid, error = validate_hypernet_address(owner)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # ... rest of function
```

Add validation to at least 3 endpoints.

**Deliverable:** Pull request or commit with bug fixes

---

### Wednesday: UI/UX Design (Figma) (4 hours)

**Task 8.1: Learn Figma Basics**

1. Create free Figma account: figma.com
2. Watch tutorial: "Figma in 40 Minutes" on YouTube
3. Complete practice exercises in tutorial

**Task 8.2: Design VR Interface Mockups**

Create Figma file with mockups for:

1. **Home Screen**
   - Floating Hypernet logo
   - Categories (Photos, People, Timeline, Search)
   - Stats summary

2. **Photo Gallery**
   - Grid of photos
   - How they're arranged in 3D space
   - Selection highlight

3. **Timeline View**
   - Photos arranged chronologically
   - Date labels
   - Navigation controls

4. **AI Assistant**
   - Avatar design
   - Speech bubble
   - Example queries

**Deliverable:** Figma link to mockups + exported PNGs

---

### Thursday: Assets & Resources (4 hours)

**Task 9.1: Find 3D Models**

Research and download free 3D models for VR:

1. Unity Asset Store (free assets)
2. Sketchfab (free Creative Commons models)
3. Poly Haven (free 3D assets)

Find:
- [ ] UI icons (photo, person, calendar, search)
- [ ] Environment (sky, floor textures)
- [ ] AI assistant avatar (simple, friendly)
- [ ] Hand models (for VR controllers)

Create folder: `Assets/3D-Models/` and organize by type

**Deliverable:** Organized folder of 10+ useful 3D assets

**Task 9.2: Color Scheme & Branding**

Create `BRAND-GUIDELINES.md`:
- Color palette (5-7 colors)
- Font choices
- Logo concepts (sketch or describe)
- Visual style (modern, minimal, futuristic?)

Use tools:
- Coolors.co (color palette generator)
- Google Fonts (font browsing)

---

### Friday: Demo Preparation (4 hours)

**Task 10.1: Create Demo Video Script**

Write script for 2-minute demo video:

```
Demo Video Script
-----------------

[0:00-0:10] Hook
"Your digital life is scattered across 50 apps. What if you could see it all in one place - in virtual reality?"

[0:10-0:30] Problem
Show screenshots of: Gmail, Google Photos, Dropbox, Calendar (fragmentation)
"You have no control. AI companies train on your data without paying you."

[0:30-1:00] Solution
Show VR screenshots:
- Person wearing Quest 3
- Inside view: Photos in 3D space
- Timeline navigation
- AI assistant answering question

[1:00-1:30] Features
- "Unified data layer - everything has an address"
- "VR interface - see your life in 3D"
- "AI marketplace - get paid for your data"

[1:30-2:00] Call to Action
- "Join the waitlist: hypernet.com"
- "Investors: schedule a demo"
- Logo + contact info
```

**Task 10.2: Gather Demo Assets**

Create folder: `Demo-Assets/`

Collect:
- [ ] Best VR screenshots (10+)
- [ ] Screen recordings of API working
- [ ] Graphics for "problem" section
- [ ] Logo mockups
- [ ] Music options (royalty-free from YouTube Audio Library)

**Deliverable:** Complete demo assets folder + video script

---

## Success Metrics

### Week 1
- [ ] Environment set up correctly
- [ ] API running and tested
- [ ] 20 test photos created
- [ ] Validation functions working
- [ ] Documentation written

### Week 2
- [ ] All endpoints tested
- [ ] Bugs fixed (if any)
- [ ] VR interface mockups created
- [ ] 3D assets collected
- [ ] Demo video planned

---

## Learning Outcomes

By end of Week 2, you should be able to:

**Technical Skills:**
- ✅ Set up Python development environment
- ✅ Run API server
- ✅ Write basic Python functions
- ✅ Test API endpoints
- ✅ Read and understand code
- ✅ Debug simple errors

**Design Skills:**
- ✅ Use Figma for mockups
- ✅ Think about UX in VR
- ✅ Find and organize 3D assets
- ✅ Create brand guidelines

**Product Skills:**
- ✅ Write technical documentation
- ✅ Create test plans
- ✅ Script demo videos
- ✅ Think about user experience

---

## Tips for Success

### Before Starting Each Task
1. Read entire task description
2. Make sure you understand what "done" looks like
3. Estimate how long it will take
4. Break into smaller sub-tasks if needed

### While Working
- Work in focused blocks (25-50 minutes)
- Take breaks every hour
- Google error messages immediately
- Take screenshots of your progress
- Ask for help if stuck > 30 minutes

### When Stuck
1. Read error message carefully
2. Google the exact error message
3. Check Stack Overflow
4. Try simplifying the problem
5. Ask Matt for help

### Communication
- End each day: Send quick update (what you did, what's next)
- Found a bug? Document it clearly
- Have an idea? Write it down
- Blocked? Say so immediately

---

## Future Tasks (Week 3+)

Once you complete these, you'll be ready for:
- Writing more complex Python code
- Contributing to Unity VR app
- Creating actual demo video
- Helping with pitch deck design
- User testing and feedback collection

---

**Remember:** The goal isn't perfection, it's progress. You're learning while contributing. Every task makes you more valuable to the team.

Good luck! 🚀
