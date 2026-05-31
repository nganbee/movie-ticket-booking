import hashlib
import hmac
import urllib.parse
from datetime import datetime
from src.config.settings import settings

class VNPayService:
    @staticmethod
    def generate_payment_url(order_id: str, amount: int, order_info: str, ip_addr: str) -> str:
        vnp_TmnCode = settings.VNPAY_TMN_CODE
        vnp_HashSecret = settings.VNPAY_HASH_SECRET
        vnp_Url = settings.VNPAY_PAYMENT_URL
        vnp_ReturnUrl = settings.VNPAY_RETURN_URL
        
        input_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Amount": str(amount * 100),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": vnp_ReturnUrl,
            "vnp_IpAddr": ip_addr,
            "vnp_CreateDate": datetime.now().strftime('%Y%m%d%H%M%S')
        }
        
        # Sort data by key
        sorted_data = sorted(input_data.items())
        
        hasDataList = []
        for key, val in sorted_data:
            if str(val).strip() != '':
                hasDataList.append(key + "=" + urllib.parse.quote_plus(str(val)))
                
        query_string = "&".join(hasDataList)
        
        # Calculate Hash
        hash_value = hmac.new(vnp_HashSecret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha512).hexdigest()
        
        # Final URL
        payment_url = f"{vnp_Url}?{query_string}&vnp_SecureHash={hash_value}"
        return payment_url

    @staticmethod
    def validate_response(query_params: dict) -> bool:
        vnp_SecureHash = query_params.pop('vnp_SecureHash', '')
        # Ignore vnp_SecureHashType if it exists
        query_params.pop('vnp_SecureHashType', None)
        
        vnp_HashSecret = settings.VNPAY_HASH_SECRET
        
        # Sort data
        sorted_data = sorted(query_params.items())
        
        hasDataList = []
        for key, val in sorted_data:
            if str(val).strip() != '':
                hasDataList.append(key + "=" + urllib.parse.quote_plus(str(val)))
                
        query_string = "&".join(hasDataList)
        
        # Calculate hash
        hash_value = hmac.new(vnp_HashSecret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha512).hexdigest()
        
        return hash_value == vnp_SecureHash
