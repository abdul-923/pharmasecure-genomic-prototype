
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = PROJECT_ROOT / "logs"
AUDIT_FILE = AUDIT_DIR / "audit.log"

# First record starts with this fixed value.
GENESIS_HASH = "0" * 64


def calculate_hash(record):
    """Calculate SHA-256 hash of an audit record."""
    record_data = {
        key: value
        for key, value in record.items()
        if key != "record_hash"
    }

    canonical_json = json.dumps(
        record_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def log_event(event, username="system", status="SUCCESS", details=None):
    """Append an audit record linked to the previous record."""

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    previous_hash = GENESIS_HASH

    # Link this record to the last record in the file.
    if AUDIT_FILE.exists():
        with AUDIT_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    previous_record = json.loads(line)
                    previous_hash = previous_record.get(
                        "record_hash",
                        GENESIS_HASH
                    )
                except json.JSONDecodeError:
                    continue

    audit_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "event": event,
        "status": status,
        "details": details or {},
        "previous_hash": previous_hash
    }

    audit_record["record_hash"] = calculate_hash(audit_record)

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(audit_record) + "\n")

    return audit_record


def verify_audit_log():
    """Verify audit records and their hash chain."""

    if not AUDIT_FILE.exists():
        return {
            "valid": True,
            "message": "No audit log exists yet.",
            "records_checked": 0
        }

    expected_previous_hash = GENESIS_HASH
    records_checked = 0

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                return {
                    "valid": False,
                    "message": f"Invalid JSON at line {line_number}.",
                    "records_checked": records_checked
                }

            if "record_hash" not in record or "previous_hash" not in record:
                return {
                    "valid": False,
                    "message": (
                        f"Record at line {line_number} "
                        "does not contain hash-chain fields."
                    ),
                    "records_checked": records_checked
                }

            if record["previous_hash"] != expected_previous_hash:
                return {
                    "valid": False,
                    "message": f"Hash-chain mismatch at line {line_number}.",
                    "records_checked": records_checked
                }

            calculated_hash = calculate_hash(record)

            if calculated_hash != record["record_hash"]:
                return {
                    "valid": False,
                    "message": f"Record tampering detected at line {line_number}.",
                    "records_checked": records_checked
                }

            expected_previous_hash = record["record_hash"]
            records_checked += 1

    return {
        "valid": True,
        "message": "Audit log integrity verified.",
        "records_checked": records_checked
    }

