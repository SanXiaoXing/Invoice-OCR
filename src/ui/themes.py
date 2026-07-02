# 界面主题预设
# 每套主题对应一组 QSS 样式字符串，可直接应用到 QMainWindow

THEMES = {
    "高对比效率风": {
        "background": "#FFFFFF",
        "card": "#FFFFFF",
        "border": "#000000",
        "text_primary": "#000000",
        "text_secondary": "#525252",
        "accent": "#000000",
        "accent_hover": "#262626",
        "accent_pressed": "#404040",
        "accent_text": "#FFFFFF",
        "danger": "#DC2626",
        "danger_bg": "#FFFFFF",
        "danger_border": "#DC2626",
        "radius": "0px",
        "small_radius": "0px",
        "selection_bg": "#F5F5F5",
        "header_bg": "#000000",
        "header_text": "#FFFFFF",
        "gridline": "#000000",
        "input_bg": "#FFFFFF",
        "progress_bg": "#E5E5E5",
        "progress_chunk": "#000000",
        "group_title_bg": "#FFFFFF",
        "overlay_bg": "rgba(0, 0, 0, 100)",
    },
    "清爽办公风": {
        "background": "#F8FAFC",
        "card": "#FFFFFF",
        "border": "#E2E8F0",
        "text_primary": "#1E293B",
        "text_secondary": "#64748B",
        "accent": "#10B981",
        "accent_hover": "#059669",
        "accent_pressed": "#047857",
        "accent_text": "#FFFFFF",
        "danger": "#DC2626",
        "danger_bg": "#FEF2F2",
        "danger_border": "#FECACA",
        "radius": "8px",
        "small_radius": "6px",
        "selection_bg": "#D1FAE5",
        "header_bg": "#F8FAFC",
        "header_text": "#475569",
        "gridline": "#F1F5F9",
        "input_bg": "#FFFFFF",
        "progress_bg": "#E2E8F0",
        "progress_chunk": "#10B981",
        "group_title_bg": "#FFFFFF",
        "overlay_bg": "rgba(15, 23, 42, 100)",
    },
    "深色专业风": {
        "background": "#0F172A",
        "card": "#1E293B",
        "border": "#334155",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "accent": "#0EA5E9",
        "accent_hover": "#0284C7",
        "accent_pressed": "#0369A1",
        "accent_text": "#FFFFFF",
        "danger": "#F87171",
        "danger_bg": "#1E293B",
        "danger_border": "#7F1D1D",
        "radius": "8px",
        "small_radius": "6px",
        "selection_bg": "#0C4A6E",
        "header_bg": "#1E293B",
        "header_text": "#94A3B8",
        "gridline": "#334155",
        "input_bg": "#0F172A",
        "progress_bg": "#334155",
        "progress_chunk": "#0EA5E9",
        "group_title_bg": "#1E293B",
        "overlay_bg": "rgba(255, 255, 255, 30)",
    },
    "柔和极简风": {
        "background": "#FAF9F6",
        "card": "#FFFFFF",
        "border": "#E7E5E4",
        "text_primary": "#292524",
        "text_secondary": "#78716C",
        "accent": "#84CC16",
        "accent_hover": "#65A30D",
        "accent_pressed": "#4D7C0F",
        "accent_text": "#FFFFFF",
        "danger": "#DC2626",
        "danger_bg": "#FEF2F2",
        "danger_border": "#FECACA",
        "radius": "16px",
        "small_radius": "8px",
        "selection_bg": "#ECFCCB",
        "header_bg": "#F5F5F4",
        "header_text": "#57534E",
        "gridline": "#F5F5F4",
        "input_bg": "#FFFFFF",
        "progress_bg": "#E7E5E4",
        "progress_chunk": "#84CC16",
        "group_title_bg": "#FFFFFF",
        "overlay_bg": "rgba(0, 0, 0, 80)",
    },
    "企业可信风": {
        "background": "#FFFFFF",
        "card": "#FFFFFF",
        "border": "#CBD5E1",
        "text_primary": "#1E293B",
        "text_secondary": "#475569",
        "accent": "#1E40AF",
        "accent_hover": "#1E3A8A",
        "accent_pressed": "#172554",
        "accent_text": "#FFFFFF",
        "danger": "#DC2626",
        "danger_bg": "#FEF2F2",
        "danger_border": "#FECACA",
        "radius": "6px",
        "small_radius": "4px",
        "selection_bg": "#DBEAFE",
        "header_bg": "#F8FAFC",
        "header_text": "#475569",
        "gridline": "#E2E8F0",
        "input_bg": "#FFFFFF",
        "progress_bg": "#E2E8F0",
        "progress_chunk": "#1E40AF",
        "group_title_bg": "#FFFFFF",
        "overlay_bg": "rgba(15, 23, 42, 100)",
    },
}


