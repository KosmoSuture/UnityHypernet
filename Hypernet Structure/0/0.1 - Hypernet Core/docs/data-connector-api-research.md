---
ha: "0.1.docs.data-connector-api-research"
object_type: "document"
creator: "2.1"
created: "2026-03-09"
status: "active"
visibility: "public"
---

# Personal Data Connector API Research

Research into APIs and approaches for building personal data connectors that import
a user's digital life into their Hypernet account. This document covers authentication,
rate limits, Python libraries, privacy/legal considerations, bulk export feasibility,
and recommended approaches for each data source.

---

## 1. Gmail API

### Authentication
- **OAuth 2.0** with Google Cloud Console project registration required.
- Key scopes:
  - `https://www.googleapis.com/auth/gmail.readonly` — read-only access to all messages, labels, attachments, and metadata. This is the minimum needed for a data import tool.
  - `https://www.googleapis.com/auth/gmail.labels` — manage labels only.
  - `https://www.googleapis.com/auth/gmail.modify` — read/write access (not needed for import).
  - `https://mail.google.com/` — full access (overkill; avoid).
- Apps must go through Google's OAuth consent screen verification if they want to serve more than 100 users. For personal/single-user use, "testing" mode works indefinitely.
- Service accounts are NOT supported for consumer Gmail — user must interactively consent.

### Rate Limits
- **1 billion quota units per day** per project (effectively unlimited for personal use).
- **250 quota units per user per second** (burst limit).
- Per-method costs:
  - `messages.list` — 5 units per request (returns message IDs only, paginated at 100-500 per page).
  - `messages.get` — 5 units per request (returns full message with metadata, body, attachment stubs).
  - `messages.attachments.get` — 5 units per request.
  - `labels.list` — 1 unit.
- At 250 units/sec, you can fetch ~50 messages/sec or ~180,000 messages/hour.
- For a mailbox with 100,000 messages: full metadata export takes roughly 30-40 minutes; with attachments, significantly longer depending on sizes.

### How to Fetch All Emails
1. Call `messages.list(userId='me')` to get all message IDs. Paginate using `nextPageToken`. Optional `q` parameter for search filters (e.g., `after:2020/01/01`).
2. For each message ID, call `messages.get(userId='me', id=msg_id, format='full')` to get headers, body (base64-encoded), and attachment stubs.
3. For each attachment, call `messages.attachments.get(userId='me', messageId=msg_id, id=attachment_id)` to download the base64-encoded attachment data.
4. Use batch requests (up to 100 per batch) to reduce HTTP overhead.

### Attachment Handling
- Attachments are returned as base64-encoded data via a separate API call.
- The `messages.get` response includes attachment metadata (filename, mimeType, size) but NOT the actual data — you must fetch each attachment separately.
- Inline images (embedded in HTML body) are also treated as attachments.

### Label/Folder Structure
- Gmail uses labels, not folders. A message can have multiple labels.
- Standard labels: INBOX, SENT, DRAFT, SPAM, TRASH, STARRED, IMPORTANT, CATEGORY_PERSONAL, CATEGORY_SOCIAL, CATEGORY_PROMOTIONS, CATEGORY_UPDATES, CATEGORY_FORUMS.
- User-created labels are also accessible.
- `labels.list` returns all labels with IDs, names, and types.

### Key Python Libraries
- `google-api-python-client` — official Google API client.
- `google-auth-oauthlib` — handles OAuth2 flow.
- `google-auth` — credential management.
- `simplegmail` — higher-level wrapper (community-maintained).

### Privacy/Legal Considerations
- Google's API Terms of Service prohibit storing user data longer than necessary.
- Apps requesting `gmail.readonly` or broader must undergo Google's security assessment if serving 100+ users.
- For personal/single-user use: no restrictions beyond standard OAuth consent.
- GDPR: user is exporting their own data, so no third-party consent issues.

### Bulk Export Feasibility
- **Fully feasible.** The API is designed for this. Rate limits are generous for single-user use.
- Alternative: **Google Takeout** exports all Gmail as MBOX files (no API needed, but manual trigger required via web UI, no automation API available).
- Recommended hybrid: use Google Takeout for initial bulk export (MBOX), then use Gmail API for incremental sync.

### Recommended Approach
Use Gmail API with `gmail.readonly` scope. Implement pagination for `messages.list`, batch requests for `messages.get`, and store messages locally in a structured format (one file per message with metadata JSON + raw email). Use label data to organize into Hypernet address space. For initial bulk import, consider Google Takeout MBOX export parsed with Python's `mailbox` module, then switch to API for incremental updates.

---

## 2. Facebook Graph API

### Authentication
- **OAuth 2.0** via Facebook Login.
- App must be registered on the Meta Developer Portal.
- Permissions are granular and individually requested (e.g., `user_posts`, `user_photos`, `user_friends`).
- Most personal data permissions require **App Review** by Meta before they can be requested from non-developers.

