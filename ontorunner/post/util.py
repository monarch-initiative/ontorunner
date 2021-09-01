import pandas as pd


def filter_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolidate entities where '_SYNONYM' entity_id is a duplicate

    :param df: Input DataFrame
    :type df: pd.DataFrame
    :return: Consolidated Dataframe
    :rtype: pd.DataFrame
    """

    condition_1 = df["matched_term"].str.lower() == \
        df["preferred_form"].str.lower()
    condition_2 = df["entity_id"].str.contains("_SYNONYM")
    fullConditionStatement = ~(condition_1 & condition_2)
    return df[fullConditionStatement]


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
        df.groupby(grouping_columns)
        .agg({"origin": lambda o: " | ".join(o)})
        .reset_index()
    )
    return new_df
