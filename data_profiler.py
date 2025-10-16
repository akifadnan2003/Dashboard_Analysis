import pandas as pd
import json

def profile_nested_zendesk_data(json_file_path):
    """
    Reads a complex, nested Zendesk JSON file, intelligently finds the list of tickets,
    analyzes its structure, and saves a complete report.
    """
    print(f"--- Loading complex JSON from '{json_file_path}' ---")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tickets_list = None
        
        # --- THIS IS THE NEW INTELLIGENT LOGIC ---
        if isinstance(data, list):
            # The file is just a simple list of tickets.
            tickets_list = data
        elif isinstance(data, dict):
            # The file is a dictionary. We need to find the list of tickets inside it.
            print(f"Found top-level keys in the JSON object: {list(data.keys())}")
            
            # Common key names for ticket lists in Zendesk exports
            possible_keys = ['results', 'tickets', 'exports', 'audits']
            
            # First, check for common key names
            for key in possible_keys:
                if key in data and isinstance(data[key], list):
                    print(f"Found list of tickets under the common key: '{key}'")
                    tickets_list = data[key]
                    break
            
            # If no common key is found, search for the first available list
            if tickets_list is None:
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"Found a list under the key: '{key}'. Assuming this is the ticket data.")
                        tickets_list = value
                        break
        
        if tickets_list is None:
            print("\n--- ERROR ---")
            print("Could not automatically find a list of tickets within the JSON file.")
            print("Please inspect the top-level keys printed above and adjust the script if needed.")
            return
        
        # Once the list is found, the rest of the process is the same.
        df = pd.json_normalize(tickets_list)
        
        # --- The rest of the report generation remains the same ---
        print("\n" + "="*50)
        print("DATA PROFILING REPORT")
        print("="*50)
        print("\n--- 1. Basic Information ---")
        print(f"Total number of tickets found: {len(df)}")
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
    profile_nested_zendesk_data(ZENDESK_JSON_FILE)
