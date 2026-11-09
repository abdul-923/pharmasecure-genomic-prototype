
import hashlib
import boto3
import tempfile

from pathlib import Path
from datetime import datetime, timedelta, timezone


def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


AWS_REGION = "us-east-1"

BUCKET_NAME = "pharmasecure-genomic-poc-599117007421"

KMS_KEY_ARN = (
    "arn:aws:kms:us-east-1:599117007421:"
    "key/f2581c5f-5937-4887-918b-640bb7c9986e"
)


def upload_genomic_file(file_path):
    """Upload genomic data and verify encryption, retention and integrity."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Calculate original file hash before uploading
    original_hash = calculate_sha256(file_path)

    s3 = boto3.client("s3", region_name=AWS_REGION)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    object_key = f"genomic-data/{timestamp}_{file_path.name}"

    retention_date = datetime.now(timezone.utc) + timedelta(days=1)

    # Upload using SSE-KMS and Object Lock
    s3.upload_file(
        str(file_path),
        BUCKET_NAME,
        object_key,
        ExtraArgs={
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": KMS_KEY_ARN,
            "ObjectLockMode": "GOVERNANCE",
            "ObjectLockRetainUntilDate": retention_date,
        }
    )

    # Verify actual AWS object metadata
    response = s3.head_object(
        Bucket=BUCKET_NAME,
        Key=object_key
    )

    encryption = response.get("ServerSideEncryption")
    kms_key = response.get("SSEKMSKeyId")
    retention = response.get("ObjectLockRetainUntilDate")
    lock_mode = response.get("ObjectLockMode")

    if encryption != "aws:kms":
        raise RuntimeError("SSE-KMS verification failed")

    if kms_key != KMS_KEY_ARN:
        raise RuntimeError("Unexpected KMS key")

    if not retention:
        raise RuntimeError("Object Lock retention not found")

    if lock_mode != "GOVERNANCE":
        raise RuntimeError("Object Lock mode verification failed")

    # Download the uploaded object temporarily and verify its hash
    with tempfile.TemporaryDirectory() as temp_dir:

        downloaded_file = Path(temp_dir) / file_path.name

        s3.download_file(
            BUCKET_NAME,
            object_key,
            str(downloaded_file)
        )

        uploaded_hash = calculate_sha256(downloaded_file)

    # Compare original and downloaded file hashes
    if original_hash != uploaded_hash:
        raise RuntimeError("SHA-256 integrity verification failed")

    return {
        "status": "Verified",
        "file": file_path.name,
        "bucket": BUCKET_NAME,
        "object_key": object_key,
        "encryption": encryption,
        "kms_key": kms_key,
        "object_lock": lock_mode,
        "retention_until": retention.isoformat(),
        "integrity_status": "Verified",
        "original_sha256": original_hash,
        "uploaded_sha256": uploaded_hash,
        "hashes_match": original_hash == uploaded_hash,
    }


if __name__ == "__main__":
    result = upload_genomic_file("data/synthetic_sample.fastq")
    print(result)

