import requests
import pdfplumber
import psycopg2

# Step 1: Download the PDF
url = "https://portal.ct.gov/-/media/dph/cyshcn/ct-collaborative-autism-services-resource-directory.pdf"
response = requests.get(url)
with open("resource_directory.pdf", "wb") as file:
    file.write(response.content)

# Step 2: Extract Data
def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data.extend(page.extract_text().split('\n'))
    return text_data

pdf_text_lines = extract_text_from_pdf("resource_directory.pdf")

# Step 3: Parse Data
def parse_text(lines):
    parsed_data = []
    entry = {}
    for line in lines:
        if line.strip() == '':  # Assuming a blank line indicates a new entry
            if entry:
                parsed_data.append(entry)
                entry = {}
        else:
            if "Organization:" in line:
                if entry:  # Save the previous entry if it exists
                    parsed_data.append(entry)
                entry = {"organization": line.replace("Organization:", "").strip()}
            elif "Contact:" in line:
                entry["contact_info"] = line.replace("Contact:", "").strip()
            elif "Services:" in line:
                entry["services"] = line.replace("Services:", "").strip()
            else:
                # Handle additional lines or append to existing entry fields
                if "additional_info" in entry:
                    entry["additional_info"] += " " + line.strip()
                else:
                    entry["additional_info"] = line.strip()
    if entry:
        parsed_data.append(entry)
    return parsed_data

structured_data = parse_text(pdf_text_lines)

conn = psycopg2.connect(
    dbname='beacon',
    user='***',
    password='***',
    host="localhost",
    port='5432'
)
cur = conn.cursor()

cur.execute('''
DROP TABLE IF EXISTS autism_services_resource_directory
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS autism_services_resource_directory (
    id SERIAL PRIMARY KEY,
    organization TEXT,
    contact_info TEXT,
    services TEXT,
    additional_info TEXT
)
''')

# Insert data into PostgreSQL
for item in structured_data:
    cur.execute('''
    INSERT INTO autism_services_resource_directory (organization, contact_info, services, additional_info)
    VALUES (%s, %s, %s, %s)
    ''', (item.get('organization'), item.get('contact_info'), item.get('services'), item.get('additional_info')))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully")
