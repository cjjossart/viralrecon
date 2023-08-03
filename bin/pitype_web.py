#!/usr/bin/env python3
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import sys

def parse_args(args=None):
    """
    Parse command-line arguments.
    """
    Description = ("Query Pitype with the amplified sequence of enterovirus VP1 region to get the enterovirus genotype.")
    Epilog = "Example usage: python3 pitype_web.py -q <QUERY> -s <SAMPLE_NAME> -c <CONTIG>"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        dest="QUERY",
        help="Enterovirus VP1 regions sequence."
    )
    parser.add_argument(
        "-s",
        "--sample_name",
        type=str,
        dest="SAMPLE_NAME",
        help="Sample Name."
    )
    parser.add_argument(
        "-c",
        "--contig",
        type=str,
        dest="CONTIG",
        help="Name or ID# of contig sequence."
    )
    return parser.parse_args(args)

def pitype(query):
    """
    Query PiType.cdc.gov with sequence to get enterovirus genotype data.
    """
    # Start Display before starting chrome
    display = Display(visible=0, size=(800, 800))
    display.start()

    # Configure as headless
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=options)

    # Open the website
    driver.get("https://pitype.cdc.gov/")

    # Find the input element and enter the query
    wait = WebDriverWait(driver, 5)
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//textarea')))
    search_box.send_keys(query)

    # Submit the form by clicking the button
    type_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button/b')))
    type_button.click()

    # Wait for the page to load
    time.sleep(5)

    # Extract the page source
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find the table element
    table = soup.find("table")

    # Extract the table rows
    data = []
    for tr in table.find_all("tr"):
        row = [td.text.strip() for td in tr.find_all("td")]
        if row:
            row = [value for value in row[0:] if not value.startswith("Query_1")]
            data.append(row)

    return data


def pitype_table(pitype_output, sample_name, contig):
    """
    Create a Pandas DataFrame from the PiType output and save it as a CSV file.
    """
    # Define column names
    column_names = ["genotype_nt", "accession_nt", "percent_identity_nt", "mismatch_nt",
                    "length_(query/alignment)", "genotyp_aa", "accession_aa", "percent_identity_aa", "mismatch_aa"]
    
    # Create DataFrame
    df = pd.DataFrame(pitype_output, columns=column_names)
    
    # Split the 'length_(query/alignment)' column and assign values to 'length' and 'alignment_length' columns
    df[['length', 'alignment_length']] = df['length_(query/alignment)'].str.split('/').apply(lambda x: pd.Series([int(x[0]), int(x[1])]))
    
    # Add sample name and contig name values to the respective columns
    df.insert(0, 'sample', sample_name)
    df.insert(1, 'contig', contig)
    
    # Save DataFrame as CSV
    #df.to_csv(f"{sample_name}_{contig}_raw_pitype.csv", index=False)
    
    return df


def filter_identity(raw_dataframe, sample_name, contig):
    """
    Filter the DataFrame based on the given criteria and save the filtered DataFrame as a CSV file.
    """
    # Define criteria
    criteria = {
        'CV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-B': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-C': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-D': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-B': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-C': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-D': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'E-': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'PeV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'RV-A': {'percent_identity_nt': 88},
        'RV-B': {'percent_identity_nt': 87},
        'RV-C': {'percent_identity_nt': 88}
    }

    # Filter rows based on criteria
    filtered_rows = []
    pass_nt_rows = []

    for row in raw_dataframe.itertuples(index=False):
        virus = row.genotype_nt
        alignment_length = row.alignment_length
        for key, crit in criteria.items():
            if virus.startswith(key) and all(float(getattr(row, column)) >= value for column, value in crit.items()) and alignment_length >= 100:
                filtered_rows.append(row)
                break
    
    for row in raw_dataframe.itertuples(index=False):
        virus = row.genotype_nt
        alignment_length = row.alignment_length
        pi_nt = row.percent_identity_nt
        for key, crit in criteria.items():
            if virus.startswith(key) and float(pi_nt) >= crit.get('percent_identity_nt', 0) and alignment_length >= 100:
                pass_nt_rows.append(row)
                break

    # Create a new DataFrame with filtered rows
    filtered_df = pd.DataFrame(filtered_rows)
    pass_nt_df = pd.DataFrame(pass_nt_rows)

    # Save the filtered DataFrames as CSV
    filtered_df.to_csv(f"{sample_name}_{contig}_filtered_pitype.csv", index=False)
    pass_nt_df.to_csv(f"{sample_name}_{contig}_pass_nt_pitype.csv", index=False)


def pitype_pass(raw_dataframe, sample_name, contig):
    """
    Filter the DataFrame based on the given criteria and save the filtered DataFrame as a CSV file.
    """
    # Define criteria
    criteria = {
        'CV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-B': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-C': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'CV-D': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-B': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-C': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'EV-D': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'E-': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'PeV-A': {'percent_identity_nt': 75, 'percent_identity_aa': 88},
        'RV-A': {'percent_identity_nt': 88},
        'RV-B': {'percent_identity_nt': 87},
        'RV-C': {'percent_identity_nt': 88}
    }

    # Add 'pitype_pass' column to raw DataFrame
    raw_dataframe['pitype_pass'] = ''

    for row in raw_dataframe.itertuples(index=False):
        virus = row.genotype_nt
        alignment_length = row.alignment_length
        pi_nt = row.percent_identity_nt
        for key, crit in criteria.items():
            if virus.startswith(key) and float(pi_nt) >= crit.get('percent_identity_nt', 0) and alignment_length >= 100:
                raw_dataframe['pitype_pass'] = 'pass'
                break
            else:
                raw_dataframe['pitype_pass'] = 'fail'

    # Save the raw DataFrame with the 'pitype_pass' column as CSV
    raw_dataframe.to_csv(f"{sample_name}_{contig}_raw_pitype.csv", index=False)

    # Create a new DataFrame with only the first row and header
    header_row = raw_dataframe.head(1)

    # Save the header row as CSV
    header_row.to_csv(f"{sample_name}_{contig}_ref_pitype.csv", index=False)

def main(args=None):
    """
    Main entry point of the script.
    """
    args = parse_args(args)
    pitype_output = pitype(query=args.QUERY)
    raw_dataframe = pitype_table(pitype_output, sample_name=args.SAMPLE_NAME, contig=args.CONTIG)
    filter_identity(raw_dataframe, sample_name=args.SAMPLE_NAME, contig=args.CONTIG)
    pitype_pass(raw_dataframe, sample_name=args.SAMPLE_NAME, contig=args.CONTIG)

if __name__ == "__main__":
    sys.exit(main())
