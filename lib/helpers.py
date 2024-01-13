def getattr_with_initial_value(obj: object, title: str, initial_value: any) -> any:
    if not getattr(obj, title, False):
        setattr(obj, title, initial_value)
    return getattr(obj, title)