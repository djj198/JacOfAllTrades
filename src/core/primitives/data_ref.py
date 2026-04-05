from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class DataRef:
    """
    Immutable reference to external data sources.
    Used for lazy loading of large datasets (e.g., CSV, SQL, MCP tools).
    """
    path: str
    reader_name: str
    format: str
    params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert DataRef to a serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataRef":
        """Reconstruct DataRef from a dictionary."""
        return cls(**data)
