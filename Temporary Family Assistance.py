import requests
from bs4 import BeautifulSoup
import psycopg2

# PostgreSQL configuration
conn = psycopg2.connect(
    dbname='beacon',
    user='***',
    password='***',
    host="localhost",
    port='5432'
)
cur = conn.cursor()

cur.execute('''
DROP TABLE IF EXISTS temporary_family_assistance
''')

# Create table if it does not exist
cur.execute('''
CREATE TABLE IF NOT EXISTS temporary_family_assistance (
    id SERIAL PRIMARY KEY,
    content TEXT
)
''')

# URL of the website to scrape
URL = 'https://portal.ct.gov/dss/archived-folder/temporary-family-assistance---tfa'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define block to scrape
block_class = 'content'

# Extract the content from the specified block
content_div = soup.find('div', class_=block_class)
if content_div:
    text = content_div.get_text(strip=True)
else:
    text = 'Content not found.'

# Insert data into PostgreSQL
cur.execute('''
INSERT INTO temporary_family_assistance (content)
VALUES (%s)
''', (text,))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully.")
