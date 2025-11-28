"""
functions.py
Contains:
- verify_user(ic_number, password)
- calculate_tax(income, tax_relief)
- save_to_csv(data_dict, filename)
- read_from_csv(filename)

Requires: pandas
"""

import pandas as pd
import os

def verify_user(ic_number: str, password: str) -> bool:
    """
    Verify IC is 12 digits and password matches last 4 digits of IC.
    Returns True if valid, False otherwise.
    """
    if not isinstance(ic_number, str) or not isinstance(password, str):
        return False
    ic_clean = ''.join(filter(str.isdigit, ic_number))
    if len(ic_clean) != 12:
        return False
    return password == ic_clean[-4:]


def calculate_tax(income: float, tax_relief: float) -> float:
    """
    Calculate Malaysian tax payable using progressive rates for YA 2024/2025.
    Chargeable income = max(0, income - tax_relief).
    Returns tax payable (float).
    Tax table implemented following LHDN / PwC published brackets.
    """
    try:
        income = float(income)
        tax_relief = float(tax_relief)
    except Exception:
        raise ValueError("Income and tax_relief must be numeric.")

    chargeable = max(0.0, income - tax_relief)

    # Progressive bands: list of tuples (upper_limit, base_tax, rate_on_excess)
    # We'll implement as cumulative brackets.
    # Using LHDN/PwC scheme (YA 2024/2025)
    brackets = [
        (5000,    0,       0.00),   # up to 5,000 -> 0%
        (20000,   0,       0.01),   # next up to 20,000 -> 1% on excess above 5,000
        (35000, 150,       0.03),
        (50000, 600,       0.06),
        (70000, 1500,      0.11),
        (100000, 3700,     0.19),
        (400000, 9400,     0.25),
        (600000, 84400,    0.26),
        (2000000,136400,   0.28),
        (float('inf'), 528400,    0.30)
    ]

    tax = 0.0
    lower = 0.0
    # compute tax progressively
    for upper, base, rate in brackets:
        if chargeable <= lower:
            break
        taxable_in_band = min(chargeable, upper) - lower
        # For first bracket (0-5000) rate 0, treat uniformly:
        if rate == 0:
            incremental = 0.0
        else:
            incremental = taxable_in_band * rate
        tax += incremental
        lower = upper

    # Note: the 'base' values in table are helpful for hand calc; using per-band multiplication is simpler and accurate.
    return round(tax, 2)


def save_to_csv(data: dict, filename: str = "tax_records.csv") -> None:
    """
    data: dict with keys ['ic_number','income','tax_relief','tax_payable']
    Appends to CSV. Creates file with header if not exists. Uses pandas.
    """
    df_new = pd.DataFrame([data])
    if os.path.exists(filename):
        df_new.to_csv(filename, mode='a', header=False, index=False)
    else:
        df_new.to_csv(filename, mode='w', header=True, index=False)


def read_from_csv(filename: str = "tax_records.csv"):
    """
    Returns pandas DataFrame if file exists, else None
    """
    if not os.path.exists(filename):
        return None
    try:
        df = pd.read_csv(filename)
        return df
    except Exception:
        return None
