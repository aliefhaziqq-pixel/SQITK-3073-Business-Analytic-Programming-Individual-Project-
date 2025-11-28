"""
main.py
Run this script to use the Malaysian Tax Input Program.
"""

from functions import verify_user, calculate_tax, save_to_csv, read_from_csv
import getpass
import pandas as pd

def prompt_registration():
    print("=== Registration ===")
    user_id = input("Enter user id (username): ").strip()
    ic = input("Enter IC number (12 digits, e.g. 980101014321): ").strip()
    last4 = input("Enter password (last 4 digits of your IC): ").strip()
    if not verify_user(ic, last4):
        print("Registration failed: IC must be 12 digits and password must be last 4 digits.")
        return None
    # store credentials locally in a simple 'users.csv' (IC + user_id)
    # For simplicity we store IC and user_id; password = last4 (derived)
    try:
        users_df = pd.read_csv("users.csv")
    except FileNotFoundError:
        users_df = pd.DataFrame(columns=["user_id","ic_number"])
    # Avoid duplicate IC
    if ic in users_df.get("ic_number", []).astype(str).tolist():
        print("IC already registered. Please login.")
        return None
    users_df.loc[len(users_df)] = {"user_id": user_id, "ic_number": ic}

    users_df.to_csv("users.csv", index=False)
    print("Registration successful. You may login now.")
    return {"user_id": user_id, "ic_number": ic}

def prompt_login():
    print("=== Login ===")
    user_id = input("Enter user id: ").strip()
    # Use getpass for password entry to hide on-screen
    password = getpass.getpass("Enter password (last 4 digits of IC): ").strip()
    # look up IC for given user_id
    try:
        users_df = pd.read_csv("users.csv")
    except FileNotFoundError:
        print("No registered users. Please register first.")
        return None
    user_row = users_df[users_df['user_id'] == user_id]
    if user_row.empty:
        print("User id not found.")
        return None
    ic = str(user_row.iloc[0]['ic_number'])
    if verify_user(ic, password):
        print("Login successful.")
        return {"user_id": user_id, "ic_number": ic}
    else:
        print("Login failed: incorrect password.")
        return None

def collect_income_and_relief():
    while True:
        try:
            income = float(input("Enter annual income (RM): ").strip())
            if income < 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Enter a non-negative number.")
    while True:
        try:
            relief = float(input("Enter total tax relief (RM): ").strip())
            if relief < 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Enter a non-negative number.")
    return income, relief

def display_records():
    df = read_from_csv("tax_records.csv")
    if df is None:
        print("No tax records found.")
        return
    try:
        from tabulate import tabulate
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    except Exception:
        print(df.to_string(index=False))

def main():
    print("Malaysian Tax Input Program")
    # check if users.csv exists and has entries
    try:
        users_df = pd.read_csv("users.csv")
        registered = not users_df.empty
    except FileNotFoundError:
        registered = False

    user = None
    if not registered:
        print("No registered users found. Please register.")
        reg = prompt_registration()
        if reg is None:
            return
        user = reg
    else:
        # ask login or register
        choice = input("Do you want to (l)ogin or (r)egister? [l/r]: ").strip().lower()
        if choice == 'r':
            reg = prompt_registration()
            if reg:
                user = reg
            else:
                # try login
                user = prompt_login()
        else:
            user = prompt_login()
            if user is None:
                return

    # at this point user dict contains ic_number
    ic = user['ic_number']

    # collect income & relief
    income, relief = collect_income_and_relief()

    # calculate tax
    tax_payable = calculate_tax(income, relief)
    print(f"\nTax payable (RM): {tax_payable:.2f}")

    # save record
    data = {
        "ic_number": ic,
        "income": income,
        "tax_relief": relief,
        "tax_payable": tax_payable
    }
    try:
        save_to_csv(data, "tax_records.csv")
        print("Record saved to tax_records.csv")
    except Exception as e:
        print("Failed to save record:", e)

    # option to view records
    view = input("Do you want to view saved tax records? (y/n): ").strip().lower()
    if view == 'y':
        display_records()

if __name__ == "__main__":
    main()
