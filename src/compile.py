import pypandoc
from pathlib import Path
import os
import shutil
from typing import List


def convert_markdown(source_md: Path, target_html: Path) -> None:
    with open(source_md) as f:
        markdown = f.read()

    html = pypandoc.convert_text(
        markdown, to="html", format="markdown+raw_html", extra_args=["--mathml"]
    )

    with open(target_html, "w+") as f:
        f.write(html)


def compile_dir(source_dir: Path, output_dir: Path) -> None:
    os.makedirs(output_dir, exist_ok=True)

    post_name = source_dir.stem
    post_dir = output_dir / post_name

    if max(get_times(source_dir)) < min(get_times(post_dir)):
        print(f"Skipping {source_dir}")
        return

    print(f"Generating {source_dir}")
    os.makedirs(post_dir, exist_ok=True)

    if os.path.isdir(source_dir):
        source_md = source_dir / "index.md"
        target_html = post_dir / "index.html"

        for file_name in os.listdir(source_dir):
            if file_name == "index.md":
                continue

            shutil.copy(source_dir / file_name, post_dir / file_name)
    else:
        source_md = source_dir
        target_html = post_dir / "index.html"

    shutil.copy(source_md, post_dir / "raw.md")
    convert_markdown(source_md, target_html)


def get_times(dir: Path) -> List[float]:
    if os.path.isfile(dir):
        return [os.stat(dir).st_ctime]

    return [p.stat().st_ctime for p in dir.rglob("*")]


def compile_all(source_dir: Path, output_dir: Path) -> None:
    for item in os.listdir(source_dir):
        full_name = os.path.join(source_dir, item)
        full_path = Path(full_name)

        if not full_name.endswith(".md") and not os.path.isdir(full_path):
            continue

        compile_dir(full_path, output_dir)


compile_all(Path("meta"), Path("static/meta"))
