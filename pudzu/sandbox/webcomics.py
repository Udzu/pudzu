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


# TODO: cache to disk
# https://web.archive.org/web/20160415033105/http://comicrack.cyolito.com/dokuwiki/doku.php?id=guides:creating_webcomics

@cache
def url_content(url: str) -> str:
    logger.debug(f"Loading {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    time.sleep(0.2)
    return response.content.decode()

def remove_duplicates_and_log(seq):
    unique_seq = remove_duplicates(seq)
    if len(seq) != len(unique_seq):
        logger.warning(f"Removed {len(seq) - len(unique_seq)} duplicate traverse URLs")
    return list(unique_seq)

def absolute(urls, base):
    return [urljoin(base, url) for url in urls]

def log_urls(urls):
    return f"{urls}" if len(urls) <= 4 else f"{len(urls)} URLs"

def progress(urls):
    return tqdm(urls) if len(urls) >= 4 else urls

@dataclass
class Matcher:
    match: str
    reverse: bool = False
    sort: bool = False

    def matches(self, html: str) -> Sequence[str]:
        matches = re.findall(self.match, html)
        if self.sort: matches = sorted(matches)
        if self.reverse: matches = reversed(matches)
        return matches

# TODO: WebComic with multiple image getters including ranges? (also supports cover)

@dataclass
class Scraper:
    name: str
    start: str
    image: Matcher
    traverse: Sequence[Matcher] = ()
    next: Optional[Matcher] = None
    # TODO: bg: Optional[str] = None
    # TODO: range based images

    def get_images(
        self,
        start: Optional[str] = None,
        previous_starts: Optional[set[str]] = None,
    ) -> list[str]:
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
            urls = remove_duplicates_and_log(new_urls)
            logger.info(f"Traverse URLS: {log_urls(urls)}")

        next_urls = []
        for url in progress(urls):
            content = url_content(url)
            new_images = absolute(self.image.matches(content), url)
            if len(new_images) == 0:
                logger.warning(f"No images found at {url}")
            images += new_images
            if self.next is not None:
                next_urls += absolute(self.next.matches(content), url)
        images = remove_duplicates_and_log(images)
        logger.info(f"Image URLS: {log_urls(images)}")
        next_urls = remove_duplicates_and_log(next_urls)
        if len(next_urls) > 1:
            logger.info(f"Next URLS: {log_urls(next_urls)}")

        for next_url in next_urls:
            images += self.scrape(next_url, previous_starts | { start })

        return remove_duplicates_and_log(images)

    def save_images(self, images: Sequence[str]) -> None:
        n = floor(log10(len(images))) + 1
        for i, url in enumerate(images, 1):
            uparse = urlparse(url)
            _, uext = os.path.splitext(uparse.path)
            Image.from_url_with_cache(url, self.name, str(i).zfill(n) + uext)

    def zip_images(self) -> None:
        with zipfile.ZipFile(f"{self.name}.cbz", 'w', compression=zipfile.ZIP_STORED) as zip:
            zip.write(self.name)
            for file in sorted(glob.glob(f"{self.name}/*")):
                if any(file.lower().endswith(ext) for ext in ("jpg", "Jpeg", "gif", "png")):
                    zip.write(file)

    def make_cbr(self) -> None:
        images = self.get_images()
        self.save_images(images)
        self.zip_images()

    @classmethod
    def from_json(cls, path: str) -> "Scraper":
        with open(path, "r") as f:
            d = json.load(f)
        return dataclass_from_json(cls, d)
