import glob
import json
import time
import zipfile
from dataclasses import dataclass
from functools import cache
from typing import Optional
from urllib.parse import urljoin

import requests
from tqdm import tqdm

from pudzu.utils import *
from pudzu.pillar import *

logger = logging.getLogger("webcomics")

# https://web.archive.org/web/20160415033105/http://comicrack.cyolito.com/dokuwiki/doku.php?id=guides:creating_webcomics


# TODO: cache to disk (but handle changes)?
@cache
def url_content(url: str) -> str:
    logger.debug(f"Loading {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    time.sleep(1.0)  # TODO: custom rate limit?
    return response.content.decode()


def remove_duplicates_and_log(seq, desc, key=lambda v: v):
    unique_seq = remove_duplicates(seq, key=key)
    if len(seq) != len(unique_seq):
        logger.warning(f"Removed {len(seq) - len(unique_seq)} duplicate {desc} URLs")
    return list(unique_seq)


def absolute(urls, base):
    return [urljoin(base, url) for url in urls]


def log_urls(urls):
    return f"{urls}" if len(urls) <= 4 else f"{len(urls)} URLs"


def progress(urls):
    return tqdm(urls) if len(urls) >= 4 else urls


@dataclass
class Matcher:
    """A regex-based URL matcher. Expects either zero or one matching groups."""

    match: str
    reverse: bool = False
    sort: bool = False

    def matches(self, html: str) -> Sequence[str]:
        matches = re.findall(self.match, html)
        if self.sort:
            matches = sorted(matches)
        if self.reverse:
            matches = reversed(matches)
        return matches


@dataclass(frozen=True)
class ImageUrl:
    """An image URL (with an optional referrer URL)"""

    url: str
    referer: Optional[str] = None

    def __eq__(self, other):
        if isinstance(other, ImageUrl):
            return self.url == other.url
        return NotImplemented


@dataclass
class Scraper:
    """A scraper image source."""

    start: str
    image: Matcher
    traverse: Sequence[Matcher] = ()
    next: Optional[Matcher] = None

    # TODO: allow ranges in start URL?
    def get_images(
        self,
        start: Optional[str] = None,
        previous_starts: Optional[set[str]] = None,
    ) -> list[ImageUrl]:
        if previous_starts is None:
            previous_starts = set()
        if start is None:
            start = self.start
            logger.info(f"Start URL: {start}")
        elif start in previous_starts:
            logger.warning(f"Skipping duplicate next URL: {start}")
            return []
        else:
            logger.info(f"Next URL: {start}")

        images = []
        urls = [start]
        for traverser in self.traverse:
            new_urls = []
            for url in progress(urls):
                new_urls += absolute(traverser.matches(url_content(url)), url)
            urls = remove_duplicates_and_log(new_urls, "traverse")
            logger.info(f"Traverse URLS: {log_urls(urls)}")

        next_urls = []
        for url in progress(urls):
            content = url_content(url)
            new_images = absolute(self.image.matches(content), url)
            if len(new_images) == 0:
                logger.warning(f"No images found at {url}")
            images += [ImageUrl(img, url) for img in new_images]
            if self.next is not None:
                next_urls += absolute(self.next.matches(content), url)
        images = remove_duplicates_and_log(images, "image")
        logger.info(f"Image URLS: {log_urls(images)}")
        next_urls = remove_duplicates_and_log(next_urls, "next")
        if len(next_urls) > 1:
            logger.info(f"Next URLS: {log_urls(next_urls)}")

        for next_url in next_urls:
            images += self.get_images(next_url, previous_starts | {start})

        return remove_duplicates_and_log(images, "image")


@dataclass
class Images:
    """A hardcoded image source (with an optional numeric range)"""

    image: str

    def get_images(self) -> list[ImageUrl]:
        ranges = re.findall(r"\[(\d+)\-(\d+)\]", self.image)
        if len(ranges) > 1:
            raise ValueError(f"Multiple ranges found in {self.image!r}")
        elif len(ranges) == 1:
            start, stop = ranges[0]
            digits = min(len(start), len(stop))
            m, n = int(start), int(stop)
            dir = 1 if n >= m else -1
            return [ImageUrl(re.sub(r"\[(\d+)\-(\d+)\]", str(n).zfill(digits), self.image)) for n in range(m, n + dir, dir)]
        else:
            return [ImageUrl(self.image)]


@dataclass
class WebComic:
    """A web comic definition."""

    name: str
    sources: Sequence[Scraper | Images]
    # TODO: bg: Optional[color] = None

    def get_images(self) -> list[ImageUrl]:
        images = []
        for source in self.sources:
            images += source.get_images()
        logger.info(f"Total image URLS: {log_urls(images)}")
        return images

    def save_images(self, images: Sequence[ImageUrl]) -> None:
        n = floor(log10(len(images))) + 1
        for i, url in enumerate(images, 1):
            headers = None if url.referer is None else {"Referer": url.referer}
            uparse = urlparse(url.url)
            _, uext = os.path.splitext(uparse.path)
            Image.from_url_with_cache(url.url, self.name, str(i).zfill(n) + uext, headers=headers)

    def zip_images(self) -> None:
        with zipfile.ZipFile(f"{self.name}.cbz", "w", compression=zipfile.ZIP_STORED) as zip:
            zip.write(self.name)
            for file in sorted(glob.glob(f"{self.name}/*")):
                if any(file.lower().endswith(ext) for ext in ("jpg", "Jpeg", "gif", "png")):
                    zip.write(file)

    def make_cbr(self) -> None:
        images = self.get_images()
        self.save_images(images)
        self.zip_images()

    @classmethod
    def from_json(cls, path: str) -> "WebComic":
        with open(path, "r") as f:
            d = json.load(f)
        return dataclass_from_json(cls, d)