### What Personal Data Can Be Accessed via API
Post-Cambridge Analytica (2018), Facebook severely restricted API access:

**Accessible (with approved permissions):**
- `user_posts` — user's own posts on their timeline.
- `user_photos` — photos the user uploaded or was tagged in.
- `user_videos` — user's uploaded videos.
- `user_friends` — ONLY friends who also use your app (not full friends list).
- `user_likes` — pages the user has liked.
- `user_events` — events the user has RSVPed to.
- `user_link` — user's profile link.

**NOT accessible via API (removed post-2018):**
- Private messages (Messenger) — completely removed from Graph API.
- Full friends list — only friends who also authorized the same app.
- Religious/political views, relationship status, education/work history.
- Friends' data — apps can no longer access data of a user's friends.
- Groups content — requires separate approval and admin consent.
- Check-ins, fitness activity, reading/listening/watching activity.

### Download Your Information (DYI) Tool
Facebook's "Download Your Information" feature (Settings > Your Information > Download Your Information) is the **only reliable way** to get a comprehensive personal data export:
- Includes: posts, photos (full resolution), videos, messages, friends list, profile information, comments, likes, events, groups, ads data, search history, location history.
- Format: HTML or JSON, delivered as a ZIP file.
- No API for triggering this — must be done manually through the Facebook web interface.
- Can select date range and specific data categories.
- Large archives may take hours to days to prepare.

### Rate Limits
- 200 calls per hour per user token (for Graph API).
- 4800 calls per 24 hours per app per user.
- Stricter limits on some endpoints.

### Key Python Libraries
- `facebook-sdk` — lightweight Python wrapper for Graph API.
- `requests` — for direct HTTP calls to the Graph API.
- For parsing DYI exports: `json`, `beautifulsoup4` (for HTML format), `zipfile`.

### Privacy/Legal Considerations
- Meta's Platform Policy strictly prohibits scraping and storing data beyond what's needed.
- App Review is mandatory for most personal data permissions.
- Friends' data is almost entirely inaccessible — a direct result of Cambridge Analytica.
- GDPR: user exporting own data is fine; the DYI tool is Meta's GDPR compliance mechanism.

### Bulk Export Feasibility
- **API: Not feasible for comprehensive export.** Too many restrictions post-2018.
- **DYI tool: Fully feasible.** This is the recommended path. Produces a complete archive.
- The DYI export is the only way to get messages, full friends list, and most historical data.

### Recommended Approach
Do NOT rely on the Graph API for personal data import. Instead:
1. Instruct users to use Facebook's "Download Your Information" tool to export as JSON (not HTML).
2. Build a parser that reads the DYI ZIP archive structure (well-documented JSON format).
3. Map the exported data to Hypernet address space.
4. For ongoing sync of new posts/photos (if needed), use Graph API with `user_posts` and `user_photos` permissions, but accept that this requires App Review and provides limited data.

---

## 3. LinkedIn API

### Authentication
- **OAuth 2.0** with LinkedIn Developer Portal registration.
- Requires joining a specific LinkedIn Partner Program to access most API features.
- Individual developers face significant barriers — LinkedIn is the most restrictive major social network for API access.

### API Access Restrictions
- **Partner Program required** for most endpoints. Must apply and be approved.
- Free/Basic tier: limited to profile data for up to 3 people.
- Standard ($59/month) and Premium ($499/month) tiers exist.
- Marketing API, Talent Solutions API, and Community Management API are separate programs with separate approval processes.
- The API is designed for business-to-business integrations (recruiting tools, marketing platforms), NOT for personal data export.
- LinkedIn actively blocks scraping and unauthorized API usage with aggressive rate limiting and legal action.

### What Data Is Available
**Via API (with appropriate partner approval):**
- Own profile data (name, headline, summary, positions, education).
- Own posts and articles.
- Company pages (if admin).
- Marketing analytics (if using Marketing API).

**NOT available via API for personal export:**
- Private messages.
- Full connection list with details.
- Who viewed your profile.
- Activity history.
- Skills endorsements (limited).

### GDPR Data Download
LinkedIn's "Download Your Data" feature (Settings > Data Privacy > Get a copy of your data) provides:
- Profile information.
- Connections (first-degree) — names, titles, companies. Email addresses only if the connection opted in.
- Messages — full message history with timestamps.
- Posts and articles.
- Activity (likes, comments, shares).
- Invitations sent/received.
- Skills, endorsements, recommendations.
- Imported contacts.
- Registration information.
- Search history.
- Ad targeting data.

Format: ZIP file containing CSV and JSON files. Download link active for 72 hours.

### Rate Limits
- Varies by endpoint and partner tier.
- Typical: 100 requests per day for basic access.
- Marketing API: tiered access with increasing limits (Development, Basic, Managed).

### Key Python Libraries
- `python-linkedin` — community library (may be outdated).
- `requests` — for direct OAuth2 + REST calls.
- For parsing GDPR export: `csv`, `json`, `zipfile`.

