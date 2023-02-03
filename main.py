# Import the core libraries and functions
from Dataframes.working_with_dataframes import (
    basic_dataframe_example,
    missing_headers_in_csv
)


# Main entry-point function to the python scripts for this project
def main():
    """
    Preferred method of setting a main entry point into the code.
    """
    print("Hello World!")
    # basic_dataframe_example()
    missing_headers_in_csv()


if __name__ == "__main__":
    main()