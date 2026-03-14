import hashlib
import json
from datetime import datetime, timezone

def generate_hash(data_block):
    """Creates a deterministic SHA-256 hash of a dictionary."""
    # sort_keys=True is critical so the hash doesn't change due to key order [cite: 296, 298]
    block_string = json.dumps(data_block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def create_audit_entry(record, worker_id, previous_hash="0" * 64):
    """Creates a chained audit entry for the ledger."""
    entry_data = {
        "record_id": record.get("id"),
        "worker_id": worker_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "previous_hash": previous_hash,
        "record_snapshot": record
    }
    # Link the current block to the previous one using SHA-256 [cite: 281, 299]
    entry_data["hash"] = generate_hash(entry_data)
    return entry_data

# Testing the logic locally
if __name__ == "__main__":
    mock_record = {"id": "REC_001", "patient": "Sunita", "bp": "110/70"}
    entry = create_audit_entry(mock_record, "worker_meena")
    print(f"Audit Entry Created Successfully!")
    print(f"Current Hash: {entry['hash']}")
