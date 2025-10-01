def get_constant_name(cls, value: int) -> str:
    for name in dir(cls):
        if not name.startswith("_"):
            if getattr(cls, name) == value:
                return name
    raise ValueError(f"No constant found with value {value}")
