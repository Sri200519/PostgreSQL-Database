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
DROP TABLE IF EXISTS women_infants_children
''')

# Create table if it does not exist
cur.execute('''
CREATE TABLE IF NOT EXISTS women_infants_children (
    id SERIAL PRIMARY KEY,
    tag TEXT,
    style TEXT,
    content TEXT
)
''')

# URL of the webpage to scrape
url = 'https://portal.ct.gov/dph/wic/wic'

# Send a GET request to the website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Define the styles to target
target_styles = [
    'margin: 0in 0in 0pt;',
    'text-align: left;'
]

# Find and extract <p> and <div> tags with the specified styles
for style in target_styles:
    for tag in soup.find_all(['p', 'div'], style=style):
        text_content = tag.get_text(strip=True)
        data.append({
            'tag': tag.name,
            'style': style,
            'content': text_content
        })

# Insert data into PostgreSQL
if data:
    for item in data:
        cur.execute('''
        INSERT INTO women_infants_children (tag, style, content)
        VALUES (%s, %s, %s)
        ''', (item['tag'], item['style'], item['content']))
    conn.commit()
    print("Data scraped and stored in PostgreSQL successfully")
else:
    print("No data found to insert.")

# Close PostgreSQL connection
cur.close()
conn.close()
