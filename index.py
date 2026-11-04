# DIGITAL PLATFORM FOR RESOURCE REUSE AND MATCHING
# Construction and Demolition Materials

available_materials = []

condition_rank = {
    "poor": 1,
    "fair": 2,
    "good": 3,
    "excellent": 4
}

availability_options = {
    "1": "Ready",
    "2": "Within 7 days",
    "3": "Within 30 days"
}


# FUNCTION 1: ADD SURPLUS MATERIALS
def add_material():

    print("\n--- REGISTER SURPLUS MATERIAL ---")

    project = input("Enter project name: ")
    material = input("Enter material type: ").strip().title()

    while True:
        try:
            quantity = float(input("Enter available quantity: "))
            if quantity > 0:
                break
            print("Quantity must be positive.")
        except ValueError:
            print("Enter a valid number.")

    while True:
        condition = input(
            "Enter condition (Poor/Fair/Good/Excellent): "
        ).strip().lower()

        if condition in condition_rank:
            break
        print("Invalid condition.")

    location = input("Enter project location: ")

    print("\nAvailability:")
    print("1. Ready")
    print("2. Within 7 days")
    print("3. Within 30 days")

    while True:
        choice = input("Select availability: ")
        if choice in availability_options:
            availability = availability_options[choice]
            break
        print("Invalid selection.")

    material_data = {
        "project": project,
        "material": material,
        "quantity": quantity,
        "condition": condition,
        "location": location,
        "availability": availability
    }

    available_materials.append(material_data)

    print("\nMaterial successfully registered!")


# FUNCTION 2: CALCULATE MATCHING SCORE
def calculate_match(supplier, requirement):

    if supplier["material"].lower() != requirement["material"].lower():
        return None

    # Quantity score (25 marks)
    quantity_score = min(
        supplier["quantity"] / requirement["quantity"], 1
    ) * 25

    # Quality / condition score (20 marks)
    supplier_condition = condition_rank[supplier["condition"]]
    required_condition = condition_rank[requirement["condition"]]

    if supplier_condition >= required_condition:
        condition_score = 20
    elif supplier_condition == required_condition - 1:
        condition_score = 10
    else:
        condition_score = 0

    # Location score (15 marks)
    if supplier["location"].lower() == requirement["location"].lower():
        location_score = 15
    else:
        location_score = 5

    # Availability score (10 marks)
    availability_points = {
        "Ready": 10,
        "Within 7 days": 7,
        "Within 30 days": 4
    }

    availability_score = availability_points[supplier["availability"]]

    # Material type score (30 marks)
    material_score = 30

    total_score = (
        material_score
        + quantity_score
        + condition_score
        + location_score
        + availability_score
    )

    return round(total_score, 2)


# FUNCTION 3: SEARCH FOR REQUIRED MATERIALS
def search_material():

    print("\n--- SEARCH FOR MATERIALS ---")

    project = input("Enter your project name: ")
    material = input("Enter required material: ").strip().title()

    while True:
        try:
            quantity = float(input("Enter required quantity: "))
            if quantity > 0:
                break
            print("Quantity must be positive.")
        except ValueError:
            print("Enter a valid number.")

    while True:
        condition = input(
            "Enter minimum required condition "
            "(Poor/Fair/Good/Excellent): "
        ).strip().lower()

        if condition in condition_rank:
            break
        print("Invalid condition.")

    location = input("Enter your project location: ")

    requirement = {
        "project": project,
        "material": material,
        "quantity": quantity,
        "condition": condition,
        "location": location
    }

    matches = []

    for supplier in available_materials:

        score = calculate_match(supplier, requirement)

        if score is not None:
            matches.append((score, supplier))

    matches.sort(key=lambda x: x[0], reverse=True)

    print("\n--- MATCHING RESULTS ---")

    if not matches:
        print("No suppliers found for this material.")
        return

    for score, supplier in matches:

        print("\n------------------------------")
        print("Supplier Project:", supplier["project"])
        print("Material:", supplier["material"])
        print("Available Quantity:", supplier["quantity"])
        print("Condition:", supplier["condition"])
        print("Location:", supplier["location"])
        print("Availability:", supplier["availability"])
        print("Matching Score:", score, "%")

        if supplier["quantity"] < quantity:
            print("Note: Available quantity is less than required.")

        if condition_rank[supplier["condition"]] < condition_rank[condition]:
            print("Note: Material condition is below the requested level.")

        if score >= 80:
            print("Compatibility: Highly Suitable")
        elif score >= 60:
            print("Compatibility: Moderately Suitable")
        else:
            print("Compatibility: Low")


# FUNCTION 4: VIEW ALL AVAILABLE MATERIALS
def view_materials():

    print("\n--- AVAILABLE MATERIALS ---")

    if not available_materials:
        print("No materials registered yet.")
        return

    for item in available_materials:
        print("\n------------------------------")
        for key, value in item.items():
            print(key.title(), ":", value)


# MAIN MENU
while True:

    print("\n===================================")
    print(" C&D MATERIAL RESOURCE EXCHANGE")
    print("===================================")

    print("1. Register surplus materials")
    print("2. Search for required materials")
    print("3. View available materials")
    print("4. Exit")

    option = input("\nEnter your choice: ")

    if option == "1":
        add_material()

    elif option == "2":
        search_material()

    elif option == "3":
        view_materials()

    elif option == "4":
        print("\nThank you for using the platform!")
        break

    else:
        print("Invalid choice. Please try again.")