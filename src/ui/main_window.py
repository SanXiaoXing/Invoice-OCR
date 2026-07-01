from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem,
    QLabel, QProgressBar, QFileDialog, QMessageBox,
    QSplitter, QGroupBox, QHeaderView, QSpinBox,
    QMenuBar, QMenu, QDialog, QDialogButtonBox, QSizePolicy,
    QCalendarWidget, QFrame
)
from PySide6.QtGui import QAction, QActionGroup, QFont, QColor
from PySide6.QtCore import Qt, QThread, Signal, QDate, QSettings
import os
from datetime import datetime
from src.services import expense_calculator, recognition_service, file_service, result_formatter
from src.ui.themes import get_theme_qss, THEMES
from src.utils.logger import logger


class MergePdfDialog(QDialog):
    """合并 PDF 文件对话框 — 展示文件列表、支持排序、显示页数"""

    def __init__(self, file_paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("合并 PDF 文件")
        self.setMinimumSize(520, 400)
        self.file_paths = list(file_paths)  # 可编辑的副本
        self._page_counts = {}  # 缓存页数

        # 继承父窗口主题
        if parent and hasattr(parent, 'current_theme'):
            self.setStyleSheet(get_theme_qss(parent.current_theme))

        self._init_ui()
        self._load_page_counts()

    # ── UI ───────────────────────────────────────────────
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 顶部说明
        hint = QLabel("以下 PDF 将按列表顺序合并，可通过上下按钮调整顺序：")
        hint.setObjectName("hint_label")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 文件列表 + 排序按钮
        body = QHBoxLayout()
        body.setSpacing(10)

        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QListWidget.NoDragDrop)
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.currentRowChanged.connect(self._on_row_changed)
        body.addWidget(self.file_list, 1)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)

        self.up_btn = QPushButton("↑ 上移")
        self.up_btn.setToolTip("将选中文件上移一位")
        self.up_btn.setEnabled(False)
        self.up_btn.clicked.connect(self._move_up)
        btn_col.addWidget(self.up_btn)

        self.down_btn = QPushButton("↓ 下移")
        self.down_btn.setToolTip("将选中文件下移一位")
        self.down_btn.setEnabled(False)
        self.down_btn.clicked.connect(self._move_down)
        btn_col.addWidget(self.down_btn)

        btn_col.addStretch()
        body.addLayout(btn_col)

        layout.addLayout(body, 1)

        # 统计信息
        self.summary_label = QLabel()
        self.summary_label.setObjectName("hint_label")
        layout.addWidget(self.summary_label)

        # 底部按钮
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.button(QDialogButtonBox.Ok).setText("合并")
        btn_box.button(QDialogButtonBox.Cancel).setText("取消")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        # 填充列表
        self._refresh_list()

    # ── 数据加载 ─────────────────────────────────────────
    def _load_page_counts(self):
        """后台统计每个 PDF 的页数"""
        class _PageCountThread(QThread):
            done = Signal(dict)

            def __init__(self, paths):
                super().__init__()
                self.paths = paths

            def run(self):
                counts = {}
                for p in self.paths:
                    try:
                        from pypdf import PdfReader
                        counts[p] = len(PdfReader(p).pages)
                    except Exception:
                        counts[p] = 0
                self.done.emit(counts)

        self._pc_thread = _PageCountThread(self.file_paths)
        self._pc_thread.done.connect(self._on_page_counts_ready)
        self._pc_thread.start()

    def _on_page_counts_ready(self, counts):
        self._page_counts = counts
        self._refresh_list()

    # ── 列表刷新 ─────────────────────────────────────────
    def _refresh_list(self):
        self.file_list.clear()
        for i, path in enumerate(self.file_paths, 1):
            name = os.path.basename(path)
            pages = self._page_counts.get(path)
            suffix = f"  ({pages} 页)" if pages is not None else ""
            item = QListWidgetItem(f"{i}.  {name}{suffix}")
            item.setToolTip(path)
            item.setData(Qt.UserRole, path)
            self.file_list.addItem(item)

        total_files = len(self.file_paths)
        total_pages = sum(v for v in self._page_counts.values() if v)
        if self._page_counts:
            self.summary_label.setText(f"共 {total_files} 个文件，{total_pages} 页")
        else:
            self.summary_label.setText(f"共 {total_files} 个文件")

    # ── 排序操作 ─────────────────────────────────────────
    def _on_row_changed(self, row):
        self.up_btn.setEnabled(row > 0)
        self.down_btn.setEnabled(0 <= row < self.file_list.count() - 1)

    def _swap_rows(self, r1, r2):
        self.file_paths[r1], self.file_paths[r2] = self.file_paths[r2], self.file_paths[r1]
        self._refresh_list()
        self.file_list.setCurrentRow(r2)

    def _move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            self._swap_rows(row, row - 1)

    def _move_down(self):
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1:
            self._swap_rows(row, row + 1)

    # ── 对外接口 ─────────────────────────────────────────
    def get_ordered_paths(self):
        return list(self.file_paths)


