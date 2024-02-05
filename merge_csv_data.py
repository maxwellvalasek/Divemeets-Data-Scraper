import os
import pandas as pd

directory = 'diver_csvs'

output_directory = 'merged_data'

csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

combined_data = pd.concat([pd.read_csv(os.path.join(directory, file)) for file in csv_files])

combined_data.to_csv(os.path.join(output_directory, 'divers_combined.csv'), index=False)