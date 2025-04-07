# File: to_spss_data.py
import pandas as pd
import os
import numpy as np
from tqdm import tqdm

def one_hot_encode_csv(file_path, columns_to_encode, output_path=None, chunksize=10000, progress_callback=None):
    """
    One-hot encodes specified columns in a CSV file, processing the file in chunks
    to handle large datasets efficiently.
    
    Args:
        file_path (str): Path to the CSV file to process
        columns_to_encode (list): List of column names to one-hot encode
        output_path (str, optional): Path where the processed CSV will be saved.
                                     If None, uses original filename with '_encoded' suffix.
        chunksize (int, optional): Number of rows to process at once. Default is 10000.
        progress_callback (function, optional): Function to call with progress updates (0-100)
    
    Returns:
        str: Path to the output file
    """
    if output_path is None:
        # Create default output path by adding '_encoded' before the extension
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_encoded{ext}"
    
    # First pass: discover unique values for each column to encode
    print(f"Scanning for unique values in {len(columns_to_encode)} columns...")
    unique_values = {col: set() for col in columns_to_encode}
    
    # Get total number of chunks for progress tracking
    total_chunks = sum(1 for _ in pd.read_csv(file_path, chunksize=chunksize))
    chunks_processed = 0
    
    # Read the file in chunks to identify all possible values
    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        for col in columns_to_encode:
            if col in chunk.columns:
                # Add unique values to our set, ignoring NaN values
                unique_values[col].update(chunk[col].dropna().unique())
        
        chunks_processed += 1
        if progress_callback:
            # First pass is 50% of total progress
            progress = int((chunks_processed / total_chunks) * 50)
            progress_callback(progress)
    
    # Convert sets to sorted lists for consistent column ordering
    for col in unique_values:
        unique_values[col] = sorted([str(val) for val in unique_values[col]])
        print(f"Column '{col}' has {len(unique_values[col])} unique values")
    
    # Create a mapping from column names to new one-hot column names
    column_mapping = {}
    for col in columns_to_encode:
        column_mapping[col] = [f"{col}_{val}" for val in unique_values[col]]
    
    # Second pass: create and write the encoded data
    print(f"Processing data and writing to {output_path}...")
    
    # Process the first chunk to get column headers
    chunks = pd.read_csv(file_path, chunksize=chunksize)
    first_chunk = next(chunks)
    
    # Create list of columns that will be in the final dataframe
    remaining_columns = [col for col in first_chunk.columns if col not in columns_to_encode]
    all_new_columns = []
    for col in columns_to_encode:
        all_new_columns.extend(column_mapping[col])
    
    # Write header to the output file
    with open(output_path, 'w') as f:
        header = ','.join(remaining_columns + all_new_columns)
        f.write(header + '\n')
    
    # Process first chunk
    _process_chunk(first_chunk, unique_values, column_mapping, columns_to_encode, 
                  remaining_columns, output_path, mode='a')
    
    chunks_processed = 1
    total_chunks_second_pass = total_chunks - 1  # Already processed the first chunk
    
    # Process remaining chunks
    for chunk in chunks:
        _process_chunk(chunk, unique_values, column_mapping, columns_to_encode, 
                      remaining_columns, output_path, mode='a')
        
        chunks_processed += 1
        if progress_callback:
            # Second pass is remaining 50% of progress
            progress = 50 + int((chunks_processed / total_chunks) * 50)
            progress_callback(min(progress, 100))  # Ensure we don't exceed 100%
    
    print(f"One-hot encoding complete. Output saved to {output_path}")
    return output_path

def _process_chunk(chunk, unique_values, column_mapping, columns_to_encode, 
                  remaining_columns, output_path, mode='a'):
    """
    Process a single chunk of data, performing one-hot encoding and writing to output file.
    
    Args:
        chunk (DataFrame): The chunk of data to process
        unique_values (dict): Dictionary of unique values for each column
        column_mapping (dict): Dictionary mapping original columns to one-hot columns
        columns_to_encode (list): List of columns to encode
        remaining_columns (list): List of columns to keep unchanged
        output_path (str): Path to output file
        mode (str): File open mode ('w' for first chunk, 'a' for subsequent chunks)
    """
    # Create a new dataframe with non-encoded columns
    result_df = chunk[remaining_columns].copy()
    
    # Process each column to encode
    for col in columns_to_encode:
        if col in chunk.columns:
            # Create one-hot columns for this feature
            for val in unique_values[col]:
                # Create a new column with 1 where the value matches, 0 otherwise
                result_df[f"{col}_{val}"] = (chunk[col].astype(str) == val).astype(int)
    
    # Write to file without header (header was written separately)
    result_df.to_csv(output_path, mode=mode, header=False, index=False)