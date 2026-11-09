
import streamlit as st
from pathlib import Path
import sys
import tempfile
import json
import pandas as pd

# --------------------------------
# Project configuration
# --------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.storage import upload_genomic_file
from src.auth import authenticate_user
from src.validation import validate_fastq
from src.pseudonymization import pseudonymize_fastq
from src.audit import log_event, verify_audit_log

# --------------------------------
# Audit log configuration
# --------------------------------

AUDIT_FILE = PROJECT_ROOT / "logs" / "audit.log"


def load_audit_events():
    events = []

    if not AUDIT_FILE.exists():
        return events

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events


# --------------------------------
# Streamlit configuration
# --------------------------------

st.set_page_config(
    page_title="PharmaSecure Genomic Prototype",
    page_icon="🧬",
    layout="wide"
)


# --------------------------------
# Authentication session
# --------------------------------

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None


# --------------------------------
# Login
# --------------------------------

st.title("🧬 PharmaSecure")

st.subheader(
    "Genomic Data Security and Precision Medicine"
)

if st.session_state.authenticated_user is None:

    st.info(
        "Please sign in to access the researcher dashboard."
    )

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button("Sign In")

    if login_button:

        user = authenticate_user(username, password)

        if user is not None:

            log_event(
                event="LOGIN",
                username=user["username"],
                status="SUCCESS"
            )

            st.session_state.authenticated_user = user

            st.success("Authentication successful.")

            st.rerun()

        else:

            log_event(
                event="LOGIN",
                username=username or "unknown",
                status="FAILED"
            )

            st.error("Invalid username or password.")

    st.stop()


# --------------------------------
# Authenticated dashboard
# --------------------------------

user = st.session_state.authenticated_user

st.success(
    f"Authenticated as {user['username']} "
    f"| Role: {user['role']}"
)

if st.button("Logout"):

    log_event(
        event="LOGOUT",
        username=user["username"],
        status="SUCCESS"
    )

    st.session_state.authenticated_user = None

    st.rerun()




# --------------------------------
# Genomic file upload
# --------------------------------

st.divider()

st.header("Genomic Sequencing File Upload")




# --------------------------------
# Upload authorization
# --------------------------------

