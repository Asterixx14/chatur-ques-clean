import sys
import os
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.general_cleaner import GeneralQuestionCleaner

def setup_logging():
    """Set up logging."""
    os.makedirs('logs', exist_ok=True)
    
    file_handler = logging.FileHandler(
        f'logs/general_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def main():
    """Main function."""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Available categories (excluding RC, spatial_reasoning, abstract_reasoning)
    available_categories = [
        'critical_reasoning',
        'verbal_reasoning', 
        'numerical_reasoning',
        'logical_reasoning',
        'quantitative_reasoning',
        'general_knowledge',
        'analytical_reasoning'
    ]
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_general_cleaner.py <category>")
        print(f"Available categories: {', '.join(available_categories)}")
        print("Use 'all' to process all categories")
        return
    
    category = sys.argv[1].lower()
    
    if category not in available_categories and category != 'all':
        print(f"Invalid category: {category}")
        print(f"Available categories: {', '.join(available_categories)}")
        print("Use 'all' to process all categories")
        return
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated")
        
        # Initialize cleaner
        cleaner = GeneralQuestionCleaner(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        
        # Get input file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        input_file = os.path.join(project_root, Config.INPUT_JSON_PATH)
        
        logger.info(f"Input file: {input_file}")
        
        # Process questions
        print("\n" + "="*80)
        print(f"STARTING {category.upper()} QUESTION CLEANING PROCESS")
        print("="*80)
        
        # Change to output directory
        os.chdir(Config.OUTPUT_DIR)
        
        # Process questions
        result = cleaner.process_questions_by_category(input_file, category)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        # Print results
        print("\n" + "="*80)
        print(f"{category.upper()} CLEANING COMPLETED!")
        print("="*80)
        print(f"Category: {result['category']}")
        print(f"Total questions processed: {result['total_processed']}")
        print(f"Successfully cleaned: {result['successfully_cleaned']}")
        print(f"Failed to process: {result['failed']}")
        print(f"\nFILES CREATED:")
        print(f"   CLEANED DATA: {result['output_file']}")
        print(f"   PROCESSING LOG: {result['log_file']}")
        
        if result['failed_questions']:
            print(f"\nFailed Questions: {', '.join(result['failed_questions'])}")
        
        print(f"\nSEND TO SENIOR: {result['output_file']}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
