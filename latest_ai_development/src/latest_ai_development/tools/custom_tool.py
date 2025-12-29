from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
import json


class EcommerceScraperInput(BaseModel):
    """Input schema for EcommerceScraper."""
    url: str = Field(..., description="The URL of the e-commerce website page to scrape.")
    product_selector: str = Field(
        default="div.product, article.product, .product-item, [data-product]",
        description="CSS selector for product containers. Default tries common selectors."
    )


class EcommerceScraper(BaseTool):
    name: str = "E-commerce Website Scraper"
    description: str = (
        "Scrapes e-commerce websites to extract product information including names, "
        "prices, descriptions, images, and ratings. Use this tool to gather product data "
        "from any e-commerce website URL."
    )
    args_schema: Type[BaseModel] = EcommerceScraperInput

    def _run(self, url: str, product_selector: str = "div.product, article.product, .product-item, [data-product]") -> str:
        """
        Scrapes an e-commerce website and extracts product information.
        
        Args:
            url: The URL to scrape
            product_selector: CSS selector for product containers
            
        Returns:
            JSON string containing scraped product data
        """
        try:
            # Set headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find products using the selector
            products = soup.select(product_selector)
            
            if not products:
                # Fallback: try to find common product indicators
                products = soup.find_all(['div', 'article', 'section'], 
                                       class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
            
            scraped_data = {
                'url': url,
                'total_products_found': len(products),
                'products': []
            }
            
            # Extract product information
            for product in products[:50]:  # Limit to 50 products to avoid too much data
                product_data = {}
                
                # Try to extract product name
                name_selectors = ['h1', 'h2', 'h3', '.product-name', '.product-title', '[data-product-name]', 'a.product-title']
                for selector in name_selectors:
                    name_elem = product.select_one(selector)
                    if name_elem:
                        product_data['name'] = name_elem.get_text(strip=True)
                        break
                
                # Try to extract price
                price_selectors = ['.price', '.product-price', '[data-price]', '.cost', '.amount', 'span.price']
                for selector in price_selectors:
                    price_elem = product.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        product_data['price'] = price_text
                        break
                
                # Try to extract description
                desc_selectors = ['.description', '.product-description', 'p.description', '.product-details']
                for selector in desc_selectors:
                    desc_elem = product.select_one(selector)
                    if desc_elem:
                        product_data['description'] = desc_elem.get_text(strip=True)
                        break
                
                # Try to extract image
                img_elem = product.select_one('img')
                if img_elem:
                    product_data['image_url'] = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
                
                # Try to extract rating
                rating_selectors = ['.rating', '.stars', '[data-rating]', '.review-score']
                for selector in rating_selectors:
                    rating_elem = product.select_one(selector)
                    if rating_elem:
                        product_data['rating'] = rating_elem.get_text(strip=True)
                        break
                
                # Try to extract link
                link_elem = product.select_one('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        product_data['product_url'] = urljoin(url, href)
                    else:
                        product_data['product_url'] = href
                
                # Only add product if it has at least a name or significant data
                if product_data.get('name') or product_data.get('price') or product_data.get('description'):
                    scraped_data['products'].append(product_data)
            
            # If no products found, return page structure info
            if not scraped_data['products']:
                scraped_data['page_info'] = {
                    'title': soup.title.string if soup.title else 'No title',
                    'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
                    'suggested_selectors': 'Try inspecting the page to find the correct product selector'
                }
            
            return json.dumps(scraped_data, indent=2, ensure_ascii=False)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                'error': f'Failed to fetch URL: {str(e)}',
                'url': url
            }, indent=2)
        except Exception as e:
            return json.dumps({
                'error': f'Scraping error: {str(e)}',
                'url': url
            }, indent=2)
