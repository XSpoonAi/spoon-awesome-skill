import os
import json
import time
import argparse
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SummaryLength(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class DocumentSummarizer:
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.mock_mode and not self.api_key:
            # We don't raise error immediately to allow instantiation if env var is set later
            pass
            
        if not self.mock_mode:
            try:
                import anthropic
                if self.api_key:
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                else:
                    self.client = None
            except ImportError:
                logger.warning("Anthropic package not found. Install with: pip install anthropic")
                self.client = None

    def summarize(self, 
                  text: str, 
                  length: str = "medium", 
                  language: str = "english", 
                  focus_areas: Optional[List[str]] = None,
                  max_retries: int = 3) -> Dict[str, Any]:
        
        if self.mock_mode:
            return self._mock_response(length, language, focus_areas)

        if not self.client:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Set it in environment or pass to constructor.")
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install the 'anthropic' package: pip install anthropic")

        try:
            length_enum = SummaryLength(length.lower())
        except ValueError:
            logger.warning(f"Invalid length '{length}', defaulting to medium.")
            length_enum = SummaryLength.MEDIUM

        prompt = self._construct_prompt(text, length_enum, language, focus_areas)
        
        for attempt in range(max_retries):
            try:
                # Using the specific model version as requested/standard
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    temperature=0.5,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                content = response.content[0].text
                return self._parse_response(content)
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise RuntimeError(f"Failed to summarize document after {max_retries} attempts") from e

    def _construct_prompt(self, text: str, length: SummaryLength, language: str, focus_areas: Optional[List[str]]) -> str:
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"Focus particularly on these areas: {', '.join(focus_areas)}."

        return f"""
You are an expert document summarizer and insight extractor. 
Please analyze the following text and provide a structured summary in JSON format.

Configuration:
- Target Language: {language}
- Summary Length: {length.value}
{focus_instruction}

The JSON output must have the following structure:
{{
    "summary": "The main summary of the document...",
    "key_insights": ["Insight 1", "Insight 2", ...],
    "sentiment": "positive/neutral/negative",
    "language": "{language}",
    "metadata": {{
        "word_count": <approx_word_count>,
        "topics": ["Topic 1", "Topic 2"]
    }}
}}

Ensure the response is valid JSON. Do not include any text outside the JSON block.

Text to summarize:
{text}
"""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            # Attempt to extract JSON if Claude wraps it in markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response from Claude")
            return {
                "error": "Failed to parse structured response",
                "raw_content": content
            }

    def _mock_response(self, length: str, language: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]:
        logger.info("Generating mock response...")
        time.sleep(1)
        return {
            "summary": f"This is a MOCK summary of length {length} in {language}.",
            "key_insights": [
                "Mock insight 1: The document discusses AI productivity.",
                "Mock insight 2: Python scripts are useful for automation."
            ],
            "sentiment": "positive",
            "language": language,
            "metadata": {
                "word_count": 100,
                "topics": focus_areas or ["General", "Testing"]
            },
            "mock_mode": True
        }

def main():
    parser = argparse.ArgumentParser(description="Document Summarizer Skill")
    parser.add_argument("--file", help="Path to the file to summarize")
    parser.add_argument("--text", help="Direct text input")
    parser.add_argument("--length", default="medium", choices=["short", "medium", "long"], help="Summary length")
    parser.add_argument("--language", default="english", help="Target language")
    parser.add_argument("--focus", nargs="*", help="Specific focus areas")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    
    args = parser.parse_args()
    
    if not args.file and not args.text:
        parser.error("Either --file or --text must be provided")
        
    input_text = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return
    else:
        input_text = args.text

    try:
        summarizer = DocumentSummarizer(mock_mode=args.mock)
        result = summarizer.summarize(
            text=input_text,
            length=args.length,
            language=args.language,
            focus_areas=args.focus
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
