from MeloTTS.melo.api import TTS
import torch
import threading
from typing import Dict, Literal, Optional, Union
import time

import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SupportedModesType = Literal['deepgram', 'melo', 'google']

class MeloTTS():
    def __init__(self, language: str = 'EN', device: str = 'auto'):
        self.language = language
        self._init_device(device)
        self.model = None
        self.speaker_ids = None
        self._model_lock = threading.Lock()
        self._init_model()
        
    def _init_device(self, device: str):
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        logger.info(f"Using device: {self.device}")
        
    def _init_model(self):
        try:
            with self._model_lock:
                if self.model is None:
                    self.model = TTS(language=self.language, device=self.device)
                    self.speaker_ids = self.model.hps.data.spk2id
                    logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000) -> list:
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def generate_speech(self, 
                        text: str, 
                        speaker_id: Optional[str] = None, 
                        output_path: str = 'output.wav',
                        speed: float = 1.0,
                        chunk_size: int = 1000) -> Dict[str, Union[bool, str, float]]:
        start_time = time.time()
        result = {
            'success': False,
            'message': '',
            'processing_time': 0
        }
        
        try:
            if speaker_id is None:
                speaker_id = 'EN-US'
                
            if speaker_id not in self.speaker_ids:
                raise ValueError(f"Invalid speaker_id. Available options: {list(self.speaker_ids.keys())}")
            
            text_chunks = self._chunk_text(text, chunk_size)
            
            with self._model_lock:
                for i, chunk in enumerate(text_chunks):
                    chunk_output = f"temp_chunk_{i}.wav" if i < len(text_chunks) - 1 else output_path
                    self.model.tts_to_file(
                        chunk, 
                        self.speaker_ids[speaker_id], 
                        chunk_output, 
                        speed=speed
                    )
            
            result['success'] = True
            result['message'] = f"Speech generated successfully and saved to {output_path}"
            
        except Exception as e:
            result['message'] = f"Error generating speech: {str(e)}"
            logger.error(result['message'])
        
        result['processing_time'] = time.time() - start_time
        return result

    def batch_generate_speech(self, 
                             texts: list, 
                             speaker_id: Optional[str] = None,
                             speed: float = 1.0,
                             max_workers: int = 3) -> Dict[str, list]:
        results = {
            'successful': [],
            'failed': []
        }
        
        def process_text(text, index):
            output_path = f'output_{index}.wav'
            result = self.generate_speech(text, speaker_id, output_path, speed)
            return index, result, output_path

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_text, text, i) for i, text in enumerate(texts)]
            
            for future in futures:
                index, result, output_path = future.result()
                if result['success']:
                    results['successful'].append({
                        'index': index,
                        'output_path': output_path,
                        'processing_time': result['processing_time']
                    })
                else:
                    results['failed'].append({
                        'index': index,
                        'error': result['message']
                    })
        
        return results

def main():
    tts_wrapper = MeloTTS()
    
    text = "Bro ate and left no crumb " * 4
    
    result = tts_wrapper.generate_speech(
        text=text,
        output_path='en-us.wav',
        speed=1.0
    )
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Processing time: {result['processing_time']:.2f} seconds")
    
    texts = [
        "This is the first text to convert.",
        "Here's another text to process.",
        "And one final text for good measure."
    ]
    
    batch_results = tts_wrapper.batch_generate_speech(texts)
    print("\nBatch Processing Results:")
    print(f"Successful: {len(batch_results['successful'])}")
    print(f"Failed: {len(batch_results['failed'])}")

if __name__ == "__main__":
    main()