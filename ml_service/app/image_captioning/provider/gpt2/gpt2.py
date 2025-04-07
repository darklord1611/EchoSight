from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image
from typing import List, Union
import logging
import io
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageCaptioningPipeline:
    def __init__(self, model_path: str = "nlpconnect/vit-gpt2-image-captioning",
                 max_length: int = 16, num_beams: int = 4, batch_size: int = 8):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = max_length
        self.num_beams = num_beams
        self.batch_size = batch_size

        logger.info(f"Loading model from {model_path}")
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        self.model.to(self.device)
        if self.device.type == 'cuda':
            self.model = self.model.half()  # FP16 for faster inference
        self.model.eval()

        self.model.gradient_checkpointing_enable()

        # Warmup
        logger.info("Warming up model...")
        dummy_image = torch.randn(1, 3, 224, 224, device=self.device)
        if self.device.type == 'cuda':
            dummy_image = dummy_image.half()
        with torch.no_grad():
            _ = self.model.generate(dummy_image,
                                    max_length=self.max_length,
                                    num_beams=self.num_beams)

        self.gen_kwargs = {
            "max_length": max_length,
            "num_beams": num_beams,
            "pad_token_id": self.tokenizer.pad_token_id,
            "use_cache": True
        }

    @staticmethod
    def load_image(image_path: Union[str, bytes, Image.Image]) -> Image.Image:
        if isinstance(image_path, str):
            image = Image.open(image_path)
        elif isinstance(image_path, bytes):
            image = Image.open(io.BytesIO(image_path))
        elif isinstance(image_path, Image.Image):
            image = image_path
        else:
            raise ValueError(f"Unsupported image type: {type(image_path)}")

        if image.mode != "RGB":
            image = image.convert(mode="RGB")
        return image

    def preprocess_images(self, image_paths: List[Union[str, bytes, Image.Image]]) -> torch.Tensor:
        with ThreadPoolExecutor() as executor:
            images = list(executor.map(self.load_image, image_paths))
        pixel_values = self.feature_extractor(images=images, return_tensors="pt").pixel_values
        pixel_values = pixel_values.pin_memory() if self.device.type == 'cuda' else pixel_values
        if self.device.type == 'cuda':
            pass
            # pixel_values = pixel_values.half()
        return pixel_values.to(self.device, non_blocking=True)

    @torch.no_grad()
    def __call__(self, image_paths: List[Union[str, bytes, Image.Image]]) -> List[str]:
        pixel_values = self.preprocess_images(image_paths)

        with torch.amp.autocast('cuda', enabled=self.device.type == 'cuda'):  # Mixed precision
            output_ids = self.model.generate(
                pixel_values,
                **self.gen_kwargs
            )

        preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return [pred.strip() for pred in preds]

if __name__ == "__main__":
    pipeline = ImageCaptioningPipeline()
    image_paths = ['/home/automl/Xuanan/HMI/VisionMate/AI/image.png']

    logger.info("Running PyTorch pipeline...")
    start_time = time.time()

    captions = pipeline(image_paths)

    end_time = time.time()
    logger.info(f"Inference time: {end_time - start_time:.2f} seconds")

    for path, caption in zip(image_paths, captions):
        logger.info(f"{path}: {caption}")
