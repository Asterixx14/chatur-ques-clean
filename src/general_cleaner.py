import json
import os
from typing import Dict, List
from openai import OpenAI
import time
from datetime import datetime
import logging

class GeneralQuestionCleaner:
    """Cleaner for all question categories except RC, spatial_reasoning, and abstract_reasoning."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.processing_log = []
        
    def load_and_filter_questions(self, file_path: str, category: str) -> List[Dict]:
        """Load JSON data and filter questions by category."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter questions by category (exclude RC, spatial_reasoning, abstract_reasoning)
            excluded_categories = ['rc', 'spatial_reasoning', 'abstract_reasoning']
            
            if category.lower() == 'all':
                # Get all categories except excluded ones
                filtered_questions = [q for q in data if q.get('category', '').lower() not in excluded_categories]
            else:
                # Get specific category
                filtered_questions = [q for q in data if q.get('category', '').lower() == category.lower()]
            
            logging.info(f"Found {len(filtered_questions)} questions for category: {category}")
            return filtered_questions
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return []
    
    def clean_and_verify_question(self, question_data: Dict) -> Dict:
        """Clean and verify a single question using AI."""
        question_id = question_data.get('_id', {}).get('$oid', 'unknown')
        category = question_data.get('category', 'unknown')
        
        try:
            # Create simplified version for AI prompt
            simplified_question = {
                "question": question_data.get('question', ''),
                "options": question_data.get('options', []),
                "answer": question_data.get('answer', ''),
                "answer_explanation": question_data.get('answer_explanation', ''),
                "category": category,
                "difficulty": question_data.get('difficulty', 'medium')
            }
            
            # Category-specific instructions
            category_instructions = {
                'critical_reasoning': 'Ensure logical reasoning is sound and conclusion follows from premises.',
                'verbal_reasoning': 'Check grammar, vocabulary, and language usage accuracy.',
                'numerical_reasoning': 'Verify mathematical calculations and ensure correct answer.',
                'logical_reasoning': 'Validate logical sequences and reasoning patterns.',
                'quantitative_reasoning': 'Check mathematical concepts and problem-solving accuracy.',
                'general_knowledge': 'Verify factual accuracy and current information.',
                'analytical_reasoning': 'Ensure logical analysis and problem-solving approach is correct.'
            }
            
            specific_instruction = category_instructions.get(category.lower(), 'Verify question accuracy and clarity.')
            
            # Prepare AI prompt
            prompt = f"""You are an expert question validator for {category} questions. 

ORIGINAL QUESTION:
{json.dumps(simplified_question, ensure_ascii=False, indent=2)}

TASKS:
1. Check if the question is clear and well-formed
2. Verify all options are relevant and appropriate
3. Confirm the answer is correct
4. Ensure answer explanation is accurate and helpful
5. {specific_instruction}
6. Fix any issues found

RESPOND WITH VALID JSON IN THIS EXACT FORMAT and update the fields according to your cleaning done:
{{
  "cleaned_question": {{
    "question": "CLEANED QUESTION TEXT",
    "options": ["option1", "option2", "option3", "option4"],
    "answer": "CORRECT ANSWER",
    "answer_explanation": "CLEAR EXPLANATION"
  }},
  "changes_made": {{
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

IMPORTANT: Return only valid JSON. No additional text."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {category} question validator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
                timeout=30
            )
            
            # Process response
            response_content = response.choices[0].message.content.strip()
            
            # Remove markdown formatting
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Parse JSON
            try:
                result = json.loads(response_content)
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing failed for question {question_id}. Response: {response_content[:200]}...")
                return None
            
            # Reconstruct full question with all original fields
            if 'cleaned_question' in result:
                full_cleaned_question = {
                    "_id": question_data.get('_id'),
                    "question": result['cleaned_question'].get('question', ''),
                    "options": result['cleaned_question'].get('options', []),
                    "answer": result['cleaned_question'].get('answer', ''),
                    "answer_explanation": result['cleaned_question'].get('answer_explanation', ''),
                    "category": question_data.get('category', ''),
                    "difficulty": question_data.get('difficulty', 'medium'),
                    "user_response": question_data.get('user_response', '')
                }
                
                # Add passage_id if it exists (some questions might have it)
                if 'passage_id' in question_data:
                    full_cleaned_question['passage_id'] = question_data['passage_id']
                
                # Add passage if it exists (some questions might have it)
                if 'passage' in question_data:
                    full_cleaned_question['passage'] = question_data['passage']
                
                result['cleaned_question'] = full_cleaned_question
            
            # Log processing
            self.processing_log.append({
                "question_id": question_id,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "changes_made": result.get("changes_made", {}),
                "issues_found": result.get("issues_found", []),
                "cleaning_summary": result.get("cleaning_summary", "")
            })
            
            logging.info(f"Successfully processed {category} question {question_id}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing {category} question {question_id}: {str(e)}"
            logging.error(error_msg)
            
            # Log error
            self.processing_log.append({
                "question_id": question_id,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "status": "failed"
            })
            
            return None
    
    def process_questions_by_category(self, file_path: str, category: str) -> Dict:
        """Process all questions for a specific category."""
        
        # Load questions
        questions = self.load_and_filter_questions(file_path, category)
        
        if not questions:
            return {"error": f"No questions found for category: {category}"}
        
        cleaned_questions = []
        failed_questions = []
        
        logging.info(f"Starting to process {len(questions)} questions for category: {category}")
        
        for i, question in enumerate(questions, 1):
            question_id = question.get('_id', {}).get('$oid', f'question_{i}')
            
            logging.info(f"Processing {i}/{len(questions)}: {question_id}")
            
            # Clean and verify question
            result = self.clean_and_verify_question(question)
            
            if result and result.get('cleaned_question'):
                cleaned_questions.append(result['cleaned_question'])
            else:
                failed_questions.append(question_id)
            
            # Rate limiting
            time.sleep(1)
            
            # Progress update
            if i % 10 == 0:
                logging.info(f"Progress: {i}/{len(questions)} questions processed")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category_name = category.upper() if category != 'all' else 'ALL_CATEGORIES'
        
        # Save cleaned questions
        output_file = f"CLEANED_{category_name}_QUESTIONS_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)
        
        # Save processing log
        log_file = f"{category_name}_PROCESSING_LOG_{timestamp}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_log, f, indent=2, ensure_ascii=False)
        
        return {
            "category": category,
            "output_file": output_file,
            "log_file": log_file,
            "total_processed": len(questions),
            "successfully_cleaned": len(cleaned_questions),
            "failed": len(failed_questions),
            "failed_questions": failed_questions
        }
