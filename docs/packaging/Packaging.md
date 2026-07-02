# 打包指令
```bash
nuitka --standalone --follow-imports --windows-console-mode=attach --onefile --windows-company-name="SanXiaoXing" --windows-product-name="InvoiceOCR" --windows-product-version="1.0.0" --file-description="Invoice recognition and reimbursement auto generation tool" --copyright="Copyright (c) 2026 SanXiaoXing. All rights reserved." --output-dir=dist --output-filename=SnapClaim --enable-plugin=pyside6 --include-data-dir=src/config=src/config --include-data-dir=src/assets=src/assets src/main.py
```