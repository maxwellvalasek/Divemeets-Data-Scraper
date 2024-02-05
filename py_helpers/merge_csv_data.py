import os
import pandas as pd

# Directory containing the CSV files
directory = 'csv'

# Output directory for the combined CSV file
output_directory = 'directory'

# Get a list of all CSV files in the directory
csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

# Combine all CSV files into one DataFrame
combined_data = pd.concat([pd.read_csv(os.path.join(directory, file)) for file in csv_files])

# Save the combined CSV file to the output directory
combined_data.to_csv(os.path.join(output_directory, 'combined.csv'), index=False)