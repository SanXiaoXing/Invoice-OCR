# 发票报销单自动生成系统

一款基于 Python + PySide6 开发的桌面应用，用于自动识别电子 PDF 发票和出行确认单，并生成费用报销单。

## 功能特性

- **PDF 自动识别**
  - 高铁电子发票：识别车次、出发站、到达站、日期、金额
  - 酒店确认单：扫描二维码提取住宿金额
  - 用车确认单：扫描二维码提取用车金额
  - 其他发票：文本识别金额

- **二维码优先策略**
  - 同程商旅的酒店和用车确认单二维码中直接包含金额
  - 优先扫描二维码获取金额，避免 OCR 文本识别出错

- **报销单生成**
  - 自动汇总交通金额、住宿、市内交通
  - 支持出差天数和每日补助标准
  - 自动计算预借金额、退补金额、总金额
  - 自动将总金额转换为大写金额

- **多主题界面**
  - 清爽办公风
  - 高对比效率风
  - 深色专业风
  - 柔和极简风
  - 企业可信风

## 技术栈

- **Python 3.10**
- **PySide6**：桌面 GUI
- **pdfplumber**：PDF 文本提取
- **pypdfium2 + OpenCV**：PDF 渲染与二维码扫描
- **openpyxl**：Excel 报销单导出

## 项目结构

```
Invoice-OCR/
├── src/
│   ├── config/
│   │   └── rules.yaml          # 发票识别规则配置
│   ├── extractor/
│   │   └── invoice_extractor.py # 发票字段提取逻辑
│   ├── generator/
│   │   └── report_generator.py # Excel 报销单生成
│   ├── parser/
│   │   └── pdf_parser.py        # PDF 解析与二维码扫描
│   ├── ui/
│   │   ├── main_window.py       # 主界面
│   │   └── themes.py            # 界面主题预设
│   ├── utils/
│   │   └── amount_converter.py  # 金额转大写
│   └── main.py                  # 程序入口
├── tests/                       # 测试脚本
├── docs/                        # 示例 PDF 和风格展示
│   └── design/
│       └── index.html           # 界面主题风格展示
├── requirements.txt             # 依赖列表
└── README.md                    # 项目说明
```

## 安装与运行

### 1. 克隆项目

```bash
git clone git@github.com:SanXiaoXing/Invoice-OCR.git
cd Invoice-OCR
```

### 2. 创建并激活虚拟环境

```bash
# 使用 conda
conda create -n yx310 python=3.10
conda activate yx310

# 或使用 venv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动应用

```bash
python -m src.main
```

## 使用方法

1. 点击「添加 PDF 文件」，选择需要识别的发票 PDF
2. 输入出差天数（补助标准为 ¥100/天）
3. 点击「开始识别」按钮
4. 查看右侧「识别结果」和「报销单预览」
5. 费用汇总区域显示预借金额、退补金额、总金额和大写金额

## 计算规则

| 项目 | 计算方式 |
|---|---|
| 交通金额 | 高铁票金额 + 其他发票金额 |
| 市内交通 | 用车确认单金额 |
| 住宿 | 酒店确认单金额 |
| 出差补助 | 100 × 出差天数 |
| 预借金额 | 住宿 + 其他发票 |
| 退补金额 | 高铁费用 + 出差补助 |
| 总金额 | 高铁 + 住宿 + 市内交通 + 其他发票 + 出差补助 |

## 注意事项

- 二维码识别对扫描质量有一定要求，请确保 PDF 页面清晰
- 高铁票仍使用文本识别，建议上传文字清晰的 PDF
- 默认主题为「清爽办公风」，可在菜单栏「视图 → 界面主题」中切换

## 许可证

本项目仅供学习和内部使用。
