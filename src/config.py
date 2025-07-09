import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-4o-mini"
    
    # File paths
    INPUT_JSON_PATH = 'cognitive_assesment_db.json'
    OUTPUT_DIR = 'cleaned_data'
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        if not os.path.exists(cls.INPUT_JSON_PATH):
            raise FileNotFoundError(f"Input file not found: {cls.INPUT_JSON_PATH}")
        
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return True