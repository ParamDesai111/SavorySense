import requests
from bs4 import BeautifulSoup
import json

def extract_recipe_from_jsonld(soup):
    """
    Look for <script type="application/ld+json"> tags and parse them.
    Returns the first JSON object with @type "Recipe" if found.
    """
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Data may be a list or dict, sometimes nested in '@graph'
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Recipe':
                        return item
            elif isinstance(data, dict):
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Recipe':
                            return item
                elif data.get('@type') == 'Recipe':
                    return data
        except Exception:
            continue
    return None

def scrape_recipe(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/103.0.0.0 Safari/537.36"
        )
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Try to get recipe data from JSON-LD structured data.
    recipe_data = extract_recipe_from_jsonld(soup)
    recipe = {}
    if recipe_data:
        # Extract title, ingredients, and instructions from structured data.
        recipe['title'] = recipe_data.get('name', 'No title found')
        recipe['ingredients'] = recipe_data.get('recipeIngredient', [])
        
        # recipeInstructions can be a list of dicts or strings.
        instructions = recipe_data.get('recipeInstructions', [])
        if isinstance(instructions, list):
            # Check if instructions are dicts containing a "text" key.
            if instructions and isinstance(instructions[0], dict):
                recipe['instructions'] = [step.get('text', '') for step in instructions if step.get('text')]
            else:
                recipe['instructions'] = instructions
        else:
            recipe['instructions'] = [instructions]
        
        return recipe

    # Fallback: Use generic selectors for pages without JSON-LD.
    # Title: Look for a prominent header tag.
    title_tag = soup.find("h1")
    recipe['title'] = title_tag.get_text(strip=True) if title_tag else "No title found"
    
    # Ingredients: Try to find list items that contain "ingredient" in a class or id.
    ingredient_tags = soup.find_all(
        lambda tag: tag.name == "li" and (
            any("ingredient" in c.lower() for c in tag.get("class", [])) or
            ("ingredient" in (tag.get("id") or "").lower())
        )
    )
    recipe['ingredients'] = [tag.get_text(strip=True) for tag in ingredient_tags if tag.get_text(strip=True)]
    
    # Instructions: Look for paragraphs or list items with "instruction" in class or id.
    instruction_tags = soup.find_all(
        lambda tag: tag.name in ["p", "li"] and (
            any("instruction" in c.lower() for c in tag.get("class", [])) or
            ("instruction" in (tag.get("id") or "").lower())
        )
    )
    recipe['instructions'] = [tag.get_text(strip=True) for tag in instruction_tags if tag.get_text(strip=True)]
    
    return recipe