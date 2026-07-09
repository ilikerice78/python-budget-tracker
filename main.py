"""A simple command-line budget tracker with planning and analysis tools."""

from collections import defaultdict
from datetime import date, datetime
from statistics import mean


transactions = []
budgets = {}


def money(amount):
    """Format an amount consistently for display."""
    return f"£{amount:,.2f}"


def read_amount(prompt):
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            print("Please enter a positive number, for example 42.50.")


def read_non_negative_amount(prompt):
    while True:
        try:
            amount = float(input(prompt))
            if amount < 0:
                raise ValueError
            return amount
        except ValueError:
            print("Please enter zero or a positive number, for example 42.50.")


def read_date(prompt="Date (YYYY-MM-DD, leave blank for today): "):
    while True:
        value = input(prompt).strip()
        if not value:
            return date.today()
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("Please use YYYY-MM-DD, for example 2026-07-09.")


def show_menu():
    print("\n" + "=" * 38)
    print("           BUDGET TRACKER")
    print("=" * 38)
    print("1.  Add income")
    print("2.  Add expense")
    print("3.  View transactions")
    print("4.  Financial summary")
    print("5.  Set or view category budgets")
    print("6.  Spending by category")
    print("7.  Monthly cash-flow report")
    print("8.  Savings goal calculator")
    print("9.  Delete a transaction")
    print("0.  Exit")


def add_transaction(transaction_type):
    category = input("Category: ").strip().title() or "Uncategorised"
    amount = read_amount("Amount: £")
    description = input("Description (optional): ").strip()
    transaction_date = read_date()
    transactions.append({
        "type": transaction_type,
        "category": category,
        "amount": amount,
        "description": description,
        "date": transaction_date,
    })
    print(f"{transaction_type.title()} added: {money(amount)} in {category}.")


def totals(items=None):
    items = transactions if items is None else items
    income = sum(item["amount"] for item in items if item["type"] == "income")
    expenses = sum(item["amount"] for item in items if item["type"] == "expense")
    return income, expenses, income - expenses


def view_transactions():
    if not transactions:
        print("No transactions yet.")
        return
    print("\n #  Date        Type     Category           Amount       Description")
    print("-" * 72)
    for number, item in enumerate(sorted(transactions, key=lambda entry: entry["date"]), 1):
        print(f"{number:>2}  {item['date']:%Y-%m-%d}  {item['type'].title():<8} "
              f"{item['category']:<18.18} {money(item['amount']):>10}  {item['description']}")


def view_summary():
    if not transactions:
        print("No transactions yet.")
        return
    income, expenses, balance = totals()
    savings_rate = (balance / income * 100) if income else 0
    expense_ratio = (expenses / income * 100) if income else 0
    days_recorded = max((date.today() - min(item["date"] for item in transactions)).days + 1, 1)
    daily_spend = expenses / days_recorded
    projected_monthly_spend = daily_spend * 30.44

    print("\nFINANCIAL SUMMARY")
    print(f"Total income:              {money(income)}")
    print(f"Total expenses:            {money(expenses)}")
    print(f"Current balance:           {money(balance)}")
    print(f"Savings rate:              {savings_rate:.1f}%")
    print(f"Income spent:              {expense_ratio:.1f}%")
    print(f"Average daily spending:    {money(daily_spend)}")
    print(f"Projected monthly spending:{money(projected_monthly_spend)}")

    if budgets:
        planned = sum(budgets.values())
        print(f"Monthly budget total:      {money(planned)}")
        print(f"Unallocated income:        {money(income - planned)}")


