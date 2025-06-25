import uk_ruc

import pytest
import pandas as pd
from pathlib import Path

package_dir = Path(__file__).parent.parent / "data" / "packages" / "uk_ruc"


def test_enough_las():
    df = pd.read_csv(package_dir / "la_ruc.csv")
    assert len(df) == 397


def test_enough_cons():
    df = pd.read_csv(package_dir / "pcon_ruc.csv")
    assert len(df) == 650
