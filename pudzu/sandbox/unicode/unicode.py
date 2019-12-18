import importlib.resources
import re
import pandas as pd

from pudzu.utils import *

UCD_COLUMNS = [
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


def ucd_data():

    with importlib.resources.open_text(__package__, "UnicodeData.txt") as fh:
        df = pd.read_csv(fh, sep=";", header=None, names=UCD_COLUMNS, index_col="Code_Point",
                         converters={'Code_Point': artial(int, 16)})

    # remove Surrogate and Private Use characters
    df = df[~df["General_Category"].isin(["Cs","Co"])]

    # expand code ranges (TODO: generate correct names)
    for a,z in zip(df[df.Name.str.contains("First")].index, df[df.Name.str.contains("Last")].index):
        df = df.reindex(df.index.append(pd.Index(range(a+1,z))).sort_values(), method='pad')
        df.loc[a:z, "Name"] = (
                df.loc[a:z].Name.str.replace(re.compile(", (First|Last)>"), "") + ", #" +
                df.loc[a:z].index.to_series().apply(artial(format, 'x')) + ">")

    return df


def additional_data(filename, properties):

    with importlib.resources.open_text(__package__, filename) as fh:
        df = pd.read_csv(fh, sep=";", header=None, skip_blank_lines=True, comment="#",
                         names=['Code_Point'] + properties)

    # remove whitespace and set index (TODO: handle non-unique properties)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.index = df.Code_Point.str.replace("\.\..*","").apply(artial(int, 16))
    df = df.sort_index()

    # expand code ranges
    for az in df[df.Code_Point.str.contains("\.\.")].Code_Point:
        a, z = map(artial(int, 16), az.split(".."))
        df = df.reindex(df.index.append(pd.Index(range(a+1,z+1))).sort_values(), method='pad')

    return df.drop(columns=["Code_Point"])


def unicode_data():
    # TODO: logging
    df = ucd_data()
    scripts = additional_data("Scripts.txt", ["Script"])
    df = pd.concat([df, scripts], axis=1)
    return df
