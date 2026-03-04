"""
Email Connector for Hypernet Personal Data Integration

Supports:
- Gmail via OAuth2 (matt.spamme@gmail.com, kosmicsuture@gmail.com)
- Generic IMAP with app passwords (matt@schaeffer.org, spammelots@schaeffer.org)

Flow:
1. Authenticate (OAuth2 or app password)
2. Scan mailboxes, build index of all messages
3. Triage: separate important emails from junk
4. Import important messages into Hypernet structure (1.1.3 Communications)
5. Archive originals locally (never delete from source)

Governed by: 2.0.19 (Data Protection), 2.0.20 (Companion Standard)
"""

import imaplib
import email
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from email.header import decode_header
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class EmailMessage:
    """Represents a single email for Hypernet ingestion."""
    message_id: str
    subject: str
    sender: str
    recipients: list[str]
    date: str
    body_text: str
    body_html: str = ""
    attachments: list[dict] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    folder: str = ""
    source_account: str = ""
    importance_score: float = 0.0
    sha256: str = ""
    hypernet_address: str = ""


@dataclass
class AccountConfig:
    """Configuration for an email account."""
    email: str
    display_name: str
    server: str
    port: int = 993
    auth_type: str = "app_password"  # "app_password" or "oauth2"
    credentials_path: str = ""  # path to stored credentials
    folders_to_scan: list[str] = field(default_factory=lambda: ["INBOX", "[Gmail]/Sent Mail", "[Gmail]/Important"])


# Known accounts for Matt's Hypernet
MATT_ACCOUNTS = {
    "matt@schaeffer.org": AccountConfig(
        email="matt@schaeffer.org",
        display_name="Matt - Schaeffer.org",
        server="",  # TBD - need to discover IMAP server
        auth_type="app_password",
    ),
    "spammelots@schaeffer.org": AccountConfig(
        email="spammelots@schaeffer.org",
        display_name="Spammelots - Schaeffer.org",
        server="",  # TBD
        auth_type="app_password",
    ),
    "matt.spamme@gmail.com": AccountConfig(
        email="matt.spamme@gmail.com",
        display_name="Matt - Gmail",
        server="imap.gmail.com",
        auth_type="oauth2",
    ),
    "kosmicsuture@gmail.com": AccountConfig(
        email="kosmicsuture@gmail.com",
        display_name="KosmicSuture - Gmail",
        server="imap.gmail.com",
        auth_type="oauth2",
    ),
}


