import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import logging
import argparse
from datetime import datetime


LOG_FOLDER = os.path.join("output", "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

log_filename = os.path.join(LOG_FOLDER, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)


BASE_URL    = "http://books.toscrape.com/catalogue/"
DELAY       = 1
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_args():
    parser = argparse.ArgumentParser(description="books.toscrape.com scraper")
    parser.add_argument("--start",  type=int, default=1,        help="start page (default: 1)")
    parser.add_argument("--end",    type=int, default=None,     help="end page (default: auto)")
    parser.add_argument("--format", choices=["csv", "excel"],   default="excel")
    parser.add_argument("--output", type=str, default="output", help="folder to save results")
    return parser.parse_args()


def get_page(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info(f"fetching {url}  (attempt {attempt}/{MAX_RETRIES})")
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            return r

        except requests.exceptions.RequestException as e:
            log.warning(f"attempt {attempt} failed -> {e}")

            if attempt < MAX_RETRIES:
                wait = attempt * 2
                log.info(f"waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                log.error(f"all {MAX_RETRIES} attempts failed for {url}")
                return None


def log_failed_url(failed_list, url, error):
    failed_list.append({
        "url":       url,
        "error":     str(error),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def get_last_page(soup):
    try:
        pager = soup.find("li", class_="current")
        if pager:
            total = pager.text.strip().split("of")[-1].strip()
            return int(total)
    except Exception:
        pass
    return 1


def parse_books(soup, page_num):
    results = []
    books = soup.find_all("article", class_="product_pod")

    for b in books:
        try:
            title = b.find("h3").find("a")["title"]

            relative_url = b.find("h3").find("a")["href"].replace("../", "")
            full_url = BASE_URL + relative_url

            price = b.find("p", class_="price_color").text.strip()
            stock = b.find("p", class_="instock availability").text.strip()

            results.append({
                "title":        title,
                "price":        price,
                "availability": stock,
                "url":          full_url,
                "page":         page_num
            })

        except AttributeError as e:
            log.warning(f"skipped a book on page {page_num} -> {e}")
            continue

    return results


def save_results(data, save_folder, file_format):
    os.makedirs(save_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    df = pd.DataFrame(data)

    if file_format == "csv":
        filepath = os.path.join(save_folder, f"books_{timestamp}.csv")
        df.to_csv(filepath, index=False)
    else:
        filepath = os.path.join(save_folder, f"books_{timestamp}.xlsx")
        df.to_excel(filepath, index=False)

    log.info(f"results saved -> {filepath}")
    return filepath


def save_failed_urls(failed_list, save_folder):
    if not failed_list:
        return

    os.makedirs(save_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filepath = os.path.join(save_folder, f"failed_urls_{timestamp}.csv")

    pd.DataFrame(failed_list).to_csv(filepath, index=False)
    log.warning(f"failed urls saved -> {filepath}")


def main():
    args = get_args()

    log.info("scraper started")
    log.info(f"format : {args.format}")
    log.info(f"output : {args.output}")

    first_response = get_page("http://books.toscrape.com/catalogue/page-1.html")

    if first_response is None:
        log.error("failed to load first page — exiting")
        return

    first_soup = BeautifulSoup(first_response.text, "html.parser")
    last_page  = get_last_page(first_soup)
    start_page = args.start
    end_page   = args.end if args.end else last_page

    log.info(f"pages: {start_page} to {end_page}  (site total: {last_page})")

    all_books   = []
    failed_urls = []

    for page in range(start_page, end_page + 1):
        url      = f"http://books.toscrape.com/catalogue/page-{page}.html"
        response = get_page(url)

        if response is None:
            log_failed_url(failed_urls, url, "max retries exceeded")
            continue

        soup  = BeautifulSoup(response.text, "html.parser")
        books = parse_books(soup, page)
        all_books.extend(books)

        log.info(f"page {page}/{end_page} -> {len(books)} books scraped")
        time.sleep(DELAY)

    if not all_books:
        log.error("no data scraped — something went wrong")
        return

    save_results(all_books, args.output, args.format)
    save_failed_urls(failed_urls, args.output)

    log.info(f"done — {len(all_books)} books total  |  {len(failed_urls)} pages failed")


main()