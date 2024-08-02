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
DROP TABLE IF EXISTS family_support_and_services
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS family_support_and_services (
    id SERIAL PRIMARY KEY,
    block_content TEXT,
    list_items TEXT[]
)
''')

# Fetch the webpage content
url = "https://portal.ct.gov/dds/supports-and-services/family-support-and-services?language=en_US"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Find all divs with the specified class
for div in soup.find_all('div', class_='cg-c-lead-story__body col'):
    block_content = div.get_text(strip=True, separator=' ')
    list_items = [li.get_text(strip=True) for li in div.find_all('li')]
    
    # Combine the block content with list items
    combined_content = {
        'block_content': block_content,
        'list_items': list_items
    }
    data.append(combined_content)

# Insert data into PostgreSQL
for item in data:
    cur.execute('''
    INSERT INTO family_support_and_services (block_content, list_items)
    VALUES (%s, %s)
    ''', (item['block_content'], item['list_items']))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully")
