import requests
import csv
import os
from typing import List, Dict, Optional

class WordPressAPIScraper:
    def __init__(self, base_url: str, endpoint: str = 'wp-json/wp/v2/posts'):
        """
        Initialize WordPress API scraper
        
        :param base_url: Base URL of the WordPress site
        :param endpoint: API endpoint to scrape (default: posts)
        """
        self.base_url = base_url.rstrip('/')
        self.endpoint = endpoint
        self.full_url = f"{self.base_url}/{self.endpoint}"

    def fetch_data(self, 
                   params: Optional[Dict] = None, 
                   per_page: int = 100, 
                   max_pages: Optional[int] = None) -> List[Dict]:
        """
        Fetch data from WordPress API
        
        :param params: Additional query parameters
        :param per_page: Number of items per page
        :param max_pages: Maximum number of pages to fetch
        :return: List of fetched data
        """
        all_data = []
        page = 1
        
        while True:
            # Prepare request parameters
            request_params = {
                'per_page': per_page,
                'page': page,
                **(params or {})
            }
            
            try:
                response = requests.get(self.full_url, params=request_params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    break
                
                all_data.extend(data)
                
                # Check for pagination limit
                if max_pages and page >= max_pages:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
        
        return all_data

    def extract_text_fields(self, item: Dict, fields: List[str] = ['title', 'content']) -> Dict:
        """
        Extract specific text fields from WordPress item
        
        :param item: WordPress API item
        :param fields: Fields to extract
        :return: Dictionary of extracted fields
        """
        extracted = {}
        for field in fields:
            if field in item and isinstance(item[field], dict):
                # For nested fields like title and content
                extracted[field] = item[field].get('rendered', '').replace('<p>', '').replace('</p>', '')
            elif field in item:
                extracted[field] = str(item[field])
        return extracted

    def save_to_csv(self, data: List[Dict], filename: str = 'wordpress_data.csv', 
                    text_fields: List[str] = ['title', 'content']) -> None:
        """
        Save scraped data to CSV
        
        :param data: List of scraped items
        :param filename: Output CSV filename
        :param text_fields: Fields to extract for text
        """
        if not data:
            print("No data to save.")
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Extract all unique keys from first item as headers
            extracted_data = [self.extract_text_fields(item, text_fields) for item in data]
            fieldnames = list(extracted_data[0].keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(extracted_data)
        
        print(f"Data saved to {filename}")

def main():
    # Example usage
    wordpress_url = 'https://example.wordpress.com'
    scraper = WordPressAPIScraper(wordpress_url)
    
    # Customize parameters as needed
    data = scraper.fetch_data(
        params={'categories': 5},  # Optional: filter by category
        per_page=50,
        max_pages=3
    )
    
    scraper.save_to_csv(data, 'wordpress_export.csv')

if __name__ == '__main__':
    main()
