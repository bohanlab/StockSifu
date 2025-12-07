# StockSifu - 股票估值和持仓分析工具

## 主要功能

- **股票DCF估值**：支持 DCF 20 years 计算器
- **投资组合管理**：跟踪持仓、盈亏计算、资产分布

## 安装指南

1. 确保已安装Python 3.8+ 
2. 克隆本仓库
3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 快速开始

1. 运行主程序：
```bash
python main.py
```
2. 首次使用请导入示例数据或创建新的投资组合
3. 在"Valuation"标签页进行股票DCF估值分析
4. 在"Wealth"标签页管理投资组合

## 文件结构

```StockSifu/
├── main.py                # 程序入口 (Entry point)
├── requirements.txt       # 依赖列表 (Dependencies)
├── config/                
│   └── app_config.json    # 应用配置 (语言设置)
└── data/                  # 数据存储目录 (Data directory)
    ├── my_portfolio.json  # [隐私] 真实持仓数据 (由程序自动生成，Git 已忽略)
    ├── dcf_watchlist.json # [隐私] 估值关注列表 (由程序自动生成，Git 已忽略)
    ├── *_sample.json      # 数据样板文件 (用于示例)
```

## 数据文件

- `data/dcf_watchlist_sample.json` - 估值分析示例数据
- `data/my_portfolio_sample.json` - 投资组合示例数据

## 免责声明 (Disclaimer)

  本软件仅供个人学习和参考使用，不构成任何投资建议。股市有风险，投资需谨慎。开发者不对因使用本软件产生的任何投资损失负责。
