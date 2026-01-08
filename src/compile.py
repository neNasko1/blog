import pypandoc
from pathlib import Path
import os
import shutil
from typing import List
import argparse
import math


def convert_markdown(source_md: Path, target_html: Path) -> None:
    with open(source_md) as f:
        markdown = f.read()

    html = pypandoc.convert_text(
        markdown,
        to="html",
        format="markdown+raw_html",
        extra_args=[
            "--mathml",
            "--template=templates/pandoc.html",
            "--lua-filter",
            "src/pandoc_filters.lua",
            "--embed-resources",
            "--standalone",
            "--css",
            "blog/static/post.css",
            "-M",
            "document-css=true",
        ],
    )

    with open(target_html, "w+") as f:
        f.write(html)


def compile_dir(source_dir: Path, output_dir: Path, force: bool) -> None:
    os.makedirs(output_dir, exist_ok=True)

    post_name = source_dir.stem
    post_dir = output_dir / post_name

    if (
        max(get_times(source_dir), default=-math.inf)
        < min(get_times(post_dir), default=math.inf)
        and not force
    ):
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

    if str(source_dir).endswith("static"):
        return

    shutil.copy(source_md, post_dir / "raw.md")
    convert_markdown(source_md, target_html)


def get_times(dir: Path) -> List[float]:
    if os.path.isfile(dir):
        return [os.stat(dir).st_ctime]

    return [p.stat().st_ctime for p in dir.rglob("*")]


def compile_all(source_dir: Path, output_dir: Path, force: bool) -> None:
    for item in os.listdir(source_dir):
        full_name = os.path.join(source_dir, item)
        full_path = Path(full_name)

        if not full_name.endswith(".md") and not os.path.isdir(full_path):
            continue

        compile_dir(full_path, output_dir, force)


def main():
    parser = argparse.ArgumentParser(description="generate blog")
    parser.add_argument(
        "--force", help="force all blogs to recompile", action="store_true"
    )
    args = parser.parse_args()

    compile_all(Path("blog"), Path("final"), args.force)


if __name__ == "__main__":
    main()
