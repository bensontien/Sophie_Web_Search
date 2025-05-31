import tools
import asyncio
import uvicorn
from pydantic import BaseModel
from duckduckgo_search import DDGS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fake_useragent import UserAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class ItemScrappedWeb(BaseModel):
    message: str

async def ddg_search(query: str):
    """
    Performs a search using DuckDuckGo and returns a list of URLs.

    Args:
        query (str): The search query string.

    Returns:
        list: A list of URLs from the search results, or an empty list if an error occurs.
    """
    try:
        loop = asyncio.get_event_loop()
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        results = await loop.run_in_executor(None, lambda: list(DDGS(headers=headers).text(keywords=query, max_results=6, region="tw-tzh")))
        urls = [result['href'] for result in results]
        return urls
    except Exception as e:
        print(f"Error during search: {e}")
        return []

@app.post("/websearch")
async def web_search(item: ItemScrappedWeb):
    """
    Handles a POST request to perform a web search and scrape content from results.

    Args:
        item (ItemScrappedWeb): The input item containing the message to search.

    Returns:
        dict: A dictionary with URLs as keys and their scraped content (up to 5000 characters) as values,
              or an error message if no results are found.
    """
    message = item.message
    urls = await ddg_search(message)
    
    if not urls:
        return {"error": "No search results found"}
    
    contents = {}
    
    scraper = tools.PlaywrightScraper()
    
    async def scrape_url(url):
        try:
            page_source = await asyncio.get_event_loop().run_in_executor(None, scraper.get_page_source, url)
            if page_source:
                content = scraper.parse_content(page_source)
                return content
            return ""
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""
    
    tasks = [scrape_url(url) for url in urls]
    results = await asyncio.gather(*tasks)

    for url, content in zip(urls, results):
        if content:
            contents[url] = content[:5000]
    
    return contents

if __name__ == "__main__":
    uvicorn.run(app="main:app", host='0.0.0.0', port= 8818, app_dir="src", workers = 1)