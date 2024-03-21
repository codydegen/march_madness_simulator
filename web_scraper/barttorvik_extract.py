import requests
import csv
from bs4 import BeautifulSoup

# Send a GET request to the website
url = "https://barttorvik.com/tourneytime.php?conlimit=All&src=cur&year=2024"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the table element
table = soup.find("table")

# Extract the table data and save it into a CSV file
with open("table_data.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    for row in table.find_all("tr"):
        data = [cell.get_text(strip=True) for cell in row.find_all("td")]
        writer.writerow(data)

print("Table data extracted and saved into table_data.csv")