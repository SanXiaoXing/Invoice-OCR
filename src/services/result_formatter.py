"""结果展示格式化服务 — 将原始识别结果转为 UI 友好的展示数据"""

from typing import Dict

TYPE_MAP = {
    'train': '高铁票',
    'hotel': '酒店住宿',
    'car': '市内用车',
    'invoice': '发票',
    'unknown': '未知',
}


def format_result_row(result: Dict) -> Dict:
    """将原始识别结果转为 UI 友好的展示数据

    Args:
        result: 原始识别结果字典

    Returns:
        包含 type_label/name/date/amount/status/status_color 的字典
    """
    amount = result.get('amount', '0')
    has_amount = bool(amount)

    return {
        'type_label': TYPE_MAP.get(result.get('type'), '未知'),
        'name': result.get('train_number', '') or result.get('hotel_name', '') or result.get('filename', ''),
        'date': result.get('departure_time', '') or result.get('check_in_date', '') or result.get('car_date', ''),
        'amount': f"¥{amount}",
        'status': '已识别' if has_amount else '未识别金额',
        'status_color': '#047857' if has_amount else '#B45309',
    }
