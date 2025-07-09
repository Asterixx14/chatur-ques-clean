import sys
import os
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.rc_cleaner import RCQuestionCleaner

def setup_logging():
    """Set up logging without emojis."""
    os.makedirs('logs', exist_ok=True)
    
    # Create file handler with UTF-8 encoding
    file_handler = logging.FileHandler(
        f'logs/rc_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    
    # Set format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def main():
    """Main function - processes all RC questions automatically."""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated")
        
        # Initialize cleaner
        cleaner = RCQuestionCleaner(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        
        # Get input file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        input_file = os.path.join(project_root, Config.INPUT_JSON_PATH)
        
        logger.info(f"Input file: {input_file}")
        
        # Process all RC questions
        print("\n" + "="*80)
        print("STARTING RC QUESTION CLEANING PROCESS")
        print("="*80)
        
        # Change to output directory
        os.chdir(Config.OUTPUT_DIR)
        
        # Process all questions
        result = cleaner.process_all_rc_questions(input_file)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        # Print final results
        print("\n" + "="*80)
        print("RC CLEANING COMPLETED!")
        print("="*80)
        print(f"Total RC questions found: {result['total_processed']}")
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