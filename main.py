from pydantic import BaseModel, model_validator, PrivateAttr
from typing import List, Optional, Any
import feedparser
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
import argparse


class Article(BaseModel):
    _blog: "Blog" = PrivateAttr()
    title: str
    date: datetime
    link: Optional[str]

    @staticmethod
    def from_entry(blog: "Blog", entry: Any):
        ret = Article(
            title=entry.title,
            date=datetime(*entry.published_parsed[:6]),
            link=entry.link if "link" in entry else None,
        )
        ret._blog = blog
        return ret


class Blog(BaseModel):
    url: str
    tags: List[str]

    # inferred
    articles: List[Article] = []
    title: str = ""
    error: Optional[str] = None

    def maybe_compute_fields(self):
        rss = feedparser.parse(self.url)

        feed = rss.feed
        if "title" in feed and feed.title != "":
            self.title = feed.title
        else:
            self.title = self.url

        self.articles = [Article.from_entry(self, entry) for entry in rss.entries]
        return self

    @model_validator(mode="after")
    def compute_fields(self):
        print("parsing ", self.url)
        try:
            self.maybe_compute_fields()
        except Exception as e:
            print("failed ", self.url)
            self.error = str(e)

        return self


class BlogRoll(BaseModel):
    blogs: List[Blog]

    @model_validator(mode="after")
    def compute_fields(self):
        dedup_blogs = []
        for blog in self.blogs:
            if any(blog.url == other.url for other in dedup_blogs):
                print("removed duplicate: ", blog.url)
                continue

            dedup_blogs.append(blog)

        self.blogs = dedup_blogs
        return self

    def accumulate_articles(self, last: int = 5) -> List[Article]:
        unsorted = [
            article
            for blog in self.blogs
            for article in sorted(blog.articles, key=lambda x: x.date, reverse=True)[
                :last
            ]
            if article.link is not None
        ]
        return sorted(unsorted, key=lambda x: x.date, reverse=True)


def generate_blog_roll(blog_roll_url: str):
    blogs_json = Path(blog_roll_url).read_text()
    blog_roll = BlogRoll.model_validate_json(blogs_json)

    os.makedirs("static", exist_ok=True)
    env = Environment(loader=FileSystemLoader("meta/templates"))

    with open("static/blog_roll.html", "w+") as f:
        template = env.get_template("blog_roll.jinja2")
        output = template.render(blog_roll=blog_roll)
        f.write(output)

    with open("static/index.html", "w+") as f:
        template = env.get_template("index.jinja2")
        output = template.render()
        f.write(output)


def main():
    parser = argparse.ArgumentParser(description="generate blog")
    parser.add_argument("blog_roll", help="path to blog roll")

    args = parser.parse_args()

    generate_blog_roll(args.blog_roll)


if __name__ == "__main__":
    main()
