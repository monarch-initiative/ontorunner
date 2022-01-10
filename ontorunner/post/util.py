import pandas as pd


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


def get_object_doc_ratio(df: pd.DataFrame) -> pd.DataFrame:
    doc_label_df = df[["document_id", "object_label"]].drop_duplicates()

    total_docs = len(df["document_id"].drop_duplicates())

    doc_count_df = (
        doc_label_df.groupby("object_label")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="doc_count")
    )
    # This new column calculates the ratio:
    # (# of documents where the object_label appears) / (Total # of docs)
    doc_count_df["term_to_doc_ratio"] = doc_count_df["doc_count"] / total_docs

    df = df.merge(doc_count_df, how="left", on="object_label")
    df = df.drop_duplicates()
    return df
