from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from typing import List, Dict
import os
from datetime import datetime
from src.utils import amount_converter
from src.utils.logger import logger


class ReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, invoice_data_list: List[Dict], output_path: str) -> bool:
        try:
            logger.info(f"[ReportGenerator] 开始生成报销单: {output_path}")
            wb = Workbook()
            ws = wb.active
            ws.title = "差旅费用报销单"
            
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            title_font = Font(name='微软雅黑', bold=True, size=18)
            header_font = Font(name='微软雅黑', bold=True, size=11)
            normal_font = Font(name='微软雅黑', size=10)
            
            gray_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
            
            row = 1
            
            ws.merge_cells(f'A{row}:O{row}')
            ws[f'A{row}'] = "差旅费用报销单"
            ws[f'A{row}'].font = title_font
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            row += 1
            
            ws[f'B{row}'] = f"报销日期：{datetime.now().strftime('%Y')}年{datetime.now().strftime('%m')}月{datetime.now().strftime('%d')}日"
            ws[f'B{row}'].font = normal_font
            ws[f'M{row}'] = "编号："
            ws[f'M{row}'].font = normal_font
            row += 1
            
            ws[f'A{row}'] = "部门："
            ws[f'A{row}'].font = normal_font
            ws.merge_cells(f'B{row}:F{row}')
            ws[f'B{row}'] = ""
            ws[f'B{row}'].font = normal_font
            row += 2
            
            ws.merge_cells(f'A{row}:B{row}')
            ws[f'A{row}'] = "出差人"
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'C{row}:F{row}')
            ws[f'C{row}'] = "出差事由"
            ws[f'C{row}'].font = header_font
            ws[f'C{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'G{row}:O{row}')
            ws[f'G{row}'] = "项目名称"
            ws[f'G{row}'].font = header_font
            ws[f'G{row}'].alignment = Alignment(horizontal='center', vertical='center')
            row += 1
            
            ws[f'A{row}'] = "出"
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'B{row}'] = "发"
            ws[f'B{row}'].font = header_font
            ws[f'B{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'C{row}'] = "到"
            ws[f'C{row}'].font = header_font
            ws[f'C{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'D{row}'] = "达"
            ws[f'D{row}'].font = header_font
            ws[f'D{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'E{row}:F{row}')
            ws[f'E{row}'] = "交通"
            ws[f'E{row}'].font = header_font
            ws[f'E{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'G{row}:H{row}')
            ws[f'G{row}'] = "出差补助"
            ws[f'G{row}'].font = header_font
            ws[f'G{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'I{row}:O{row}')
            ws[f'I{row}'] = "其他费用金额"
            ws[f'I{row}'].font = header_font
            ws[f'I{row}'].alignment = Alignment(horizontal='center', vertical='center')
            row += 1
            
            ws[f'A{row}'] = "月"
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'B{row}'] = "日"
            ws[f'B{row}'].font = header_font
            ws[f'B{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'C{row}'] = "时"
            ws[f'C{row}'].font = header_font
            ws[f'C{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'D{row}'] = "地点"
            ws[f'D{row}'].font = header_font
            ws[f'D{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'E{row}'] = "月"
            ws[f'E{row}'].font = header_font
            ws[f'E{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'F{row}'] = "日"
            ws[f'F{row}'].font = header_font
            ws[f'F{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'G{row}'] = "时"
            ws[f'G{row}'].font = header_font
            ws[f'G{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'H{row}'] = "地点"
            ws[f'H{row}'].font = header_font
            ws[f'H{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws.merge_cells(f'I{row}:J{row}')
            ws[f'I{row}'] = "交通"
            ws[f'I{row}'].font = header_font
            ws[f'I{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'K{row}'] = "金额"
            ws[f'K{row}'].font = header_font
            ws[f'K{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'L{row}'] = "人数"
            ws[f'L{row}'].font = header_font
            ws[f'L{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'M{row}'] = "天数"
            ws[f'M{row}'].font = header_font
            ws[f'M{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'N{row}'] = "补助金额"
            ws[f'N{row}'].font = header_font
            ws[f'N{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'O{row}'] = "住宿"
            ws[f'O{row}'].font = header_font
            ws[f'O{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'P{row}'] = "市内交通"
            ws[f'P{row}'].font = header_font
            ws[f'P{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'Q{row}'] = "其他"
            ws[f'Q{row}'].font = header_font
            ws[f'Q{row}'].alignment = Alignment(horizontal='center', vertical='center')
            
            ws[f'R{row}'] = "合计"
            ws[f'R{row}'].font = header_font
            ws[f'R{row}'].alignment = Alignment(horizontal='center', vertical='center')
            row += 1
            
            train_data = [d for d in invoice_data_list if d.get('type') == 'train']
            hotel_data = [d for d in invoice_data_list if d.get('type') == 'hotel']
            car_data = [d for d in invoice_data_list if d.get('type') == 'car']
            invoice_data = [d for d in invoice_data_list if d.get('type') == 'invoice']
            
            train_total = sum(float(d.get('amount', '0')) for d in train_data)
            hotel_total = sum(float(d.get('amount', '0')) for d in hotel_data)
            car_total = sum(float(d.get('amount', '0')) for d in car_data)
            invoice_total = sum(float(d.get('amount', '0')) for d in invoice_data)
            
            for i, train in enumerate(train_data):
                dep_time = train.get('departure_time', '')
                arr_time = ''
                
                if dep_time:
                    date_part = dep_time.split(' ')[0]
                    time_part = dep_time.split(' ')[1] if ' ' in dep_time else ''
                    month = date_part.split('-')[1] if '-' in date_part else ''
                    day = date_part.split('-')[2] if '-' in date_part else ''
                    hour = time_part.split(':')[0] if ':' in time_part else ''
                else:
                    month = day = hour = ''
                
                ws[f'A{row}'] = month.replace('0', '') if month else ''
                ws[f'A{row}'].font = normal_font
                ws[f'A{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'B{row}'] = day.replace('0', '') if day else ''
                ws[f'B{row}'].font = normal_font
                ws[f'B{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'C{row}'] = hour.replace('0', '') if hour else ''
                ws[f'C{row}'].font = normal_font
                ws[f'C{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'D{row}'] = train.get('departure_station', '')
                ws[f'D{row}'].font = normal_font
                
                ws[f'E{row}'] = month.replace('0', '') if month else ''
                ws[f'E{row}'].font = normal_font
                ws[f'E{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'F{row}'] = day.replace('0', '') if day else ''
                ws[f'F{row}'].font = normal_font
                ws[f'F{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'G{row}'] = ''
                ws[f'G{row}'].font = normal_font
                ws[f'G{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'H{row}'] = train.get('arrival_station', '')
                ws[f'H{row}'].font = normal_font
                
                ws[f'I{row}'] = train.get('train_number', '')
                ws[f'I{row}'].font = normal_font
                ws[f'I{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'J{row}'] = ''
                ws[f'J{row}'].font = normal_font
                
                ws[f'K{row}'] = float(train.get('amount', '0'))
                ws[f'K{row}'].font = normal_font
                ws[f'K{row}'].alignment = Alignment(horizontal='right')
                
                ws[f'L{row}'] = 1
                ws[f'L{row}'].font = normal_font
                ws[f'L{row}'].alignment = Alignment(horizontal='center')
                
                ws[f'M{row}'] = ''
                ws[f'M{row}'].font = normal_font
                
                ws[f'N{row}'] = ''
                ws[f'N{row}'].font = normal_font
                
                ws[f'O{row}'] = ''
                ws[f'O{row}'].font = normal_font
                
                ws[f'P{row}'] = ''
                ws[f'P{row}'].font = normal_font
                
                ws[f'Q{row}'] = ''
                ws[f'Q{row}'].font = normal_font
                
                ws[f'R{row}'] = float(train.get('amount', '0'))
                ws[f'R{row}'].font = normal_font
                ws[f'R{row}'].alignment = Alignment(horizontal='right')
                
                row += 1
            
            if hotel_data:
                ws[f'A{row}'] = ''
                ws[f'B{row}'] = ''
                ws[f'C{row}'] = ''
                ws[f'D{row}'] = ''
                ws[f'E{row}'] = ''
                ws[f'F{row}'] = ''
                ws[f'G{row}'] = ''
                ws[f'H{row}'] = ''
                ws[f'I{row}'] = ''
                ws[f'J{row}'] = ''
                ws[f'K{row}'] = ''
                ws[f'L{row}'] = ''
                ws[f'M{row}'] = ''
                ws[f'N{row}'] = ''
                ws[f'O{row}'] = hotel_total
                ws[f'O{row}'].font = normal_font
                ws[f'O{row}'].alignment = Alignment(horizontal='right')
                ws[f'P{row}'] = ''
                ws[f'Q{row}'] = ''
                ws[f'R{row}'] = hotel_total
                ws[f'R{row}'].font = normal_font
                ws[f'R{row}'].alignment = Alignment(horizontal='right')
                row += 1
            
            if car_data:
                ws[f'A{row}'] = ''
                ws[f'B{row}'] = ''
                ws[f'C{row}'] = ''
                ws[f'D{row}'] = ''
                ws[f'E{row}'] = ''
                ws[f'F{row}'] = ''
                ws[f'G{row}'] = ''
                ws[f'H{row}'] = ''
                ws[f'I{row}'] = ''
                ws[f'J{row}'] = ''
                ws[f'K{row}'] = ''
                ws[f'L{row}'] = ''
                ws[f'M{row}'] = ''
                ws[f'N{row}'] = ''
                ws[f'O{row}'] = ''
                ws[f'P{row}'] = car_total
                ws[f'P{row}'].font = normal_font
                ws[f'P{row}'].alignment = Alignment(horizontal='right')
                ws[f'Q{row}'] = ''
                ws[f'R{row}'] = car_total
                ws[f'R{row}'].font = normal_font
                ws[f'R{row}'].alignment = Alignment(horizontal='right')
                row += 1
            
            if invoice_data:
                ws[f'A{row}'] = ''
                ws[f'B{row}'] = ''
                ws[f'C{row}'] = ''
                ws[f'D{row}'] = ''
                ws[f'E{row}'] = ''
                ws[f'F{row}'] = ''
                ws[f'G{row}'] = ''
                ws[f'H{row}'] = ''
                ws[f'I{row}'] = ''
                ws[f'J{row}'] = ''
                ws[f'K{row}'] = ''
                ws[f'L{row}'] = ''
                ws[f'M{row}'] = ''
                ws[f'N{row}'] = ''
                ws[f'O{row}'] = ''
                ws[f'P{row}'] = ''
                ws[f'Q{row}'] = invoice_total
                ws[f'Q{row}'].font = normal_font
                ws[f'Q{row}'].alignment = Alignment(horizontal='right')
                ws[f'R{row}'] = invoice_total
                ws[f'R{row}'].font = normal_font
                ws[f'R{row}'].alignment = Alignment(horizontal='right')
                row += 1
            
            ws[f'A{row}'] = ''
            ws[f'B{row}'] = ''
            ws[f'C{row}'] = ''
            ws[f'D{row}'] = ''
            ws[f'E{row}'] = ''
            ws[f'F{row}'] = ''
            ws[f'G{row}'] = ''
            ws[f'H{row}'] = ''
            ws[f'I{row}'] = ''
            ws[f'J{row}'] = ''
            ws[f'K{row}'] = ''
            ws[f'L{row}'] = ''
            ws[f'M{row}'] = ''
            ws[f'N{row}'] = ''
            ws[f'O{row}'] = ''
            ws[f'P{row}'] = ''
            ws[f'Q{row}'] = ''
            row += 1
            
            ws[f'A{row}'] = ''
            ws[f'B{row}'] = ''
            ws[f'C{row}'] = ''
            ws[f'D{row}'] = ''
            ws[f'E{row}'] = ''
            ws[f'F{row}'] = ''
            ws[f'G{row}'] = ''
            ws[f'H{row}'] = ''
            ws[f'I{row}'] = "合计"
            ws[f'I{row}'].font = header_font
            ws[f'I{row}'].alignment = Alignment(horizontal='center')
            
            ws[f'J{row}'] = ''
            
            ws[f'K{row}'] = train_total
            ws[f'K{row}'].font = header_font
            ws[f'K{row}'].alignment = Alignment(horizontal='right')
            
            ws[f'L{row}'] = ''
            
            ws[f'M{row}'] = ''
            
            ws[f'N{row}'] = ''
            
            ws[f'O{row}'] = hotel_total
            ws[f'O{row}'].font = header_font
            ws[f'O{row}'].alignment = Alignment(horizontal='right')
            
            ws[f'P{row}'] = car_total
            ws[f'P{row}'].font = header_font
            ws[f'P{row}'].alignment = Alignment(horizontal='right')
            
            ws[f'Q{row}'] = invoice_total
            ws[f'Q{row}'].font = header_font
            ws[f'Q{row}'].alignment = Alignment(horizontal='right')
            
            total_amount = train_total + hotel_total + car_total + invoice_total
            ws[f'R{row}'] = total_amount
            ws[f'R{row}'].font = header_font
            ws[f'R{row}'].alignment = Alignment(horizontal='right')
            row += 2
            
            ws[f'A{row}'] = "报销总额（大写）："
            ws[f'A{row}'].font = header_font
            
            ws.merge_cells(f'B{row}:N{row}')
            chinese_amount = amount_converter.convert(total_amount)
            ws[f'B{row}'] = chinese_amount
            ws[f'B{row}'].font = Font(name='微软雅黑', bold=True, size=12)
            
            ws[f'O{row}'] = f"¥{total_amount:.2f}"
            ws[f'O{row}'].font = Font(name='微软雅黑', bold=True, size=12)
            ws[f'O{row}'].alignment = Alignment(horizontal='right')
            row += 1
            
            ws[f'A{row}'] = "预借金额："
            ws[f'A{row}'].font = normal_font
            
            ws.merge_cells(f'B{row}:N{row}')
            ws[f'B{row}'] = "¥"
            ws[f'B{row}'].font = normal_font
            
            ws[f'O{row}'] = "退/补金额："
            ws[f'O{row}'].font = normal_font
            
            ws.merge_cells(f'P{row}:R{row}')
            ws[f'P{row}'] = "¥"
            ws[f'P{row}'].font = normal_font
            row += 2
            
            ws[f'A{row}'] = "附单据张数合计（对应上方的项目）"
            ws[f'A{row}'].font = normal_font
            
            ws[f'F{row}'] = "城际交通："
            ws[f'F{row}'].font = normal_font
            
            ws[f'G{row}'] = len(train_data)
            ws[f'G{row}'].font = normal_font
            ws[f'G{row}'].alignment = Alignment(horizontal='center')
            
            ws[f'I{row}'] = "其他："
            ws[f'I{row}'].font = normal_font
            
            ws[f'J{row}'] = len(hotel_data) + len(car_data) + len(invoice_data)
            ws[f'J{row}'].font = normal_font
            ws[f'J{row}'].alignment = Alignment(horizontal='center')
            row += 2
            
            ws[f'A{row}'] = "领导批示"
            ws[f'A{row}'].font = header_font
            
            ws.merge_cells(f'B{row}:E{row}')
            ws[f'B{row}'] = ""
            ws[f'B{row}'].font = normal_font
            
            ws[f'F{row}'] = "部门主管"
            ws[f'F{row}'].font = header_font
            
            ws.merge_cells(f'G{row}:J{row}')
            ws[f'G{row}'] = ""
            ws[f'G{row}'].font = normal_font
            
            ws[f'K{row}'] = "财务主管"
            ws[f'K{row}'].font = header_font
            
            ws.merge_cells(f'L{row}:O{row}')
            ws[f'L{row}'] = ""
            ws[f'L{row}'].font = normal_font
            
            ws[f'P{row}'] = "会计"
            ws[f'P{row}'].font = header_font
            
            ws[f'Q{row}'] = ""
            ws[f'Q{row}'].font = normal_font
            
            ws[f'R{row}'] = "出纳"
            ws[f'R{row}'].font = header_font
            row += 1
            
            ws[f'S{row-1}'] = "领款人"
            ws[f'S{row-1}'].font = header_font
            
            for col in range(1, 19):
                ws.column_dimensions[get_column_letter(col)].width = 8
            
            for row_num in range(1, row + 1):
                for col_num in range(1, 19):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical='center', wrap_text=True)
            
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            wb.save(output_path)
            logger.info(f"[ReportGenerator] 报销单生成成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"[ReportGenerator] 生成报销单错误: {e}")
            import traceback
            traceback.print_exc()
            return False
