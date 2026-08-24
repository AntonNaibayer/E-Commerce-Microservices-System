from slugify import slugify


def generate_slug(text: str) -> str:
    return slugify(text)  # "Электроника" -> "elektronika", "Nike Inc." -> "nike-inc"