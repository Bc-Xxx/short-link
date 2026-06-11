from pyzbar.pyzbar import decode
from PIL import Image
from typing import Optional
import tempfile
import os


def scan_qrcode_from_image(image_path: str) -> Optional[str]:
    """
    从图片文件路径识别二维码内容
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        二维码内容（通常是URL），如果识别失败返回None
    """
    try:
        img = Image.open(image_path)
        decoded_objects = decode(img)
        
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            if data.startswith(('http://', 'https://')):
                return data
                
        return None
    except Exception:
        return None


def scan_qrcode_from_bytes(image_bytes: bytes) -> Optional[str]:
    """
    从图片字节数据识别二维码内容
    
    Args:
        image_bytes: 图片字节数据
        
    Returns:
        二维码内容（通常是URL），如果识别失败返回None
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name
        
        result = scan_qrcode_from_image(tmp_path)
        os.unlink(tmp_path)
        
        return result
    except Exception:
        return None