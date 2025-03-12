import requests
from bs4 import BeautifulSoup
import json

def extract_recipe_from_jsonld(soup):
    """
    Look for <script type="application/ld+json"> tags and parse them.
    Returns the first JSON object with @type 'Recipe' if found.
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
        # Extract title, ingredients, instructions, description, and nutrition from structured data.
        recipe['title'] = recipe_data.get('name', 'No title found')
        recipe['ingredients'] = recipe_data.get('recipeIngredient', [])
        recipe['description'] = recipe_data.get('description', 'No description found')
        
        # Nutrition information.
        if 'nutrition' in recipe_data:
            nutrition = recipe_data['nutrition']
            recipe['nutrition'] = {key: nutrition.get(key, '') for key in ['calories', 'fatContent', 'carbohydrateContent', 'proteinContent']}
        
        # Handling instructions that are potentially in different formats.
        instructions = recipe_data.get('recipeInstructions', [])
        if isinstance(instructions, list) and instructions and isinstance(instructions[0], dict):
            recipe['instructions'] = [step.get('text', '') for step in instructions if 'text' in step]
        else:
            recipe['instructions'] = [instructions]

        return recipe

    # Fallback: Use generic selectors for pages without JSON-LD.
    title_tag = soup.find("h1")
    recipe['title'] = title_tag.get_text(strip=True) if title_tag else "No title found"
    
    # Extract description from a paragraph if available.
    description_tag = soup.find(lambda tag: tag.name == "p" and 'description' in (tag.get("class", []) or tag.get("id", "")))
    recipe['description'] = description_tag.get_text(strip=True) if description_tag else "No description found"
    
    # Ingredients and Instructions as previously defined.
    ingredient_tags = soup.find_all(lambda tag: tag.name == "li" and any("ingredient" in c.lower() for c in tag.get("class", [])))
    recipe['ingredients'] = [tag.get_text(strip=True) for tag in ingredient_tags]
    
    instruction_tags = soup.find_all(lambda tag: tag.name in ["p", "li"] and any("instruction" in c.lower() for c in tag.get("class", [])))
    recipe['instructions'] = [tag.get_text(strip=True) for tag in instruction_tags]

    # Attempt to find and parse a simple nutrition facts section.
    nutrition_tags = soup.find_all("table", class_="nutrition-table")
    if nutrition_tags:
        nutrition_info = {}
        for row in nutrition_tags[0].find_all("tr"):
            columns = row.find_all("td")
            if len(columns) == 2:
                key = columns[0].get_text(strip=True).lower().replace(" ", "")
                value = columns[1].get_text(strip=True)
                nutrition_info[key] = value
        recipe['nutrition'] = nutrition_info
    
    return recipe
