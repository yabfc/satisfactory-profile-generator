import re
import dataclasses


def uncamelcase(src: str) -> str:
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", src)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)
    return s.lower().replace("_", "-")


def unclassname(src: str, classes: list[str]) -> str:
    for c in classes:
        src = re.sub(rf"{c}(.*?)_C$", r"\1", src)
    return uncamelcase(src).replace("_", "-").replace("--", "-")


def dump(obj):
    if dataclasses.is_dataclass(obj):
        out = {}
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if val is None:
                continue
            key = f.metadata.get("alias", f.name)
            out[key] = dump(val)
        return out
    if isinstance(obj, list):
        return [dump(e) for e in obj]
    if isinstance(obj, dict):
        return {k: dump(v) for k, v in obj.items()}
    return obj


def removeAll(src: str, to_remove: list[str]) -> str:
    for rep in to_remove:
        src = src.replace(rep, "")
    return src


def purge_optional_fields(obj):
    # if name is not present, it's an implicit null
    # => we can delete the field when it's null
    if isinstance(obj, dict):
        return {
            k: purge_optional_fields(v)
            for k, v in obj.items()
            if not (k in ["name", "craftable"] and v is None)
        }
    elif isinstance(obj, list):
        return [purge_optional_fields(x) for x in obj]
    return obj
