# Import the core libraries and functions
from datetime import datetime
from numpy import nan as np_nan
from os import getcwd
from os.path import join as join_path
import pandas as pd
import re
import usaddress


# Set the base directory path as a GLOBAL value that all functions can access
BASE_PATH = join_path(getcwd(), "Files")


# Function to parse an address and associate the data to their columns
def parse_address(row):
    """
    Takes in a dataframe row and outputs the parsed address fields
    """

    # Get the target rows
    addr_array = row[["Address 1", "Address 2", "Address 3", "overflow"]].to_numpy()

    # Initialize the output string
    address_string = ""
    for value in addr_array:
        # Skip over any `nan` values
        if value is np_nan:
            continue

        # Build the address string
        address_string += f" {value}"

    # Parse the address to get the different fields
    address_fields = usaddress.parse(address_string)

    # Initialize the output values
    address_1 = []
    address_2 = []
    city = []
    state = []
    zipcode = []

    for field in address_fields:

        # Get Address 1 fields
        if field[1] in ["AddressNumber", "StreetName", "StreetNamePostType"]:
            address_1.append(field[0])

        # Get Address 2 fields
        elif field[1] in ["OccupancyType", "OccupancyIdentifier"]:
            address_2.append(field[0])

        # Get City fields
        elif field[1] in ["PlaceName"]:
            city.append(field[0])

        # Get State fields
        elif field[1] in ["StateName"]:
            state.append(field[0])

        elif field[1] in ["ZipCode"]:
            zipcode.append(field[0])

    return ", ".join([" ".join(address_1), " ".join(address_2), " ".join(city), " ".join(state), " ".join(zipcode)])

# Function to load and display a dataframe
def basic_dataframe_example():
    """
    Load and display a CSV file.
    """

    # Set the path to the basic CSV file
    file_path = join_path(BASE_PATH, "file_with_headers.csv")

    # Load the CSV into a dataframe
    df = pd.read_csv(file_path, sep=",")

    # Lets view the dataframe
    print(df)

    # View a specific column
    print(df["Name"])

    # Or specify specific colums you want to see
    print(df[["Name", "Money", "Is Robot"]])

    # What are the data-types
    print(df.dtypes)

    # Modify the column types to align with the data-types we need
    df = df.astype({
        "Name": "string",
    })

    # Check that "Name" is now the correct type
    print(df["Name"].dtypes)

    # Let's use a parser to determine the birthday
    df["Birthday"] = pd.to_datetime(df["Birthday"], format="%Y%m%d")

    # Check the updated birthday
    print(df)
    print(df["Birthday"].dtypes)

    # Create a new column using a map function on the dataframe
    df["Actual Age"] = round((datetime.utcnow() - df["Birthday"]).dt.days / 365.25, 0)
    df = df.astype({
        "Actual Age": "int",
    })
    print(df)

    # Change specific cell value -- index value, column name, over-write value
    df._set_value(1, "Is Robot", True)
    print(df)

    # Save the updated CSV file
    df.to_csv(join_path(BASE_PATH, "updated_file_with_headers.csv"), sep=",")


# Dataframe without headers
def missing_headers_in_csv():
    """
    Function that shows how to handle a CSV without headers.
    """

    # Load the CSV file into a dataframe
    file_path = join_path(BASE_PATH, "missing_headers.xls")
    print(file_path)

    # Try to load the dataframe, but it fails...
    # df = d.read_excel(file_path, header=None)
    # print(df)
    
    # Instead, let's both set the column headers and the expected number of columns
    df = pd.read_excel(file_path, header=None, names=[
        "Name", "Email", "Phone", "Address 1", "Address 2", "Address 3", "overflow"
    ])
    print(df)

    # Check the types
    print(df.dtypes)

    # Start with seperating the first, middle, and last names
    print(df["Name"].str.split(pat=None, n=-1))

    df["First Name"] = [
        # Output value
        x[0]
        # Logic check
        if len(x) > 1
        # If logic check fails, send this to output value
        else ""
        # Set the x value to evaluate (and if above check is true, send to output value)
        for x in df["Name"].str.split(pat=None, n=-1)
    ]
    df["Middle Name"] = [
        # Output value -- joins items in array as a singular string
        " ".join(x[1:len(x) - 1])
        if len(x) > 2
        else ""
        for x in df["Name"].str.split(pat=None, n=-1)
    ]
    df["Last Name"] = [x[-1] if len(x) > 0 else "" for x in df["Name"].str.split(pat=None, n=-1)]

    # Update the data types to be strings
    df = df.astype({
        "Name": "string",
        "First Name": "string",
        "Middle Name": "string",
        "Last Name": "string",
        "Email": "string",
    })

    # Check to see the results worked as intended
    print(df[["Name", "First Name", "Middle Name", "Last Name"]].dtypes)

    email_regex = "(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"

    # Validate emails, this one uses a lambda function
    # NOTE: Could also have used the if-else-for express as above for faster results
    df["Valid Email"] = df["Email"].apply(lambda x: bool(re.match(email_regex, str(x))))

    # Check if emails were valid
    print(df[["Email", "Valid Email"]])

    # Reduce the phone to just the integer values
    df["Phone"] = df["Phone"].apply(lambda x: "".join(re.findall(r'\d+', str(x))))

    df["Valid Phone #"] = df["Phone"].apply(lambda x: len(x) == 10)

    df["Phone"] = df["Phone"].apply(
        lambda x: f"({x[:3]}) {x[3:6]}-{x[6:]}"
        if len(x) == 10
        else x
    )

    print(df[["Phone", "Valid Phone #"]])

    df["Temp Address"] = df.apply(lambda row: parse_address(row), axis=1)
    
    print(df["Temp Address"])

    df["New Address 1"] = df["Temp Address"].apply(lambda x: x.split(",")[0].strip())
    df["New Address 2"] = df["Temp Address"].apply(lambda x: x.split(",")[1].strip())
    df["New City"] = df["Temp Address"].apply(lambda x: x.split(",")[2].strip())
    df["New State"] = df["Temp Address"].apply(lambda x: x.split(",")[3].strip())
    df["New Zipcode"] = df["Temp Address"].apply(lambda x: x.split(",")[4].strip())

    print(df[["New Address 1", "New Address 2", "New City", "New State", "New Zipcode"]])


    # df = df.loc[df["Valid Phone #"] & df["Valid Email"]], ["First Name", "Middle Name", "Last Name", "Email", "Phone", "New Address 1", "New Address 2", "New City", "New State", "New Zipcode"]

    df.rename(columns = {
        "New Address 1": "Address 1",
        "New Address 2": "Address 2",
        "New City": "City",
        "New State": "State",
        "New Zipcode": "Zipcode",
    })

    df[["First Name", "Middle Name", "Last Name", "Email", "Phone", "New Address 1", "New Address 2", "New City", "New State", "New Zipcode"]].to_excel("Address Output.xlsx", index=False)