"""费用计算服务 — 纯业务逻辑，不依赖 UI"""

from typing import List, Dict
from src.utils import amount_converter

SUBSIDY_PER_DAY = 100


def calc_totals(results: List[Dict], days: int) -> Dict:
    """计算费用汇总，返回各分项及合计

    Args:
        results: 识别结果列表
        days: 出差天数

    Returns:
        包含 train/hotel/car/invoice/subsidy/advance/refund/total/chinese 的字典
    """
    train = sum(float(r.get('amount', '0')) for r in results if r.get('type') == 'train')
    hotel = sum(float(r.get('amount', '0')) for r in results if r.get('type') == 'hotel')
    car = sum(float(r.get('amount', '0')) for r in results if r.get('type') == 'car')
    invoice = sum(float(r.get('amount', '0')) for r in results if r.get('type') == 'invoice')

    subsidy = days * SUBSIDY_PER_DAY
    advance = hotel + invoice + car
    refund = train + subsidy
    total = train + hotel + car + invoice + subsidy
    chinese = amount_converter.convert(total)

    return {
        'train': train, 'hotel': hotel, 'car': car, 'invoice': invoice,
        'subsidy': subsidy, 'advance': advance, 'refund': refund,
        'total': total, 'chinese': chinese,
    }


def build_preview_rows(results: List[Dict], days: int) -> List[Dict]:
    """构建报销单预览行数据（纯数据，不含 QTableWidgetItem）

    每行包含:
        - cells: 长度为 8 的列表，对应 [出发地点, 到达地点, 交通金额, 住宿, 市内交通, 补助标准, 出差天数, 合计]
        - bold: 是否加粗显示

    Args:
        results: 识别结果列表
        days: 出差天数

    Returns:
        结构化行列表
    """
    train_data = [r for r in results if r.get('type') == 'train']
    hotel_data = [r for r in results if r.get('type') == 'hotel']
    car_data = [r for r in results if r.get('type') == 'car']
    invoice_data = [r for r in results if r.get('type') == 'invoice']

    train_total = sum(float(r.get('amount', '0')) for r in train_data)
    hotel_total = sum(float(r.get('amount', '0')) for r in hotel_data)
    car_total = sum(float(r.get('amount', '0')) for r in car_data)
    invoice_total = sum(float(r.get('amount', '0')) for r in invoice_data)

    subsidy_total = days * SUBSIDY_PER_DAY
    rows = []

    # 高铁票行
    for train in train_data:
        amount = float(train.get('amount', '0'))
        cells = [
            train.get('departure_station', ''),  # 出发地点
            train.get('arrival_station', ''),     # 到达地点
            amount,                                # 交通金额
            '',                                    # 住宿
            '',                                    # 市内交通
            '',                                    # 补助标准
            '',                                    # 出差天数
            amount,                                # 合计
        ]
        rows.append({'cells': cells, 'bold': False})

    # 住宿合计行
    if hotel_total:
        rows.append({'cells': ['住宿', '', '', hotel_total, '', '', '', hotel_total], 'bold': False})

    # 市内交通合计行
    if car_total:
        rows.append({'cells': ['市内交通', '', '', '', car_total, '', '', car_total], 'bold': False})

    # 其他发票行
    if invoice_total:
        rows.append({'cells': ['其他', '', invoice_total, '', '', '', '', invoice_total], 'bold': False})

    # 出差补助行
    if subsidy_total:
        rows.append({'cells': ['出差补助', '', '', '', '', SUBSIDY_PER_DAY, days, subsidy_total], 'bold': False})

    # 合计行
    total_amount = train_total + hotel_total + car_total + invoice_total + subsidy_total
    rows.append({
        'cells': [
            '合计', '',
            train_total + invoice_total,  # 交通金额合计
            hotel_total,                  # 住宿合计
            car_total,                    # 市内交通合计
            '',                           # 补助标准
            '',                           # 出差天数
            total_amount,                 # 总合计
        ],
        'bold': True,
    })

    return rows
