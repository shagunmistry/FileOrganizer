from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Callable
import anthropic
import anthropic
import groq
import logging
import mimetypes
import openai
import os
import shutil
import time

class AIProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @abstractmethod
    def classify_file(self, file_info: Dict) -> str:
        pass

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def classify_file(self, file_info: Dict) -> str:
        try:
            prompt = f"""
            You are a productivity guru! 🧠📚🚀
            Based on the following file information, suggest a single appropriate category folder name:
            Filename: {file_info['name']}
            Type: {file_info['mime_type']}
            Created: {file_info['created']}
            
            Respond with just the category name (one word, lowercase) from these options:
            documents, images, audio, video, archives, code, data, downloads, other
            """
            
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            category = message.content[0].text.strip().lower()
            return category if category in ["documents", "images", "audio", "video", "archives", "code", "data", "downloads", "other"] else "other"
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)
    
    def classify_file(self, file_info: Dict) -> str:
        try:
            prompt = f"""
            You are a productivity guru! 🧠📚🚀
            Based on the following file information, suggest a single appropriate category folder name:
            Filename: {file_info['name']}
            Type: {file_info['mime_type']}
            Created: {file_info['created']}
            
            Respond with just the category name (one word, lowercase) from these options:
            documents, images, audio, video, archives, code, data, downloads, other
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful file organization assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            category = response.choices[0].message.content.strip().lower()
            return category if category in ["documents", "images", "audio", "video", "archives", "code", "data", "downloads", "other"] else "other"
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class GroqProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = groq.Groq(api_key=api_key)
    
    def classify_file(self, file_info: Dict) -> str:
        try:
            prompt = f"""
            You are a productivity guru! 🧠📚🚀
            Based on the following file information, suggest a single appropriate category folder name:
            Filename: {file_info['name']}
            Type: {file_info['mime_type']}
            Created: {file_info['created']}
            
            Respond with just the category name (one word, lowercase) from these options:
            documents, images, audio, video, archives, code, data, downloads, other
            """
            
            completion = self.client.chat.completions.create(
                model="llama-3.2-3b-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful file organization assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            category = completion.choices[0].message.content.strip().lower()
            return category if category in ["documents", "images", "audio", "video", "archives", "code", "data", "downloads", "other"] else "other"
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

class ClaudeFileOrganizer:
    def __init__(self, api_key: str, source_dir: Path, provider_type: str = "claude"):
        """Initialize the File Organizer."""
        self.source_dir = source_dir
        self.organized_dir = self.source_dir / "organized"
        
        # Initialize AI provider
        if provider_type == "claude":
            self.ai_provider = ClaudeProvider(api_key)
        elif provider_type == "openai":
            self.ai_provider = OpenAIProvider(api_key)
        elif provider_type == "groq":
            self.ai_provider = GroqProvider(api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_type}")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_organizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_file_info(self, file_path: Path) -> Dict:
        """Get file information including type, size, and creation date."""
        stats = file_path.stat()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d"),
            "mime_type": mime_type or "unknown"
        }

    def classify_file(self, file_info: Dict) -> str:
        try:
            return self.ai_provider.classify_file(file_info)
        except Exception as e:
            self.logger.error(f"Error classifying file {file_info['name']}: {str(e)}")
            return "other"

    def organize_files(self, progress_callback: Callable[[int], None] = None,
                      file_callback: Callable[[str], None] = None,
                      pause_check: Callable[[], bool] = None,
                      cancel_check: Callable[[], bool] = None):
        """Main method to organize files using AI classification."""
        try:
            # Create organized directory if it doesn't exist
            self.organized_dir.mkdir(exist_ok=True)
            
            # Get list of files
            files = [f for f in self.source_dir.iterdir() 
                    if f.is_file() and f != "file_organizer.log" 
                    and not str(f).startswith(str(self.organized_dir))]
            
            if not files:
                return

            total_files = len(files)
            processed_files = 0
            
            for file_path in files:
                try:
                    # Check for cancellation
                    if cancel_check and cancel_check():
                        return

                    # Check for pause
                    while pause_check and pause_check():
                        time.sleep(0.1)
                        if cancel_check and cancel_check():
                            return

                    # Sleep to avoid rate limiting
                    time.sleep(5)
                    
                    # Update progress
                    processed_files += 1
                    if progress_callback:
                        progress_callback(int((processed_files / total_files) * 100))
                    
                    if file_callback:
                        file_callback(file_path.name)
                    
                    # Get file information and classify
                    file_info = self.get_file_info(file_path)
                    category = self.classify_file(file_info)
                    
                    # Create category directory
                    category_dir = self.organized_dir / category
                    category_dir.mkdir(exist_ok=True)
                    
                    # Move file
                    new_path = category_dir / file_path.name
                    if new_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_path = category_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    
                    shutil.move(str(file_path), str(new_path))
                    self.logger.info(f"Moved {file_path.name} to {category}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error during organization process: {str(e)}")
            raise