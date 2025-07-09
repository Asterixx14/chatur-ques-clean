import json
import os
from typing import Dict, List
from openai import OpenAI
import time
from datetime import datetime
import logging

class RCQuestionCleaner:
    """Simple RC question cleaner - processes all RC questions automatically."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.processing_log = []
        
    def load_and_filter_rc_questions(self, file_path: str) -> List[Dict]:
        """Load JSON data and filter only RC questions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter only RC category questions
            rc_questions = [q for q in data if q.get('category', '').lower() == 'rc']
            
            logging.info(f"Found {len(rc_questions)} RC questions out of {len(data)} total questions")
            return rc_questions
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return []
    
    def clean_and_verify_question(self, question_data: Dict) -> Dict:
        """Clean, verify, and correct a single RC question using AI."""
        question_id = question_data.get('_id', {}).get('$oid', 'unknown')
        
        try:
            # Create a simplified version of the question data for the prompt
            simplified_question = {
                "passage": question_data.get('passage', ''),
                "question": question_data.get('question', ''),
                "options": question_data.get('options', []),
                "answer": question_data.get('answer', ''),
                "answer_explanation": question_data.get('answer_explanation', ''),
                "category": question_data.get('category', 'rc'),
                "difficulty": question_data.get('difficulty', 'medium')
            }
            
            # Prepare the AI prompt
            prompt = f"""You are an expert RC question cleaner. Clean and verify this RC question:

ORIGINAL QUESTION DATA:
{json.dumps(simplified_question, ensure_ascii=False, indent=2)}

TASKS:
1. Clean the passage by removing ads, explanations, unrelated content
2. Verify if question is answerable from cleaned passage
3. Check if options are appropriate and relevant
4. Confirm answer is correct and based on the passage
5. Verify answer explanation is accurate
6. Fix any issues found

RESPOND WITH VALID JSON IN THIS EXACT FORMAT and update the fields according to your cleaning done:
{{
  "cleaned_question": {{
    "passage": "CLEANED PASSAGE TEXT HERE",
    "question": "QUESTION TEXT",
    "options": ["option1", "option2", "option3", "option4"],
    "answer": "CORRECT ANSWER",
    "answer_explanation": "EXPLANATION TEXT"
  }},
  "changes_made": {{
    "passage_cleaned": true/false,
    "question_modified": true/false,
    "options_modified": true/false,
    "answer_corrected": true/false,
    "explanation_improved": true/false
  }},
  "issues_found": [
    Write all the issues found (if any),
  ],
  "cleaning_summary": Small summary of the what changes and cleaning you did
}}

IMPORTANT: Return only valid JSON. No additional text before or after."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert RC question cleaner. Always respond with valid JSON only. Never include markdown formatting or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
                timeout=30
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting if present
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Parse the JSON response
            try:
                result = json.loads(response_content)
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing failed for question {question_id}. Response: {response_content[:200]}...")
                return None
            
            # Reconstruct the full cleaned question with all original fields
            if 'cleaned_question' in result:
                full_cleaned_question = {
                    "_id": question_data.get('_id'),
                    "passage_id": question_data.get('passage_id', ''),
                    "passage": result['cleaned_question'].get('passage', ''),
                    "question": result['cleaned_question'].get('question', ''),
                    "options": result['cleaned_question'].get('options', []),
                    "answer": result['cleaned_question'].get('answer', ''),
                    "answer_explanation": result['cleaned_question'].get('answer_explanation', ''),
                    "category": question_data.get('category', 'rc'),
                    "difficulty": question_data.get('difficulty', 'medium'),
                    "user_response": question_data.get('user_response', '')
                }
                
                result['cleaned_question'] = full_cleaned_question
            
            # Log the processing
            self.processing_log.append({
                "question_id": question_id,
                "timestamp": datetime.now().isoformat(),
                "changes_made": result.get("changes_made", {}),
                "issues_found": result.get("issues_found", []),
                "cleaning_summary": result.get("cleaning_summary", "")
            })
            
            logging.info(f"Successfully processed question {question_id}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing question {question_id}: {str(e)}"
            logging.error(error_msg)
            
            # Log the error
            self.processing_log.append({
                "question_id": question_id,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "status": "failed"
            })
            
            return None
    
    def process_all_rc_questions(self, file_path: str) -> Dict:
        """Process all RC questions from the input file."""
        
        # Load RC questions
        rc_questions = self.load_and_filter_rc_questions(file_path)
        
        if not rc_questions:
            return {"error": "No RC questions found"}
        
        cleaned_questions = []
        failed_questions = []
        
        logging.info(f"Starting to process {len(rc_questions)} RC questions...")
        
        for i, question in enumerate(rc_questions, 1):
            question_id = question.get('_id', {}).get('$oid', f'question_{i}')
            
            logging.info(f"Processing {i}/{len(rc_questions)}: {question_id}")
            
            # Clean and verify the question
            result = self.clean_and_verify_question(question)
            
            if result and result.get('cleaned_question'):
                cleaned_questions.append(result['cleaned_question'])
            else:
                failed_questions.append(question_id)
            
            # Rate limiting
            time.sleep(2)
            
            # Progress update every 10 questions
            if i % 10 == 0:
                logging.info(f"Progress: {i}/{len(rc_questions)} questions processed")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save cleaned questions (for your senior)
        output_file = f"CLEANED_RC_QUESTIONS_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)
        
        # Save processing log
        log_file = f"RC_PROCESSING_LOG_{timestamp}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_log, f, indent=2, ensure_ascii=False)
        
        return {
            "output_file": output_file,
            "log_file": log_file,
            "total_processed": len(rc_questions),
            "successfully_cleaned": len(cleaned_questions),
            "failed": len(failed_questions),
            "failed_questions": failed_questions
        }