if user["role"] == "researcher":

    st.success("Upload permission granted.")

    uploaded_file = st.file_uploader(
        "Select a synthetic FASTQ or BAM file",
        type=["fastq", "fq", "bam"]
    )

    if uploaded_file is not None:

        st.write("Selected file:", uploaded_file.name)

        st.write(
            "File size:",
            f"{uploaded_file.size:,} bytes"
        )

        if st.button(
            "Validate, Protect and Upload",
            type="primary"
        ):

            validation_passed = False
            pseudonymization_passed = False

            # --------------------------------
            # Permanent pseudonymized output
            # --------------------------------

            output_dir = (
                PROJECT_ROOT
                / "data"
                / "pseudonymized"
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            original_name = Path(uploaded_file.name)

            pseudonymized_filename = (
                f"{original_name.stem}_pseudonymized.fastq"
            )

            pseudonymized_path = (
                output_dir / pseudonymized_filename
            )

            # --------------------------------
            # Temporary original file
            # --------------------------------

            with tempfile.TemporaryDirectory() as temp_dir:

                original_path = (
                    Path(temp_dir)
                    / Path(uploaded_file.name).name
                )

                original_path.write_bytes(
                    uploaded_file.getvalue()
                )

                st.subheader(
                    "Security Processing Checklist"
                )

                # --------------------------------
                # FASTQ validation
                # --------------------------------

                if uploaded_file.name.lower().endswith(
                    (".fastq", ".fq")
                ):

                    try:

                        validation_result = validate_fastq(
                            original_path
                        )

                        st.write("FASTQ Validation")

                        st.json(validation_result)

                        validation_passed = (
                            validation_result.get("valid", False)
                        )

                        if validation_passed:

                            st.success(
                                "✅ FASTQ validation completed"
                            )

                            log_event(
                                event="FASTQ_VALIDATION",
                                username=user["username"],
                                status="SUCCESS",
                                details={
                                    "records": validation_result.get(
                                        "records", 0
                                    )
                                }
                            )

                        else:

                            st.error(
                                "FASTQ validation failed. "
                                "Upload rejected."
                            )

                            log_event(
                                event="FASTQ_VALIDATION",
                                username=user["username"],
                                status="FAILED"
                            )

                    except Exception as error:

                        st.error(
                            f"FASTQ validation failed: {error}"
                        )

                        log_event(
                            event="FASTQ_VALIDATION",
                            username=user["username"],
                            status="FAILED",
                            details={
                                "error": str(error)
                            }
                        )

                    # --------------------------------
                    # Pseudonymization
                    # --------------------------------

                    if validation_passed:

                        try:

                            pseudonymization_result = (
                                pseudonymize_fastq(
                                    original_path,
                                    pseudonymized_path
                                )
                            )

                            pseudonymization_passed = (
                                pseudonymization_result.get(
                                    "success", False
                                )
                            )

                            if pseudonymization_passed:

                                st.success(
                                    "✅ FASTQ identifier "
                                    "pseudonymization completed"
                                )

                                st.write(
                                    "Records pseudonymized:",
                                    pseudonymization_result[
                                        "records_processed"
                                    ]
                                )

                                log_event(
                                    event="PSEUDONYMIZATION",
                                    username=user["username"],
                                    status="SUCCESS",
                                    details={
                                        "records_processed":
                                            pseudonymization_result[
                                                "records_processed"
                                            ]
                                    }
                                )

                            else:

                                st.error(
                                    "Pseudonymization failed."
                                )

                                log_event(
                                    event="PSEUDONYMIZATION",
                                    username=user["username"],
                                    status="FAILED"
                                )

                        except Exception as error:

                            st.error(
                                f"Pseudonymization failed: {error}"
                            )

                            log_event(
                                event="PSEUDONYMIZATION",
                                username=user["username"],
                                status="FAILED",
                                details={
                                    "error": str(error)
                                }
                            )

                else:

                    st.warning(
                        "BAM upload is not supported by the "
                        "current pseudonymization pipeline. "
                        "Please use a FASTQ file."
                    )

                    log_event(
                        event="UNSUPPORTED_FILE_TYPE",
                        username=user["username"],
                        status="REJECTED",
                        details={
                            "file_type": "BAM"
                        }
                    )

                # --------------------------------
                # AWS secure upload
                # --------------------------------

                if (
                    validation_passed
                    and pseudonymization_passed
                ):

                    try:

                        with st.spinner(
                            "Uploading pseudonymized data "
                            "and verifying AWS security..."
                        ):

                            result = upload_genomic_file(
                                pseudonymized_path
                            )

                        st.success(
                            "Pseudonymized file uploaded "
                            "and AWS verification completed."
                        )

                        log_event(
                            event="AWS_UPLOAD",
                            username=user["username"],
                            status="SUCCESS",
                            details={
                                "bucket": result.get("bucket"),
                                "object_key": result.get("object_key"),
                                "integrity_status": result.get(
                                    "integrity_status"
                                ),
                                "encryption": result.get(
                                    "encryption"
                                ),
                                "object_lock": result.get(
                                    "object_lock"
                                )
                            }
                        )

                        st.subheader(
                            "AWS Security Verification"
                        )

                        st.json(result)

                        st.subheader(
                            "Security Verification Checklist"
                        )

                        st.write(
                            "✅ Researcher authentication"
                        )

                        st.write(
                            "✅ Role-based upload authorization"
                        )

                        st.write(
                            "✅ FASTQ validation"
                        )

                        st.write(
                            "✅ FASTQ identifier pseudonymization"
                        )

                        st.write(
                            "✅ AWS S3 upload"
                        )

                        st.write(
                            "KMS metadata verification:",
                            result.get("encryption", "Not reported")
                        )

                        st.write(
                            "Object Lock verification:",
                            result.get("object_lock", "Not reported")
                        )

                        st.write(
                            "SHA-256 verification:",
                            result.get("hashes_match", "Not reported")
                        )

                    except Exception as error:

                        st.error(
                            f"Upload or verification failed: {error}"
                        )

                        log_event(
                            event="AWS_UPLOAD",
                            username=user["username"],
                            status="FAILED",
                            details={
                                "error": str(error)
                            }
                        )

                elif not validation_passed:

                    st.error(
                        "Upload cancelled because FASTQ "
                        "validation failed."
                    )

                elif not pseudonymization_passed:

                    st.error(
                        "Upload cancelled because "
                        "pseudonymization failed."
                    )


elif user["role"] != "admin":

    log_event(
        event="UNAUTHORIZED_UPLOAD_ATTEMPT",
        username=user["username"],
        status="DENIED",
        details={
            "role": user["role"]
        }
    )

    st.error(
        "Access denied. Your account does not "
        "have permission to upload genomic data."
    )


# --------------------------------
# Audit Log Viewer
# --------------------------------

if user["role"] in ["admin", "researcher"]:

    st.divider()

    st.header("🔐 Audit Log Viewer")

    st.caption(
        "Review security events recorded by PharmaSecure."
    )

    # --------------------------------
    # Audit Log Integrity Verification
    # --------------------------------

    st.subheader("Audit Log Integrity")

    if st.button("Verify Audit Log Integrity"):

        integrity_result = verify_audit_log()

        if integrity_result["valid"]:

            st.success(
                integrity_result["message"]
            )

        else:

            st.error(
                integrity_result["message"]
            )

        st.write(
            "Records checked:",
            integrity_result["records_checked"]
        )

    # --------------------------------
    # Refresh Audit Logs
    # --------------------------------

    if st.button("Refresh Audit Logs"):

        st.rerun()

    # --------------------------------
    # Load Audit Events
    # --------------------------------

    audit_events = load_audit_events()

    if not audit_events:

        st.info("No audit events have been recorded yet.")

    else:

        # Newest events first
        audit_events.reverse()

        audit_df = pd.DataFrame(audit_events)

        # --------------------------------
        # Event filter
        # --------------------------------

        event_types = sorted(
            audit_df["event"].dropna().unique().tolist()
        )

        selected_event = st.selectbox(
            "Filter by event",
            ["All Events"] + event_types
        )

        # --------------------------------
        # Status filter
        # --------------------------------

        statuses = sorted(
            audit_df["status"].dropna().unique().tolist()
        )

        selected_status = st.selectbox(
            "Filter by status",
            ["All Statuses"] + statuses
        )

        filtered_df = audit_df.copy()

        if selected_event != "All Events":

            filtered_df = filtered_df[
                filtered_df["event"] == selected_event
            ]

        if selected_status != "All Statuses":

            filtered_df = filtered_df[
                filtered_df["status"] == selected_status
            ]

        # --------------------------------
        # Display audit events
        # --------------------------------

        st.write(
            f"Audit events displayed: {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------
        # Download audit logs
        # --------------------------------

        audit_json = json.dumps(
            filtered_df.to_dict(orient="records"),
            indent=2
        )

        st.download_button(
            label="Download displayed audit logs",
            data=audit_json,
            file_name="pharmasecure_audit_logs.json",
            mime="application/json"
        )


# --------------------------------
# Footer
# --------------------------------

st.divider()

st.caption(
    "PharmaSecure Educational Prototype | "
    "Synthetic data only | "
    "Not intended for real patient information"
)

