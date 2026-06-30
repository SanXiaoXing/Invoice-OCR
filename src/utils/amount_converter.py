_DIGIT_MAP = {
    '0': '零', '1': '壹', '2': '贰', '3': '叁', '4': '肆',
    '5': '伍', '6': '陆', '7': '柒', '8': '捌', '9': '玖'
}
_UNIT_MAP = ['元', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
_DECIMAL_UNIT = ['角', '分']


def convert(amount: float) -> str:
    """
    将数字金额转换为大写金额
    
    Args:
        amount: 数字金额
        
    Returns:
        大写金额字符串
    """
    if amount < 0:
        return "金额不能为负数"

    if amount == 0:
        return "零元整"

    amount_str = f"{amount:.2f}"
    integer_part, decimal_part = amount_str.split('.')

    integer_chinese = _convert_integer(integer_part)
    decimal_chinese = _convert_decimal(decimal_part)

    return integer_chinese + decimal_chinese if decimal_chinese else integer_chinese + "整"


def _convert_integer(integer_str: str) -> str:
    """转换整数部分"""
    result = []
    length = len(integer_str)

    for i, digit in enumerate(integer_str):
        pos = length - 1 - i
        unit = _UNIT_MAP[pos % len(_UNIT_MAP)]

        if digit == '0':
            if result and result[-1] != '零':
                result.append('零')
        else:
            if result and result[-1] == '零' and i > 0:
                result.pop()
            result.append(_DIGIT_MAP[digit])
            result.append(unit)

    while result and result[-1] == '零':
        result.pop()

    return ''.join(result)


def _convert_decimal(decimal_str: str) -> str:
    """转换小数部分"""
    result = []

    if decimal_str[0] != '0':
        result.append(_DIGIT_MAP[decimal_str[0]])
        result.append(_DECIMAL_UNIT[0])

    if decimal_str[1] != '0':
        result.append(_DIGIT_MAP[decimal_str[1]])
        result.append(_DECIMAL_UNIT[1])

    return ''.join(result)
