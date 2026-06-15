"""
To insert data from an Excel (.xlsx) file into a PostgreSQL table using queries,
there's one important limitation:
    "PostgreSQL cannot directly read .xlsx files using SQL Qurey alone."

So we have to Convert Excel (.xlsx) file into CSV file (Excel → CSV) Using Python
and also Convert JSON file into CSV file (Json → CSV).
"""

import pandas as pd

# Files paths
excel_files = [
    ("./Data/Raw_data/AS2/","returns"),
    ("./Data/Raw_data/HRM/","campaigns"),
    ("./Data/Raw_data/HRM/","employees"),
    ("./Data/Raw_data/SCI/","inventory")    
    ]

json_files = [
    ("./Data/Raw_data/AS2/","service_centers"),
    ("./Data/Raw_data/HRM/","products"),
    ("./Data/Raw_data/SCI/","warehouses") 
]

for path , name  in excel_files:
    df = pd.read_excel(f"{path}{name}.xlsx") # Read Excel file
    
    df.to_csv(f"{path}{name}.csv", index=False) # Convert & Save as CSV
    
    print(f"Done converting {name}.xlsx to {name}.csv")


for path , name  in json_files:
    df = pd.read_json(f"{path}{name}.json") # Read Json file
    
    df.to_csv(f"{path}{name}.csv", index=False) # Convert & Save as CSV
    
    print(f"Done converting {name}.json to {name}.csv")

print("Conversion completed successfully!")