def get_theme_qss(theme_name):
    """根据主题名称返回完整 QSS 字符串"""
    if theme_name not in THEMES:
        theme_name = "高对比效率风"

    t = THEMES[theme_name]

    return f"""
        QMainWindow {{
            background-color: {t['background']};
        }}
        QGroupBox {{
            font-weight: 600;
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['radius']};
            margin-top: 12px;
            padding: 14px;
            padding-top: 18px;
            background-color: {t['card']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            top: -2px;
            padding: 0 6px;
            color: {t['text_secondary']};
            font-size: 14px;
            background-color: {t['group_title_bg']};
        }}
        QPushButton {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            padding: 4px 14px;
            font-weight: 500;
            min-height: 26px;
        }}
        QPushButton:hover {{
            background-color: {t['selection_bg']};
        }}
        QPushButton:pressed {{
            background-color: {t['border']};
        }}
        QPushButton:disabled {{
            background-color: {t['card']};
            color: {t['text_secondary']};
            border-color: {t['border']};
        }}
        QPushButton#primary_btn {{
            background-color: {t['accent']};
            color: {t['accent_text']};
            border: 1px solid {t['accent']};
        }}
        QPushButton#primary_btn:hover {{
            background-color: {t['accent_hover']};
            border-color: {t['accent_hover']};
        }}
        QPushButton#primary_btn:pressed {{
            background-color: {t['accent_pressed']};
            border-color: {t['accent_pressed']};
        }}
        QPushButton#danger_btn {{
            color: {t['danger']};
            border-color: {t['danger_border']};
            background-color: {t['danger_bg']};
        }}
        QPushButton#danger_btn:hover {{
            background-color: {t['selection_bg']};
        }}
        QTableWidget {{
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            background-color: {t['card']};
            gridline-color: {t['gridline']};
            selection-background-color: {t['selection_bg']};
        }}
        QHeaderView::section {{
            background-color: {t['header_bg']};
            color: {t['header_text']};
            font-weight: 600;
            padding: 8px;
            border: none;
            border-bottom: 1px solid {t['border']};
        }}
        QTableWidget::item {{
            padding: 6px 8px;
            color: {t['text_primary']};
        }}
        QTableWidget::item:selected {{
            background-color: {t['accent']};
            color: {t['accent_text']};
        }}
        QTableWidget::item:selected:hover {{
            background-color: {t['accent_hover']};
            color: {t['accent_text']};
        }}
        QListWidget {{
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            background-color: {t['card']};
            padding: 4px;
            outline: none;
        }}
        QListWidget::item {{
            border-radius: {t['small_radius']};
            padding: 6px 8px;
            color: {t['text_primary']};
        }}
        QListWidget::item:selected {{
            background-color: {t['accent']};
            color: {t['accent_text']};
        }}
        QListWidget::item:hover {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QListWidget::item:selected:hover {{
            background-color: {t['accent_hover']};
            color: {t['accent_text']};
        }}
        QProgressBar {{
            border: none;
            border-radius: {t['small_radius']};
            background-color: {t['progress_bg']};
            text-align: center;
            color: {t['text_primary']};
            height: 18px;
        }}
        QProgressBar::chunk {{
            background-color: {t['progress_chunk']};
            border-radius: {t['small_radius']};
        }}
        QLabel {{
            color: {t['text_primary']};
        }}
        QLabel#hint_label {{
            color: {t['text_secondary']};
            font-size: 12px;
        }}
        QLabel#empty_label {{
            color: {t['text_secondary']};
            font-size: 14px;
        }}
        QLabel#total_value {{
            color: {t['text_primary']};
            font-weight: 700;
            font-size: 18px;
        }}
        QLabel#total_chinese {{
            color: {t['text_secondary']};
            font-size: 14px;
            font-weight: 500;
        }}
        QComboBox {{
            background-color: {t['input_bg']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            padding: 6px 10px;
            min-height: 28px;
        }}
        QComboBox:hover {{
            border-color: {t['text_secondary']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            selection-background-color: {t['accent']};
            selection-color: {t['accent_text']};
        }}
        QSpinBox {{
            background-color: {t['input_bg']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            padding: 6px;
            min-height: 28px;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {t['selection_bg']};
            border: 1px solid {t['border']};
            width: 18px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {t['border']};
        }}
        QCalendarWidget {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
        }}
        QCalendarWidget QWidget {{
            background-color: {t['card']};
            color: {t['text_primary']};
        }}
        QCalendarWidget QToolButton {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            padding: 4px 8px;
            font-weight: 500;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: {t['selection_bg']};
        }}
        QCalendarWidget QMenu {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
        }}
        QCalendarWidget QMenu::item:selected {{
            background-color: {t['accent']};
            color: {t['accent_text']};
        }}
        QCalendarWidget QAbstractItemView {{
            background-color: {t['card']};
            color: {t['text_primary']};
            selection-background-color: {t['accent']};
            selection-color: {t['accent_text']};
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {t['header_bg']};
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {{
            background-color: {t['header_bg']};
            color: {t['header_text']};
            border: none;
            font-weight: 600;
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton:hover {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QCalendarWidget QWidget#qt_calendar_monthbutton {{
            color: {t['header_text']};
        }}
        QCalendarWidget QWidget#qt_calendar_yearbutton {{
            color: {t['header_text']};
        }}
        QCalendarWidget QTableView {{
            background-color: {t['card']};
            color: {t['text_primary']};
            selection-background-color: {t['accent']};
            selection-color: {t['accent_text']};
            gridline-color: {t['gridline']};
            border: none;
        }}
        QCalendarWidget QTableView::item:hover {{
            background-color: {t['selection_bg']};
        }}
        QSplitter::handle {{
            background-color: {t['border']};
        }}
        QMessageBox {{
            background-color: {t['card']};
        }}
        QMessageBox QLabel {{
            color: {t['text_primary']};
            font-size: 14px;
        }}
        QMessageBox QPushButton {{
            background-color: {t['card']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['small_radius']};
            padding: 5px 20px;
            min-height: 24px;
            font-weight: 500;
            font-size: 13px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {t['selection_bg']};
        }}
        QMessageBox QPushButton:pressed {{
            background-color: {t['border']};
        }}
        QFrame#drag_mask {{
            background-color: {t['overlay_bg']};
            border: 3px dashed {t['accent']};
            border-radius: {t['radius']};
        }}
        QLabel#drag_mask_hint {{
            color: {t['accent']};
            font-size: 24px;
            font-weight: 700;
        }}
        QLabel#drag_mask_subhint {{
            color: {t['text_secondary']};
            font-size: 13px;
        }}
    """
