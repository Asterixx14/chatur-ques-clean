import subprocess
import sys
import os

def main():
    """Process all categories one by one."""
    
    categories = [
        'critical_reasoning',
        'verbal_reasoning', 
        'numerical_reasoning',
        'logical_reasoning',
        'quantitative_reasoning',
        'general_knowledge',
        'analytical_reasoning'
    ]
    
    print("="*80)
    print("BATCH PROCESSING ALL CATEGORIES")
    print("="*80)
    
    for category in categories:
        print(f"\n>>> Processing {category}...")
        
        try:
            # Run the general cleaner for this category
            result = subprocess.run([
                sys.executable, 
                'scripts/run_general_cleaner.py', 
                category
            ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            if result.returncode == 0:
                print(f"✓ {category} completed successfully")
            else:
                print(f"✗ {category} failed")
                
        except Exception as e:
            print(f"✗ {category} failed with error: {e}")
    
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()