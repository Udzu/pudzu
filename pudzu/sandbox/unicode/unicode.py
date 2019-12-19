import importlib.resources
import re
import numpy as np
import pandas as pd

from pudzu.utils import *

logger = logging.getLogger('unicode')

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
    "Simple_Titlecase_Mapping"
]

def extract_unicodedata():
    """ Convert UnicodeData.txt into a DataFrame. """
    logger.info("Extracting UnicodeData.txt...")
    
    with importlib.resources.open_text(__package__, "UnicodeData.txt") as fh:
        df = pd.read_csv(fh, sep=";", header=None, names=UNICODEDATA_COLUMNS, index_col="Code_Point",
                         converters={'Code_Point': artial(int, 16)})

    # remove Surrogate and Private Use characters
    df = df[~df["General_Category"].isin(["Cs","Co"])]

    # expand code ranges (TODO: generate correct names)
    for a,z in zip(df[df.Name.str.contains("First")].index, df[df.Name.str.contains("Last")].index):
        df = df.reindex(df.index.append(pd.Index(range(a+1,z))).sort_values(), method='pad')
        df.loc[a:z, "Name"] = (
                df.loc[a:z].Name.str.replace(re.compile(", (First|Last)>"), "") + ", #" +
                df.loc[a:z].index.to_series().apply(artial(format, '04x')) + ">")

    df["Code_Point"] = df.index.to_series().apply(artial(format, '04x'))
    return df


def extract_property(filename, property):
    """ Convert a standard UCD file. Currently only handles a subset of enumerated and binary properties. """
    logger.info(f"Extracting {property} from {filename}...")
    
    with importlib.resources.open_text(__package__, filename) as fh:
        df = pd.read_csv(fh, sep=";", header=None, skip_blank_lines=True, comment="#",
                         names=['Code_Point', property])

    # remove whitespace and set (possibly non-unique) index
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.index = df.Code_Point.str.replace("\.\..*","").apply(artial(int, 16))
    
    # Filter out Surrogate and Private Use characters (though non-existent characters may remain)
    df = df.loc[(df.index < 0xD800) | ((df.index > 0xF8FF) & (df.index < 0xF0000))]

    # expand code ranges (TODO: make more efficient)
    expanded = df
    ranges = df[df.Code_Point.str.contains("\.\.")]
    for i, az in enumerate(ranges.Code_Point):
        a, z = map(artial(int, 16), az.split(".."))
        copies = ranges.iloc[np.full(z-a, i)]
        copies.index = range(a+1,z+1)
        expanded = expanded.append(copies)

    # combine properties
    df = expanded.sort_index()
    df = df.groupby(df.index).agg(set)
    exclusive = (df.applymap(len) == 1).all()
    df = df.apply(lambda s: s.apply(lambda i: next(iter(i))) if exclusive[s.name] else s.apply(tuple))

    return df.drop(columns=["Code_Point"])


def unicode_data():
    df = extract_unicodedata()
    df["Script"] = extract_property("Scripts.txt", "Script")["Script"]
    df["ScriptExtensions"] = extract_property("ScriptExtensionss.txt", "ScriptExtensions")["ScriptExtensions"]
    df["Emoji"] = extract_property("emoji-data.txt", "Emoji")["Emoji"]
    df["Properties"] = extract_property("PropList.txt", "Properties")["Properties"]
    df["Block"] = extract_property("Blocks.txt", "Block")["Block"]
    return df
