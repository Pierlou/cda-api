def get(d: dict, path: str, sep: str = "."):
    "Get nested values with JSON path"
    res = None
    for k in path.split(sep):
        res = d[k] if res is None else res[k]
    return res
