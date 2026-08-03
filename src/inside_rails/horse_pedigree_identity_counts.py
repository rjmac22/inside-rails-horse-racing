"""Populate-aware contradiction counting for Notebook 19 identity governance.

This module patches the internal contradiction-label selector used by
``horse_pedigree_identity`` so blank source strings are treated as missing,
matching the executed notebook's "multiple populated labels" rule.
"""

from __future__ import annotations

import pandas as pd

from . import horse_pedigree_identity as _identity


def populated_nunique(values: pd.Series) -> int:
    """Count distinct non-null, non-blank source values."""
    populated = values.loc[
        values.notna() & values.astype(str).str.strip().ne("")
    ]
    return int(populated.nunique(dropna=True))


def populated_contradiction_labels(
    rows: pd.DataFrame,
    dam_column: str,
) -> pd.Index:
    """Return horse labels with multiple populated pedigree assertions."""
    counts = rows.groupby("horse", sort=False).agg(
        sire_values=("sire", populated_nunique),
        dam_values=(dam_column, populated_nunique),
        damsire_values=("damsire", populated_nunique),
    )
    return counts.index[
        counts[["sire_values", "dam_values", "damsire_values"]]
        .gt(1)
        .any(axis=1)
    ]


# Keep the public implementation module as the single workflow entry point while
# correcting its internal selector to match the notebook's governed definition.
_identity._contradiction_labels = populated_contradiction_labels
