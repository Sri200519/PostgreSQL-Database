import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import sql
import json

# Fetch the webpage content
url = 'https://www.connecticutchildrens.org/specialties-conditions/developmental-behavioral-pediatrics/autism-spectrum-disorder-asd'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Find and extract all <p> tags
for tag in soup.find_all(['p']):
    text_content = tag.get_text(strip=True)
    data.append({
        'tag': tag.name,
        'content': text_content
    })

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname='beacon',
    user='***',
    password='***',
    host="localhost",
    port='5432'
)
cur = conn.cursor()

cur.execute('''
DROP TABLE IF EXISTS autism_spectrum_disorder
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS autism_spectrum_disorder (
    id SERIAL PRIMARY KEY,
    tag TEXT,
    content TEXT
)
''')

# Insert data into PostgreSQL
for item in data:
    cur.execute('''
    INSERT INTO autism_spectrum_disorder (tag, content)
    VALUES (%s, %s)
    ''', (item['tag'], item['content']))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully")