def manage_budgets():
    while True:
        print("\nCATEGORY BUDGETS")
        if budgets:
            for category, limit in sorted(budgets.items()):
                print(f"- {category}: {money(limit)}")
        else:
            print("No category budgets set.")
        print("1. Set a budget  2. Remove a budget  0. Back")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            return
        if choice == "1":
            category = input("Category: ").strip().title()
            if category:
                budgets[category] = read_amount("Monthly budget: £")
                print(f"Budget saved for {category}.")
        elif choice == "2":
            category = input("Category to remove: ").strip().title()
            if budgets.pop(category, None) is None:
                print("That category has no saved budget.")
            else:
                print("Budget removed.")
        else:
            print("Invalid option.")


def spending_by_category():
    expenses = [item for item in transactions if item["type"] == "expense"]
    if not expenses:
        print("No expenses yet.")
        return
    total_spending = sum(item["amount"] for item in expenses)
    categories = defaultdict(float)
    for item in expenses:
        categories[item["category"]] += item["amount"]

    print("\nSPENDING BY CATEGORY")
    print("Category              Spent       Share    Budget status")
    print("-" * 62)
    for category, spent in sorted(categories.items(), key=lambda entry: entry[1], reverse=True):
        limit = budgets.get(category)
        status = "No budget"
        if limit:
            difference = limit - spent
            status = f"{money(abs(difference))} {'left' if difference >= 0 else 'over'}"
        print(f"{category:<21} {money(spent):>10}  {spent / total_spending:>5.1%}   {status}")

    unspent_budget_categories = set(budgets) - set(categories)
    for category in sorted(unspent_budget_categories):
        print(f"{category:<21} {money(0):>10}  {0:>5.1%}   {money(budgets[category])} left")


def monthly_cash_flow():
    if not transactions:
        print("No transactions yet.")
        return
    months = defaultdict(list)
    for item in transactions:
        months[item["date"].strftime("%Y-%m")].append(item)
    print("\nMONTHLY CASH FLOW")
    print("Month       Income       Expenses     Net")
    print("-" * 46)
    monthly_nets = []
    for month, entries in sorted(months.items()):
        income, expenses, net = totals(entries)
        monthly_nets.append(net)
        print(f"{month:<11} {money(income):>10}  {money(expenses):>10}  {money(net):>10}")
    if len(monthly_nets) > 1:
        print(f"Average monthly net: {money(mean(monthly_nets))}")


def savings_goal_calculator():
    target = read_amount("Savings target: £")
    current = read_non_negative_amount("Current savings: £")
    monthly_contribution = read_amount("Amount you can save each month: £")
    annual_rate = read_non_negative_amount("Annual interest rate (%): ") / 100
    if current >= target:
        print("You have already reached this goal!")
        return
    monthly_rate = annual_rate / 12
    balance = current
    months = 0
    while balance < target and months < 1200:
        balance += balance * monthly_rate
        balance += monthly_contribution
        months += 1
    interest = balance - current - monthly_contribution * months
    finish_date = date.today().replace(day=1)
    finish_month = finish_date.month + months
    finish_year = finish_date.year + (finish_month - 1) // 12
    finish_month = (finish_month - 1) % 12 + 1
    print(f"\nYou will reach {money(target)} in about {months} month(s), around {finish_year}-{finish_month:02d}.")
    print(f"Projected balance: {money(balance)} (including {money(interest)} interest).")


def delete_transaction():
    if not transactions:
        print("No transactions to delete.")
        return
    view_transactions()
    try:
        number = int(input("Transaction number to delete (0 to cancel): "))
        if number == 0:
            return
        # The displayed list is date-sorted, so delete the selected object itself.
        displayed = sorted(transactions, key=lambda entry: entry["date"])
        transaction = displayed[number - 1]
        transactions.remove(transaction)
        print("Transaction deleted.")
    except (ValueError, IndexError):
        print("Please enter a valid transaction number.")


def main():
    actions = {
        "1": lambda: add_transaction("income"), "2": lambda: add_transaction("expense"),
        "3": view_transactions, "4": view_summary, "5": manage_budgets,
        "6": spending_by_category, "7": monthly_cash_flow,
        "8": savings_goal_calculator, "9": delete_transaction,
    }
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
