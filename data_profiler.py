import pandas as pd
import json

def profile_robust_zendesk_data(json_file_path):
    """
    Reads a large Zendesk JSON file line-by-line, skipping any corrupted
    or non-JSON lines, analyzes it, and saves a report.
    """
    print(f"--- Robustly streaming data from large file: '{json_file_path}' ---")
    
    records = []
    invalid_line_count = 0
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # --- THIS IS THE KEY CHANGE ---
                try:
                    # Attempt to load the line as a JSON object
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    # If it fails, increment the counter and skip the line
                    invalid_line_count += 1
                    # Optional: uncomment the line below to see which lines are failing
                    # print(f"Warning: Skipping invalid JSON on line {i+1}")
                    continue
        
        if not records:
            print("Error: No valid JSON records were found in the file.")
            return

        df = pd.json_normalize(records)
        
        print("\n" + "="*50)
        print("DATA PROFILING REPORT")
        print("="*50)
        if invalid_line_count > 0:
            print(f"NOTE: Skipped {invalid_line_count} invalid or non-JSON lines.")

        # --- The rest of the report generation is the same ---
        print("\n--- 1. Basic Information ---")
        print(f"Total number of valid tickets found: {len(df)}")
        # (The rest of the reporting code remains the same...)
        print(f"Total number of columns (fields) found: {len(df.columns)}")
        print("\n--- 2. Column Names & Data Types ---")
        with pd.option_context('display.max_rows', None):
            df.info(verbose=True, show_counts=True)
        print("\n--- 3. Missing Data Report ---")
        missing_values = df.isnull().sum()
        missing_values_filtered = missing_values[missing_values > 0].sort_values(ascending=False)
        if not missing_values_filtered.empty:
            print(missing_values_filtered)
        else:
            print("No missing data found.")
        print("\n--- 4. Analysis of Key Fields ---")
        key_columns = {'status': 'Status', 'via.channel': 'Channel', 'priority': 'Priority'}
        for col, title in key_columns.items():
            if col in df.columns:
                print(f"\n--- Top 5 Values for '{title}' ---")
                print(df[col].value_counts().head(5))
            else:
                print(f"\n--- Column '{col}' not found. Skipping analysis. ---")
        if 'created_at' in df.columns:
            print("\n--- 5. Date Range of Tickets ---")
            df['created_at'] = pd.to_datetime(df['created_at'])
            print(f"Earliest Ticket: {df['created_at'].min()}")
            print(f"Latest Ticket:   {df['created_at'].max()}")
        
        output_csv_path = 'zendesk_data_organized_full.csv'
        print("\n" + "="*50)
        print(f"Saving the complete organized dataset to '{output_csv_path}'...")
        df.to_csv(output_csv_path, index=False)
        print(f"✅ SUCCESS: The full dataset with {len(df)} rows has been saved.")
        print("="*50)

    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    ZENDESK_JSON_FILE = "your_data_file.json" 
    profile_robust_zendesk_data(ZENDESK_JSON_FILE)
