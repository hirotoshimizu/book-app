from flask import request


def get_page_num() -> int:
    return int(request.args.get("page", "1"))


def get_limit() -> int:
    return int(request.args.get("limit", "9"))


def get_start_index(page_num: int, limit: int) -> int:
    return (page_num - 1) * limit


def get_pagination_num(total_num: int, limit: int) -> int:
    return -(-total_num // limit)
