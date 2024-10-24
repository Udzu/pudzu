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
rate_limit_ms = ThreadLocalBox()

# https://web.archive.org/web/20160415033105/http://comicrack.cyolito.com/dokuwiki/doku.php?id=guides:creating_webcomics

def url_content(url: str, cache: bool) -> str:
    filepath = os.path.join("cache", url_to_filepath(url))
    if cache and os.path.isfile(filepath):
        logger.debug(f"Loading {url} from cache")
        return Path(filepath).read_text()

    logger.debug(f"Loading {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    content = response.content.decode()
    time.sleep(rate_limit_ms.value / 1000)

    if cache:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        Path(filepath).write_text(content)
        Path(filepath+".source").write_text(url)
    return content

def uncache(url: str) -> None:
    logger.info(f"Removing {url} from disk cache")
    filepath = os.path.join("cache", url_to_filepath(url))
    Path(filepath).unlink()

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


def expand_range(url):
    ranges = re.findall(r"\[(\d+)\-(\d+)\]", url)
    if len(ranges) > 1:
        raise ValueError(f"Multiple ranges found in {url!r}")
    elif len(ranges) == 1:
        start, stop = ranges[0]
        digits = min(len(start), len(stop))
        m, n = int(start), int(stop)
        dir = 1 if n >= m else -1
        return [re.sub(r"\[(\d+)\-(\d+)\]", str(n).zfill(digits), url) for n in range(m, n + dir, dir)]
    else:
        return [url]


@dataclass
class Matcher:
    """A regex-based URL matcher. Expects either zero or one matching groups."""

    match: str
    reverse: bool = False
    sort: bool = False
    cache: bool = True

    def matches(self, html: str) -> Sequence[str]:
        matches = re.findall(self.match, html)
        if self.sort:
            matches = sorted(matches)
        if self.reverse:
            matches = reversed(matches)
        return matches


@dataclass(frozen=True)
class PostProcessing:
    """Image postprocessing"""

    bg: Optional[RGBA | str | int] = None  # background colour to apply
    remove_transparency: bool = False  # remove GIF transparency
    convert: Optional[str] = None  # file format to convert to
    quality: Optional[int] = None  # jpeg quality
    optimize: bool = False # optimize conversion

    def process(self, img: Image.Image, path: str, filename: str) -> str:

        stem, ext = os.path.splitext(filename)
        if self.convert is not None:
            ext = self.convert
        filename = f"{stem}[{hash(self)}].{ext}"

        if os.path.isfile(f"{path}/{filename}"):
            return filename

        # transparency
        if self.remove_transparency and "transparency" in img.info:
            del img.info["transparency"]
        elif self.bg is not None:
            img = img.convert("RGBA").remove_transparency(self.bg)

        # save
        if ext.lower() in {"jpg", "jpeg"}:
            img.convert("RGB").save(f"{path}/{filename}", quality=self.quality or 75, optimize=self.optimize)
        else:
            img.save(f"{path}/{filename}", optimize=self.optimize)

        return filename

@dataclass(frozen=True)
class ImageUrl:
    """An image URL (with an optional referrer URL)"""

    url: str
    referer: Optional[str] = None
    process: Optional[PostProcessing] = None

    def __eq__(self, other):
        if isinstance(other, ImageUrl):
            return self.url == other.url and self.process == other.process
        return NotImplemented


@dataclass
class Images:
    """A hardcoded image source (with an optional numeric range)"""

    image: str  # image URL (can contain a numeric range)
    process: Optional[PostProcessing] = None  # image post-processing

    def get_images(self) -> list[ImageUrl]:
        return [ImageUrl(url, process=self.process) for url in expand_range(self.image)]


@dataclass
class Scraper:
    """A scraper image source."""

    start: str  # start page (can contain a numeric range)
    image: Matcher  # matcher for images
    traverse: Sequence[Matcher] = ()  # matchers to get to image pages
    next: Optional[Matcher] = None  # matcher to get to next start page
    process: Optional[PostProcessing] = None  # image post-processing
    cache: bool = True # whether to cache the start pages

    def get_images(self) -> list[ImageUrl]:
        images = []
        previous_starts = set()
        for url in expand_range(self.start):
            images += self.get_images_from(url, previous_starts)
        return images

    def get_images_from(self, start: str, previous_starts: set[str]) -> list[ImageUrl]:
        if not previous_starts:
            logger.info(f"Start URL: {start}")
        elif start in previous_starts:
            logger.warning(f"Skipping duplicate next URL: {start}")
            return []
        else:
            logger.info(f"Next URL: {start}")

        images = []
        urls = [start]
        cache = self.cache
        for traverser in self.traverse:
            new_urls = []
            for url in progress(urls):
                new_urls += absolute(traverser.matches(url_content(url, cache)), url)
            urls = remove_duplicates_and_log(new_urls, "traverse")
            logger.info(f"Traverse URLS: {log_urls(urls)}")
            cache = traverser.cache

        next_urls = []
        for url in progress(urls):
            content = url_content(url, cache)
            new_images = absolute(self.image.matches(content), url)
            if len(new_images) == 0:
                logger.warning(f"No images found at {url}")
            images += [ImageUrl(img, referer=url, process=self.process) for img in new_images]
            if self.next is not None:
                new_next_urls = absolute(self.next.matches(content), url)
                if cache and len(new_next_urls) == 0:
                    uncache(url)
                next_urls += new_next_urls
        images = remove_duplicates_and_log(images, "image")
        logger.info(f"Image URLS: {log_urls(images)}")
        next_urls = remove_duplicates_and_log(next_urls, "next")
        if len(next_urls) > 1:
            logger.info(f"Next URLS: {log_urls(next_urls)}")

        for next_url in next_urls:
            images += self.get_images_from(next_url, previous_starts | {start})

        return remove_duplicates_and_log(images, "image")



@dataclass
class WebComic:
    """A web comic definition."""

    name: str  # comic name
    sources: Sequence[Scraper | Images]  # sequence of image sources
    rate_limit_ms: int = 200  # sleep between url requests

    def get_images(self) -> list[ImageUrl]:
        with self.rate_limit_ms >> rate_limit_ms:
            images = []
            for source in self.sources:
                images += source.get_images()
            logger.info(f"Total image URLS: {log_urls(images)}")
            return images

    def save_images(self, images: Sequence[ImageUrl]) -> list[str]:
        paths = []
        n = floor(log10(len(images))) + 1
        for i, url in enumerate(images, 1):
            headers = None if url.referer is None else {"Referer": url.referer}
            uparse = urlparse(url.url)
            _, uext = os.path.splitext(uparse.path)
            filename = str(i).zfill(n) + uext
            img = Image.from_url_with_cache(url.url, self.name, filename, headers=headers, sleep_ms=self.rate_limit_ms)
            if url.process is not None:
                filename = url.process.process(img, self.name, filename)
            paths.append(filename)
        return paths

    def zip_images(self, filenames: Sequence[str]) -> None:
        with zipfile.ZipFile(f"{self.name}.cbz", "w", compression=zipfile.ZIP_STORED) as zip:
            zip.write(self.name)
            for filename in filenames:
                zip.write(f"{self.name}/{filename}")

    def make_cbr(self) -> None:
        images = self.get_images()
        filenames = self.save_images(images)
        self.zip_images(filenames)

    @classmethod
    def from_json(cls, path: str) -> "WebComic":
        with open(path, "r") as f:
            d = json.load(f)
        return dataclass_from_json(cls, d)
