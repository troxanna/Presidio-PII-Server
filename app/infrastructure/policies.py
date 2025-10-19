# Policies placeholder
from app.config import DEFAULT_POLICY

def get_default_policy():
    """Return a copy of the default anonymization policy."""
    return {**DEFAULT_POLICY}
