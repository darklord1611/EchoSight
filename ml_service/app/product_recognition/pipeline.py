import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
import pandas as pd
from typing import Dict, Any, Optional

class BarcodeProcessor:
    def __init__(self):
        pass 
    def detect_barcode(self, image: np.ndarray) -> Optional[str]:
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Decode barcodes in the grayscale image
        barcodes = decode(gray)
        
        if not barcodes:
            raise ValueError("No barcode detected")
        
        # Return the first detected barcode data
        return barcodes[0].data.decode('utf-8')
    
    def get_product_info(self, barcode: str) -> Dict[str, Any]:
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 1:
                    product = data['product']
                    nutriments = product.get('nutriments', {})
                    result = {
                        'name': product.get('product_name', 'Unknown'),
                        'type': product.get('product_type', 'Unknown'),
                        'quantity': product.get('quantity', 'Unknown'),
                        'brand': product.get('brands', 'Unknown'),
                        'category': product.get('categories', 'Unknown'),
                    }
                    nutrition = {
                        'energy_kcal': nutriments.get('energy-kcal_100g', 'Unknown'),
                        'fat': nutriments.get('fat_100g', 'Unknown'),
                        'saturated_fat': nutriments.get('saturated-fat_100g', 'Unknown'),
                        'carbohydrates': nutriments.get('carbohydrates_100g', 'Unknown'),
                        'sugars': nutriments.get('sugars_100g', 'Unknown'),
                        'proteins': nutriments.get('proteins_100g', 'Unknown'),
                        'salt': nutriments.get('salt_100g', 'Unknown'),
                        'sodium': nutriments.get('sodium_100g', 'Unknown'),
                    }
                    
                    result['nutrition'] = nutrition
                    
                    result = self.format_result(result)
                    return result
        except requests.RequestException as e:
            print(f"Error fetching product info: {e}")
        
        return {'error': 'Product not found'}

    def process_image(self, image_path: str) -> Dict[str, Any]:
        barcode = self.detect_barcode(image_path)
        if barcode:
            print(f"Detected barcode: {barcode}")
            return self.get_product_info(barcode)
        return {'error': 'No barcode detected'}

    def format_result(self, result: Dict[str, Any]) -> str:
        output = []
        if 'error' not in result:
            output.append("Product Information:")
            for key, value in result.items():
                if key == 'nutrition':
                    output.append("\nNutritional Information (per 100g):")
                    for nutrient, amount in value.items():
                        output.append(f"  {nutrient.replace('_', ' ').title()}: {amount}")
                else:
                    output.append(f"{key.capitalize()}: {value}")
        else:
            output.append(f"Error: {result['error']}")
        return "\n".join(output)


def main():
    processor = BarcodeProcessor()
    image_path = '/home/xuananle/Documents/Learn/HMI/VisionMate/AI/app/product_recognition/image.png'
    
    try:
        result = processor.process_image(image_path)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()