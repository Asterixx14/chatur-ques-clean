import json

# Read the JSON file with UTF-8 encoding
with open('ALL_CATEGORIES_COMPILED_20250715_205425.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter out rc category questions
filtered = [item for item in data if item['category'] != 'rc']

# Save the filtered data with proper formatting
with open('ALL_CATEGORIES_NO_RC.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2)

print(f"Removed {len(data) - len(filtered)} RC questions")