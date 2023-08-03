#!/usr/bin/env python3
import os
import csv
import argparse
import sys
import pandas as pd

def parse_args(args=None):
    """
    Parse command-line arguments.
    """
    Description = ("Split TSV file into four columns.")
    Epilog = "Example usage: python3 filter_contigs.py -i <INPUT> -l <MIN_LENGTH> -c <MIN_COVERAGE>"

    parser = argparse.ArgumentParser(description='Split TSV file into four columns', epilog=Epilog)
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        dest="INPUT",
        help="input TSV file"
    )
    parser.add_argument(
        "-l",
        "--min_length",
        type=int,
        dest="MIN_LENGTH",
        default=100,
        help='minimum length for filtering'
    )
    parser.add_argument(
        "-c",
        "--min_coverage",
        type=float,
        dest="MIN_COVERAGE",
        default=1000,
        help='minimum coverage for filtering'
    )
    return parser.parse_args(args)

def sample_name(input_file):
    """
    Get sample name from input file.
    """
    file_name = os.path.basename(input_file)  # Get the base name of the file
    file_name_without_ext = os.path.splitext(file_name)[0]  # Remove the file extension
    sample_name = file_name_without_ext.replace('.contigs', '')  # Remove the ".contigs" suffix

    return sample_name

def split_tsv_file(input_file, sample_name):
    """
    Split the TSV file into four columns: sample, contig, length, coverage, and sequence.
    Save the split DataFrame to the output file.
    """
    # Read the TSV file into a pandas DataFrame
    df = pd.read_csv(input_file, delimiter='\t', header=None)
        
    # Split the first column into contig, length, and coverage
    split_values = df[0].str.split('_length_|_cov_', expand=True)
    df['sample'] = sample_name
    df['contig'] = split_values[0]
    df['length'] = split_values[1].str.extract('(\d+)')  # Extract numeric value after 'length_'
    df['coverage'] = split_values[2].str.extract('(\d+\.?\d*)')  # Extract numeric value after 'cov_'
    df['sequence'] = df[1]

    # Drop the unnecessary columns
    split_tsv = df[['sample', 'contig', 'length', 'coverage', 'sequence']]

    # Save the split DataFrame to the output file
    split_tsv.to_csv(f"{sample_name}_raw.tsv", sep='\t', index=False)

    print(f"The TSV file has been split into four columns and saved to {sample_name}_raw.tsv.")

    return split_tsv


def filter_tsv_file(split_tsv, sample_name, min_length, min_coverage):
    """
    Filter the split TSV file based on the minimum length and coverage thresholds.
    Save the filtered DataFrame to the output file.
    """
    # Create a DataFrame from the split TSV
    df = pd.DataFrame(split_tsv, columns=['sample', 'contig', 'length', 'coverage', 'sequence'])

    # Convert length and coverage columns to numeric types
    df['length'] = pd.to_numeric(df['length'], errors='coerce')
    df['coverage'] = pd.to_numeric(df['coverage'], errors='coerce')

    # Filter rows based on length and coverage thresholds
    filtered_rows = df[(df['length'] >= min_length) & (df['coverage'] >= min_coverage)]

    # Save the filtered DataFrame to the output file
    filtered_rows.to_csv(f"{sample_name}_filtered.tsv", sep='\t', index=False)

    print(f"The TSV file has been filtered and saved to {sample_name}_filtered.tsv.")

    return filtered_rows


def output_highest_coverage(filtered_rows, sample_name):
    """
    Get the row with the highest coverage from the filtered DataFrame.
    Save the row to the output file.
    """
    # Create a DataFrame from the filtered rows
    df = pd.DataFrame(filtered_rows, columns=['sample', 'contig', 'length', 'coverage', 'sequence'])

    # Convert the 'coverage' column to numeric type
    df['coverage'] = pd.to_numeric(df['coverage'])

    # Sort the DataFrame based on coverage in descending order
    sorted_df = df.sort_values('coverage', ascending=False)

    # Get the row with the highest coverage
    highest_coverage_row = sorted_df.iloc[0]

    # Write the header row and the row with the highest coverage to the output file
    with open(f"{sample_name}_highest_coverage.tsv", 'w', newline='') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(['sample', 'contig', 'length', 'coverage', 'sequence'])
        tsv_writer.writerow(highest_coverage_row)

    print(f"The row with the highest coverage has been saved to {sample_name}_highest_coverage.tsv.")


def main(args=None):
    """
    Main entry point of the script.
    """
    args = parse_args(args)
    sample = sample_name(input_file=args.INPUT)
    split_tsv = split_tsv_file(input_file=args.INPUT, sample_name=sample)
    filtered_rows = filter_tsv_file(split_tsv=split_tsv, sample_name=sample, min_length=args.MIN_LENGTH, min_coverage=args.MIN_COVERAGE)
    output_highest_coverage(filtered_rows=filtered_rows, sample_name=sample)


if __name__ == "__main__":
    sys.exit(main())
