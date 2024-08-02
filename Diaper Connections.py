import requests
from bs4 import BeautifulSoup
import psycopg2

# Configuration for PostgreSQL
conn = psycopg2.connect(
    dbname='beacon',
    user='***',
    password='***',
    host="localhost",
    port='5432'
)
cur = conn.cursor()

cur.execute('''
DROP TABLE IF EXISTS diaper_connections
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS diaper_connections (
    id SERIAL PRIMARY KEY,
    text TEXT
)
''')

# URL of the website to scrape
URL = 'https://www.thediaperbank.org/diaper-connections/'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define blocks to scrape
blocks = [
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_1 et_pb_css_mix_blend_mode_passthrough et-last-child'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_2 et_pb_css_mix_blend_mode_passthrough'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_5 et_pb_css_mix_blend_mode_passthrough et-last-child'}
]

documents = []

for block in blocks:
    for div in soup.find_all('div', class_=block['class']):
        # Extracting text from the div
        text = div.get_text(strip=True)
        # Adding text to the documents list
        documents.append((text,))

# Insert documents into PostgreSQL
if documents:
    cur.executemany('INSERT INTO diaper_connections (text) VALUES (%s)', documents)
    print(f'{len(documents)} documents inserted.')
else:
    print('No data found to insert.')

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()
