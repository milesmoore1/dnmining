"""Reusable layer loading, column selection, labeling, and sample joins."""

import geopandas as gpd
import pandas as pd
import pyogrio

from .ree_interpolation import interpolate_row


def list_layers(path):
    """Return available layer names and geometry types."""
    return pd.DataFrame(pyogrio.list_layers(path), columns=["name", "geometry_type"])


def load_layer(path, layer):
    """Load a layer and print its size and coordinate reference system."""
    data = gpd.read_file(path, layer=layer)
    print(f"Loaded {len(data):,} features; CRS: {data.crs}")
    return data


def select_columns(data, columns):
    """Select an independent copy, failing clearly if required columns are absent."""
    missing = [col for col in columns if col not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return data[columns].copy()


def fill_missing_ree(data, targets):
    """Fill missing target elements without replacing observed values."""
    data = data.copy()
    interpolated = data.apply(interpolate_row, axis=1)
    for element in targets:
        filled = data[element].isna() & interpolated[element].notna()
        data[element] = data[element].fillna(interpolated[element])
        print(f"{element}: filled {filled.sum()} missing values")
    return data


def add_priority_labels(data, label_elements, prices, class_names):
    """Reproduce the price-weighted score and quantile-based target labels."""
    data = data.copy()
    required = sum(data[e] * prices[e] / 1000 for e in label_elements)
    # Preserve the existing assumption that missing Y contributes zero.
    y_value = (data["Y"] * prices["Y"] / 1000).fillna(0)
    data["critical_ree_value_per_ton"] = required + y_value
    data["priority_tier"] = pd.qcut(
        data["critical_ree_value_per_ton"], q=len(class_names), labels=class_names
    )
    print(data["priority_tier"].value_counts(dropna=False))
    return data


def merge_samples(elements, quality):
    """Left-join sample tables, retaining the element table's State field."""
    data = elements.merge(
        quality.drop(columns=["State"]), on="Sample_ID", how="left", indicator=True
    )
    print(data["_merge"].value_counts())
    return data.drop(columns="_merge")
