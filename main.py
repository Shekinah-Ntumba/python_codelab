import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import json
from __future__ import print_function
import os
import pickle
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

file_path = 'Test_Files.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')
print(df.head())


def generate_email(name):
    try:
        # Split the name assuming the format 'Last, First Middle'
        parts = name.split(', ')
        if len(parts) != 2:
            return None  # Handle unexpected formats

        first_name_lastname = parts[1].split(' ')
        first_name = first_name_lastname[0]
        last_name = first_name_lastname[-1]

        # Create email address
        email = f"{first_name[0].lower()}{last_name.lower()}@gmail.com"
        return email
    except Exception as e:
        print(f"Error generating email for {name}: {e}")
        return None


# Load the Excel file
input_file = 'Test_Files.xlsx'  # Change this to your input file
df = pd.read_excel(input_file, engine='openpyxl')

# Check the structure of the data
print(df.head())

# Apply the email generation function
df['Email Address'] = df['Student Name'].apply(generate_email)

# Save the results to a new Excel file
output_file = 'students_with_emails.xlsx'  # Change this to your desired output file
df.to_excel(output_file, index=False)

print(f"Email addresses have been generated and saved to {output_file}.")
# Save to CSV
csv_file_path = 'students.csv'
df.to_csv(csv_file_path, index=False)

# Save to TSV
tsv_file_path = 'students.tsv'
df.to_csv(tsv_file_path, sep='\t', index=False)

print(f"Files saved as {csv_file_path} and {tsv_file_path}.")
male_students = df[df['Gender'] == 'M']
female_students = df[df['Gender'] == 'F']

# Log the number of students
print(f"Number of Male Students: {len(male_students)}")
print(f"Number of Female Students: {len(female_students)}")

# Optionally, save these lists to separate files
male_students.to_csv('male_students.csv', index=False)
female_students.to_csv('female_students.csv', index=False)

#This is my part#



# Step 1: Load data from Excel
# Replace 'names.xlsx' with the actual file path to your Excel file
# Assume Excel has one sheet named 'Names' with a column 'Gender' for male and female designations
df = pd.read_excel('Test_Files.xlsx', sheet_name='Sheet1')

# Add gender column based on existing 'Gender' column
df['gender'] = df['Gender'].map({'M': 'm', 'F': 'f'})

# Step 2: Shuffle the names
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Step 3: Generate additional fields
np.random.seed(42)
df['student_number'] = np.random.randint(100000, 999999, size=len(df))
df['dob'] = pd.to_datetime(np.random.choice(pd.date_range("1990-01-01", "2005-12-31"), size=len(df))).strftime('%Y-%m-%d')
df['special_character'] = np.random.choice(["['yes']", "['no']"], size=len(df))
df['name_similar'] = np.random.choice(["['yes']", "['no']"], size=len(df))

# Step 4: Create JSON format
json_data = []
for idx, row in df.iterrows():
    json_data.append({
        "id": str(idx),
        "student_number": str(row['student_number']),
        "additional_details": [
            {
                "dob": row['dob'],
                "gender": row['gender'],
                "special_character": row['special_character'],
                "name_similar": row['name_similar']
            }
        ]
    })

# Step 5: Save as a JSON file
with open('shuffled_names.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Step 6: Save as a JSONL file
with open('shuffled_names.jsonl', 'w') as jsonl_file:
    for entry in json_data:
        jsonl_file.write(json.dumps(entry) + '\n')

print("Files saved as 'shuffled_names.json' and 'shuffled_names.jsonl'.")



#google api
# If modifying the file scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Path to your service account key file

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def upload_file(file_path, mime_type):
    service = authenticate_google_drive()
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

# Upload files
files_to_upload = [
    ('shuffled_names.json', 'pythonCodelab/json'),
    ('shuffled_names.jsonl', 'pythonCodelab/jsonl'),
    ('female_students.csv', 'pythonCodelab/csv'),
    ('main.py', 'pythonCodelab/py'),
    ('male_students.csv', 'pythonCodelab/csv'),
    ('name_similarities.json', 'pythonCodelab/json'),
    ('students.csv', 'pythonCodelab/csv'),
    ('students.tsv', 'pythonCodelab/tsv'),
    ('students_with_emails.xlsx', 'pythonCodelab/xlsx'),
    ('Test_Files.xlsx', 'pythonCodelab/xlsx'),
]

for file_path, mime_type in files_to_upload:
    upload_file(file_path, mime_type)