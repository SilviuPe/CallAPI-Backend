import re


import re

def normalize_title(title: str) -> str:
    """
    Removes a numeric suffix like '(n)' from the end of a title.
    Example:
      "ServerByte"      -> "ServerByte"
      "ServerByte(2)"   -> "ServerByte"
      "ServerByte(123)" -> "ServerByte"
    """
    return re.sub(r"\(\d+\)$", "", title)


def generate_duplicate_title(title: str, existing_titles: list[str]) -> str:
    """
    Generates the next available duplicate title.

    Example:
      title = "ServerByte"
      existing_titles = ["ServerByte", "ServerByte(1)", "ServerByte(2)"]
      -> returns "ServerByte(3)"

    Rules:
      - If the title already contains (n), it's normalized first (e.g. "ServerByte(2)" -> "ServerByte").
      - Finds the highest existing suffix and increments it.
    """
    import re

    # 1. Normalize to remove any "(n)" at the end
    base = normalize_title(title)

    # 2. Regex to match same base with optional "(n)"
    pattern = re.compile(rf"^{re.escape(base)}(?:\((\d+)\))?$")

    # 3. Collect used numbers (0 = base without suffix)
    numbers = []
    for t in existing_titles:
        match = pattern.match(t)
        if match:
            if match.group(1):
                numbers.append(int(match.group(1)))
            else:
                numbers.append(0)

    # 4. Determine next number
    next_number = (max(numbers) + 1) if numbers else 1

    return f"{base}({next_number})"