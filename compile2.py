#!/usr/bin/env python3
"""
Script to extract spatial_reasoning and abstract_reasoning from main database,
then compile all 7 categories into one JSON file.
"""

import json
import os
from datetime import datetime

def extract_categories_from_main_db(db_path, categories_to_extract):
    """Extract specific categories from the main database."""
    print(f"📂 Loading main database: {db_path}")
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        print(f"   ✅ Loaded {len(all_data)} total questions")
        
        extracted = {}
        
        for category in categories_to_extract:
            # Filter questions by category
            category_questions = [
                q for q in all_data 
                if q.get('category', '').lower() == category.lower()
            ]
            
            extracted[category] = category_questions
            print(f"   📊 Found {len(category_questions)} {category} questions")
            
            # Save individual category file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"EXTRACTED_{category.upper()}_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(category_questions, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Saved to: {output_file}")
        
        return extracted
        
    except Exception as e:
        print(f"   ❌ Error loading database: {e}")
        return {}

def find_cleaned_files():
    """Find all cleaned category files in current directory."""
    import glob
    
    file_patterns = {
        'critical_reasoning': 'CLEANED_CRITICAL_REASONING_*.json',
        'logical_reasoning': 'CLEANED_LOGICAL_REASONING_*.json',
        'numerical_reasoning': 'CLEANED_NUMERICAL_REASONING_*.json',
        'verbal_reasoning': 'CLEANED_VERBAL_REASONING_*.json',
        'rc': 'CLEANED_RC_*.json'
    }
    
    found_files = {}
    
    for category, pattern in file_patterns.items():
        matches = glob.glob(pattern)
        if matches:
            found_files[category] = matches[0]  # Use first match
            print(f"   ✅ Found {category}: {matches[0]}")
        else:
            print(f"   ❌ No file found for {category} (pattern: {pattern})")
    
    return found_files

def compile_all_categories(main_db_path="cognitive_assessment_db.json"):
    """Extract spatial/abstract categories and compile all 7 categories."""
    
    print("🚀 EXTRACTING AND COMPILING ALL CATEGORIES")
    print("=" * 70)
    
    # Step 1: Extract spatial_reasoning and abstract_reasoning from main DB
    print("\n📋 STEP 1: Extracting categories from main database")
    print("-" * 50)
    
    categories_to_extract = ['spatial_reasoning', 'abstract_reasoning']
    extracted_categories = extract_categories_from_main_db(main_db_path, categories_to_extract)
    
    if not extracted_categories:
        print("❌ Failed to extract categories from main database!")
        return None
    
    # Step 2: Find cleaned files
    print("\n📋 STEP 2: Finding cleaned category files")
    print("-" * 50)
    
    cleaned_files = find_cleaned_files()
    
    # Step 3: Compile everything
    print("\n📋 STEP 3: Compiling all categories")
    print("-" * 50)
    
    all_questions = []
    category_stats = {}
    
    # Add extracted categories (spatial_reasoning, abstract_reasoning)
    for category, questions in extracted_categories.items():
        all_questions.extend(questions)
        category_stats[category] = len(questions)
        print(f"   ✅ Added {len(questions)} {category} questions")
    
    # Add cleaned categories
    for category, file_path in cleaned_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            # Ensure category field is set
            for question in questions:
                if 'category' not in question:
                    question['category'] = category
            
            all_questions.extend(questions)
            category_stats[category] = len(questions)
            print(f"   ✅ Added {len(questions)} {category} questions from {file_path}")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
            category_stats[category] = 0
    
    # Step 4: Save final compiled file
    print("\n📋 STEP 4: Saving compiled file")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ALL_CATEGORIES_COMPILED_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved to: {output_file}")
        
        # Final statistics
        print("\n" + "=" * 70)
        print("✅ COMPILATION COMPLETED!")
        print("=" * 70)
        print(f"📁 Final file: {output_file}")
        print(f"📊 Total questions: {len(all_questions)}")
        print("\n📈 Category breakdown:")
        
        # Define expected order
        category_order = [
            'critical_reasoning', 'logical_reasoning', 'numerical_reasoning',
            'verbal_reasoning', 'rc', 'spatial_reasoning', 'abstract_reasoning'
        ]
        
        total_questions = 0
        for category in category_order:
            count = category_stats.get(category, 0)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {category:<20}: {count:>6} questions")
            total_questions += count
        
        print(f"\n   📊 TOTAL: {total_questions} questions")
        
        if total_questions == len(all_questions):
            print("   ✅ All questions accounted for!")
        else:
            print(f"   ⚠️  Mismatch: {len(all_questions)} in file vs {total_questions} counted")
        
        return output_file
        
    except Exception as e:
        print(f"   ❌ Error saving compiled file: {e}")
        return None

def main():
    """Main function."""
    print("🎯 COMPLETE CATEGORY EXTRACTION AND COMPILATION TOOL")
    print("=" * 70)
    print("This script will:")
    print("1. Extract spatial_reasoning & abstract_reasoning from main DB")
    print("2. Find your cleaned category files")
    print("3. Compile all 7 categories into one master JSON")
    print()
    
    # Check for main database
    main_db = "cognitive_assessment_db.json"
    if not os.path.exists(main_db):
        print(f"❌ Main database not found: {main_db}")
        alt_db = input("Enter path to your main database file: ").strip()
        if alt_db and os.path.exists(alt_db):
            main_db = alt_db
        else:
            print("❌ Database file not found. Exiting.")
            return
    
    print(f"✅ Using database: {main_db}")
    
    # Show current directory contents
    print(f"\n📂 Current directory: {os.getcwd()}")
    print("📋 JSON files found:")
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    for file in sorted(json_files):
        size = os.path.getsize(file) // 1024  # KB
        print(f"   📄 {file} ({size} KB)")
    
    print()
    response = input("🚀 Start extraction and compilation? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Process cancelled.")
        return
    
    # Run the compilation
    result = compile_all_categories(main_db)
    
    if result:
        print(f"\n🎉 SUCCESS! Your complete database is ready: {result}")
        print("\n📋 Next steps:")
        print(f"   1. Review the file: {result}")
        print("   2. Send to your senior for final approval")
        print("   3. Use this as your master question database")
    else:
        print("\n❌ Compilation failed! Check the error messages above.")

if __name__ == "__main__":
    main()