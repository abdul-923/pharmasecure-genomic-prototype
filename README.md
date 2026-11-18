
# PharmaSecure Genomic Prototype

## Overview

PharmaSecure is a Python-based prototype designed to demonstrate secure handling of genomic sequencing data for precision medicine research.

The system provides researcher authentication, FASTQ file validation, pseudonymisation, encrypted AWS S3 storage and tamper-evident audit logging. It uses AWS KMS for data encryption and SHA-256 hashing to verify file integrity.

The project demonstrates how sensitive genomic research data can be processed and stored with basic security and access controls.

## Key Features

- **Researcher Authentication** — Secure login using Argon2 password hashing.
- **Role-Based Access** — Controls genomic file upload permissions based on user roles.
- **FASTQ Validation** — Checks sequencing file structure and DNA sequence data.
- **Data Pseudonymisation** — Replaces original FASTQ read identifiers with generated pseudonymous identifiers.
- **AWS S3 Storage** — Stores processed genomic files in Amazon S3.
- **KMS Encryption** — Uses AWS Key Management Service for server-side encryption.
- **S3 Object Lock** — Applies Governance-mode retention to uploaded objects.
- **SHA-256 Integrity Verification** — Compares file hashes before and after upload.
- **Tamper-Evident Audit Logging** — Uses a SHA-256 hash chain to detect changes in audit records.
- **Audit Log Viewer** — Allows users to review security events and verify audit log integrity.

## Architecture and Workflow

The prototype follows a simple genomic data protection workflow.

1. Researcher signs in through the Streamlit application.
2. The system checks the user's credentials and role.
3. The researcher uploads a FASTQ sequencing file.
4. The system validates the FASTQ file structure and DNA sequence.
5. Original read identifiers are replaced with generated pseudonyms.
6. The processed file is uploaded to Amazon S3.
7. AWS SSE-KMS encryption and S3 Object Lock settings are applied.
8. The uploaded file is downloaded temporarily and checked using SHA-256 hashing.
9. Security activities are recorded in a tamper-evident audit log.

## Technologies Used

### Programming and Application

- Python
- Streamlit
- Pandas
- Argon2

### AWS Cloud Services

- Amazon S3
- AWS Key Management Service (KMS)
- AWS SDK for Python (Boto3)

### Security and Data Protection

- Argon2 Password Hashing
- SHA-256
- FASTQ Validation
- Data Pseudonymisation
- Server-Side Encryption with KMS
- S3 Object Lock
- Hash-Chain Audit Logging

## Project Structure

    pharmasecure-genomic-prototype/
    │
    ├── app/
    │   └── dashboard.py
    │
    ├── src/
    │   ├── auth.py
    │   ├── validation.py
    │   ├── pseudonymization.py
    │   ├── storage.py
    │   └── audit.py
    │
    ├── data/
    │   ├── sample_data_2.fastq
    │   ├── synthetic_sample.fastq
    │   └── pseudonymized/
    │
    ├── logs/
    │   ├── audit.log
    │   └── audit_legacy_backup.log
    │
    ├── test_audit.py
    └── .gitignore

## Security Implementation

### Authentication

The application uses Argon2 to verify researcher passwords against stored password hashes. Credentials are loaded from Streamlit secrets rather than being written directly into the application source code.

### FASTQ Validation

The validation module checks:

- FASTQ read identifiers
- DNA sequence characters
- FASTQ separator lines
- Sequence and quality length matching
- Incomplete or empty records

### Pseudonymisation

The pseudonymisation module replaces original FASTQ read identifiers with randomly generated identifiers.

The DNA sequence itself is retained.

### AWS Data Protection

Processed genomic files are uploaded to Amazon S3 using:

- SSE-KMS encryption
- AWS KMS key configuration
- S3 Object Lock in Governance mode
- One-day retention configuration in the prototype

### File Integrity

SHA-256 hashes are calculated before and after uploading. The hashes are compared to verify that the downloaded file matches the uploaded file.

### Audit Logging

Security events are recorded using a SHA-256 hash-chain mechanism. Each record contains the hash of the previous record. The verification function checks the chain for modifications.

## Installation and Setup

### 1. Clone the Repository

    git clone https://github.com/abdul-923/pharmasecure-genomic-prototype.git

    cd pharmasecure-genomic-prototype

### 2. Install Dependencies

Install the Python packages required by the application:

    pip install streamlit boto3 argon2-cffi pandas

### 3. Configure Streamlit Secrets

Create a local Streamlit secrets file at:

    .streamlit/secrets.toml

Configure researcher accounts with usernames, Argon2 password hashes and roles.

Do not commit this file or expose credentials in the public repository.

### 4. Configure AWS Access

Configure AWS credentials using an approved method such as an IAM role or AWS credentials profile.

The AWS identity needs the required permissions for the configured S3 bucket and KMS key.

### 5. Run the Application

    streamlit run app/dashboard.py

## Testing and Verification

The prototype includes audit logging verification through:

    python test_audit.py

The application also provides an audit integrity verification option through its dashboard.

The AWS upload workflow checks:

- Encryption algorithm
- KMS key identifier
- Object Lock retention
- Object Lock mode
- SHA-256 file integrity

## Current Scope and Limitations

PharmaSecure is an educational proof of concept focused on genomic data protection.

The current implementation demonstrates authentication, FASTQ validation, pseudonymisation, AWS storage security, file integrity verification and audit logging.

The following capabilities belong to the wider proposed architecture and are not implemented in this prototype:

- Federated learning using PySyft or TensorFlow Federated
- Genomic analysis using GATK and Bioconductor
- Clinical trial security using REDCap or OpenClinica
- Hyperledger Fabric blockchain integration
- AI-driven drug discovery and model governance
- Vaccine manufacturing and cold-chain monitoring
- Automated pharmaceutical regulatory compliance

The prototype uses synthetic research data and is not intended for real patient information or production pharmaceutical environments.

## Future Improvements

- Implement federated genomic learning.
- Add advanced genomic analysis workflows.
- Integrate privacy-preserving analytics.
- Introduce centralized cloud audit storage.
- Strengthen access control and security monitoring.
- Add automated security testing and deployment pipelines.
- Expand regulatory compliance monitoring.

## Disclaimer

This project is developed for educational and demonstration purposes as part of an EduQual Level 6 Diploma in Artificial Intelligence Operations.

It uses synthetic genomic data and is not a certified clinical or pharmaceutical system.
