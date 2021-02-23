import logging
from urllib.parse import unquote

import bs4
import lxml  # pylint: disable=unused-import
import pandas as pd
import requests
from pudzu.dates import *
from pudzu.utils import *
from pudzu.utils import cached_property, ignoring_exceptions, optional_import, partial

from pudzu.sandbox.tureen import *

requests_cache = optional_import("requests_cache")

# Utilities for scraping with Wikipedia and WikiData.

logger = logging.getLogger("wikipage")


class CachedPage:
    """Base class representing a page loaded from an optional requests cache. To enable cacheing, call set_cache on the derived class."""

    CACHE = requests
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    @classmethod
    def set_cache(cls, cache_path, **kwargs):
        cls.CACHE = requests if cache_path is None else requests_cache.CachedSession(cache_path, **kwargs)


class WikiPage(CachedPage):
    """Class representing a Wikipedia page."""

    @staticmethod
    def hostname_from_lang(lang):
        return "{}.wikipedia.org".format(lang)

    @classmethod
    def url_from_title(cls, title, lang="en"):
        """The Wikipedia URL for a given page title."""
        return "http://{}/wiki/{}".format(cls.hostname_from_lang(lang), title)

    @staticmethod
    def title_from_url(url):
        """The page title of a given Wikipedia URL. URL-decoded but underscores are not replaced with spaces."""
        t = re.findall("/wiki/(.*)$", url)
        return None if len(t) == 0 else unquote(t[0])

    def __init__(self, title, lang="en"):
        """The Wikipedia page with a given title."""
        self.request_title = title
        self.lang = lang
        self.hostname = self.hostname_from_lang(lang)
        self.url = self.url_from_title(title, lang=lang)
        self.response = self.CACHE.get(self.url, headers=self.HEADERS)
        self.bs4 = bs4.BeautifulSoup(self.response.content, "lxml")
        if self.bs4.find(id="t-permalink") is None:
            raise KeyError("Wikipedia article not found for '{}' at {}".format(title, self.hostname))

    def __repr__(self):
        return "<WikiPage at {}{} [{}]>".format(
            self.title, "" if self.title == self.request_title else " (redirect from {})".format(self.request_title), self.lang
        )

    @cached_property
    def title(self):
        """The page title"""
        return self.bs4.find(id="firstHeading").text

    @cached_property
    @ignoring_exceptions
    def entity(self):
        """The page wikidata entity if it exists."""
        return self.bs4.find(id="t-wikibase").a["href"].split("/")[-1]

    @cached_property
    @ignoring_exceptions
    def image_url(self):
        """The page og:image URL if it exists."""
        return self.bs4.find("meta", {"property": "og:image"})["content"]

    @ignoring_exceptions
    def to_wikidata(self, lang=None):
        """The wikidata page if it exists."""
        return WDPage(self.entity, lang=lang or self.lang)

    # api calls

    def pageviews(self, start, end, granularity="monthly", access="all-access", agent="all-agents"):
        """A JSON object representing the number of page views for a given period."""

        def format_date(d):
            if isinstance(d, Date):
                d = d.to_date()
            if hasattr(d, "strftime"):
                return d.strftime("%Y%m%d")
            return d

        pageview_api = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
        url = "{}/per-article/{}/{}/{}/{}/{}/{}/{}".format(
            pageview_api, self.hostname, access, agent, self.title, granularity, format_date(start), format_date(end)
        )
        return requests.get(url, headers=self.HEADERS).json().get("items", [])

    def revision_count(self):
        """The total number of page revisions. May require repeated API calls."""
        query_api = "https://{}/w/api.php".format(self.hostname)
        parameters = {"action": "query", "titles": self.title, "prop": "revisions", "rvprop": "", "rvlimit": "max", "format": "json", "continue": ""}
        revisions = 0
        while True:
            response = requests.get(query_api, params=parameters).json()
            for page_id in response["query"]["pages"]:
                if "revisions" not in response["query"]["pages"][page_id]:
                    logger.warning("Missing revision information for %s", self.title)
                    break
                revisions += len(response["query"]["pages"][page_id]["revisions"])
            if "continue" in response:
                parameters["continue"] = response["continue"]["continue"]
                parameters["rvcontinue"] = response["continue"]["rvcontinue"]
            else:
                break
        return revisions

    # the remaining methods are domain-specific

    @staticmethod
    def wiki_year_title(year, lang="en"):
        if lang != "en":
            raise NotImplementedError
        if year > 100:
            return "{}".format(year)
        elif year >= 0:
            return "AD {}".format(year)
        else:
            return "{} BC".format(-year)

    @classmethod
    def from_year(cls, year, lang="en"):
        """The Wikipedia page about a given historic year."""
        return WikiPage(WikiPage.wiki_year_title(year, lang))


