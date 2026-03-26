import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

def get_quotes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        quotes_data = []
        quotes = soup.find_all('div', class_='quote')

        for quote in quotes:
            text = quote.find('span', class_='text').get_text()
            author = quote.find('small', class_='author').get_text()
            tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]

            quotes_data.append({
                "quote": text,
                "author": author,
                "tags": tags
            })

        return quotes_data, soup 

    except requests.RequestException as e:
        print(f"Error fetching quotes from {url}: {e}")
        return [], None


def get_next_page(soup, base_url):
    try:
        next_button = soup.find('li', class_='next')
        if next_button:
            link = next_button.find('a')
            if link and link.get('href'):
                return urljoin(base_url, link['href'])
        return None

    except Exception as e:
        print(f"Error finding next page: {e}")
        return None


def parse(url):
    all_quotes = []
    current_url = url

    while current_url:
        quotes, soup = get_quotes(current_url)
        all_quotes.extend(quotes)

        if soup is None:
            break

        current_url = get_next_page(soup, current_url)  # ← важно!

    return all_quotes


def save_to_csv(quotes, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Quote', 'Author', 'Tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for quote in quotes:
                writer.writerow({
                    'Quote': quote['quote'],
                    'Author': quote['author'],
                    'Tags': ', '.join(quote['tags'])
                })

    except IOError as e:
        print(f"Error writing to CSV file: {e}")


def main():
    url = "http://quotes.toscrape.com/"
    quotes = parse(url)
    save_to_csv(quotes, 'quotes.csv')


if __name__ == "__main__":
    main()