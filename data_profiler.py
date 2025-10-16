import pandas as pd
import json

def profile_zendesk_data_lines(json_file_path):
    """
    Reads a large Zendesk JSON Lines file, analyzes it, and saves a report.
    """
    print(f"--- Streaming data from large JSON Lines file: '{json_file_path}' ---")
    
    # This list will hold each individual ticket (JSON object) we read.
    records = []
    
    try:
        # We open the file and read it line by line.
        with open(json_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # For each line, we load it as a separate JSON object.
                records.append(json.loads(line))

        # Once all lines are read, we create the DataFrame.
        df = pd.json_normalize(records)
        
        # --- The rest of the report generation is the same ---

        print("\n" + "="*50)
        print("DATA PROFILING REPORT")
        print("="*50)

        # 1. Basic Information
        print("\n--- 1. Basic Information ---")
        print(f"Total number of tickets found: {len(df)}")
        print(f"Total number of columns (fields) found: {len(df.columns)}")

        # 2. Column Names and Data Types
        print("\n--- 2. Column Names & Data Types ---")
        with pd.option_context('display.max_rows', None):
            df.info(verbose=True, show_counts=True)

        # 3. Missing Data Report
        print("\n--- 3. Missing Data Report ---")
        missing_values = df.isnull().sum()
        missing_values_filtered = missing_values[missing_values > 0].sort_values(ascending=False)
        if not missing_values_filtered.empty:
            print(missing_values_filtered)
        else:
            print("No missing data found.")

        # 4. Key Categorical Field Analysis
        print("\n--- 4. Analysis of Key Fields ---")
        key_columns = {'status': 'Status', 'via.channel': 'Channel', 'priority': 'Priority'}
        for col, title in key_columns.items():
            if col in df.columns:
                print(f"\n--- Top 5 Values for '{title}' ---")
                print(df[col].value_counts().head(5))
            else:
                print(f"\n--- Column '{col}' not found. Skipping analysis. ---")

        # 5. Date Range Analysis
        if 'created_at' in df.columns:
            print("\n--- 5. Date Range of Tickets ---")
            df['created_at'] = pd.to_datetime(df['created_at'])
            print(f"Earliest Ticket: {df['created_at'].min()}")
            print(f"Latest Ticket:   {df['created_at'].max()}")
        
        # 6. Saving the COMPLETE Organized Data
        output_csv_path = 'zendesk_data_organized_full.csv'
        print("\n" + "="*50)
        print(f"Saving the complete organized dataset to '{output_csv_path}'...")
        df.to_csv(output_csv_path, index=False)
        print(f"✅ SUCCESS: The full dataset with {len(df)} rows has been saved.")
        print("="*50)

    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"\n--- JSON DECODE ERROR ---")
        print(f"The script failed to parse a line in your JSON file. This can happen if a line is corrupted.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    ZENDESK_JSON_FILE = "your_data_file.json" 
    profile_zendesk_data_lines(ZENDESK_JSON_FILE)
