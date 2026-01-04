from pydantic import BaseModel, PrivateAttr
from typing import List, Optional, Any, Dict
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import os
import argparse
import asyncio


class Article(BaseModel):
    _blog: "Blog" = PrivateAttr()
    title: str
    date: datetime
    link: Optional[str]

    @staticmethod
    def from_entry(blog: "Blog", entry: Any):
        entry_timestamp = (
            entry.updated_parsed
            if "updated_parsed" in entry
            else entry.published_parsed
        )

        ret = Article(
            title=entry.title,
            date=datetime(*entry_timestamp[:6]),
            link=entry.link if "link" in entry else None,
        )
        ret._blog = blog
        return ret


class Blog(BaseModel):
    url: str
    tags: List[str]

    # loaded
    articles: List[Article] = []
    title: str = ""
    error: Optional[str] = None

    async def load(self):
        try:
            print("parsing", self.url)
            rss = await asyncio.to_thread(feedparser.parse, self.url)

            feed = rss.feed
            self.title = feed.title if getattr(feed, "title", "") else self.url
            self.articles = [Article.from_entry(self, entry) for entry in rss.entries]

        except Exception as e:
            print("failed", self.url)
            self.error = str(e)

        return self

    def get_last_articles(
        self,
        minimum: int = 3,
        last_month_max: int = 5,
        timeframe: timedelta = timedelta(days=31),
    ) -> List[Article]:
        srt_articles = sorted(self.articles, key=lambda x: x.date, reverse=True)
        relevant = sum(1 for x in srt_articles if datetime.now() - x.date <= timeframe)
        to_show = max(minimum, max(last_month_max, relevant))
        return srt_articles[:to_show]


class BlogRoll(BaseModel):
    blogs: List[Blog]

    async def load(self):
        dedup = {}
        for blog in self.blogs:
            if blog.url not in dedup:
                dedup[blog.url] = blog
            else:
                print("removed duplicate:", blog.url)

        self.blogs = list(dedup.values())

        await asyncio.gather(*(blog.load() for blog in self.blogs))
        return self

    def get_shown_articles(self) -> List[Article]:
        unsorted = [
            article
            for blog in self.blogs
            for article in blog.get_last_articles()
            if article.link is not None
        ]
        return sorted(unsorted, key=lambda x: x.date, reverse=True)

    @property
    def forwarded_info(self) -> Dict[Any, Any]:
        shown_articles = self.get_shown_articles()
        return {
            "articles": {
                "shown": shown_articles,
                "shown_count": len(shown_articles),
                "all_count": sum(len(blog.articles) for blog in self.blogs),
            },
            "blogs": {
                "success": len([x for x in self.blogs if x.error is None]),
                "all": len(self.blogs),
            },
        }


async def generate_blog_roll(blog_roll_url: str):
    blogs_json = Path(blog_roll_url).read_text()
    blog_roll = BlogRoll.model_validate_json(blogs_json)

    await blog_roll.load()

    os.makedirs("static", exist_ok=True)
    env = Environment(loader=FileSystemLoader("meta/templates"))

    with open("static/blog_roll.html", "w+") as f:
        template = env.get_template("blog_roll.jinja2")
        output = template.render(blog_info=blog_roll.forwarded_info)
        f.write(output)

    with open("static/index.html", "w+") as f:
        template = env.get_template("index.jinja2")
        output = template.render()
        f.write(output)


def main():
    parser = argparse.ArgumentParser(description="generate blog")
    parser.add_argument("blog_roll", help="path to blog roll")
    args = parser.parse_args()

    asyncio.run(generate_blog_roll(args.blog_roll))


if __name__ == "__main__":
    main()
