def show_menu():
    print("\nBudget Tracker")
    print("1. Add income")
    print("2. Add expense")
    print("3. View transactions")
    print("4. View summary")
    print("5. Exit")


while True:
    show_menu()
    choice = input("Choose an option: ")

    if choice == "1":
        print("Add income selected")
    elif choice == "2":
        print("Add expense selected")
    elif choice == "3":
        print("View transactions selected")
    elif choice == "4":
        print("View summary selected")
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid option. Try again.")