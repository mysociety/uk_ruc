"""
Script to create a single unified measures of urban/rural across the UK

See readme for details

"""
import pandas as pd
from pathlib import Path


def create_soa_bands_ni():
    """
    create SOA level bands, and then assign rucs
    """
    source = Path("source_files", "Settlement15-lookup.xls")
    df = pd.read_excel(source, sheet_name="Allocation", skiprows=3)
    df = df[["SA2011", "SOA2011", "Settlement Classification Band"]]
    df = df.rename(columns={"Settlement Classification Band": "band",
                            "SOA2011": "lsoa"})
    df["band"] = df["band"].apply(lambda x: ord(x)-64)

    pt = df.pivot_table(
        values="band", index="lsoa").reset_index()
    pt["band"] = pt["band"].round().astype(int).apply(lambda x: chr(x + 64))
    pt["ukruc-2"] = 0
    pt["ukruc-3"] = 0
    pt.loc[pt["band"].isin(["E", "F", "G", "H"]), "ukruc-2"] = 1
    pt.loc[pt["band"].isin(["E", "F"]), "ukruc-3"] = 1
    pt.loc[pt["band"].isin(["G", "H"]), "ukruc-3"] = 2
    pt = pt.drop(columns=["band"])
    pt["nation"] = "N"
    return pt


def create_datazone_s():
    """
    create 2 and 3-fold rucs for Scotland
    """
    source = Path("source_files", "DZ2011_SGUR2016_Lookup.csv")
    df = pd.read_csv(source)
    df = df.rename(columns={"DZ_CODE": "lsoa"})
    df["ukruc-2"] = 0
    df["ukruc-3"] = 0
    df.loc[df["UR6FOLD"].isin([3, 4, 5, 6]), "ukruc-2"] = 1
    df.loc[df["UR6FOLD"].isin([3, 4]), "ukruc-3"] = 1
    df.loc[df["UR6FOLD"].isin([5, 6]), "ukruc-3"] = 2
    df = df[["lsoa", "ukruc-2", "ukruc-3"]]
    df["nation"] = "S"
    return df


def create_lsoa_ew():
    """
    create 2 and 3 fold rucs for England/Wales
    """
    source = Path("source_files", "ruc_2011.csv")
    df = pd.read_csv(source)
    df["ukruc-2"] = 0
    df["ukruc-3"] = 0
    df.loc[df["RUC11CD"].isin(["D1", "D2", "E1", "E2"]), "ukruc-2"] = 1
    df.loc[df["RUC11CD"].isin(["D1", "D2"]), "ukruc-3"] = 1
    df.loc[df["RUC11CD"].isin(["E1", "E2"]), "ukruc-3"] = 2
    df = df[["lsoa", "ukruc-2", "ukruc-3"]]
    df["nation"] = df["lsoa"].str.slice(stop=1)
    return df


def create_composite_measure():
    """
    Create cross-national RUC
    """
    components = [create_soa_bands_ni(),
                  create_datazone_s(),
                  create_lsoa_ew()
                  ]

    df = pd.concat(components)
    df.to_csv(Path("output", "composite_ruc.csv"), index=False)


def analysis_pivot():
    """
    Composition by nation
    """
    df = pd.read_csv(Path("output", "composite_ruc.csv"))
    for var in ["ukruc-2", "ukruc-3"]:
        pt = df.pivot_table("lsoa", var, "nation", aggfunc="count")
        pt = pt.apply(lambda x: (x / float(x.sum())) * 100
                      ).round(2)
        pt = pt.reset_index()  # bring back column name
        pt[var] = pt[var].map({0: "Urban", 1: "Rural", 2: "More Rural"})
        pt.to_csv(Path("analysis", var + ".csv"), index=False)
        for nation in "ESWN":
            pt[nation] = pt[nation].map("{:,.0f}%".format)
        pt.to_markdown(Path("analysis", var + ".md"), index=False)


if __name__ == "__main__":
    create_composite_measure()
    analysis_pivot()
