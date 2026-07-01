from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem,
    QLabel, QProgressBar, QFileDialog, QMessageBox,
    QSplitter, QGroupBox, QHeaderView, QSpinBox,
    QMenuBar, QMenu
)
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
import os
from src.parser.pdf_parser import PDFParser
from src.extractor.invoice_extractor import InvoiceExtractor
from src.utils import amount_converter
from src.ui.themes import get_theme_qss, THEMES
from src.utils.logger import logger


class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        try:
            logger.info(f"[WorkerThread] 开始识别，共 {len(self.file_paths)} 个文件")
            pdf_parser = PDFParser()
            extractor = InvoiceExtractor()
            results = []

            total = len(self.file_paths)
            processed_count = 0

            for i, file_path in enumerate(self.file_paths):
                logger.info(f"[WorkerThread] 处理文件 ({i + 1}/{total}): {os.path.basename(file_path)}")
                pages = pdf_parser.extract_text_by_page(file_path)
                qr_codes_by_page = pdf_parser.extract_qr_codes(file_path)
                qr_map = {page_num: codes for page_num, codes in qr_codes_by_page}

                if not pages:
                    logger.warning(f"[WorkerThread] 文件无文本内容: {os.path.basename(file_path)}")
                    processed_count += 1
                    progress = int(processed_count / total * 100)
                    self.progress.emit(progress)
                    continue

                for page_num, page_text in pages:
                    qr_codes = qr_map.get(page_num, [])
                    invoice_type = extractor.detect_invoice_type(page_text, qr_codes)
                    fields = extractor.extract_fields(page_text, invoice_type, qr_codes)
                    fields['filename'] = os.path.basename(file_path)
                    fields['full_path'] = file_path
                    fields['page_number'] = page_num
                    results.append(fields)
                    logger.info(f"[WorkerThread] 第 {page_num} 页识别结果: 类型={invoice_type}, 金额={fields.get('amount', '无')}")

                processed_count += 1
                progress = int(processed_count / total * 100)
                self.progress.emit(progress)

            logger.info(f"[WorkerThread] 识别完成，共 {len(results)} 条记录")
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"[WorkerThread] 识别过程异常: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("发票报销单自动生成系统")
        self.setMinimumSize(1200, 800)

        self.file_paths = []
        self.parsed_results = []
        self.current_theme = "清爽办公风"

        self.apply_theme(self.current_theme)
        self.init_ui()

    def apply_theme(self, theme_name):
        """应用指定主题"""
        logger.info(f"[MainWindow] 切换主题: {theme_name}")
        self.current_theme = theme_name
        self.setStyleSheet(get_theme_qss(theme_name))
        # 同步菜单栏选中状态
        if hasattr(self, 'theme_action_group'):
            for action in self.theme_action_group.actions():
                action.setChecked(action.text() == theme_name)

    def on_theme_action_triggered(self):
        """菜单栏主题切换回调"""
        action = self.sender()
        if action and action.text() != self.current_theme:
            self.apply_theme(action.text())
            # 切换主题后刷新界面显示
            self.update_preview()
            self.update_total()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        left_panel = self.build_left_panel()
        right_panel = self.build_right_panel()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([340, 820])
        splitter.setHandleWidth(2)
        main_layout.addWidget(splitter)

        # 顶部菜单栏主题切换（macOS 会自动合并到系统菜单栏）
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        view_menu = self.menu_bar.addMenu("视图")
        self.theme_menu = view_menu.addMenu("界面主题")

        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        for theme_name in THEMES.keys():
            action = QAction(theme_name, self)
            action.setCheckable(True)
            action.setChecked(theme_name == self.current_theme)
            action.triggered.connect(self.on_theme_action_triggered)
            self.theme_action_group.addAction(action)
            self.theme_menu.addAction(action)

    def build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # 文件上传区
        upload_group = QGroupBox("上传 PDF 文件")
        upload_layout = QVBoxLayout(upload_group)
        upload_layout.setSpacing(10)

        hint = QLabel("选择包含高铁票、酒店或用车确认单的 PDF 文件")
        hint.setObjectName("hint_label")
        hint.setWordWrap(True)
        upload_layout.addWidget(hint)

        self.upload_btn = QPushButton("添加 PDF 文件")
        self.upload_btn.setToolTip("添加一个或多个 PDF 文件")
        self.upload_btn.clicked.connect(self.upload_files)
        upload_layout.addWidget(self.upload_btn)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.setMinimumHeight(160)
        upload_layout.addWidget(self.file_list)

        file_actions = QHBoxLayout()
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.setObjectName("danger_btn")
        self.delete_btn.clicked.connect(self.delete_selected)
        file_actions.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_list)
        file_actions.addWidget(self.clear_btn)
        upload_layout.addLayout(file_actions)

        layout.addWidget(upload_group)

        # 操作区
        action_group = QGroupBox("识别")
        action_layout = QVBoxLayout(action_group)
        action_layout.setSpacing(10)

        self.recognize_btn = QPushButton("开始识别")
        self.recognize_btn.setObjectName("primary_btn")
        self.recognize_btn.setMinimumHeight(40)
        self.recognize_btn.clicked.connect(self.start_recognition)
        action_layout.addWidget(self.recognize_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        action_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("等待上传文件...")
        self.status_label.setObjectName("hint_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        action_layout.addWidget(self.status_label)

        layout.addWidget(action_group)

        # 出差设置
        travel_group = QGroupBox("出差设置")
        travel_layout = QVBoxLayout(travel_group)
        travel_layout.setSpacing(10)

        standard_hint = QLabel("补助标准：¥100 / 天")
        standard_hint.setObjectName("hint_label")
        travel_layout.addWidget(standard_hint)

        days_layout = QHBoxLayout()
        days_label = QLabel("出差天数：")
        days_layout.addWidget(days_label)

        self.days_spinbox = QSpinBox()
        self.days_spinbox.setRange(0, 999)
        self.days_spinbox.setValue(0)
        self.days_spinbox.setSuffix(" 天")
        self.days_spinbox.valueChanged.connect(self.on_days_changed)
        days_layout.addWidget(self.days_spinbox)
        travel_layout.addLayout(days_layout)

        layout.addWidget(travel_group)

        # 费用汇总
        summary_group = QGroupBox("费用汇总")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setSpacing(8)

        self.total_label = QLabel("¥ 0.00")
        self.total_label.setObjectName("total_value")
        self.total_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.total_label)

        self.chinese_label = QLabel("零元整")
        self.chinese_label.setObjectName("total_chinese")
        self.chinese_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.chinese_label)

        detail_layout = QHBoxLayout()

        advance_layout = QVBoxLayout()
        advance_title = QLabel("预借金额")
        advance_title.setObjectName("hint_label")
        advance_title.setAlignment(Qt.AlignCenter)
        advance_layout.addWidget(advance_title)
        self.advance_label = QLabel("¥ 0.00")
        self.advance_label.setObjectName("total_chinese")
        self.advance_label.setAlignment(Qt.AlignCenter)
        advance_layout.addWidget(self.advance_label)
        detail_layout.addLayout(advance_layout)

        refund_layout = QVBoxLayout()
        refund_title = QLabel("退补金额")
        refund_title.setObjectName("hint_label")
        refund_title.setAlignment(Qt.AlignCenter)
        refund_layout.addWidget(refund_title)
        self.refund_label = QLabel("¥ 0.00")
        self.refund_label.setObjectName("total_chinese")
        self.refund_label.setAlignment(Qt.AlignCenter)
        refund_layout.addWidget(self.refund_label)
        detail_layout.addLayout(refund_layout)

        summary_layout.addLayout(detail_layout)

        layout.addWidget(summary_group)

        layout.addStretch()
        return panel

    def build_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # 识别结果
        result_group = QGroupBox("识别结果")
        result_layout = QVBoxLayout(result_group)
        result_layout.setSpacing(10)

        result_hint = QLabel("每张 PDF 的每一页识别结果")
        result_hint.setObjectName("hint_label")
        result_layout.addWidget(result_hint)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "类型", "名称 / 车次", "日期 / 时间", "金额", "状态"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        result_layout.addWidget(self.result_table)

        layout.addWidget(result_group, 1)

        # 报销单预览
        preview_group = QGroupBox("报销单预览")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(10)

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(8)
        self.preview_table.setHorizontalHeaderLabels([
            "出发地点", "到达地点", "交通金额", "住宿",
            "市内交通", "补助标准", "出差天数", "合计"
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        preview_layout.addWidget(self.preview_table)

        layout.addWidget(preview_group, 2)

        return panel

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择 PDF 文件", "", "PDF 文件 (*.pdf)"
        )

        if not files:
            return
        logger.info(f"[MainWindow] 用户选择 {len(files)} 个文件")

        added = 0
        for file in files:
            if file not in self.file_paths:
                self.file_paths.append(file)
                item = QListWidgetItem(os.path.basename(file))
                item.setData(Qt.UserRole, file)
                item.setToolTip(file)
                self.file_list.addItem(item)
                added += 1

        if added:
            logger.info(f"[MainWindow] 新增 {added} 个文件，总计 {len(self.file_paths)} 个")
            self.status_label.setText(f"已添加 {len(self.file_paths)} 个文件，点击「开始识别」")

    def delete_selected(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        logger.info(f"[MainWindow] 删除 {len(selected_items)} 个文件")
        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            if file_path in self.file_paths:
                self.file_paths.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))

        self.status_label.setText(f"已添加 {len(self.file_paths)} 个文件")

    def clear_list(self):
        logger.info(f"[MainWindow] 清空文件列表，清理前共 {len(self.file_paths)} 个文件")
        self.file_paths.clear()
        self.file_list.clear()
        self.result_table.setRowCount(0)
        self.preview_table.setRowCount(0)
        self.parsed_results = []
        self.update_total()
        self.status_label.setText("等待上传文件...")

    def on_days_changed(self):
        logger.debug(f"[MainWindow] 出差天数变更: {self.days_spinbox.value()}")
        self.update_preview()
        self.update_total()

    def start_recognition(self):
        if not self.file_paths:
            logger.warning("[MainWindow] 用户未上传文件就点击开始识别")
            QMessageBox.warning(self, "提示", "请先上传 PDF 文件")
            return

        logger.info(f"[MainWindow] 启动识别任务，文件数: {len(self.file_paths)}")
        self.recognize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在识别...")

        self.worker = WorkerThread(self.file_paths)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_recognition_finished)
        self.worker.error.connect(self.on_recognition_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_recognition_finished(self, results):
        logger.info(f"[MainWindow] 识别完成，共 {len(results)} 条记录")
        self.parsed_results = results
        self.progress_bar.setVisible(False)
        self.recognize_btn.setEnabled(True)

        self.display_results(results)
        self.update_total()
        self.update_preview()

        if results:
            self.status_label.setText(f"识别完成，共 {len(results)} 条记录")
        else:
            self.status_label.setText("未识别到有效发票数据")

    def on_recognition_error(self, error_msg):
        logger.error(f"[MainWindow] 识别失败: {error_msg}")
        QMessageBox.critical(self, "错误", f"识别过程中发生错误：{error_msg}")
        self.progress_bar.setVisible(False)
        self.recognize_btn.setEnabled(True)
        self.status_label.setText("识别失败")

    def display_results(self, results):
        self.result_table.setRowCount(0)

        type_map = {
            'train': '高铁票',
            'hotel': '酒店住宿',
            'car': '市内用车',
            'invoice': '发票',
            'unknown': '未知'
        }

        for result in results:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)

            invoice_type = type_map.get(result.get('type'), '未知')
            self.result_table.setItem(row, 0, QTableWidgetItem(invoice_type))

            name = result.get('train_number', '') or result.get('hotel_name', '') or result.get('filename', '')
            self.result_table.setItem(row, 1, QTableWidgetItem(name))

            date = result.get('departure_time', '') or result.get('check_in_date', '') or result.get('car_date', '')
            self.result_table.setItem(row, 2, QTableWidgetItem(date))

            amount = result.get('amount', '0')
            amount_item = QTableWidgetItem(f"¥{amount}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.result_table.setItem(row, 3, amount_item)

            if amount:
                status_text = "已识别"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#047857"))
            else:
                status_text = "未识别金额"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#B45309"))
            self.result_table.setItem(row, 4, status_item)

    def update_total(self):
        train_total = sum(float(r.get('amount', '0')) for r in self.parsed_results if r.get('type') == 'train')
        hotel_total = sum(float(r.get('amount', '0')) for r in self.parsed_results if r.get('type') == 'hotel')
        car_total = sum(float(r.get('amount', '0')) for r in self.parsed_results if r.get('type') == 'car')
        invoice_total = sum(float(r.get('amount', '0')) for r in self.parsed_results if r.get('type') == 'invoice')

        days = self.days_spinbox.value()
        subsidy = days * 100

        advance = hotel_total + invoice_total + car_total
        refund = train_total + subsidy
        total = train_total + hotel_total + car_total + invoice_total + subsidy

        self.total_label.setText(f"¥ {total:,.2f}")
        self.advance_label.setText(f"¥ {advance:,.2f}")
        self.refund_label.setText(f"¥ {refund:,.2f}")

        chinese = amount_converter.convert(total)
        self.chinese_label.setText(chinese)

    def update_preview(self):
        self.preview_table.setRowCount(0)

        train_data = [r for r in self.parsed_results if r.get('type') == 'train']
        hotel_data = [r for r in self.parsed_results if r.get('type') == 'hotel']
        car_data = [r for r in self.parsed_results if r.get('type') == 'car']
        invoice_data = [r for r in self.parsed_results if r.get('type') == 'invoice']

        train_total = sum(float(r.get('amount', '0')) for r in train_data)
        hotel_total = sum(float(r.get('amount', '0')) for r in hotel_data)
        car_total = sum(float(r.get('amount', '0')) for r in car_data)
        invoice_total = sum(float(r.get('amount', '0')) for r in invoice_data)

        days = self.days_spinbox.value()
        subsidy_per_day = 100
        subsidy_total = days * subsidy_per_day

        def set_amount_item(row, col, value):
            item = QTableWidgetItem(f"{value:.2f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.preview_table.setItem(row, col, item)

        def set_empty_cells(row, cols):
            for col in cols:
                self.preview_table.setItem(row, col, QTableWidgetItem(''))

        # 高铁票行
        for train in train_data:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)

            self.preview_table.setItem(row, 0, QTableWidgetItem(train.get('departure_station', '')))
            self.preview_table.setItem(row, 1, QTableWidgetItem(train.get('arrival_station', '')))
            set_empty_cells(row, (3, 4, 5, 6))

            amount = float(train.get('amount', '0'))
            set_amount_item(row, 2, amount)
            set_amount_item(row, 7, amount)

        # 住宿合计行
        if hotel_total:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem('住宿'))
            set_empty_cells(row, (1, 2, 4, 5, 6))
            set_amount_item(row, 3, hotel_total)
            set_amount_item(row, 7, hotel_total)

        # 市内交通合计行
        if car_total:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem('市内交通'))
            set_empty_cells(row, (1, 2, 3, 5, 6))
            set_amount_item(row, 4, car_total)
            set_amount_item(row, 7, car_total)

        # 其他发票行
        if invoice_total:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem('其他'))
            set_empty_cells(row, (1, 3, 4, 5, 6))
            set_amount_item(row, 2, invoice_total)
            set_amount_item(row, 7, invoice_total)

        # 出差补助行
        if subsidy_total:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem('出差补助'))
            set_empty_cells(row, (1, 2, 3, 4))
            self.preview_table.setItem(row, 5, QTableWidgetItem(str(subsidy_per_day)))
            self.preview_table.setItem(row, 6, QTableWidgetItem(str(days)))
            set_amount_item(row, 7, subsidy_total)

        # 合计行
        row = self.preview_table.rowCount()
        self.preview_table.insertRow(row)
        self.preview_table.setItem(row, 0, QTableWidgetItem('合计'))
        set_empty_cells(row, (1, 5, 6))

        total_amount = train_total + hotel_total + car_total + invoice_total + subsidy_total
        font = QFont()
        font.setBold(True)

        for value, col in (
            (train_total + invoice_total, 2),
            (hotel_total, 3),
            (car_total, 4),
        ):
            item = QTableWidgetItem(f"{value:.2f}")
            item.setFont(font)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.preview_table.setItem(row, col, item)

        total_item = QTableWidgetItem(f"{total_amount:.2f}")
        total_item.setFont(font)
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.preview_table.setItem(row, 7, total_item)


