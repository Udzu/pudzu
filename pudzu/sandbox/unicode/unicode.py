import importlib.resources
import logging
import re
from pathlib import Path
from typing import Collection, Optional, Sequence

import numpy as np
import pandas as pd
from pkg_resources import resource_listdir
from pudzu.utils import artial

logger = logging.getLogger("unicode")
logger.setLevel(logging.INFO)

UNICODEDATA_FILENAME = "UnicodeData.txt"

UNICODEDATA_COLUMNS = [
    "Code_Point",
    "Name",
    "General_Category",
    "Canonical_Combining_Class",
    "Bidi_Class",
    "Decomposition_Type_Mapping",
    "Numeric_Type_Mapping_Decimal",
    "Numeric_Type_Mapping_Digit",
    "Numeric_Type_Mapping_Numeric",
    "Bidi_Mirrored",
    "Unicode_1_Name",
    "ISO_Comment",
    "Simple_Uppercase_Mapping",
    "Simple_Lowercase_Mapping",
    "Simple_Titlecase_Mapping",
]


def extract_unicodedata(path: Optional[Path] = None) -> pd.DataFrame:
    """ Convert UnicodeData.txt into a DataFrame. """
    logger.info(f"Extracting {UNICODEDATA_FILENAME} from {path or 'package'}...")

    with open(path / UNICODEDATA_FILENAME, encoding="utf-8") if path else importlib.resources.open_text(__package__, UNICODEDATA_FILENAME) as fh:
        df = pd.read_csv(fh, sep=";", header=None, names=UNICODEDATA_COLUMNS, index_col="Code_Point", converters={"Code_Point": artial(int, 16)})

    # remove Surrogate and Private Use characters
    df = df[~df["General_Category"].isin(["Cs", "Co"])]

    # drop obsolete columns
    df = df.drop(columns=["Unicode_1_Name", "ISO_Comment"])

    # expand code ranges (TODO: generate correct names)
    for a, z in zip(df[df.Name.str.contains("First")].index, df[df.Name.str.contains("Last")].index):
        df = df.reindex(df.index.append(pd.Index(range(a + 1, z))).sort_values(), method="pad")
        df.loc[a:z, "Name"] = (
            df.loc[a:z].Name.str.replace(re.compile(", (First|Last)>"), "") + ", #" + df.loc[a:z].index.to_series().apply(artial(format, "04x")) + ">"
        )

    df["Code_Point"] = df.index.to_series().apply(artial(format, "04x"))
    return df


def extract_property(filename: str, path: Optional[Path] = None) -> pd.DataFrame:
    """ Convert a UCD file containing enumerated or binary properties. """
    logger.info(f"Extracting {filename} from {path or 'package'}...")

    with open(path / filename, encoding="utf-8") if path else importlib.resources.open_text(__package__, filename) as fh:
        df = pd.read_csv(fh, sep=";", header=None, skip_blank_lines=True, comment="#", names=["Code_Point", Path(filename).stem])

    # remove whitespace and set (possibly non-unique) index
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.index = df.Code_Point.str.replace(r"\.\..*", "", regex=True).apply(artial(int, 16))

    # Filter out Surrogate and Private Use characters (though non-existent characters may remain)
    df = df.loc[(df.index < 0xD800) | ((df.index > 0xF8FF) & (df.index < 0xF0000))]

    # expand code ranges
    expanded = df
    ranges = df[df.Code_Point.str.contains(r"\.\.")]
    for i, az in enumerate(ranges.Code_Point):
        a, z = map(artial(int, 16), az.split(".."))
        copies = ranges.iloc[np.full(z - a, i)]
        copies.index = range(a + 1, z + 1)
        expanded = expanded.append(copies)

    # combine properties (TODO: handle valued properties)
    df = expanded.drop(columns=["Code_Point"]).sort_index()
    df = df.groupby(df.index).agg(tuple)
    exclusive = (df.applymap(len) == 1).all()
    df = df.apply(lambda s: s.apply(lambda i: i[0]) if exclusive[s.name] else s)

    return df


def unicode_data(properties: Collection[str] = ("Blocks", "PropList"), path: Optional[Path] = None) -> pd.DataFrame:
    """ Extract core unicode data and properties, from the packaged files or from a given path. """
    df = extract_unicodedata(path)
    for property in sorted(set(properties)):
        df[property] = extract_property(f"{property}.txt", path)
    return df


def unicode_resources(path: Optional[Path] = None) -> Sequence[str]:
    """ List Unicode resource *.txt files in the package or given path. """
    if path:
        return sorted(r.stem for r in Path(path).glob("*.txt"))
    else:
        return sorted(r[:-4] for r in resource_listdir(__package__, "") if r.endswith(".txt"))
