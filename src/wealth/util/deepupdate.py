"""Contains a function to update a dict with another dict while preserving
possible nested dicts."""
from copy import deepcopy


def deepupdate(d: dict, u: dict) -> dict:
    """Update a given dict `d` with another dict `u`. Recursively retain and
    update nested dicts in `u`."""
    r = deepcopy(d)
    r.update(u)
    for k, v in d.items():
        if isinstance(v, dict):
            w = u.get(k, {})
            r[k] = deepupdate(v, w) if isinstance(w, dict) else d[k]

    return r
