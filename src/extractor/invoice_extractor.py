import re
import yaml
import os
from typing import Dict, Optional, List, Tuple, Union, Any


class InvoiceExtractor:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rules.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.invoice_types = self.config.get('invoice_types', {})

    def detect_invoice_type(self, text: str,
                            qr_codes: Optional[List[str]] = None) -> str:
        """
        根据文本内容和二维码判断发票类型
        
        同程商旅的用车/住宿确认单优先以二维码中的协议头为准，避免文本中
        的字母/站点等关键词被误判为高铁票。
        
        Args:
            text: PDF提取的文本
            qr_codes: 当前页面识别到的二维码内容列表
            
        Returns:
            发票类型字符串 (train/hotel/car/invoice/unknown)
        """
        qr_codes = qr_codes or []
        
        # 优先根据二维码协议头判断同程商旅确认单类型
        for qr_data in qr_codes:
            if isinstance(qr_data, str):
                if qr_data.startswith('etripCar://'):
                    return 'car'
                elif qr_data.startswith('etripHotel://'):
                    return 'hotel'
        
        # 否则按文本关键词判断
        for invoice_type, config in self.invoice_types.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword in text:
                    return invoice_type
        
        return 'unknown'

    def extract_fields(self, text: str, invoice_type: str,
                       qr_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        根据发票类型提取关键字段
        
        Args:
            text: PDF提取的文本
            invoice_type: 发票类型
            qr_codes: 当前页面识别到的二维码内容列表，用于优先获取用车/住宿金额
            
        Returns:
            提取的字段字典
        """
        result = {'type': invoice_type}
        qr_codes = qr_codes or []
        
        if invoice_type not in self.invoice_types:
            return result
            
        patterns = self.invoice_types[invoice_type].get('patterns', {})
        
        for field_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    if field_name == 'departure_time' and len(match.groups()) == 4:
                        result[field_name] = f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}"
                    else:
                        result[field_name] = match.group(1).strip()
                    break
        
        # 对于用车和住宿确认单，优先使用二维码中的金额，准确率更高
        qr_amount = self._extract_amount_from_qr(qr_codes, invoice_type)
        if qr_amount is not None:
            result['amount'] = qr_amount
            result['qr_amount'] = True
        else:
            amount = self.extract_amount(text)
            if amount is not None:
                result['amount'] = amount
        
        return result

    def _extract_amount_from_qr(self, qr_codes: List[str],
                                invoice_type: str) -> Optional[float]:
        """
        从二维码内容中提取同程商旅用车/住宿金额
        
        二维码格式示例：
        - etripCar://745322,闫兴,DC260623184746145505,68.26
        - etripHotel://870667,闫兴,2485235576652567552,3261.0
        最后一个逗号后的字段即为金额。
        
        Args:
            qr_codes: 二维码内容列表
            invoice_type: 当前发票类型 (hotel/car)
            
        Returns:
            提取到的金额，未匹配到则返回None
        """
        prefix_map = {
            'car': 'etripCar://',
            'hotel': 'etripHotel://'
        }
        prefix = prefix_map.get(invoice_type)
        if not prefix:
            return None
        
        for qr_data in qr_codes:
            if not isinstance(qr_data, str) or not qr_data.startswith(prefix):
                continue
            
            payload = qr_data[len(prefix):]
            parts = payload.split(',')
            if len(parts) < 4:
                continue
            
            try:
                return float(parts[-1])
            except ValueError:
                continue
        
        return None

    def extract_amount(self, text: str) -> Optional[float]:
        """
        从文本中提取金额
        
        Args:
            text: PDF提取的文本
            
        Returns:
            金额（浮点数），提取失败返回None
        """
        amount_patterns = [
            r"价税合计[：:]?\s*([\d.]+)元?",
            r"实付金额[：:]?\s*([\d.]+)",
            r"费用合计[：:]?\s*([\d.]+)",
            r"合+计+[：:]?\s*([\d.]+)(?:\s+\d+\s+\d+\s+([\d.]+))?",
            r"金额[：:]?\s*([\d.]+)元?",
            r"[￥¥]\s*([\d.]+)",
            r"总金额[：:]?\s*([\d.]+)",
            r"订单金额[：:]?\s*([\d.]+)"
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    for group in reversed(match.groups()):
                        if group is not None:
                            return float(group)
                except ValueError:
                    continue

        return None
