from typing import Any, Dict, List

EXPORT_DIFF_VERSION = "export_diff_v1_readonly"


def diff_exports(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic diff of two export dicts.
    Returns JSON-serializable dict with stable keys/order.
    """
    warnings: List[str] = []
    changed: Dict[str, Any] = {}
    added: Dict[str, Any] = {}
    removed: Dict[str, Any] = {}

    def warn(msg: str) -> None:
        warnings.append(msg)

    def is_json_scalar(x: Any) -> bool:
        return x is None or isinstance(x, (bool, int, float, str))

    def to_jsonable(x: Any, path: str) -> Any:
        if is_json_scalar(x):
            return x
        if isinstance(x, dict):
            out: Dict[str, Any] = {}
            for k in sorted(x.keys(), key=lambda z: str(z)):
                ks = str(k)
                if not isinstance(k, str):
                    warn(f"non-string dict key at '{path}': {type(k).__name__} coerced to str")
                out[ks] = to_jsonable(x[k], f"{path}.{ks}" if path else ks)
            return out
        if isinstance(x, list):
            return [to_jsonable(v, f"{path}[{i}]") for i, v in enumerate(x)]
        warn(f"non-JSON type at '{path}': {type(x).__name__} coerced to repr")
        return repr(x)

    def join_path(base: str, key: str) -> str:
        return f"{base}.{key}" if base else key

    def diff_node(path: str, av: Any, bv: Any) -> None:
        if type(av) is not type(bv):
            warn(f"type change at '{path}': {type(av).__name__} -> {type(bv).__name__}")

        if isinstance(av, dict) and isinstance(bv, dict):
            akeys = set(av.keys())
            bkeys = set(bv.keys())

            for k in sorted(akeys - bkeys, key=lambda z: str(z)):
                ks = str(k)
                p = join_path(path, ks)
                removed[p] = to_jsonable(av[k], p)

            for k in sorted(bkeys - akeys, key=lambda z: str(z)):
                ks = str(k)
                p = join_path(path, ks)
                added[p] = to_jsonable(bv[k], p)

            for k in sorted(akeys & bkeys, key=lambda z: str(z)):
                ks = str(k)
                p = join_path(path, ks)
                diff_node(p, av[k], bv[k])
            return

        if isinstance(av, list) and isinstance(bv, list):
            min_len = min(len(av), len(bv))

            for i in range(min_len):
                p = f"{path}[{i}]" if path else f"[{i}]"
                diff_node(p, av[i], bv[i])

            for i in range(min_len, len(av)):
                p = f"{path}[{i}]" if path else f"[{i}]"
                removed[p] = to_jsonable(av[i], p)

            for i in range(min_len, len(bv)):
                p = f"{path}[{i}]" if path else f"[{i}]"
                added[p] = to_jsonable(bv[i], p)
            return

        aj = to_jsonable(av, path)
        bj = to_jsonable(bv, path)
        if aj != bj:
            changed[path] = {"from": aj, "to": bj}

    if not isinstance(a, dict) or not isinstance(b, dict):
        warn("root inputs are not both dicts; coercing to dict-ish comparison")
        a = {"_root": a}
        b = {"_root": b}

    diff_node("", a, b)

    def sorted_map(m: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k in sorted(m.keys()):
            out[k] = m[k]
        return out

    warnings_sorted = sorted(set(warnings))

    summary = {
        "changed_count": len(changed),
        "added_count": len(added),
        "removed_count": len(removed),
    }

    out: Dict[str, Any] = {}
    out["version"] = EXPORT_DIFF_VERSION
    out["summary"] = summary
    out["changed"] = sorted_map(changed)
    out["added"] = sorted_map(added)
    out["removed"] = sorted_map(removed)
    out["warnings"] = warnings_sorted
    return out
