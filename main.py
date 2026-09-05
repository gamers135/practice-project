import json
import uuid
import os


DATA_FILE = "data/reports.json"


# ==========================================
# DATA HANDLING
# ==========================================

def load_data():

    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)

        data = {
            "lost": [],
            "found": []
        }

        save_data(data)

        return data

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)

    except json.JSONDecodeError:

        data = {
            "lost": [],
            "found": []
        }

        save_data(data)

        return data


def save_data(data):

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# ==========================================
# REPORT ID
# ==========================================

def generate_id(prefix):

    return prefix + "-" + str(uuid.uuid4())[:6].upper()


# ==========================================
# DESCRIPTION SIMILARITY
# ==========================================

def description_similarity(description1, description2):

    words1 = set(description1.lower().split())
    words2 = set(description2.lower().split())

    if not words1 or not words2:
        return 0

    common_words = words1.intersection(words2)

    return len(common_words) / len(words1.union(words2))


# ==========================================
# MATCHING ENGINE
# ==========================================

def calculate_match(lost, found):

    score = 0

    # Item name
    if lost["item"].lower() == found["item"].lower():
        score += 40

    # Location
    if lost["location"].lower() == found["location"].lower():
        score += 30

    # Description
    similarity = description_similarity(
        lost["description"],
        found["description"]
    )

    score += similarity * 30

    return round(score)


# ==========================================
# REPORT LOST ITEM
# ==========================================

def report_lost(data):

    print("\n========== REPORT LOST ITEM ==========")

    name = input("Your name: ")
    contact = input("Contact number/email: ")
    item = input("Item name: ")
    description = input("Item description: ")
    location = input("Where was it lost? ")
    date_time = input("When was it lost? ")

    print("\n🔐 Private verification detail")
    print("Example: unique scratch, sticker, mark, wallpaper, etc.")

    verification = input("Private verification detail: ")

    report = {

        "id": generate_id("LF"),

        "name": name,

        "contact": contact,

        "item": item,

        "description": description,

        "location": location,

        "date_time": date_time,

        "verification": verification,

        "status": "ACTIVE"
    }

    data["lost"].append(report)

    save_data(data)

    print("\n✅ Lost item reported successfully!")

    print("Report ID:", report["id"])


# ==========================================
# REPORT FOUND ITEM
# ==========================================

def report_found(data):

    print("\n========== REPORT FOUND ITEM ==========")

    name = input("Your name: ")
    contact = input("Contact number/email: ")
    item = input("Item name: ")
    description = input("Item description: ")
    location = input("Where was it found? ")
    date_time = input("When was it found? ")

    report = {

        "id": generate_id("FF"),

        "name": name,

        "contact": contact,

        "item": item,

        "description": description,

        "location": location,

        "date_time": date_time,

        "status": "ACTIVE"
    }

    data["found"].append(report)

    save_data(data)

    print("\n✅ Found item reported successfully!")

    print("Report ID:", report["id"])


# ==========================================
# VIEW REPORTS
# ==========================================

def view_reports(data):

    print("\n========== LOST ITEMS ==========")

    if not data["lost"]:

        print("No lost items.")

    else:

        for report in data["lost"]:

            print("\nID:", report["id"])
            print("Item:", report["item"])
            print("Description:", report["description"])
            print("Location:", report["location"])
            print("Date/Time:", report["date_time"])
            print("Status:", report["status"])


    print("\n========== FOUND ITEMS ==========")

    if not data["found"]:

        print("No found items.")

    else:

        for report in data["found"]:

            print("\nID:", report["id"])
            print("Item:", report["item"])
            print("Description:", report["description"])
            print("Location:", report["location"])
            print("Date/Time:", report["date_time"])
            print("Status:", report["status"])


# ==========================================
# FIND MATCHES
# ==========================================

def find_matches(data):

    print("\n========== MATCHING ENGINE ==========")

    matches = []

    for lost in data["lost"]:

        if lost["status"] != "ACTIVE":
            continue

        for found in data["found"]:

            if found["status"] != "ACTIVE":
                continue

            score = calculate_match(lost, found)

            if score >= 50:

                matches.append(
                    (score, lost, found)
                )


    if not matches:

        print("\n❌ No possible matches found.")

        return


    matches.sort(
        key=lambda x: x[0],
        reverse=True
    )


    for score, lost, found in matches:

        print("\n--------------------------------")

        print("🎯 POSSIBLE MATCH")

        print("\nLost Report:", lost["id"])
        print("Item:", lost["item"])
        print("Location:", lost["location"])

        print("\nFound Report:", found["id"])
        print("Item:", found["item"])
        print("Location:", found["location"])

        print("\nMatch Score:", score, "/ 100")

        if score >= 80:

            print("🟢 STRONG MATCH")

        else:

            print("🟡 POSSIBLE MATCH")


# ==========================================
# VERIFY OWNER
# ==========================================

def verify_owner(data):

    print("\n========== OWNER VERIFICATION ==========")

    active_lost = [
        r for r in data["lost"]
        if r["status"] == "ACTIVE"
    ]

    active_found = [
        r for r in data["found"]
        if r["status"] == "ACTIVE"
    ]

    if not active_lost or not active_found:

        print("\nNo active reports available.")

        return


    print("\nLost Reports:")

    for report in active_lost:

        print(
            report["id"],
            "-",
            report["item"],
            "-",
            report["location"]
        )


    lost_id = input(
        "\nEnter lost report ID: "
    ).upper()


    lost = next(
        (
            r for r in active_lost
            if r["id"] == lost_id
        ),
        None
    )


    if lost is None:

        print("\n❌ Lost report not found.")

        return


    print("\nFound Reports:")

    for report in active_found:

        print(
            report["id"],
            "-",
            report["item"],
            "-",
            report["location"]
        )


    found_id = input(
        "\nEnter found report ID: "
    ).upper()


    found = next(
        (
            r for r in active_found
            if r["id"] == found_id
        ),
        None
    )


    if found is None:

        print("\n❌ Found report not found.")

        return


    score = calculate_match(
        lost,
        found
    )


    print("\nMatch Score:", score, "/ 100")


    if score < 50:

        print(
            "\n❌ These reports do not appear to match."
        )

        return


    print("\n🔐 OWNER VERIFICATION")

    verification = input(
        "Enter your private verification detail: "
    )


    if (
        verification.strip().lower()
        ==
        lost["verification"].strip().lower()
    ):

        print("\n✅ OWNERSHIP VERIFIED!")

        print(
            "University confirmation is required "
            "before returning the item."
        )

        # Update statuses
        lost["status"] = "VERIFIED"
        found["status"] = "MATCHED"

        save_data(data)


    else:

        print("\n❌ VERIFICATION FAILED!")

        print(
            "The verification detail does not match."
        )


# ==========================================
# MAIN MENU
# ==========================================

def main():

    data = load_data()

    while True:

        print("\n")
        print("======================================")
        print("     UNIVERSITY LOST & FOUND")
        print("======================================")

        print("1. Report Lost Item")
        print("2. Report Found Item")
        print("3. View Reports")
        print("4. Find Matches")
        print("5. Verify Ownership")
        print("6. Exit")

        choice = input(
            "\nEnter your choice: "
        )


        if choice == "1":

            report_lost(data)


        elif choice == "2":

            report_found(data)


        elif choice == "3":

            view_reports(data)


        elif choice == "4":

            find_matches(data)


        elif choice == "5":

            verify_owner(data)


        elif choice == "6":

            print(
                "\nThank you for using "
                "University Lost & Found! 👋"
            )

            break


        else:

            print(
                "\n❌ Invalid choice."
            )


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":

    main()
