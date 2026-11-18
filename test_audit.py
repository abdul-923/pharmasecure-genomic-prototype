

from src.audit import log_event, verify_audit_log

log_event(
    event="HASH_CHAIN_TEST",
    username="admin",
    status="SUCCESS",
    details={"message": "Testing audit integrity "}
)

result = verify_audit_log()

print(result)
