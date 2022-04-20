"""Utility functions called after NER."""
import os
from typing import List

import numpy as np
import pandas as pd

from . import NODE_AND_EDGE_DIR, SUBCLASS_PREDICATE


def filter_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolidate entities where '_SYNONYM' object_id is a duplicate.

    :param df: Input DataFrame
    :type df: pd.DataFrame
    :return: Consolidated Dataframe
    :rtype: pd.DataFrame
    """
    condition_1 = df["matched_term"].str.lower() == df["preferred_form"].str.lower()
    condition_2 = df["object_id"].str.contains("_SYNONYM")
    same_yet_syn_condition = condition_1 & condition_2
    new_df = df[~same_yet_syn_condition]
    tmp_df = df[same_yet_syn_condition]
    tmp_df["object_id"] = tmp_df["object_id"].str.replace("_SYNONYM", "")
    new_df = pd.concat([new_df, tmp_df])
    return new_df


def consolidate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group rows by all columns except "origin".

    This is done to remove redundancies
    created by entity recognition from multiple sources/ontologies

    :param df: Input DataFrame
    :type df: pd.DataFrame
    :return: Consolidated DataFrame
    :rtype: pd.DataFrame
    """
    # drops columns where all rows are None
    df.dropna(axis=1, how="all", inplace=True)
    grouping_columns = df.columns.tolist()
    grouping_columns.remove("origin")

    new_df = (
        df.fillna("tmp")
        .groupby(grouping_columns)
        .agg({"origin": lambda o: " | ".join(o)})
        .reset_index()
        .replace({"object_match_field": {"tmp": ""}})
    )
    return new_df


def get_column_doc_ratio(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Get str to document ratio of given column in a pandas DataFrame.

    :param df: Pandas DataFrame
    :param column: Column name of the term
    :return: Pandas DataFrame with additional
            columns showing term:document ratio
    """
    df[column] = df[column].str.lower()
    doc_label_df = df[["document_id", column]].drop_duplicates()

    total_docs = len(df["document_id"].drop_duplicates())

    doc_count = column + "_doc_count"

    doc_count_df = (
        doc_label_df.groupby(column)
        .size()
        .sort_values(ascending=False)
        .reset_index(name=doc_count)
    )
    # This new column calculates the ratio:
    # (# of documents where the str in 'column' appears) / (Total # of docs)
    new_column = column + "_doc_ratio"

    doc_count_df[new_column] = doc_count_df[doc_count] / total_docs

    df = df.merge(doc_count_df, how="left", on=column)
    df = df.loc[df.astype(str).drop_duplicates().index]
    return df


def ancestor_generator(df: pd.DataFrame, obj_series: pd.DataFrame) -> List[str]:
    """
    Return an ancestor list of a CURIE.

    :param df: KGX edges of source ontology in DataFrame form.
    :return: List of CURIES (ancestors)
    """
    ancestor_list = []
    obj_series_df = df.loc[df["subject"] == obj_series.object_id]
    while not df.loc[df["subject"] == obj_series.object_id].empty:
        obj_series_df = df.loc[df["subject"] == obj_series.object_id]
        ancestor_list.append(obj_series_df.iloc[0].object_id)
        obj_series = obj_series_df.iloc[0]

    return ancestor_list


def get_ancestors(
    df: pd.DataFrame, nodes_and_edges_dir: str = NODE_AND_EDGE_DIR
) -> pd.DataFrame:
    """
    Return a DataFrame with 'ancestors' column.

    :param df: Input dataframe containing intermediate NER result.
    :param nodes_and_edges_dir: Dir location of KGX edges & nodes file (tsv)
    :return: Dataframe with an 'ancestors' column.
    """
    df["ancestors"] = ""
    object_origin = df[["object_id", "origin"]]
    object_origin["object_id"] = object_origin["object_id"].str.replace("_SYNONYM", "")
    object_origin = object_origin.drop_duplicates()
    all_origins = object_origin["origin"].drop_duplicates().tolist()
    all_origins = [ogn for ogn in all_origins if "|" not in ogn]

    for o in all_origins:
        object_origin_subset = object_origin.loc[object_origin["origin"] == o]
        ont_name = o.split(".")[0]
        ont_edge_file = os.path.join(nodes_and_edges_dir, ont_name + "_edges.tsv")
        print(f"Getting ancestors for {ont_name} terms....")
        ont_edge_df = pd.read_csv(ont_edge_file, sep="\t", low_memory=False)
        ont_edge_df = ont_edge_df.loc[ont_edge_df["predicate"] == SUBCLASS_PREDICATE]
        ont_edge_df.rename(columns={"object": "object_id"}, inplace=True)
        for idx, obj in object_origin_subset.T.iteritems():
            list_of_ancestors = ancestor_generator(ont_edge_df, pd.Series(obj).T)
            df.loc[
                (df["object_id"] == object_origin_subset["object_id"][idx])
                & (df["origin"] == object_origin_subset["origin"][idx]),
                "ancestors",
            ] = str(list_of_ancestors)

    return df.replace(np.nan, "")
