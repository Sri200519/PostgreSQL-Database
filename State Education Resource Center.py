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
DROP TABLE IF EXISTS state_education_resource_center
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS state_education_resource_center (
    id SERIAL PRIMARY KEY,
    source_url TEXT,
    content TEXT
)
''')

# URL of the webpage to scrape
url = 'https://ctserc.org/services'

# Make an HTTP GET request to the webpage
response = requests.get(url)

# Parse the HTML content of the webpage
soup = BeautifulSoup(response.content, 'html.parser')

# Find the div with the id 'serc-services'
services_div = soup.find('div', id='serc-services')

# Extract text from the div
services_text = services_div.get_text(strip=True) if services_div else 'Div with id "serc-services" not found.'

# Prepare the data to insert into PostgreSQL
data = {
    'source_url': url,
    'content': services_text
}

# Insert the data into PostgreSQL
cur.execute('''
INSERT INTO state_education_resource_center (source_url, content)
VALUES (%s, %s)
''', (data['source_url'], data['content']))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully.")