class EmailConnector:
    """Connects to email accounts and imports messages into Hypernet."""

    def __init__(self, archive_root: str, private_root: str):
        """
        Args:
            archive_root: Path to Hypernet Structure root
            private_root: Path to private/ directory (gitignored)
        """
        self.archive_root = Path(archive_root)
        self.private_root = Path(private_root)
        self.staging_dir = self.private_root / "import-staging" / "email"
        self.credentials_dir = self.private_root / "credentials"
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def connect_imap(self, config: AccountConfig) -> imaplib.IMAP4_SSL:
        """Establish IMAP connection using stored credentials."""
        if not config.server:
            raise ValueError(f"No IMAP server configured for {config.email}")

        cred_file = self.credentials_dir / f"{config.email}.json"
        if not cred_file.exists():
            raise FileNotFoundError(
                f"No credentials found for {config.email}. "
                f"Store credentials at: {cred_file}\n"
                f"Format: {{\"password\": \"your-app-password\"}}\n"
                f"File permissions should be 600 (owner read/write only)."
            )

        creds = json.loads(cred_file.read_text())

        if config.auth_type == "oauth2":
            return self._connect_oauth2(config, creds)
        else:
            mail = imaplib.IMAP4_SSL(config.server, config.port)
            mail.login(config.email, creds["password"])
            return mail

    def _connect_oauth2(self, config: AccountConfig, creds: dict) -> imaplib.IMAP4_SSL:
        """Connect using OAuth2 (required for Gmail)."""
        # Gmail requires OAuth2 for IMAP since 2022
        # This uses the XOAUTH2 SASL mechanism
        access_token = creds.get("access_token")
        if not access_token:
            raise ValueError(
                f"OAuth2 access token not found for {config.email}. "
                "Run the OAuth2 setup flow first:\n"
                "  python -m hypernet.integrations.oauth_setup gmail"
            )

        auth_string = f"user={config.email}\x01auth=Bearer {access_token}\x01\x01"
        mail = imaplib.IMAP4_SSL(config.server, config.port)
        mail.authenticate("XOAUTH2", lambda x: auth_string.encode())
        return mail

    def scan_mailbox(self, config: AccountConfig, max_messages: int = 0) -> list[dict]:
        """Scan a mailbox and return message summaries without downloading bodies."""
        mail = self.connect_imap(config)
        summaries = []

        for folder in config.folders_to_scan:
            try:
                status, _ = mail.select(folder, readonly=True)
                if status != "OK":
                    continue

                _, message_ids = mail.search(None, "ALL")
                ids = message_ids[0].split()

                if max_messages > 0:
                    ids = ids[-max_messages:]  # most recent first

                for msg_id in ids:
                    _, header_data = mail.fetch(msg_id, "(BODY.PEEK[HEADER] FLAGS)")
                    if header_data[0] is None:
                        continue

                    msg = email.message_from_bytes(header_data[0][1])
                    subject = self._decode_header(msg.get("Subject", ""))
                    sender = self._decode_header(msg.get("From", ""))
                    date = msg.get("Date", "")

                    summaries.append({
                        "id": msg_id.decode(),
                        "folder": folder,
                        "subject": subject,
                        "sender": sender,
                        "date": date,
                        "account": config.email,
                    })
            except Exception as e:
                print(f"  Error scanning {folder}: {e}")
            finally:
                try:
                    mail.close()
                except Exception:
                    pass

        mail.logout()
        return summaries

    def download_message(self, config: AccountConfig, folder: str, msg_id: str) -> EmailMessage:
        """Download a complete email message."""
        mail = self.connect_imap(config)
        mail.select(folder, readonly=True)

        _, data = mail.fetch(msg_id.encode(), "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)

        # Extract fields
        subject = self._decode_header(msg.get("Subject", ""))
        sender = self._decode_header(msg.get("From", ""))
        recipients = [self._decode_header(r) for r in (msg.get("To", "").split(","))]
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")

        # Extract body
        body_text = ""
        body_html = ""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in disposition:
                    filename = part.get_filename() or "unnamed"
                    attachments.append({
                        "filename": self._decode_header(filename),
                        "content_type": content_type,
                        "size": len(part.get_payload(decode=True) or b""),
                    })
                elif content_type == "text/plain":
                    body_text = part.get_payload(decode=True).decode("utf-8", errors="replace")
                elif content_type == "text/html":
                    body_html = part.get_payload(decode=True).decode("utf-8", errors="replace")
        else:
            body_text = msg.get_payload(decode=True).decode("utf-8", errors="replace")

        # Compute hash for deduplication
        content_hash = hashlib.sha256(raw).hexdigest()

        mail.close()
        mail.logout()

        return EmailMessage(
            message_id=message_id,
            subject=subject,
            sender=sender,
            recipients=recipients,
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            folder=folder,
            source_account=config.email,
            sha256=content_hash,
        )

    def triage_messages(self, summaries: list[dict]) -> dict:
        """
        Triage email summaries into categories.

        Returns dict with keys: important, receipts, newsletters, junk, unknown
        """
        result = {
            "important": [],
            "receipts": [],
            "newsletters": [],
            "junk": [],
            "unknown": [],
        }

        # Pattern-based triage (will be enhanced with AI triage later)
        receipt_keywords = ["receipt", "order confirmation", "invoice", "payment", "purchase", "transaction"]
        newsletter_keywords = ["unsubscribe", "newsletter", "weekly digest", "daily update"]
        junk_keywords = ["viagra", "casino", "lottery", "prince", "inheritance", "click here"]

        for msg in summaries:
            subject_lower = (msg.get("subject") or "").lower()
            sender_lower = (msg.get("sender") or "").lower()

            if any(kw in subject_lower for kw in junk_keywords):
                result["junk"].append(msg)
            elif any(kw in subject_lower for kw in receipt_keywords):
                result["receipts"].append(msg)
            elif any(kw in subject_lower or kw in sender_lower for kw in newsletter_keywords):
                result["newsletters"].append(msg)
            elif msg.get("folder") in ("[Gmail]/Important", "[Gmail]/Starred", "INBOX"):
                result["important"].append(msg)
            else:
                result["unknown"].append(msg)

        return result

    def export_to_staging(self, messages: list[EmailMessage], account: str):
        """Export downloaded messages to staging directory as JSON."""
        account_dir = self.staging_dir / account.replace("@", "_at_").replace(".", "_")
        account_dir.mkdir(parents=True, exist_ok=True)

        for msg in messages:
            filename = f"{msg.sha256[:12]}_{self._safe_filename(msg.subject)[:50]}.json"
            filepath = account_dir / filename
            filepath.write_text(json.dumps(asdict(msg), indent=2, default=str))

        manifest = {
            "account": account,
            "exported_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "files": [f.name for f in account_dir.glob("*.json")],
        }
        (account_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2))

    def import_to_hypernet(self, message: EmailMessage, owner_ha: str = "1.1") -> str:
        """
        Import a triaged email into the Hypernet structure.

        Places in 1.1.3 - Communications with proper Hypernet frontmatter.
        Returns the assigned Hypernet address.
        """
        comms_dir = self.archive_root / "1 - People" / "1.1 Matt Schaeffer" / "1.1.3 - Communications"
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Create category subdirectory
        if message.importance_score > 0.7:
            subdir = "1.1.3.0 - Email Archives"
        else:
            subdir = "1.1.3.0 - Email Archives"

        target_dir = comms_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_subject = self._safe_filename(message.subject)[:60]
        filename = f"{date_str}_{safe_subject}.md"
        ha = f"1.1.3.0.{message.sha256[:8]}"

        content = f"""---
ha: "{ha}"
object_type: "email"
creator: "{owner_ha}"
created: "{date_str}"
status: "active"
visibility: "private"
source_account: "{message.source_account}"
original_date: "{message.date}"
sha256: "{message.sha256}"
flags: ["imported", "email"]
---

# {message.subject}

**From:** {message.sender}
**To:** {', '.join(message.recipients)}
**Date:** {message.date}
**Source:** {message.source_account}

---

{message.body_text}
"""

        (target_dir / filename).write_text(content, encoding="utf-8")
        return ha

    @staticmethod
    def _decode_header(value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                result.append(part)
        return " ".join(result)

    @staticmethod
    def _safe_filename(s: str) -> str:
        """Convert string to safe filename."""
        return "".join(c if c.isalnum() or c in "- _" else "_" for c in s).strip()