class TravelDateDialog(QDialog):
    """出差日期选择对话框 — 两个并排日历，选择出发和返回日期"""

    def __init__(self, start_date, end_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择出差日期")
        self.setMinimumSize(640, 420)
        self._start_date = start_date
        self._end_date = end_date

        if parent and hasattr(parent, 'current_theme'):
            self.setStyleSheet(get_theme_qss(parent.current_theme))

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 两个并排日历
        calendars_layout = QHBoxLayout()
        calendars_layout.setSpacing(12)

        # 出发日历
        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        start_title = QLabel("出发日期")
        start_title.setAlignment(Qt.AlignCenter)
        start_title.setObjectName("hint_label")
        start_col.addWidget(start_title)

        self.start_calendar = QCalendarWidget()
        self.start_calendar.setSelectedDate(self._start_date)
        self.start_calendar.setGridVisible(True)
        self.start_calendar.clicked.connect(self._on_start_clicked)
        start_col.addWidget(self.start_calendar)
        calendars_layout.addLayout(start_col)

        # 返回日历
        end_col = QVBoxLayout()
        end_col.setSpacing(4)
        end_title = QLabel("返回日期")
        end_title.setAlignment(Qt.AlignCenter)
        end_title.setObjectName("hint_label")
        end_col.addWidget(end_title)

        self.end_calendar = QCalendarWidget()
        self.end_calendar.setSelectedDate(self._end_date)
        self.end_calendar.setGridVisible(True)
        self.end_calendar.clicked.connect(self._on_end_clicked)
        end_col.addWidget(self.end_calendar)
        calendars_layout.addLayout(end_col)

        layout.addLayout(calendars_layout, 1)

        # 摘要行
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setObjectName("total_chinese")
        self._update_summary()
        layout.addWidget(self.summary_label)

        # 底部按钮
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.button(QDialogButtonBox.Ok).setText("确定")
        btn_box.button(QDialogButtonBox.Cancel).setText("取消")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_start_clicked(self, date):
        """点击出发日历时，确保返回日期不早于出发日期"""
        if date > self.end_calendar.selectedDate():
            self.end_calendar.setSelectedDate(date)
        self._update_summary()

    def _on_end_clicked(self, date):
        """点击返回日历时，确保出发日期不晚于返回日期"""
        if date < self.start_calendar.selectedDate():
            self.start_calendar.setSelectedDate(date)
        self._update_summary()

    def _update_summary(self):
        start = self.start_calendar.selectedDate()
        end = self.end_calendar.selectedDate()
        days = start.daysTo(end) + 1
        self.summary_label.setText(
            f"{start.toString('yyyy-MM-dd')} ~ {end.toString('yyyy-MM-dd')}，共 {days} 天"
        )

    def get_date_range(self):
        """返回 (出发日期, 返回日期)"""
        return self.start_calendar.selectedDate(), self.end_calendar.selectedDate()


class AboutDialog(QDialog):
    """关于对话框 — 展示应用名称、版本、功能简介等信息"""

    def __init__(self, parent=None, first_launch=False):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedWidth(420)
        self._first_launch = first_launch

        # 继承父窗口主题
        if parent and hasattr(parent, 'current_theme'):
            self.setStyleSheet(get_theme_qss(parent.current_theme))

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 20)

        # 应用名称
        title = QLabel("SnapClaim")
        title.setObjectName("total_value")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 版本
        version = QLabel("Verison: 0.1.0")
        version.setObjectName("hint_label")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 功能简介
        desc = QLabel(
            "自动识别 PDF 发票和出行确认单，生成费用报销单。\n\n"
            "支持识别：高铁票、酒店确认单、用车确认单、飞机确认单\n"
            "自动汇总费用，一键导出报销单 Excel 和合并 PDF。"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # 提示信息（仅首次启动时显示）
        if self._first_launch:
            tip = QLabel("💡 后续可在菜单栏「帮助 → 关于」再次查看。")
            tip.setObjectName("hint_label")
            tip.setAlignment(Qt.AlignCenter)
            tip.setWordWrap(True)
            layout.addWidget(tip)

        layout.addStretch()

        # 底部按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.button(QDialogButtonBox.Ok).setText("知道了")
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)


