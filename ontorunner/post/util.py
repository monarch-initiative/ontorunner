from venv import create
import pandas as pd
from ontobio import OntologyFactory


def filter_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolidate entities where '_SYNONYM' object_id is a duplicate

    :param df: Input DataFrame
    :type df: pd.DataFrame
    :return: Consolidated Dataframe
    :rtype: pd.DataFrame
    """

    condition_1 = (
        df["matched_term"].str.lower() == df["preferred_form"].str.lower()
    )
    condition_2 = df["object_id"].str.contains("_SYNONYM")
    same_yet_syn_condition = condition_1 & condition_2
    new_df = df[~same_yet_syn_condition]
    tmp_df = df[same_yet_syn_condition]
    tmp_df["object_id"] = tmp_df["object_id"].str.rstrip("_SYNONYM")
    new_df = pd.concat([new_df, tmp_df])
    return new_df


def consolidate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group rows by all columns except "origin" to remove redundancies
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
    :return: Pandas DataFrame with additional columns showing term:document ratio
    """
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
    df = df.drop_duplicates()
    return df


def get_ancestors(df: pd.DataFrame) -> pd.DataFrame:
    origin_object_df = df[["origin", "object_id"]].drop_duplicates()
    origin_object_df["object_id"] = origin_object_df["object_id"].apply(
        lambda x: x.split("_")[0]
    )

    origin_object_df = origin_object_df.drop_duplicates()
    origin_list = list(origin_object_df["origin"].drop_duplicates())
    for origin in origin_list:
        sub_df = df[df["origin"] == origin]
        ont = origin.split(".")[0]
        if "_" in ont:
            ont = origin.split("_")[0]
        ontFact = OntologyFactory().create(ont)
        sub_df["ancestors"] = sub_df["object_id"].apply(
            lambda obj: ontFact.ancestors(ontFact.search(obj)[0])
        )
        df = pd.merge(df, sub_df, how="left", on=list(df.columns))

    return df
