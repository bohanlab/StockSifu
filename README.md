# StockSifu - 股票内在价值计算器和投资组合跟踪器
# StockSifu - Intrinsic Value Calculator & Portfolio Tracker

- StockSifu 是一个基于 Python 和 CustomTkinter 个人投资组合追踪与股票估值工具。
- StockSifu is a portfolio tracker and stock valuation tool built with Python & CustomTkinter.

## 主要功能 | Main Features

### **股票内在价值计算器 (Intrinsic Value Calculator)：**
- 内置现金流折现模型
- 自动保存估值快照到关注列表
- Built-in Discounted Cash Flow (DCF) model
- Automatically save valuation snapshots to a watchlist

### **投资组合跟踪器 (Portfolio Tracker)：** 
- 一目了然地展示持仓代码、名称、市值及盈亏
- 支持美元、人民币、港币等多种资产混合管理
- 自动生成持仓分布、板块配置和地区分布饼图
- Display holdings, names, market value, and profit/loss at a glance
- Supports mixed asset management in multiple currencies like USD, CNY, HKD, etc.
- Automatically generate pie charts for holding distribution, sector allocation, and regional distribution

### **自动行情刷新 (Automatic Data Refresh)：** 
- 调用`yfinance`API，一键批量更新所有持仓的最新股价和实时汇率
- Fetches the latest stock prices and real-time exchange rates for all holdings with one click using the `yfinance` API

### **保护隐私 (Privacy Protection)：** 
- 所有持仓和财务数据仅存储在本地 JSON 文件中，不上传任何服务器
- All holdings and financial data are stored locally in JSON files and are not uploaded to any server
  
## 安装指南 | Installation Guide

1. 确保已安装Python 3.8+ 
   (Ensure you have Python 3.8+ installed)
2. 克隆本仓库
   (Clone this repository)
3. 安装依赖 (Install dependencies)：
```bash
pip install -r requirements.txt
```

## 快速开始 | Quick Start

1. 运行主程序 (Run the main program)：
```bash
python main.py
```
2. 首次使用请导入示例数据或创建新的投资组合
   (On first use, import sample data or create a new portfolio)
3. 在"内在价值计算器"标签页进行股票DCF估值分析
   (Perform DCF stock valuation analysis in the "Intrinsic Value Calculator" tab)
4. 在"资产管理"标签页追踪投资组合
   (Track your portfolio in the "Portfolio Tracker" tab)

## 文件结构 | File Structure

```StockSifu/
├── main.py                # 程序入口 (Entry point)
├── requirements.txt       # 依赖列表 (Dependencies)
├── config/                
│   └── app_config.json    # 应用配置 (Language settings)
└── data/                  # 数据存储目录 (Data directory)
    ├── my_portfolio.json  # [隐私] 投资组合数据 (由程序自动生成，Git 已忽略)
    ├── dcf_watchlist.json # [隐私] 关注列表 (由程序自动生成，Git 已忽略)
    ├── *_sample.json      # 数据样板文件 (Sample data files)
```

## 数据文件 | Data Files

- `data/dcf_watchlist_sample.json` - 估值分析示例数据 (Sample data for valuation analysis)
- `data/my_portfolio_sample.json` - 投资组合示例数据 (Sample data for portfolio)

## 截图 | Screenshots

### **内在价值计算器 (Intrinsic Value Calculator)**
<img src="images/valuation_preview.jpg" width="100%" alt="Portfolio Dashboard" />

### **投资组合跟踪器 (Portfolio Tracker)**
<img src="images/portfolio_preview.jpg" width="100%" alt="Portfolio Dashboard" />

## 免责声明 | Disclaimer
- 本软件仅供个人学习和参考使用，不构成任何投资建议。股市有风险，投资需谨慎。开发者不对因使用本软件产生的任何投资损失负责。
- This software is for personal study and reference only and does not constitute any investment advice. Investing involves risks, including the possible loss of principal. Past performance is not indicative of future results. The developer is not responsible for any investment losses resulting from the use of this software.

## 许可证 | License
- 本项目采用 MIT 许可证。详情请见 `LICENSE` 文件。
- This project is licensed under the MIT License. See the `LICENSE` file for details.
