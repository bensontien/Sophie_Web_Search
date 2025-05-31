from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright

class PlaywrightScraper:
    """
    A class for scraping web pages using Playwright to fetch content and BeautifulSoup to parse it.
    """       
    def get_page_source(self, url):
        """
        Fetches the HTML source of a given URL using Playwright.

        Args:
            url (str): The URL to scrape.

        Returns:
            str: The page content as HTML, or None if an error occurs.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True) 
                page = browser.new_page(user_agent=f"{UserAgent().random}") 
                page.goto(url, timeout=5000, wait_until="domcontentloaded")
                page_content = page.content()
                browser.close()
            return page_content
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
            
    def parse_content(self, page_source):
        """
        Parses the HTML content and extracts text from specified elements.

        Args:
            page_source (str): The HTML content to parse.

        Returns:
            str: A string containing the extracted text from headings, paragraphs, lists, and links.
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'a'])
        
        content = []
        for element in elements:
            text = element.get_text(strip=True)
            if text:
                content.append(text)
        
        return '\n'.join(content)