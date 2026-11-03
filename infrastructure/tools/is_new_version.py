def is_new_version(new_version: str, old_version: str) -> bool:
    """Сравнение двух версий. True - версия новее"""
    # print(type(new_version))
    new_version_tuple = tuple(map(int, new_version.split(".")))
    old_version_tuple = tuple(map(int, old_version.split(".")))
    for i in range(3):
        if new_version_tuple[i] > old_version_tuple[i]:
            return True
    return False