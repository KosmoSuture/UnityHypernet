"""
Hypernet Personal Data Integrations

Tools for importing, triaging, and organizing personal data from external
services into the Hypernet address space.

Connectors:
- Gmail (OAuth2 + IMAP)
- Generic IMAP (schaeffer.org, etc.)
- Dropbox (OAuth2 API)
- OneDrive (Microsoft Graph API)
- Photo deduplication and organization
- Google Maps Location History (Takeout export)
- Facebook, LinkedIn, Google Photos (GDPR exports)
- GEDCOM/PAF Genealogy (6 - People of History)
- Local file scanner

Architecture:
- Each connector authenticates and pulls raw data into private/import-staging/
- Triage engine separates signal from noise
- Important items get Hypernet addresses and move into the public structure
- Nothing is deleted — originals archived per 2.0.19
"""
