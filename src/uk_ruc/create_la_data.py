import pandas as pd
from pathlib import Path
from data_common.dataset import get_dataset_df
from data_common.pandas.df_extensions import la, common
from data_common.management.run_notebook import run_notebook


def get_lsoa_data():
    return get_dataset_df(
        "uk_local_authority_names_and_codes",
        "uk_la_past_current",
        "1",
        "lookup_lsoa_to_registry.csv",
    )


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

    df = la.get_la_df()
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
        .la.to_multiple_higher(aggfunc="sum")
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
    df.to_csv(Path("data", "packages", "uk_ruc", "la_ruc.csv"), index=False)


def generate_la_data():

    run_notebook(Path("notebooks", "ruc_clustering.ipynb"))
    add_clusters_to_la_data()


if __name__ == "__main__":
    generate_la_data()