class WorkerThread(QThread):
    """识别任务线程 — 薄壳，调用 recognition_service 执行业务逻辑"""
    progress = Signal(int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        try:
            results = recognition_service.process_files(
                self.file_paths, self._on_progress
            )
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"[WorkerThread] 识别过程异常: {e}")
            self.error.emit(str(e))

    def _on_progress(self, current, total):
        self.progress.emit(int(current / total * 100))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("发票报销单自动生成系统")
        self.setMinimumSize(1200, 800)

        self.file_paths = []
        self.parsed_results = []
        self.current_theme = "清爽办公风"
        self._start_date = QDate.currentDate()
        self._end_date = QDate.currentDate()

        self.settings = QSettings("SanXiaoXing", "SnapClaim")

        self.apply_theme(self.current_theme)
        self.init_ui()

        # 首次启动自动弹出关于对话框
        if not self.settings.value("about_shown", type=bool):
            self._show_about(first_launch=True)
            self.settings.setValue("about_shown", True)

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

        file_menu = self.menu_bar.addMenu("文件(&F)")
        merge_action = QAction("合并 PDF…", self)
        merge_action.setShortcut("Ctrl+M")
        merge_action.setToolTip("将已上传的所有 PDF 文件按顺序合并为一个文件")
        merge_action.triggered.connect(self.merge_uploaded_pdfs)
        file_menu.addAction(merge_action)

        export_action = QAction("导出报销单…", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setToolTip("将识别结果导出为报销单 Excel 表格")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)

        one_click_action = QAction("一键导出", self)
        one_click_action.setShortcut("Ctrl+Shift+E")
        one_click_action.setToolTip("同时导出合并 PDF 和报销单 Excel")
        one_click_action.triggered.connect(self.one_click_export)
        file_menu.addAction(one_click_action)

        file_menu.addSeparator()

        # 帮助菜单
        help_menu = self.menu_bar.addMenu("帮助(&H)")
        about_action = QAction("关于", self)
        about_action.setShortcut("Ctrl+Shift+A")
        about_action.setToolTip("查看应用信息")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        view_menu = self.menu_bar.addMenu("视图")
        self.theme_menu = view_menu.addMenu("主题")

        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        for theme_name in THEMES.keys():
            action = QAction(theme_name, self)
            action.setCheckable(True)
            action.setChecked(theme_name == self.current_theme)
            action.triggered.connect(self.on_theme_action_triggered)
            self.theme_action_group.addAction(action)
            self.theme_menu.addAction(action)

    def _show_about(self, first_launch=False):
        """弹出关于对话框"""
        dialog = AboutDialog(self, first_launch=first_launch)
        dialog.exec()

    def build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 文件上传区
        upload_group = QGroupBox("上传 PDF 文件")
        upload_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        upload_layout = QVBoxLayout(upload_group)
        upload_layout.setSpacing(8)

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
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        upload_layout.addWidget(self.file_list, 1)

        file_actions = QHBoxLayout()
        file_actions.setSpacing(8)
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.setObjectName("danger_btn")
        self.delete_btn.clicked.connect(self.delete_selected)
        file_actions.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_list)
        file_actions.addWidget(self.clear_btn)
        upload_layout.addLayout(file_actions)

        layout.addWidget(upload_group, 1)

        # 操作区
        action_group = QGroupBox("识别")
        action_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        action_layout = QVBoxLayout(action_group)
        action_layout.setSpacing(8)

        self.recognize_btn = QPushButton("开始识别")
        self.recognize_btn.setObjectName("primary_btn")
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

        # 出差设置（紧凑布局：一行显示日期区间 + 天数 + 选择按钮）
        travel_group = QGroupBox("出差设置")
        travel_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        travel_layout = QVBoxLayout(travel_group)
        travel_layout.setSpacing(6)

        date_row = QHBoxLayout()
        date_row.setSpacing(6)

        self.travel_date_label = QLabel()
        self.travel_date_label.setObjectName("hint_label")
        self._refresh_travel_date_label(QDate.currentDate(), QDate.currentDate())
        date_row.addWidget(self.travel_date_label, 1)

        self.days_spinbox = QSpinBox()
        self.days_spinbox.setRange(0, 999)
        self.days_spinbox.setValue(1)
        self.days_spinbox.setSuffix(" 天")
        self.days_spinbox.setFixedWidth(72)
        self.days_spinbox.valueChanged.connect(self.on_days_changed)
        self.days_spinbox.setToolTip("出差天数（可手动微调）")
        date_row.addWidget(self.days_spinbox)

        self.date_pick_btn = QPushButton("选择日期")
        self.date_pick_btn.setToolTip("通过日历选择出差日期区间")
        self.date_pick_btn.clicked.connect(self.open_travel_date_dialog)
        date_row.addWidget(self.date_pick_btn)

        travel_layout.addLayout(date_row)
        layout.addWidget(travel_group)

        # 费用汇总
        summary_group = QGroupBox("费用汇总")
        summary_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setSpacing(6)

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
        advance_layout.setSpacing(2)
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
        refund_layout.setSpacing(2)
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
        self.preview_table.setColumnCount(9)
        self.preview_table.setHorizontalHeaderLabels([
            "出发地点", "到达地点", "交通金额", "飞机票", "住宿",
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

    # ── 文件管理 ─────────────────────────────────────────

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

    # ── 出差天数 ─────────────────────────────────────────

    def _refresh_travel_date_label(self, start, end):
        """更新面板上的日期区间摘要文本"""
        days = start.daysTo(end) + 1
        if start == end:
            self.travel_date_label.setText(f"出差: {start.toString('MM/dd')} (1天)")
        else:
            self.travel_date_label.setText(
                f"出差: {start.toString('MM/dd')} ~ {end.toString('MM/dd')} ({days}天)"
            )

    def open_travel_date_dialog(self):
        """打开出差日期选择弹窗"""
        dialog = TravelDateDialog(self._start_date, self._end_date, self)
        if dialog.exec() == QDialog.Accepted:
            start, end = dialog.get_date_range()
            self._start_date = start
            self._end_date = end
            days = start.daysTo(end) + 1

            self._refresh_travel_date_label(start, end)
            self.days_spinbox.blockSignals(True)
            self.days_spinbox.setValue(days)
            self.days_spinbox.blockSignals(False)
            self.update_preview()
            self.update_total()
            logger.debug(f"[MainWindow] 日期区间变更: {start.toString('yyyy-MM-dd')} ~ {end.toString('yyyy-MM-dd')}, 天数={days}")

    def on_days_changed(self):
        logger.debug(f"[MainWindow] 出差天数变更: {self.days_spinbox.value()}")
        self.update_preview()
        self.update_total()

    # ── 合并 / 导出 ─────────────────────────────────────

    def merge_uploaded_pdfs(self):
        if not self.file_paths:
            QMessageBox.warning(self, "提示", "请先上传 PDF 文件")
            return

        dialog = MergePdfDialog(self.file_paths, self)
        if dialog.exec() != QDialog.Accepted:
            return

        ordered_paths = dialog.get_ordered_paths()

        default_name = datetime.now().strftime("%Y%m%d") + ".pdf"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存合并后的 PDF", default_name, "PDF 文件 (*.pdf)"
        )
        if not save_path:
            return

        success = file_service.merge_pdfs(ordered_paths, save_path)

        if success:
            self._show_success_dialog(
                "合并完成",
                f"已成功合并 {len(ordered_paths)} 个 PDF 文件",
                save_path,
            )
        else:
            QMessageBox.critical(self, "合并失败", "PDF 合并失败，请检查文件是否有效")

    def export_report(self):
        """导出报销单 Excel 表格"""
        if not self.parsed_results:
            QMessageBox.warning(self, "提示", "请先完成发票识别后再导出报销单")
            return

        default_name = datetime.now().strftime("%Y%m%d") + ".xlsx"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "导出报销单", default_name, "Excel 文件 (*.xlsx)"
        )
        if not save_path:
            return

        success = file_service.export_report(self.parsed_results, save_path, self.days_spinbox.value())

        if success:
            self._show_success_dialog("导出完成", "报销单已成功导出", save_path)
        else:
            QMessageBox.critical(self, "导出失败", "报销单导出失败，请检查数据是否有效")

    def one_click_export(self):
        """一键导出：同时生成合并 PDF 和报销单 Excel"""
        if not self.file_paths:
            QMessageBox.warning(self, "提示", "请先上传 PDF 文件")
            return
        if not self.parsed_results:
            QMessageBox.warning(self, "提示", "请先完成发票识别后再导出")
            return

        # 选择保存目录
        save_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not save_dir:
            return

        date_prefix = datetime.now().strftime("%Y%m%d")
        pdf_path = os.path.join(save_dir, f"{date_prefix}.pdf")
        xlsx_path = os.path.join(save_dir, f"{date_prefix}.xlsx")

        # 合并 PDF
        pdf_success = file_service.merge_pdfs(self.file_paths, pdf_path)
        # 导出 Excel
        xlsx_success = file_service.export_report(self.parsed_results, xlsx_path, self.days_spinbox.value())

        # 汇总结果
        results = []
        if pdf_success:
            results.append(f"✓ 合并 PDF：{pdf_path}")
        else:
            results.append("✗ 合并 PDF 失败")
        if xlsx_success:
            results.append(f"✓ 报销单 Excel：{xlsx_path}")
        else:
            results.append("✗ 报销单 Excel 导出失败")

        if pdf_success and xlsx_success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("一键导出完成")
            msg.setText("所有文件已成功导出")
            msg.setInformativeText("\n".join(results))
            open_btn = msg.addButton("打开所在文件夹", QMessageBox.ActionRole)
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec()
            if msg.clickedButton() == open_btn:
                file_service.open_containing_folder(save_dir)
        else:
            QMessageBox.warning(self, "导出部分失败", "\n".join(results))

    def _show_success_dialog(self, title, text, save_path):
        """通用的成功提示对话框，带「打开所在文件夹」按钮"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(f"保存至：{save_path}")
        open_btn = msg.addButton("打开所在文件夹", QMessageBox.ActionRole)
        msg.addButton("确定", QMessageBox.AcceptRole)
        msg.exec()

        if msg.clickedButton() == open_btn:
            file_service.open_containing_folder(save_path)

    # ── 识别流程 ─────────────────────────────────────────

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

    # ── 表格展示 ─────────────────────────────────────────

    def display_results(self, results):
        self.result_table.setRowCount(0)

        for result in results:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)

            fmt = result_formatter.format_result_row(result)

            self.result_table.setItem(row, 0, QTableWidgetItem(fmt['type_label']))
            self.result_table.setItem(row, 1, QTableWidgetItem(fmt['name']))
            self.result_table.setItem(row, 2, QTableWidgetItem(fmt['date']))

            amount_item = QTableWidgetItem(fmt['amount'])
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.result_table.setItem(row, 3, amount_item)

            status_item = QTableWidgetItem(fmt['status'])
            status_item.setForeground(QColor(fmt['status_color']))
            self.result_table.setItem(row, 4, status_item)

    def update_total(self):
        t = expense_calculator.calc_totals(self.parsed_results, self.days_spinbox.value())
        self.total_label.setText(f"¥ {t['total']:,.2f}")
        self.advance_label.setText(f"¥ {t['advance']:,.2f}")
        self.refund_label.setText(f"¥ {t['refund']:,.2f}")
        self.chinese_label.setText(t['chinese'])

    def update_preview(self):
        self.preview_table.setRowCount(0)

        rows = expense_calculator.build_preview_rows(
            self.parsed_results, self.days_spinbox.value()
        )

        bold_font = QFont()
        bold_font.setBold(True)

        for row_data in rows:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)

            cells = row_data['cells']
            for col, value in enumerate(cells):
                if isinstance(value, float):
                    item = QTableWidgetItem(f"{value:.2f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item = QTableWidgetItem(str(value))

                if row_data['bold']:
                    item.setFont(bold_font)

                self.preview_table.setItem(row, col, item)
