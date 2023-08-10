import pandas as pd
from pathlib import Path
from data_common.dataset import get_dataset_df
from data_common.pandas.df_extensions import la, common
from data_common.management.run_notebook import run_notebook
from datetime import date

# get the current pictuer of councils on this date
council_date = date(2023, 4, 2)


def get_lsoa_data() -> pd.DataFrame:
    lsoa_lookup = get_dataset_df(
        "uk_local_authority_names_and_codes",
        "uk_la_past_current",
        "latest",
        "lookup_lsoa_to_registry.csv",
    )

    # map of old to new
    la_df = la.get_la_df(include_historical=True, as_of_date=council_date)
    # just where there is a replaced-by
    la_df = la_df[la_df["replaced-by"].notnull()]
    # map of old to replaced code
    old_to_new_lookup = la_df.set_index("local-authority-code")["replaced-by"].to_dict()

    # update the lsoa mapping with any changes
    lsoa_lookup["local-authority-code"] = lsoa_lookup["local-authority-code"].apply(
        lambda x: old_to_new_lookup.get(x, x)
    )
    return lsoa_lookup


def get_la_with_leagues() -> pd.DataFrame:
    """
    Get combined leagues
    """
    unitaries = [
        "Welsh unitary authority",
        "Scottish unitary authority",
        "Unitary authority",
        "Metropolitan district",
        "London borough",
        "City corporation",
    ]

    league_map = {x: "Single tier" for x in unitaries}
    league_map["NI district"] = "Northern Ireland"
    league_map["County"] = "County councils"
    league_map["Non-metropolitan district"] = "District councils"
    league_map["Combined authority"] = "Combined/strategic authorities"
    league_map["Strategic Regional Authority"] = "Combined/strategic authorities"

    df = la.get_la_df(as_of_date=council_date)
    df["league-group"] = df["local-authority-type-name"].apply(
        lambda x: league_map.get(x, x)
    )
    return df


def create_la_data():
    """
    Create a dataframe of the proportion of LSOAS in each local authority in our free RUC bands
    """

    ruc = pd.read_csv(Path("data", "packages", "uk_ruc", "composite_ruc.csv"))
    ruc = ruc[["lsoa", "ukruc-3", "pop"]].set_index("lsoa")

    # get this into the form of a sheet where the percentage of each lower-tier la is urban, rural, and highly rural is a row

    df = get_lsoa_data().set_index("lsoa")
    df = ruc.join(df, how="outer")
    df["ukruc-3"] = df["ukruc-3"].map({0: "Urban", 1: "Rural", 2: "Highly rural"})
    pt = df.pivot_table(
        "pop", index="local-authority-code", columns=["ukruc-3"], aggfunc="sum"
    ).fillna(0)

    # add higher levels
    hpt = (
        pt.reset_index()
        .la.to_multiple_higher(aggfunc="sum", as_of_date=council_date)
        .set_index("local-authority-code")
    )
    pt = pd.concat([pt, hpt])

    pt = pt.common.row_percentages()
    return pt


def add_clusters_to_la_data():
    df = create_la_data()
    cluster_data = pd.read_csv(Path("data", "interim", "ruc_cluster.csv"))
    df = df.merge(cluster_data, on="local-authority-code")
    df.columns = [x.lower().replace(" ", "-") for x in df.columns]
    start_columns = ["local-authority-code", "official-name"]
    df = df[start_columns + [x for x in df.columns if x not in start_columns]]
    df.to_csv(Path("data", "packages", "uk_ruc", "la_ruc.csv"), index=False)


def create_con_data() -> pd.DataFrame:
    """
    Create a dataframe of the proportion of LSOAS in each local authority in our free RUC bands
    """

    ruc = pd.read_csv(Path("data", "packages", "uk_ruc", "composite_ruc.csv"))
    ruc = ruc[["lsoa", "ukruc-3", "pop"]].set_index("lsoa")

    # get this into the form of a sheet where the percentage of each con is urban, rural, and highly rural is a row

    df = (
        pd.read_csv(Path("data", "raw", "pcon_lsoa.csv"))
        .rename(columns={"lsoa11": "lsoa"})
        .drop(columns=["pcds"])
        .set_index("lsoa")
    )
    df = ruc.join(df, how="outer")
    df["ukruc-3"] = df["ukruc-3"].map({0: "Urban", 1: "Rural", 2: "Highly rural"})
    pt = df.pivot_table("pop", index="pcon", columns=["ukruc-3"], aggfunc="sum").fillna(
        0
    )

    pt = pt.common.row_percentages()
    return pt


def add_clusters_to_con_data():
    df = create_con_data()
    cluster_data = pd.read_csv(Path("data", "interim", "ruc_cluster_con.csv"))
    df = df.merge(cluster_data, on="pcon")
    df.columns = [x.lower().replace(" ", "-") for x in df.columns]

    name_lookup = (
        get_dataset_df(
            "uk_westminster_constituency_names_and_codes",
            "uk_westminster_constituency_names_and_codes",
            "latest",
            "constituencies_and_codes.csv",
        )
        .rename(columns={"gss-code": "pcon", "name": "constituency-name"})
        .drop(columns=["country", "mapit-id", "parliament-id"])
    )

    df = df.merge(name_lookup, on="pcon")
    df = df.rename(columns={"pcon": "gss-code"})

    start_columns = ["gss-code", "constituency-name"]

    df = df[start_columns + [x for x in df.columns if x not in start_columns]]  # type: ignore
    df.to_csv(Path("data", "packages", "uk_ruc", "pcon_ruc.csv"), index=False)


def generate_la_data():

    run_notebook(Path("notebooks", "ruc_clustering.ipynb"))
    add_clusters_to_la_data()


def generate_con_data():
    run_notebook(Path("notebooks", "ruc_clustering_cons.ipynb"))
    add_clusters_to_con_data()


def generate_con_2025_data():
    run_notebook(Path("notebooks", "ruc_clustering_cons_2025.ipynb"))


if __name__ == "__main__":
    generate_la_data()
    generate_con_data()
    generate_con_2025_data()
