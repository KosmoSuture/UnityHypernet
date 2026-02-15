# Audio - Audio Media Type

**Type ID:** `hypernet.media.audio`
**Version:** 1.0
**Category:** 0.0.2 - Media Types
**Parent:** Media (extends BaseObject)
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Audio"
type_id: "hypernet.media.audio"
version: "1.0"
parent_type: "Media"
category: "0.0.2 - Media Types"
```

---

## Purpose

### What
Audio files - music, podcasts, voice recordings, voice memos, audiobooks.

### Why
- Music libraries and playlists
- Voice notes and memos
- Podcast collections
- Recorded conversations
- Minimal storage compared to video

### When to Use
- Music files (MP3, AAC, FLAC)
- Voice recordings
- Podcasts and audiobooks
- Extracted audio from videos

---

## Required Fields

```yaml
filename: String(255)
media_type: "audio" (fixed)
mime_type: String(100)
  - audio/mpeg (MP3)
  - audio/aac
  - audio/ogg
  - audio/flac
  - audio/wav
  - audio/x-m4a

file_size: Integer (max 500MB)
file_path: String(512)
hash: String(64)
```

---

## Optional Fields

```yaml
duration: Float (seconds)
codec: String(50)
  - "mp3", "aac", "flac", "opus", "vorbis"

bitrate: Integer (kbps)
sample_rate: Integer (Hz)
  - 44100, 48000, 96000

channels: Integer
  - 1 (mono), 2 (stereo), 6 (5.1)

recorded_at: DateTime

processing_status: Enum
  - pending, processing, ready, error

waveform_path: String(512) (visual waveform)
```

---

## Metadata Schema

```json
{
  "id3": {
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "year": 2024,
    "genre": "Rock",
    "track_number": 5
  },
  "tags": ["music", "rock"],
  "ai_analysis": {
    "transcript": "...",
    "language": "en-US",
    "speakers": 2,
    "sentiment": "positive"
  },
  "spotify": {
    "track_id": "...",
    "uri": "spotify:track:..."
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (Spotify, Apple Music)
  - duplicate_of: Audio
  - variant_of: Audio (different quality)

Incoming:
  - contains: Playlist, Album
  - referenced_by: Note, Message
```

---

## Validation

```sql
CHECK (media_type = 'audio')
CHECK (file_size > 0 AND file_size <= 524288000) -- 500MB
CHECK (duration IS NULL OR duration > 0)
CHECK (channels IS NULL OR channels IN (1, 2, 6, 8))

INDEX ON (mime_type, codec)
```

---

## API Endpoints

```http
POST /api/v1/media/upload
GET /api/v1/media/{id}/stream
GET /api/v1/media/{id}/waveform
POST /api/v1/media/{id}/transcribe (speech-to-text)
```

---

**Status:** Active - Phase 1
**Version:** 1.0