### Privacy/Legal Considerations
- LinkedIn's User Agreement prohibits scraping and unauthorized data collection.
- They have filed lawsuits against scrapers (hiQ Labs v. LinkedIn went to Supreme Court).
- GDPR data download is the legally safe path for personal data.
- API usage requires compliance with LinkedIn's API Terms of Use.

### Bulk Export Feasibility
- **API: Not feasible** for personal data. Access is too restricted and expensive.
- **GDPR Download: Fully feasible.** Comprehensive personal data export available.
- Export must be manually triggered (no API for it).

### Recommended Approach
Use LinkedIn's GDPR "Download Your Data" feature exclusively. Build a parser for the CSV/JSON export format. Do not attempt API access for personal data import — the partner program requirements and costs make it impractical for a personal tool. Map exported connections, messages, and activity to Hypernet address space.

---

## 4. Dropbox API

### Authentication
- **OAuth 2.0** with PKCE (Proof Key for Code Exchange) for public clients.
- Register app at Dropbox App Console (https://www.dropbox.com/developers/apps).
- Two permission models:
  - **App folder** — app can only access its own designated folder.
  - **Full Dropbox** — app can access all files and folders (needed for import tool).
- Use `token_access_type='offline'` to get a refresh token for long-lived access.
- Short-lived access tokens expire after 4 hours; refresh tokens are long-lived.

### File Listing
- `files_list_folder(path)` — returns entries (FileMetadata, FolderMetadata, DeletedMetadata) with cursor-based pagination.
- `files_list_folder_continue(cursor)` — continues listing from a cursor.
- `files_list_folder/longpoll` — long-polling endpoint for real-time change notifications.
- Recursive listing available via `recursive=True` parameter.

### Download
- `files_download(path)` — returns file metadata + file content.
- `files_download_zip(path)` — downloads a folder as ZIP (max 20GB or 10,000 files).
- Content served from `content.dropboxapi.com` domain.
- Large files: chunked download supported.

### Metadata
- FileMetadata includes: name, path, id, size, rev (revision), content_hash, client_modified, server_modified, is_downloadable, sharing_info, media_info (for photos/videos).
- `content_hash` is a Dropbox-specific hash useful for deduplication.
- `media_info` includes time_taken and GPS location for photos.
- `files_get_metadata(path)` — get metadata for a specific file.

### Sync Approaches
- **Cursor-based sync**: Save the cursor from `list_folder`, then use `list_folder/continue` to get only changes since last sync.
- **Content hash comparison**: Dropbox provides `content_hash` on every file — compare to detect changes without downloading.
- **Webhook notifications**: Dropbox can POST to your server when files change.

### Rate Limits
- Not formally documented with specific numbers.
- Generally generous for personal use — per-app-per-user basis.
- 429 responses include `Retry-After` header.
- Data transport limit for Business plans: 1 billion upload operations/month (not applicable to free/personal).

### Key Python Libraries
- `dropbox` — official Dropbox Python SDK (pip install dropbox).
- Handles OAuth2 flow, all file operations, and automatic retry on rate limits.

### Privacy/Legal Considerations
- User is exporting their own files — no third-party privacy issues.
- Dropbox API Terms of Use are relatively permissive for personal use.
- Must store OAuth tokens securely.
- App Review not required for personal use.

### Bulk Export Feasibility
- **Fully feasible.** The API is well-designed for bulk file access.
- Cursor-based sync makes incremental updates efficient.
- Content hashing enables fast change detection.
- No documented hard limits on personal accounts for read operations.

### Recommended Approach
Use the official `dropbox` Python SDK with Full Dropbox access permission. Implement cursor-based sync for incremental imports. Use `content_hash` for deduplication. Store file metadata in Hypernet's object system and actual files in the local archive. For initial bulk import, recursively list all files, then download in parallel (respect rate limits). Use long-polling or webhooks for ongoing sync.

---

## 5. OneDrive / Microsoft Graph API

### Authentication
- **OAuth 2.0** via Microsoft Identity Platform (Azure AD).
- Register app in Azure Portal (App Registrations).
- Supports both "personal Microsoft accounts" and "work/school accounts."
- Use MSAL (Microsoft Authentication Library) for token management.
- Key scopes:
  - `Files.Read` — read user's files (delegated, personal + work).
  - `Files.Read.All` — read all files user can access (including shared).
  - `Files.ReadWrite` — read/write user's files.
  - `User.Read` — basic profile info.
  - `offline_access` — get refresh token for long-lived access.

### File Listing
- `GET /me/drive/root/children` — list files in root.
- `GET /me/drive/items/{item-id}/children` — list children of a folder.
- `GET /me/drive/root:/{path}:/children` — list by path.
- Delta query (`GET /me/drive/root/delta`) — get changes since last sync, returns all changes with a delta token for incremental sync.
- Supports `$filter`, `$select`, `$orderby`, `$top` OData query parameters.

### Download
- `GET /me/drive/items/{item-id}/content` — download file content (returns 302 redirect to download URL).
- Large files: range-based downloads supported.
- The metadata response includes `@microsoft.graph.downloadUrl` — a pre-authenticated URL valid for a short time.

### Metadata
- DriveItem properties: name, id, size, createdDateTime, lastModifiedDateTime, file (mimeType, hashes), folder (childCount), image (height, width), photo (cameraMake, cameraModel, takenDateTime), location (latitude, longitude), audio, video.
- Rich metadata for photos including EXIF data, GPS coordinates, and camera info.
- File hashes (SHA1, SHA256, quickXorHash) available for deduplication.

### Rate Limits
- **130,000 requests per 10 seconds per app** across all tenants (global limit).
- SharePoint/OneDrive charges in "resource units" (RUs): read = 1 RU, create/update/delete = 2 RUs.
- Per-tenant limits; starting September 2025, per-app/per-user limit reduced to half of tenant limit.
- Throttled requests return 429 with `Retry-After` header.

### Key Python Libraries
- `msal` — Microsoft Authentication Library for Python.
- `msgraph-sdk` — official Microsoft Graph SDK for Python.
- `requests` — for direct REST calls.
- `azure-identity` — Azure credential management.

### Privacy/Legal Considerations
- User exporting their own OneDrive data — no third-party issues.
- Azure AD app registration is free for personal use.
- Must comply with Microsoft's API Terms of Use.
- Token storage must be secure.

### Bulk Export Feasibility
- **Fully feasible.** Delta queries make incremental sync very efficient.
- File hashes available for deduplication.
- Well-documented API with excellent Python SDK support.
- Photo/video metadata (EXIF, GPS) available directly through the API.

### Recommended Approach
Use Microsoft Graph API with MSAL for authentication. Implement delta-based sync for efficient incremental imports. Leverage the rich metadata (especially for photos with GPS/EXIF data). Use file hashes for deduplication. The `msgraph-sdk` Python package provides a modern async-capable client. For initial import, use delta query with no initial token to get all items, then store the delta token for subsequent syncs.

---

## 6. Google Photos API

### CRITICAL: API Deprecation (March 31, 2025)

As of March 31, 2025, the Google Photos Library API has been **severely restricted**:
- The `photoslibrary.readonly`, `photoslibrary.sharing`, and `photoslibrary` scopes have been **removed**.
- API calls using these scopes return **403 PERMISSION_DENIED**.
- Apps can now **only access media items and albums they created** — not the user's existing library.
- The replacement is the **Google Photos Picker API**, which requires the user to manually select individual photos/albums to share with the app. Full library enumeration is no longer possible.

### What Still Works
- **Picker API**: user manually selects photos/albums in a Google-provided UI. App receives access to only those selected items.
- **Library API (restricted)**: can list/search/retrieve only media items created by YOUR app.
- **Upload**: apps can still upload new photos and create albums.

### What No Longer Works
- Listing all photos in a user's library.
- Searching across the full library.
- Automated full-library backup/sync.
- Any bulk export via API.

### Metadata Limitations (Even Pre-Deprecation)
- **Location data (GPS) is stripped** from API responses — this was always the case, not new.
- Available metadata: creation time, width, height, camera make/model, aperture, ISO, exposure time, focal length, filename, mimeType.
- Video metadata: frame rate, processing status.
- Base URLs for downloading expire after 60 minutes.

### Rate Limits (Current)
- 10,000 requests/day for general API functions.
- 75,000 requests/day for accessing media bytes (downloads).

### Key Python Libraries
- `google-api-python-client` — official client.
- `google-auth-oauthlib` — OAuth2 flow.
- For Google Takeout parsing: `json`, `PIL`/`Pillow` (for EXIF extraction), `exifread`.

### Privacy/Legal Considerations
- Google's deprecation was explicitly framed as a privacy improvement.
- The Picker API model puts the user in control of exactly what data is shared.
- For personal export: Google Takeout is now the only comprehensive option.

### Bulk Export Feasibility
- **API: No longer feasible.** The March 2025 changes killed this use case.
- **Google Takeout: Fully feasible.** Exports all photos/videos with metadata JSON sidecar files.
- **Google Takeout for Photos** includes: original resolution photos/videos, JSON metadata files (with GPS coordinates, creation time, description, people tags, album info).

### Recommended Approach
**Do not use the Google Photos API for personal data import.** Instead:
1. Use **Google Takeout** to export all photos (Settings > Google Takeout > select Google Photos).
2. Takeout produces ZIP files containing original photos/videos plus JSON sidecar files with full metadata (including GPS location, which the API always stripped).
3. Build a parser that reads the Takeout archive structure:
   - Each album is a folder.
   - Each photo has a corresponding `.json` file with metadata.
   - Metadata JSON includes: `title`, `description`, `imageViews`, `creationTime`, `photoTakenTime`, `geoData` (latitude, longitude, altitude), `geoDataExif`, `people`, `url`.
4. Use `Pillow` or `exifread` to extract additional EXIF data from the image files themselves.
5. Map to Hypernet address space with full location and temporal metadata.

---

## 7. Receipt Parsing

### The Problem
Users have years of purchase receipts scattered across email (order confirmations from Amazon, Best Buy, Apple, etc.), photos of paper receipts, and PDF attachments. The goal is to extract structured purchase data (merchant, date, items, amounts, payment method).

### Approach 1: Email Receipt Identification
**Identifying receipt emails from a Gmail archive:**
- **Sender-based filtering**: Match known retailer domains (e.g., `@amazon.com`, `@bestbuy.com`, `@apple.com`, `@paypal.com`, `@venmo.com`, `@square.com`).
- **Subject line patterns**: Regex for patterns like "Order Confirmation", "Your receipt", "Payment received", "Invoice", "Order #", "Transaction".
- **Label-based**: Gmail's "Purchases" category (CATEGORY_PURCHASES in newer accounts) or "Receipts" label.
- **HTML structure**: Receipt emails often contain structured data (tables with item names, quantities, prices).

### Approach 2: HTML Email Parsing
For known retailers, build retailer-specific parsers:
- **Amazon**: order confirmation emails have consistent HTML structure with order ID, items, prices, shipping address, payment method. Use BeautifulSoup to extract structured tables.
- **Best Buy**: similar structured HTML with order numbers and item details.
- **Apple**: App Store/iTunes receipts have a very consistent format.
- General approach: parse HTML with BeautifulSoup, look for table structures, extract text, use regex to identify dollar amounts, dates, and order numbers.

### Approach 3: OCR for Image/PDF Receipts
**Tools for OCR:**
- **Tesseract OCR** (free, open source): `pytesseract` Python wrapper. Good for clean printed text, struggles with crumpled/faded receipts.
- **PaddleOCR** (free, open source): often better accuracy than Tesseract, especially for complex layouts.
- **Amazon Textract** (paid): AWS service with dedicated `AnalyzeExpense` action that understands receipt layouts natively — extracts merchant, date, items, totals, tax, payment method as structured data. Pricing: ~$0.01 per page for expense analysis.
- **Google Cloud Vision** (paid): general OCR with good accuracy. ~$1.50 per 1000 pages.
- **Azure AI Document Intelligence** (paid): has pre-built receipt model. ~$0.01 per page.

### Approach 4: LLM-Based Extraction
- Feed raw OCR text or email HTML to an LLM (GPT-4, Claude) with a prompt requesting structured JSON output.
- Works well as a post-processing step after initial OCR.
- Can handle varied formats without retailer-specific parsers.
- Cost: depends on token usage, but typically < $0.01 per receipt.
- Libraries: `receipt-ocr` (PyPI) uses LLM for structured extraction from receipt images.

### Key Python Libraries
- `pytesseract` — Tesseract OCR wrapper.
- `paddleocr` — PaddleOCR wrapper.
- `beautifulsoup4` — HTML parsing for email receipts.
- `Pillow` — image preprocessing before OCR.
- `boto3` — for Amazon Textract.
- `receipt-ocr` — FastAPI service for LLM-powered receipt extraction.
- `email` (stdlib) — parsing email messages.

### Structured Data Output
A receipt should produce:
```
{
  "merchant": "Amazon",
  "date": "2025-11-15",
  "order_id": "113-1234567-8901234",
  "items": [
    {"name": "USB-C Cable", "quantity": 2, "price": 9.99},
    {"name": "Phone Case", "quantity": 1, "price": 14.99}
  ],
  "subtotal": 34.97,
  "tax": 2.87,
  "total": 37.84,
  "payment_method": "Visa ending in 1234",
  "source": "email",
  "source_message_id": "abc123"
}
```

### Recommended Approach
Multi-layered strategy:
1. **Email identification**: sender domain matching + subject line regex to flag receipt emails.
2. **Retailer-specific parsers**: for top 10-20 retailers (Amazon, Best Buy, Apple, Walmart, Target, etc.), build HTML parsers using BeautifulSoup. These are the highest-value and most consistent.
3. **Generic email parser**: for unknown retailers, use LLM extraction on the email body.
4. **Image/PDF OCR**: for photo receipts and PDF attachments, use PaddleOCR or Tesseract for text extraction, then LLM for structuring.
5. **Deduplication**: match receipts across sources (same order number, same amount + date).

---

## 8. Spam Detection

### The Problem
When importing a personal email archive (potentially tens of thousands of emails), a significant portion is spam. Users don't want spam polluting their Hypernet account. Need to identify and filter spam during or after import.

### Approach 1: Leverage Gmail's Existing Classification
- Gmail already classifies spam (SPAM label) and categories (PROMOTIONS, SOCIAL, UPDATES, FORUMS, PRIMARY).
- When importing via Gmail API, check each message's `labelIds` — messages with the `SPAM` label are already identified.
- Messages in CATEGORY_PROMOTIONS are often marketing/newsletters (not exactly spam, but low-value).
- **This is the easiest and most effective first pass** — Gmail's spam detection is world-class.

### Approach 2: Header-Based Heuristics
- Check for `X-Spam-Status`, `X-Spam-Score`, `X-Spam-Flag` headers (set by mail servers).
- Check `Authentication-Results` header for SPF, DKIM, DMARC failures.
- Sender domain reputation: flag emails from known spam domains.
- Missing or suspicious `Reply-To` / `Return-Path` mismatches.

### Approach 3: Machine Learning Classification
**Traditional ML approach:**
- Feature extraction: TF-IDF on email body + subject, plus engineered features (has URL, has attachment, sender domain age, etc.).
- Algorithms: Naive Bayes (fast, effective baseline — 95%+ accuracy), SVM (slightly better accuracy), Random Forest.
- Training data: use Gmail's own spam labels as ground truth, or public datasets like SpamAssassin corpus, Enron email dataset.
- Library: `scikit-learn` provides all necessary tools.

**Deep Learning approach:**
- BERT fine-tuned on email classification — achieves 98%+ accuracy.
- LSTM/CNN on email text — 97%+ accuracy.
- Significantly more compute-intensive; overkill for personal email archive.

**Hybrid approach:**
- TF-IDF features + LSTM + XGBoost ensemble — 97%+ accuracy.

### Approach 4: Rule-Based Filtering
- SpamAssassin rules adapted for Python (many are regex-based).
- Keyword blacklists (common spam phrases).
- URL analysis (shortened URLs, known phishing domains).
- Simple but effective as a supplementary layer.

### Key Python Libraries
- `scikit-learn` — Naive Bayes, SVM, TF-IDF vectorization, model evaluation.
- `transformers` (Hugging Face) — for BERT-based classification.
- `spacy` — NLP preprocessing.
- `email` (stdlib) — header parsing.

### Recommended Approach
For a personal data import tool:
1. **Primary**: Use Gmail's existing labels. Messages labeled SPAM are spam. This alone eliminates 99%+ of spam with zero effort.
2. **Secondary**: For MBOX imports or other sources without pre-classification, train a simple Naive Bayes classifier using scikit-learn with TF-IDF features. Use Gmail's labeled data as training set (SPAM vs. INBOX).
3. **Supplementary**: Header-based heuristics for edge cases (SPF/DKIM failures, suspicious sender patterns).
4. **User override**: allow users to manually reclassify in the Hypernet UI.

Do NOT over-engineer this. Gmail's built-in classification is already extremely good. Focus engineering effort on the import pipeline, not on reinventing spam detection.

---

## 9. Deduplication

### The Problem
When importing data from multiple sources, duplicates are inevitable:
- Same photo in Google Photos and Dropbox.
- Same file in OneDrive and local drive.
- Same email forwarded multiple times.
- Same receipt from email and a photo of the paper copy.
- Near-duplicates: resized photos, re-encoded videos, slightly edited documents.

### Strategy 1: Hash-Based (Exact Duplicates)
- **SHA-256 hash** of file contents — identical files produce identical hashes. O(1) lookup.
- **MD5 hash** — faster but theoretically collision-prone (acceptable for dedup, not for security).
- **xxHash** — extremely fast non-cryptographic hash, ideal for dedup.
- **Dropbox content_hash** — Dropbox provides its own content hash; reuse it.
- **Microsoft Graph quickXorHash / SHA1** — OneDrive provides file hashes in metadata.
- Implementation: hash every file during import, store in a set/database, skip files whose hash is already present.
- Limitation: any modification (even adding a single byte) produces a completely different hash.

### Strategy 2: Content-Based (Near-Duplicates for Text/Documents)
- **SimHash / MinHash** — locality-sensitive hashing for text documents. Similar documents produce similar hashes.
- **Cosine similarity on TF-IDF vectors** — compute TF-IDF for documents, compare cosine similarity. Threshold > 0.85 indicates near-duplicate.
- **Jaccard similarity** — compare sets of words/n-grams between documents.
- **difflib.SequenceMatcher** (stdlib) — for comparing text content with a similarity ratio.
- Use case: detecting duplicate emails with slightly different headers, or documents with minor edits.

### Strategy 3: Perceptual Hashing (Images/Media)
- **pHash (Perceptual Hash)** — produces similar hashes for visually similar images, even if resolution, compression, or format differs.
- **dHash (Difference Hash)** — faster than pHash, based on gradient direction.
- **aHash (Average Hash)** — simplest, compares each pixel to the average.
- **CNN-based similarity** — deep learning models that produce embedding vectors; cosine similarity on embeddings detects near-duplicates.
- `imagededup` library supports all of the above: PHash, DHash, AHash, and CNN-based dedup.
- Use case: same photo at different resolutions, re-compressed JPEGs, cropped versions, photos with filters.

### Strategy 4: Metadata-Based
- **Same filename + same size + same modified date** — strong indicator of duplicate.
- **Same creation timestamp + same camera model** (for photos) — likely same photo.
- **Same email Message-ID header** — definitive email duplicate detection.
- **Same order number** (for receipts) — definitive purchase duplicate detection.
- Fast pre-filter before more expensive content comparison.

### Strategy 5: Multi-Stage Pipeline
1. **Stage 1 — Metadata pre-filter**: group files by size (files of different sizes cannot be identical). This eliminates most comparisons.
2. **Stage 2 — Quick hash**: compute hash of first 4KB of each file in same-size groups. Eliminates files that differ in header.
3. **Stage 3 — Full hash**: compute SHA-256 of entire file for remaining candidates. Identifies exact duplicates.
4. **Stage 4 — Perceptual hash**: for images/media that passed Stage 3 (not exact matches), compute pHash to find near-duplicates.
5. **Stage 5 — Content similarity**: for text documents, compute TF-IDF cosine similarity on remaining candidates.

### Key Python Libraries
- `hashlib` (stdlib) — SHA-256, MD5.
- `xxhash` — fast non-cryptographic hashing.
- `imagededup` — perceptual hashing and CNN dedup for images.
- `Pillow` — image processing for perceptual hashing.
- `dedupe` — fuzzy matching and entity resolution for structured records.
- `datasketch` — MinHash, LSH for near-duplicate detection at scale.
- `rapidfuzz` — fast fuzzy string matching (C++ backend).
- `scikit-learn` — TF-IDF vectorization and cosine similarity.

### Privacy/Legal Considerations
- Deduplication is purely local processing — no privacy concerns.
- When deduplicating across sources, maintain provenance (record which sources contained each item).
- Never delete originals during dedup — mark as duplicate and keep the "best" version (highest resolution, most metadata, etc.).

### Recommended Approach
Implement a multi-stage pipeline:
1. **Import phase**: compute SHA-256 hash for every file as it's imported. Store in a hash-to-path index. Skip exact duplicates immediately.
2. **Metadata grouping**: use file size, creation date, and type as pre-filters.
3. **Image dedup**: after import, run `imagededup` with pHash on all image files to find near-duplicate photos.
4. **Email dedup**: use Message-ID header as primary key. For emails without Message-ID, fall back to subject + sender + timestamp matching.
5. **Receipt dedup**: match on order number first, then amount + merchant + date.
6. **Document dedup**: for text files, compute SimHash and flag pairs with high similarity for user review.
7. **User review**: present detected near-duplicates in the Hypernet UI for manual resolution. Never auto-delete.

---

## Summary Table

| Source | Auth Method | Bulk Export? | Best Approach | Key Library |
|--------|------------|-------------|---------------|-------------|
| Gmail | OAuth 2.0 | Yes (API + Takeout) | API for incremental, Takeout for bulk | `google-api-python-client` |
| Facebook | OAuth 2.0 | API: No, DYI: Yes | Download Your Information (JSON) | `json`, `beautifulsoup4` |
| LinkedIn | OAuth 2.0 | API: No, GDPR: Yes | Download Your Data (CSV/JSON) | `csv`, `json` |
| Dropbox | OAuth 2.0 + PKCE | Yes (API) | Official SDK with cursor sync | `dropbox` |
| OneDrive | OAuth 2.0 (MSAL) | Yes (API) | Graph API with delta queries | `msgraph-sdk`, `msal` |
| Google Photos | OAuth 2.0 | API: No (deprecated), Takeout: Yes | Google Takeout only | `Pillow`, `exifread` |
| Receipts | N/A | N/A | Sender matching + HTML parsing + OCR | `beautifulsoup4`, `pytesseract` |
| Spam | N/A | N/A | Gmail labels + Naive Bayes fallback | `scikit-learn` |
| Deduplication | N/A | N/A | Multi-stage: hash → perceptual → content | `hashlib`, `imagededup`, `dedupe` |

---

## Key Takeaways

1. **Social networks are locked down.** Facebook and LinkedIn have made API-based personal data export nearly impossible. Their GDPR-mandated "download your data" tools are the only viable path.

2. **Cloud storage APIs are excellent.** Dropbox and OneDrive both offer well-designed APIs with incremental sync (cursors/delta queries) and file hashing for deduplication. These are the easiest connectors to build.

3. **Gmail API is the goldmine.** Email is the richest personal data source — it contains receipts, confirmations, correspondence, and attachments from every service. The API is generous with rate limits and well-documented.

4. **Google Photos API is dead for import.** The March 2025 deprecation killed full-library access. Google Takeout is the only option, and it actually provides BETTER metadata (including GPS, which the API always stripped).

5. **Receipt parsing is best done as a layer on top of email import.** Don't build a separate receipt connector — parse receipts from the Gmail import pipeline using sender matching and HTML extraction.

6. **Spam detection should not be over-engineered.** Gmail's built-in labels handle 99% of the work. A simple ML classifier handles the rest.

7. **Deduplication requires a multi-stage approach.** Hash-based for exact matches (cheap), perceptual hashing for images (medium cost), content similarity for documents (expensive). Always let the user make final decisions on near-duplicates.

8. **Google Takeout is the Swiss Army knife.** It covers Gmail, Google Photos, Google Drive, Calendar, Contacts, and more — all in one export. Consider building a Takeout parser as the primary Google data import path.

---

## Sources

### Gmail API
- [OAuth 2.0 for Google APIs](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Gmail API Usage Limits](https://developers.google.com/workspace/gmail/api/reference/quota)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [OAuth Application Rate Limits](https://support.google.com/cloud/answer/9028764?hl=en)

### Facebook Graph API
- [Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Facebook Download Your Information](https://www.facebook.com/help/212802592074644)
- [Facebook Data Access Restrictions (2018)](https://about.fb.com/news/2018/04/restricting-data-access/)
- [Facebook Unofficial APIs Overview 2026](https://data365.co/blog/facebook-unofficial-api)
- [Facebook API Guide 2026](https://getlate.dev/blog/facebook-api)

### LinkedIn API
- [LinkedIn API Guide 2026](https://www.outx.ai/blog/linkedin-api-guide)
- [LinkedIn GDPR Developer Resources](https://www.linkedin.com/help/linkedin/answer/a1337538)
- [Download Your LinkedIn Data](https://www.linkedin.com/help/linkedin/answer/a1339364/downloading-your-account-data)
- [Getting Access to LinkedIn APIs](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access)
- [What LinkedIn Data Can Be Pulled](https://www.unipile.com/what-linkedin-data-can-be-pulled-from-their-api/)

### Dropbox API
- [Dropbox OAuth Guide](https://developers.dropbox.com/oauth-guide)
- [Dropbox Python SDK Documentation](https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html)
- [Dropbox Files API Reference](https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html)
- [Dropbox Performance Guide](https://developers.dropbox.com/dbx-performance-guide)
- [Dropbox Getting Started](https://www.dropbox.com/developers/reference/getting-started)

### OneDrive / Microsoft Graph
- [OneDrive API Getting Started](https://learn.microsoft.com/en-us/onedrive/developer/rest-api/getting-started/?view=odsp-graph-online)
- [OneDrive File Storage Overview](https://learn.microsoft.com/en-us/graph/onedrive-concept-overview)
- [Microsoft Graph Throttling Limits](https://learn.microsoft.com/en-us/graph/throttling-limits)
- [OneDrive Permission Scopes](https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/permissions_reference?view=odsp-graph-online)
- [OneDrive API Python Integration](https://www.merge.dev/blog/onedrive-api-python)

### Google Photos
- [Google Photos API Limits and Quotas](https://developers.google.com/photos/overview/api-limits-quotas)
- [Google Photos API Updates](https://developers.google.com/photos/support/updates)
- [Photos Picker API Launch](https://developers.googleblog.com/en/google-photos-picker-api-launch-and-library-api-updates/)
- [Google Photos API Deprecation Discussion](https://github.com/gilesknap/gphotos-sync/issues/511)
- [EXIF Metadata Missing Issue](https://issuetracker.google.com/issues/111228390)

### Receipt Parsing
- [Amazon Textract](https://aws.amazon.com/textract/)
- [receipt-ocr on PyPI](https://pypi.org/project/receipt-ocr/)
- [Receipt OCR Using Python Guide](https://tabscanner.com/receipt-ocr-using-python/)
- [Email Parsing with Python (Nylas)](https://www.nylas.com/blog/email-parsing-with-python-a-comprehensive-guide/)
- [AIReceiptParser on GitHub](https://github.com/JustCabaret/AIReceiptParser)

### Spam Detection
- [ML and DL for Email Spam Detection (IEEE)](https://ieeexplore.ieee.org/document/10150836/)
- [Email Spam Detection with Scikit-Learn](https://medium.com/@oluyaled/email-spam-detection-using-machine-learning-scikit-python-1b15ee1c6f75)
- [Spam Detection with TensorFlow](https://www.geeksforgeeks.org/nlp/detecting-spam-emails-using-tensorflow-in-python/)
- [Real-Time ML Spam Detection System (Wiley 2025)](https://onlinelibrary.wiley.com/doi/abs/10.1002/itl2.618)
- [ML Email Spam Detector (LogRocket)](https://blog.logrocket.com/email-spam-detector-python-machine-learning/)

### Deduplication
- [imagededup Library](https://github.com/idealo/imagededup)
- [dedupe Library](https://github.com/dedupeio/dedupe)
- [Duplicate Image Detection with Perceptual Hashing](https://benhoyt.com/writings/duplicate-image-detection/)
- [semhash - Semantic Deduplication](https://github.com/MinishLab/semhash)
- [Data Deduplication Techniques Guide](https://scrapingproxies.best/blog/web-data/data-deduplication-techniques/)

### General / Cross-Cutting
- [Google Takeout](https://en.wikipedia.org/wiki/Google_Takeout)
- [Google Takeout Alternatives 2025](https://www.arysontechnologies.com/blog/best-google-takeout-alternatives/)
