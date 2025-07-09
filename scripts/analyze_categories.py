import json
import sys
import os
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config

def analyze_categories(file_path: str):
    """Analyze all categories in the database."""
    
    try:
        # Load the database
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=" * 80)
        print("DATABASE CATEGORY ANALYSIS")
        print("=" * 80)
        print(f"Total questions in database: {len(data)}")
        
        # Count categories
        categories = []
        for question in data:
            category = question.get('category', 'NO_CATEGORY')
            categories.append(category)
        
        # Get category counts
        category_counts = Counter(categories)
        
        print(f"\nFound {len(category_counts)} different categories:")
        print("-" * 50)
        
        # Sort by count (descending)
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            print(f"{category:<25} : {count:>6} questions")
        
        print("\n" + "=" * 80)
        print("CATEGORY BREAKDOWN FOR CLEANING")
        print("=" * 80)
        
        # Identify which categories need which type of cleaning
        rc_categories = []
        excluded_categories = []
        general_categories = []
        
        for category, count in sorted_categories:
            if category.lower() == 'rc':
                rc_categories.append(category)
            elif category.lower() in ['spatial_reasoning', 'abstract_reasoning']:
                excluded_categories.append(category)
            else:
                general_categories.append(category)
        
        print("RC CATEGORIES (use RC cleaner):")
        for cat in rc_categories:
            print(f"  - {cat} ({category_counts[cat]} questions)")
        
        print("\nEXCLUDED CATEGORIES (skip these):")
        for cat in excluded_categories:
            print(f"  - {cat} ({category_counts[cat]} questions)")
        
        print("\nGENERAL CATEGORIES (use general cleaner):")
        for cat in general_categories:
            print(f"  - {cat} ({category_counts[cat]} questions)")
        
        print("\n" + "=" * 80)
        print("COMMANDS TO RUN:")
        print("=" * 80)
        
        print("1. For RC questions:")
        print("   python scripts/run_rc_cleaner.py")
        
        print("\n2. For individual categories:")
        for cat in general_categories:
            if cat != 'NO_CATEGORY':
                print(f"   python scripts/run_general_cleaner.py {cat}")
        
        print("\n3. For all general categories at once:")
        print("   python scripts/run_general_cleaner.py all")
        
        print("\n4. For batch processing:")
        print("   python scripts/process_all_categories.py")
        
        # Sample questions for each category
        print("\n" + "=" * 80)
        print("SAMPLE QUESTIONS BY CATEGORY")
        print("=" * 80)
        
        category_samples = {}
        for question in data:
            category = question.get('category', 'NO_CATEGORY')
            if category not in category_samples:
                category_samples[category] = question
        
        for category in sorted(category_samples.keys()):
            sample = category_samples[category]
            print(f"\n{category.upper()}:")
            print(f"  Question: {sample.get('question', 'N/A')[:80]}...")
            print(f"  Options: {len(sample.get('options', []))} options")
            print(f"  Has passage: {'passage' in sample}")
            print(f"  Answer: {sample.get('answer', 'N/A')[:50]}...")
        
        return category_counts
        
    except Exception as e:
        print(f"Error analyzing categories: {e}")
        return None

def main():
    """Main function."""
    
    try:
        # Get input file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        input_file = os.path.join(project_root, Config.INPUT_JSON_PATH)
        
        if not os.path.exists(input_file):
            print(f"Error: Input file not found at {input_file}")
            print("Make sure your database file exists and Config.INPUT_JSON_PATH is correct")
            return
        
        # Analyze categories
        category_counts = analyze_categories(input_file)
        
        if category_counts:
            # Save analysis to file
            output_file = "category_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dict(category_counts), f, indent=2, ensure_ascii=False)
            
            print(f"\nAnalysis saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    