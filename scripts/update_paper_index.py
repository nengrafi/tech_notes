from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "Paper_summaries"
README_PATH = PAPER_DIR / "README.md"

START_MARKER = "<!-- AUTO-PAPER-INDEX:START -->"
END_MARKER = "<!-- AUTO-PAPER-INDEX:END -->"


def read_properties(path: Path):
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)

    if len(parts) < 3:
        return None

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None

def collect_papers():
    papers = []

    for path in PAPER_DIR.rglob("*.md"):

        if path.name.lower() == "readme.md":
            continue

        properties = read_properties(path)

        if not properties:
            continue

        title = properties.get("title", path.stem)
        field = properties.get("field")
        category = properties.get("category", "Other")
        status = properties.get("status", "")
        
        if not field:
            continue

        if status == "reading":
            continue

        relative_path = path.relative_to(PAPER_DIR).as_posix()

        link = quote(relative_path, safe="/")

        papers.append({
            "title": str(title),
            "field": str(field),
            "category": str(category),
            "status": str(status),
            "link": link,
        })

    return papers


def make_index(papers):
    grouped = defaultdict(lambda: defaultdict(list))

    for paper in papers:
        grouped[paper["field"]][paper["category"]].append(paper)

    lines = []

    field_order = sorted(grouped)

    for field in field_order:

        lines.append(f"## {field} Papers")
        lines.append("")

        categories = grouped[field]

        for category in sorted(categories):

            lines.append(f"### {category}")
            lines.append("")
            lines.append("| Paper | Status |")
            lines.append("|---|---|")

            category_papers = sorted(
                categories[category],
                key=lambda paper: paper["title"].lower()
            )

            for paper in category_papers:
                title = paper["title"].replace("|", "\\|")
                status = paper["status"].replace("|", "\\|")

                lines.append(
                    f'| [{title}]({paper["link"]}) | {status} |'
                )

            lines.append("")

    if not lines:
        return "_No papers found._"

    return "\n".join(lines).rstrip()


def update_readme(index):
    readme = README_PATH.read_text(encoding="utf-8")

    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError(
            "README에 AUTO-PAPER-INDEX marker가 없습니다."
        )

    before, rest = readme.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)

    new_readme = (
        before
        + START_MARKER
        + "\n\n"
        + index
        + "\n\n"
        + END_MARKER
        + after
    )

    README_PATH.write_text(new_readme, encoding="utf-8")


def main():
    papers = collect_papers()
    index = make_index(papers)
    update_readme(index)

    print(f"Updated README with {len(papers)} papers.")


if __name__ == "__main__":
    main()