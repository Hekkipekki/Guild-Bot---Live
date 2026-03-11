from data.character_store import (
    get_user_characters as store_get_user_characters,
    get_character_by_class as store_get_character_by_class,
    add_character as store_add_character,
    remove_character as store_remove_character,
    update_character_name_by_class as store_update_character_name_by_class,
    update_character_spec_by_class as store_update_character_spec_by_class,
)


def get_user_characters(user_id: int):
    return store_get_user_characters(user_id)


def get_character_by_class(user_id: int, class_name: str):
    return store_get_character_by_class(user_id, class_name)


def add_user_character(user_id: int, char: dict) -> bool:
    return store_add_character(user_id, char)


def remove_user_character(user_id: int, index: int) -> bool:
    return store_remove_character(user_id, index)


def update_character_name(user_id: int, class_name: str, new_name: str) -> bool:
    return store_update_character_name_by_class(user_id, class_name, new_name)


def update_character_spec(user_id: int, class_name: str, new_spec: str, new_role: str) -> bool:
    return store_update_character_spec_by_class(user_id, class_name, new_spec, new_role)