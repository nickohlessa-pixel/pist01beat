# ops package (infrastructure only)
from . import util_hash

__all__ = ["util_hash"]

from . import ops_inventory_cli
__all__.append("ops_inventory_cli")

# --- edge slots schema (read-only) ---
from . import edge_slots_schema as _edge_slots_schema

EDGE_SLOTS_SCHEMA_VERSION = _edge_slots_schema.EDGE_SLOTS_SCHEMA_VERSION
new_edge_slots_payload = _edge_slots_schema.new_edge_slots_payload
validate_edge_slots = _edge_slots_schema.validate_edge_slots

__all__.extend([
    "EDGE_SLOTS_SCHEMA_VERSION",
    "new_edge_slots_payload",
    "validate_edge_slots",
])
