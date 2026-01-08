import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_website_contents(
    url: str,
    max_chars: int = 2000,
    timeout: int = 10,
    headers: Optional[dict] = None
) -> Tuple[str, str]:
    """
    Fetch and extract the title and main text content from a website.
    
    Args:
        url: The website URL to scrape
        max_chars: Maximum characters to return (default: 2000)
        timeout: Request timeout in seconds (default: 10)
        headers: Optional custom headers dict
    
    Returns:
        Tuple of (title, text_content) - both strings
        Returns error messages if scraping fails
    
    Raises:
        None - errors are caught and returned as strings
    """
    # Default headers with user agent
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse with appropriate parser
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
        
        # Extract text content
        text = ""
        if soup.body:
            # Remove irrelevant elements
            for element in soup.body(["script", "style", "img", "input", "svg", "iframe", "noscript"]):
                element.decompose()
            
            # Get text with better formatting
            text = soup.body.get_text(separator="\n", strip=True)
            
            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
        
        # Combine and truncate
        full_content = f"{title}\n\n{text}"
        
        if len(full_content) > max_chars:
            truncated = full_content[:max_chars]
            # Try to truncate at last complete word
            last_space = truncated.rfind(' ')
            if last_space > max_chars * 0.9:  # Only if we're close to the limit
                truncated = truncated[:last_space]
            return title, truncated + "..."
        
        return title, full_content
        
    except requests.exceptions.Timeout:
        error_msg = f"Timeout: Website took longer than {timeout} seconds to respond"
        logger.error(error_msg)
        return "Error", error_msg
        
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection Error: Could not connect to {url}"
        logger.error(error_msg)
        return "Error", error_msg
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {url}"
        logger.error(error_msg)
        return "Error", error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error scraping {url}: {str(e)}"
        logger.error(error_msg)
        return "Error", error_msg


# Alternative version that returns a single string (matching your original)
def fetch_website_contents_simple(
    url: str,
    max_chars: int = 10000,
    timeout: int = 10,
    headers: Optional[dict] = None
) -> str:
    """
    Simplified version that returns a single string like the original.
    
    Args:
        url: The website URL to scrape
        max_chars: Maximum characters to return (default: 2000)
        timeout: Request timeout in seconds (default: 10)
        headers: Optional custom headers dict
    
    Returns:
        String containing title and content, or error message
    """
    title, content = fetch_website_contents(url, max_chars, timeout, headers)
    return content


# Example usage
if __name__ == "__main__":
    # Test the scraper
    test_url = "https://example.com"
    
    print("Testing improved scraper...")
    title, content = fetch_website_contents(test_url)
    print(f"\nTitle: {title}")
    print(f"\nContent preview:\n{content[:500]}...")
    
    print(f"\n\nTotal length: {len(content)} characters")