class WDPage(CachedPage):
    """Base class representing a wikidata entity."""

    API = "https://www.wikidata.org/w/api.php"

    def __init__(self, id, lang="en"):
        """A Wikidata entry with the given id."""
        self.id = id
        self.json = self.get_entity(self.id)
        self.lang = lang
        self.claims = self.json["entities"][id]["claims"]

    @classmethod
    def from_name(cls, name, lang="en", property=False):
        """A Wikidata entry with the given name."""
        id = cls.search_entity(name, property, lang)
        if id is None:
            raise KeyError("No entity found for {} ({})".format(name, lang))
        return cls(id, lang)

    @classmethod
    def from_wikipedia(cls, title, lang="en"):
        """A Wikidata entry for the given Wikipedia page"""
        wp = title if isinstance(title, WikiPage) else WikiPage(title, lang=lang)
        return cls(wp.entity, lang)

    # API calls

    @classmethod
    def api_call(cls, parameters):
        """Wikidata api call."""
        logurl = "{}?{}".format(cls.API, "&".join("{}={}".format(k, v) for k, v in parameters.items()))
        logger.debug("WikiData API: %s", logurl)
        json = cls.CACHE.get(cls.API, params=assoc_in(parameters, ["format"], "json"), headers=cls.HEADERS).json()
        if "error" in json:
            raise Exception("WikiData API error for {}: {}".format(logurl, json["error"].get("info", "(no info)")))
        return json

    @classmethod
    def get_entity(cls, id):
        """Return claims and labels for a given entity"""
        parameters = {"action": "wbgetentities", "ids": id, "props": "claims|labels|sitelinks|aliases", "format": "json"}
        return cls.api_call(parameters)

    @classmethod
    def search_entity(cls, name, property=False, lang="en", precise=True):
        """Returns the entity codes for a given search."""
        type = "property" if property else "item"
        parameters = {"action": "wbsearchentities", "search": name, "language": lang, "type": type, "format": "json"}
        results = cls.api_call(parameters).get("search", [])
        if precise:
            results = [d for d in results if d["match"]["text"].lower() == name.lower()]
        ids = [d["id"] for d in results]
        return first(ids) if precise else ids

    # methods

    def __repr__(self):
        return "<WDPage at {} ({})>".format(self.id, self.name())

    def __eq__(self, other):
        if isinstance(other, WDPage):
            return self.id == other.id
        else:
            return NotImplemented

    def name(self, lang=None):
        """Wikidata entity name"""
        return self.json["entities"][self.id]["labels"].get(lang or self.lang, {"value": "(unknown)"})["value"]

    def names(self, lang=None, aliases=True):
        """Wikidata entity names, including aliases"""
        name = self.json["entities"][self.id]["labels"].get(lang or self.lang)
        names = [] if name is None else [name["value"]]
        aliases = [alias["value"] for alias in self.json["entities"][self.id]["aliases"].get(lang or self.lang, [])] * aliases
        return names + aliases

    @ignoring_exceptions
    def to_wikipedia(self, lang=None):
        """Wikipedia page for the given Wikidata entry, if there is one."""
        lang = lang or self.lang
        return WikiPage(self.json["entities"][self.id]["sitelinks"][lang + "wiki"]["title"], lang=lang)

    def to_labels(self, langs=None, aliases=True, id=False):
        """Dataframe containing per-language labels."""
        columns = ["language", "id", "label"] if id else ["language", "label"]
        labels = [
            (lang, self.id, label) if id else (lang, label)
            for lang in langs or self.json["entities"][self.id]["labels"]
            for label in self.names(lang, aliases=aliases)
        ]
        if langs:
            missing_langs = [l for l in langs if not any(lang == l for lang, *_ in labels)]
            if missing_langs:
                logger.warning("Missing %s labels for %s", self.name(), ", ".join(missing_langs))
        return pd.DataFrame(labels, columns=columns)

    @staticmethod
    def convert_value(value):
        """Convert wikidata value to an appropriate Python type. Currently handles just string, entity and time, and even those not perfectly."""
        if "time" in value:
            year = int(value["time"][0:5])
            month = int(value["time"][6:8])
            day = int(value["time"][9:11])
            date = tuple(x for x in (year, month, day) if x != 0)
            precision = DatePrecision(11 - int(value["precision"]))
            return ApproximateDate(date, precision)
        elif "id" in value:
            return WDPage(value["id"])
        else:
            return value

    def property_values(self, property, qualifier_filter=lambda qs: True, convert=True):
        """Basic property value extractor. For more complex queries, use self.claims directly for now."""
        id = property.id if isinstance(property, WDPage) else property
        convert = self.convert_value if convert else identity
        return [
            convert(claim["mainsnak"]["datavalue"]["value"])
            for claim in self.claims.get(id, [])
            if claim["mainsnak"]["snaktype"] == "value" and qualifier_filter(claim.get("qualifiers", {}))
        ]

    # the remaining methods are domain-specific

    COUNTRY = "P17"
    PLACE_OF_BIRTH = "P19"
    PLACE_OF_DEATH = "P20"
    DATE_OF_BIRTH = "P569"
    DATE_OF_DEATH = "P570"
    END_TIME = "P582"

    @cached_property
    def dates_of_birth(self):
        """Dates of birth."""
        return sorted(self.property_values(self.DATE_OF_BIRTH))

    @cached_property
    def dates_of_death(self):
        """Dates of birth."""
        return sorted(self.property_values(self.DATE_OF_DEATH))

    @cached_property
    def places_of_birth(self):
        """Places of birth."""
        return self.property_values(self.PLACE_OF_BIRTH)

    @cached_property
    def places_of_death(self):
        """Places of birth."""
        return self.property_values(self.PLACE_OF_DEATH)

    @cached_property
    def countries_of_birth(self):
        """Countries of birth (based on modern borders)."""
        cobs = []
        for pob in self.places_of_birth:
            for cob in pob.property_values(self.COUNTRY, lambda qs: self.END_TIME not in qs):
                cobs.append(cob)
        return list(remove_duplicates(cobs, lambda wd: wd.id))


WDProp = partial(WDPage.from_name, property=True)
