"""
CAPTCHA Generator Utility
Custom image-based CAPTCHA for security
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os
from django.conf import settings


class CaptchaGenerator:
    """
    Generate custom CAPTCHA images
    """
    
    @staticmethod
    def generate_captcha_text(length=6):
        """Generate random CAPTCHA text"""
        characters = string.ascii_uppercase + string.digits
        # Exclude confusing characters
        characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def create_captcha_image(text, width=200, height=80):
        """
        Create CAPTCHA image with text
        Returns: PIL Image object
        """
        # Create image with white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Add background noise (lines)
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)
        
        # Add background noise (dots)
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill='lightgray')
        
        # Try to use a system font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with slight rotation
        for i, char in enumerate(text):
            char_x = x + (i * text_width // len(text))
            char_y = y + random.randint(-5, 5)
            
            # Random color for each character
            color = (
                random.randint(0, 100),
                random.randint(0, 100),
                random.randint(0, 100)
            )
            
            draw.text((char_x, char_y), char, font=font, fill=color)
        
        # Apply slight blur
        image = image.filter(ImageFilter.SMOOTH)
        
        return image
    
    @staticmethod
    def save_captcha(text, filename):
        """
        Generate and save CAPTCHA image
        Returns: filepath
        """
        image = CaptchaGenerator.create_captcha_image(text)
        
        # Ensure captcha directory exists
        captcha_dir = os.path.join(settings.MEDIA_ROOT, 'captcha')
        os.makedirs(captcha_dir, exist_ok=True)
        
        filepath = os.path.join(captcha_dir, filename)
        image.save(filepath)
        
        return filepath
    
    @staticmethod
    def generate_and_save(session_key):
        """
        Generate CAPTCHA, save image, and return text and path
        """
        text = CaptchaGenerator.generate_captcha_text()
        filename = f'captcha_{session_key}.png'
        filepath = CaptchaGenerator.save_captcha(text, filename)
        
        return text, filename
