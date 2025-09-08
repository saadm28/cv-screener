import re

def clean_text(t: str) -> str:
    t = re.sub(r"\u00A0", " ", t)   # nbsp
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\r", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def summarize_for_similarity(current_title: str, must_hits: list[str], nice_hits: list[str], roles: list[dict]) -> str:
    last_roles = []
    for r in roles[:2]:
        last_roles.append(f"{r.get('title','')} {r.get('org','')} {r.get('start','')}–{r.get('end','')}")
    skills = ", ".join(must_hits + nice_hits) or ""
    return f"title: {current_title}\nskills: {skills}\nrecent: {' | '.join(last_roles)}"
