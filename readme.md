# Python Web Scraper — Book Data Extraction

## What this does
Scrapes book data from books.toscrape.com and saves it to CSV or Excel.
Built as a practice project to simulate real freelance data collection work.

---

## Features
- Scrapes multiple pages in one run
- Pulls title, price, availability, and product URL for each book
- Export to CSV or Excel — your choice
- Retries automatically if a page fails
- Logs everything so you can see exactly what happened
- Waits between requests so it doesn't hammer the server

---

## Stack
- Python 3
- requests — page fetching
- BeautifulSoup4 — HTML parsing
- pandas — data export
- argparse — CLI arguments
- logging — run logs

---

## Running it

Install dependencies first:
```bash:
pip install -r requirements.txt
```

Basic run:
```bash:
python scraper.py --start 1 --end 5 --format csv
```

All options:
| Argument | What it does | Default |
|----------|--------------|---------|
| `--start`| First page to| 1       |
|          |     scrape   |         |
|----------|--------------|---------|
| `--end`  | Last page to |auto     |
|          |   scrape     |         |
|----------|--------------|---------|
|`--format`| csv or excel | excel   |
|----------|--------------|---------|
|`--output`|Where to save | output/ | 
|          |    the file  |         |
|----------|--------------|---------|

---

## Output
Saves a timestamped file to your output folder:
```
books_20260524_1430.csv
```
Containing these columns:

| title | price_gbp | availability |    url    | page |
|-------|-----------|--------------|-----------|------|
|Book   |  51.77    | In stock     |http://... |   1  |
|  Name |           |              |           |      |
|-------|-----------|--------------|-----------|------|
---

## Purpose
This project demonstrates:
- Web scraping and HTML parsing
- Data extraction and automation
- File export handling (CSV + Excel)
- Error handling and retry logic
- Real-world Python scripting

---

##  Author
Python developer focused on automation, data scraping, and AI tools.