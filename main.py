import shutil
import customtkinter as ctk
import json
import os
import threading
import sys
from tkinter import messagebox, simpledialog
import matplotlib
# 设置后端为 Agg 以防止某些环境下的内存泄漏，必须在导入 pyplot 之前设置
matplotlib.use("TkAgg") 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# 尝试导入 yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ==========================================
# 🎨 Modern Light Theme (Fintech Style)
# ==========================================
THEME = {
    "bg": "#F3F4F6",           # 极浅灰背景
    "sidebar": "#FFFFFF",      # 纯白侧边栏
    "card": "#FFFFFF",         # 纯白卡片
    "card_hover": "#F9FAFB",   # 悬停微灰
    "list_selected": "#EFF6FF",# 选中项高亮
    "input_bg": "#F3F4F6",     # 输入框浅灰
    "input_text": "#111827",   # 输入框深黑
    
    "primary": "#2563EB",      # 品牌蓝
    "primary_hover": "#1D4ED8",
    
    "text_main": "#111827",    # 近乎纯黑
    "text_sub": "#6B7280",     # 中灰
    "border": "#E5E7EB",       # 极淡分割线
    "tag_bg": "#E0E7FF",       # 标签背景(浅蓝)
    "tag_text": "#3730A3",     # 标签文字(深靛蓝)
    "header_bg": "#F1F5F9",    # 分组标题背景
    
    # 盈亏颜色
    "profit_bg": "#DCFCE7",    "profit_text": "#166534",
    "loss_bg": "#FEE2E2",      "loss_text": "#991B1B",
    
    # 估值光谱
    "v_deep_val": "#059669",   "v_val": "#34D399", 
    "v_fair": "#64748B",       "v_over": "#F59E0B", "v_risk": "#EF4444",
    "bg_deep_val": "#ECFDF5",  "bg_val": "#D1FAE5", "bg_fair": "#F1F5F9", 
    "bg_over": "#FFFBEB",      "bg_risk": "#FEF2F2"
}

import platform

# --- 字体配置逻辑 ---
def get_font_stack():
    """根据操作系统选择最佳字体栈"""
    system = platform.system()
    
    # 1. 优先尝试现代 UI 字体
    # 如果你安装了 Inter，这里会优先使用。否则回退到系统默认。
    if system == "Windows":
        ui_family = "Microsoft YaHei UI" # 包含中文的更安全选择，或者 "Segoe UI"
        # 如果你想强制尝试 Inter (需用户安装): 
        # ui_family = "Inter" 
        mono_family = "Consolas"
    elif system == "Darwin": # macOS
        ui_family = ".AppleSystemUIFont" # San Francisco
        mono_family = "Menlo"
    else: # Linux
        ui_family = "DejaVu Sans"
        mono_family = "DejaVu Sans Mono"
        
    return ui_family, mono_family

UI_FONT, MONO_FONT = get_font_stack()

# 更加细腻的字体层级定义
FONTS = {
    # 核心数字展示 (如账户总值) - 大、粗、醒目
    "hero": (UI_FONT, 40, "bold"),
    
    # 一级标题 (如页面标题)
    "h1": (UI_FONT, 24, "bold"),
    
    # 二级标题 (如卡片标题)
    "h2": (UI_FONT, 16, "bold"),
    
    # 三级标题 (如分组名)
    "h3": (UI_FONT, 14, "bold"),
    
    # 正文 (列表内容) - 稍微调小字号增加精致感
    "body": (UI_FONT, 12),
    
    # 正文强调 (代码列)
    "body_bold": (UI_FONT, 12, "bold"),
    
    # 辅助信息 (名称、次要标签) - 使用更小的字号和灰色
    "sub": (UI_FONT, 11),
    
    # 辅助强调 (表头)
    "sub_bold": (UI_FONT, 11, "bold"),
    
    # 标签/胶囊文字 (极小，精细)
    "tag": (UI_FONT, 10, "bold"),
    
    # 等宽数据 (日志、对齐的表格数据)
    "mono": (MONO_FONT, 10),
    
    # 卡片数值 (盈亏数字)
    "card_val": (UI_FONT, 20, "bold")
}

# 货币符号映射
CURRENCY_SYMBOLS = {
    "USD": "$", "CNY": "¥", "HKD": "HK$", "EUR": "€", 
    "JPY": "¥", "GBP": "£", "AUD": "A$", "CAD": "C$", "SGD": "S$"
}

# ==========================================
# 🌍 I18N 配置
# ==========================================
LANG = {
    "CN": {
        "app_title": "Build Your Wealth",
        "nav_dcf": "内在价值计算器",
        "nav_port": "资产管理",
        
        "wl_title": "关注列表",
        "dcf_title": "参数配置",
        "res_title": "内在价值评估",
        
        "btn_calc": "开始计算",
        "btn_save_wl": "保存快照",
        "btn_new_val": "＋ 新建", 
        
        "grp_basic": "基础信息",
        "grp_fin": "财务数据",
        "grp_growth": "增长与折现",
        "grp_more": "汇率",
        
        "name": "名称", "symbol": "股票代码", "method": "估值模型", 
        "cf_val": "现金流 (百万元)", "debt": "负债 (百万元)", "cash": "现金 (百万元)", "shares": "股本 (百万)",
        "g1": "1-5年增长 (%)", "g2": "6-10年增长 (%)", "g3": "11-20年增长 (%)", "dr": "折现率 (%)",
        "fin_curr": "财报货币", "list_curr": "上市交易货币", "rate": "汇率", "close": "最新价 (元/股)",
        "rate_hint": "即: 1 {0} = {2} {1}", 
        "iv_lbl": "每股内在价值", "mos_lbl": "溢价率 (Price vs IV)",
        "val_date": "估值更新于 (年/月)", 
        
        "r_v_und": "💎 非常低估", "r_und": "✅ 低估", "r_fair": "⚖️ 合理",
        "r_over": "⚠️ 高估", "r_v_over": "⛔️ 非常高估",
        
        "p_title": "我的财富概览", 
        "card_net_worth": "总资产净值", 
        "card_cost": "总投入成本",
        "card_pl": "浮动盈亏",
        
        "p_add_btn": "➕ 记一笔持仓", 
        "p_close_btn": "− 收起面板",
        "p_batch_btn": "📈 批量更新行情",
        "p_batch_title": "批量更新 (市价 & 汇率)",
        "p_fetch": "⚡ 联网获取",
        "p_price_col": "最新市价",
        "p_fx_col": "当前汇率",
        "p_disp_curr": "显示货币:", 
        "p_global_rate": "汇率 (1 USD = ?):", 
        
        "p_edit_title": "编辑持仓",
        "p_del": "删除", 
        "p_save": "保存持仓",
        "p_clear": "重置",
        "p_add": "添加持仓",
        "p_edit": "编辑",
        
        "f_ticker": "代码", "f_name": "名称", "f_sec": "板块","f_country": "国家/地区",
        "f_curr": "货币", "f_fx": "汇率", "f_qty": "持仓数", "f_cost": "持仓均价",
        
        "tab_holdings": "持仓分布", "tab_sectors": "板块配置", "tab_countries": "地区分布",
        "msg_updating": "正在同步全球行情...",
        "msg_updated": "更新完成！",
        "err_no_yf": "未安装 yfinance 库",
        "err_input_missing": "请填写所有必要参数。",
        "err_input_invalid": "请输入有效的数字。",
        "err_cf_missing": "请输入现金流数据。",
        
        "settings": "设置",
        "lang_sel": "语言选择",
        "restart_msg": "语言已更改，请重启应用以生效。",
        "save_btn": "保存并关闭",
        "msg_calc_done": "计算完成 ✅",
        "msg_save_done": "已保存到关注列表 💾",
        "msg_new_ready": "已重置，准备新建 ✨",
        
        "sort_lbl": "排序:",
        "group_lbl": "分组:",
        "sort_opts": ["市值 (高→低)", "市值 (低→高)", "盈亏 (高→低)", "代码 (A-Z)"],
        "group_opts": ["不分组", "按版块", "按地区"],
        "other_group": "其他",
        "wl_welcome_title": "👋 欢迎使用!",
        "wl_welcome_msg": "点击右侧的 [+ 新建] 按钮\n开始您的第一次估值分析吧！",

        "methods": {
            "ocf": {"name": "经营现金流贴现", "label": "经营现金流 (百万元)"},
            "ni":  {"name": "净利润贴现", "label": "净利润 (百万元)"},
            "fcf": {"name": "自由现金流贴现", "label": "自由现金流 (百万元)"}
        },
        "default_method_key": "ocf"
    },
    "EN": {
        "app_title": "Build Your Wealth",
        "nav_dcf": "Intrinsic Value Calculator",
        "nav_port": "My Portfolio",
        
        "wl_title": "Watchlist",
        "dcf_title": "Configuration",
        "res_title": "Intrinsic Value",
        
        "btn_calc": "Calculate",
        "btn_save_wl": "Save Snapshot",
        "btn_new_val": "＋ New", 
        
        "grp_basic": "Basics",
        "grp_fin": "Financials",
        "grp_growth": "Growth & Discount",
        "grp_more": "Exchange Rate",
        
        "name": "Name", "symbol": "Ticker Symbol", "method": "Valuation Model", 
        "cf_val": "Base CF (Millions)", "debt": "Total Debt (Short Term + LT Debt) (Millions)", "cash": "Cash & Short Term Investments (Millions)", "shares": "No. of Shares Outstanding (Millions)",
        "g1": "Growth 1-5y (%)", "g2": "Growth 6-10y (%)", "g3": "Growth 11-20y (%)", "dr": "Discount Rate (%)",
        "fin_curr": "Financial Statement Currency", "list_curr": "Stock Listing Currency", "rate": "Exchange Rate", "close": "Last Close (Per Share)",
        "rate_hint": "i.e. 1 {0} = {2} {1}",
        "iv_lbl": "Intrinsic Value Per Share", "mos_lbl": "Premium/Discount",
        "val_date": "Valuation Date (Y/M)",
        
        "r_v_und": "💎 Very Undervalued", "r_und": "✅ Undervalued", "r_fair": "⚖️ Fair Value",
        "r_over": "⚠️ Overvalued", "r_v_over": "⛔️ Very Overvalued",
        
        "p_title": "Wealth Overview", 
        "card_net_worth": "Net Worth",
        "card_cost": "Cost",
        "card_pl": "Unrealized P&L",
        
        "p_add_btn": "➕ Add Position", 
        "p_close_btn": "− Close",
        "p_batch_btn": "📈 Batch Update",
        "p_batch_title": "Batch Update Market Data",
        "p_fetch": "⚡ Auto Fetch",
        "p_price_col": "Last Price",
        "p_fx_col": "Current Exchange Rate",
        "p_disp_curr": "Display Currency:", 
        "p_global_rate": "Rate (1 USD = ?):", 
        
        "p_edit_title": "Edit Position",
        "p_del": "Del", 
        "p_save": "Save Position",
        "p_clear": "Reset",
        "p_add": "Add Position",
        "p_edit": "Edit",
        
        "f_ticker": "Ticker", "f_name": "Name", "f_sec": "Sector","f_country": "Country",
        "f_curr": "Listed Currency", "f_fx": "Exchange Rate", "f_qty": "Quantity", "f_cost": "Avg Cost per Share",
        
        "tab_holdings": "Holdings %", "tab_sectors": "Sector %", "tab_countries": "Country %",
        "msg_updating": "Updating prices...",
        "msg_updated": "Update Complete!",
        "err_no_yf": "yfinance not found",
        "err_input_missing": "Please fill in all required fields.",
        "err_input_invalid": "Please enter valid numbers.",
        "err_cf_missing": "Cash Flow data is required.",
        
        "settings": "Settings",
        "lang_sel": "Language Selection",
        "restart_msg": "Language changed. Please restart the app.",
        "save_btn": "Save & Close",
        # --- New Feedback Messages ---
        "msg_calc_done": "Calculation complete ✅",
        "msg_save_done": "Saved to Watchlist 💾",
        "msg_new_ready": "Form reset. Ready for new input ✨",
        
        # --- New: Sort & Group ---
        "sort_lbl": "Sort:",
        "group_lbl": "Group:",
        "sort_opts": ["Value Desc", "Value Asc", "P&L Desc", "Ticker A-Z"],
        "group_opts": ["None", "By Sector", "By Country"],
        "other_group": "Other",
        "wl_welcome_title": "👋 Welcome!",
        "wl_welcome_msg": "Click the [+ New] button on the right\nto start your first valuation analysis!",

        "methods": {
            "ocf": {"name": "Discounted Cash Flow", "label": "Operating Cash Flow (Millions)"},
            "ni":  {"name": "Discounted Net Income", "label": "Net Income (Millions)"},
            "fcf": {"name": "Discounted Free Cash Flow", "label": "Free Cash Flow (Millions)"}
        },
        "default_method_key": "ocf"
    }
}

DATA_DIR = "data"
CONFIG_DIR = "config"

# 自动创建目录（如果不存在）
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)

PORTFOLIO_FILE = os.path.join(DATA_DIR, "my_portfolio.json")
WATCHLIST_FILE = os.path.join(DATA_DIR, "dcf_watchlist.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "app_config.json")

# 定义样板文件路径 (Samples)
PORTFOLIO_SAMPLE = os.path.join(DATA_DIR, "my_portfolio_sample.json")
WATCHLIST_SAMPLE = os.path.join(DATA_DIR, "dcf_watchlist_sample.json")

# --- 初始化用户数据函数 ---
def init_user_data():
    if not os.path.exists(PORTFOLIO_FILE):
        if os.path.exists(PORTFOLIO_SAMPLE):
            try:
                shutil.copy(PORTFOLIO_SAMPLE, PORTFOLIO_FILE)
                print(f"初始化成功: 已从样板创建 {PORTFOLIO_FILE}")
            except Exception as e:
                print(f"复制样板失败: {e}")
        else:
            # 样板也不存在，创建空数组
            print(f"未找到样板，创建空持仓文件: {PORTFOLIO_FILE}")
            with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    # 2. 初始化关注列表文件 (dcf_watchlist.json)
    if not os.path.exists(WATCHLIST_FILE):
        if os.path.exists(WATCHLIST_SAMPLE):
            try:
                shutil.copy(WATCHLIST_SAMPLE, WATCHLIST_FILE)
                print(f"初始化成功: 已从样板创建 {WATCHLIST_FILE}")
            except Exception as e:
                print(f"复制样板失败: {e}")
        else:
            # 样板也不存在，创建空字典结构
            print(f"未找到样板，创建空关注列表: {WATCHLIST_FILE}")
            default_wl = {"Default": []}
            with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_wl, f)

# --- 在类定义之前，必须调用一次初始化 ---
init_user_data()

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ==========================================
# 🧩 优化后的 UI 组件库
# ==========================================
class CleanCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", THEME["card"])
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", THEME["border"])
        super().__init__(master, **kwargs)

class StatsCard(CleanCard):
    def __init__(self, master, title, value, sub_text="", value_color=THEME["text_main"], **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=THEME["card"]) 
        ctk.CTkLabel(self, text=title, font=FONTS["sub_bold"], text_color=THEME["text_sub"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.lbl_val = ctk.CTkLabel(self, text=value, font=FONTS["card_val"], text_color=value_color)
        self.lbl_val.pack(anchor="w", padx=15)
        self.lbl_sub = ctk.CTkLabel(self, text=sub_text, font=FONTS["sub"], text_color=THEME["text_sub"])
        self.lbl_sub.pack(anchor="w", padx=15, pady=(0, 15))

    def update_value(self, value, sub_text="", color=None):
        self.lbl_val.configure(text=value)
        if color: self.lbl_val.configure(text_color=color)
        if sub_text: self.lbl_sub.configure(text=sub_text)

class CleanEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", THEME["input_bg"])
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("text_color", THEME["input_text"])
        kwargs.setdefault("placeholder_text_color", THEME["text_sub"])
        kwargs.setdefault("height", 34)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", FONTS["body"])
        super().__init__(master, **kwargs)

class CleanCombo(ctk.CTkComboBox):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", THEME["input_bg"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", THEME["border"])
        kwargs.setdefault("button_color", THEME["input_bg"])
        kwargs.setdefault("button_hover_color", THEME["card_hover"])
        kwargs.setdefault("text_color", THEME["text_main"])
        kwargs.setdefault("dropdown_fg_color", THEME["card"])
        kwargs.setdefault("dropdown_text_color", THEME["text_main"])
        kwargs.setdefault("dropdown_hover_color", THEME["list_selected"])
        kwargs.setdefault("height", 34)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", FONTS["body"])
        
        super().__init__(master, **kwargs)

class SectionHeader(ctk.CTkLabel):
    def __init__(self, master, text):
        super().__init__(master, text=text, font=FONTS["sub_bold"], text_color=THEME["primary"], anchor="w")

class OptimizedChart(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.fig, self.ax = plt.subplots(figsize=(4, 4), dpi=100)
        self.fig.patch.set_facecolor(THEME["card"])
        self.ax.set_facecolor(THEME["card"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def update_data(self, data_map, is_donut=False):
        try:
            self.ax.clear()
            if not data_map:
                self.canvas.draw()
                return

            cols = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
            vals = list(data_map.values())
            labels = list(data_map.keys())
            
            wedges, texts, autotexts = self.ax.pie(
                vals, labels=labels, autopct='%1.1f%%', startangle=90, 
                colors=cols[:len(vals)], pctdistance=0.85,
                textprops={'color': THEME["text_main"], 'fontsize': 8}
            )
            
            if is_donut:
                centre_circle = plt.Circle((0,0), 0.60, fc='white')
                self.ax.add_artist(centre_circle)
                
            self.ax.axis('equal')
            
            # 4. 重绘
            self.canvas.draw()
        except Exception:
            pass

class CleanInputDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Input", prompt="Enter value:"):
        super().__init__(master)
        self.title(title)
        self.geometry("320x180")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card"])
        
        # 居中显示
        # self.eval(f'tk::PlaceWindow {self._w} center') # 有时在CTk中不稳定，手动计算位置更好
        
        self.result = None
        
        # 界面布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text=prompt, font=FONTS["h3"], text_color=THEME["text_main"]).pack(anchor="w", pady=(0, 10))
        
        self.entry = CleanEntry(container)
        self.entry.pack(fill="x", pady=(0, 20))
        self.entry.bind("<Return>", self.on_ok)
        self.entry.focus_set() # 自动聚焦
        
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x")
        
        ctk.CTkButton(btn_box, text="Cancel", width=100, fg_color=THEME["input_bg"], 
                      text_color=THEME["text_main"], hover_color=THEME["card_hover"], 
                      command=self.destroy).pack(side="left")
                      
        ctk.CTkButton(btn_box, text="Confirm", width=100, fg_color=THEME["primary"], 
                      text_color="white", command=self.on_ok).pack(side="right")

    def on_ok(self, event=None):
        self.result = self.entry.get()
        self.destroy()

    def show(self):
        self.transient(self.master) # 设置为临时窗口
        self.grab_set()             # 模态：禁止操作主窗口
        self.wait_window(self)      # 等待窗口关闭
        return self.result

# ==========================================
# 🚀 主程序
# ==========================================
class StockSifuUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 修改 1: 加载配置 ---
        self.config = self.load_json(CONFIG_FILE, {"language": "CN"})
        self.lang_code = self.config.get("language", "CN")
        self.t = LANG[self.lang_code]
        # ----------------------
        
        self.geometry("1920x1080")
        self.title(self.t["app_title"])
        self.configure(fg_color=THEME["bg"])

        # 绑定关闭事件，处理 "invalid command name" 错误
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 数据加载
        self.watchlist_data = self.load_json(WATCHLIST_FILE, {"Default": []})
        self.portfolio_data = self.load_json(PORTFOLIO_FILE, [])
        self.editing_port_idx = -1
        
        self.selected_wl_symbol = None
        self.watchlist_width = 320
        self.show_input_panel = False
        
        # --- 新增：Watchlist 编辑模式状态 ---
        self.wl_edit_mode = False

        # --- 拖拽状态 ---
        self.drag_data = {"group": None, "index": None, "item": None}
        self.drag_active_row = None # 当前被拖拽的行引用
        self.drag_indicator_window = None # 使用独立窗口作为指引线
        self.proposed_drop_index = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.show_dcf()
        
        self.is_running = True

    def on_closing(self):
        self.is_running = False
        plt.close('all')
        self.quit()
        self.destroy()

    def load_json(self, f, default):
        if os.path.exists(f):
            try: return json.load(open(f, "r", encoding="utf-8"))
            except: return default
        return default

    # 优化：异步保存，避免 IO 阻塞 UI
    def save_json_async(self, f, d):
        def _save_task():
            try:
                with open(f, "w", encoding="utf-8") as file:
                    json.dump(d, file, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Save failed: {e}")
        
        threading.Thread(target=_save_task, daemon=True).start()

    # --- 侧边栏 ---
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=THEME["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_box.pack(pady=(30, 30), padx=20, anchor="w")
        ctk.CTkLabel(logo_box, text=self.t["app_title"], font=FONTS["h2"], text_color=THEME["text_main"]).pack(anchor="w")
        
        self.nav_btns = {}
        self.create_nav_btn("dcf", "📊  " + self.t["nav_dcf"], self.show_dcf)
        self.create_nav_btn("port", "💰  " + self.t["nav_port"], self.show_port)

        # --- 修改 2: 侧边栏按钮改为“设置” ---
        settings_text = "⚙️ " + self.t["settings"]
        ctk.CTkButton(self.sidebar, text=settings_text, width=140, height=32, 
                      fg_color=THEME["input_bg"], hover_color=THEME["card_hover"],
                      text_color=THEME["text_main"], font=FONTS["sub"], command=self.open_settings).pack(side="bottom", pady=20)
        # -----------------------------------

    def create_nav_btn(self, key, text, cmd):
        btn = ctk.CTkButton(self.sidebar, text=text, font=FONTS["body"], 
                            fg_color="transparent", text_color=THEME["text_sub"], 
                            hover_color=THEME["card_hover"], anchor="w", height=42, corner_radius=8, command=cmd)
        btn.pack(fill="x", padx=10, pady=2)
        self.nav_btns[key] = btn

    def set_active_nav(self, key):
        for k, btn in self.nav_btns.items():
            if k == key: btn.configure(fg_color=THEME["input_bg"], text_color=THEME["primary"], font=FONTS["body_bold"])
            else: btn.configure(fg_color="transparent", text_color=THEME["text_sub"], font=FONTS["body"])

    def rebuild_ui(self):
        """销毁并重建所有UI组件以应用更改(如语言)"""
        # 1. 销毁顶层组件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 2. 重新加载翻译
        self.t = LANG[self.lang_code]
        self.title(self.t["app_title"])
        
        # 3. 重新构建UI
        self.setup_sidebar()
        self.setup_main_area()
        
        # 4. 恢复到之前的视图 (或默认视图)
        # 注意: 如果视图状态很复杂, 这里可能需要保存和恢复更多状态
        self.show_dcf()

    # --- 修改 3: 新增设置窗口逻辑 ---
    def open_settings(self):
        t = ctk.CTkToplevel(self)
        t.geometry("400x250")
        t.title(self.t["settings"])
        t.configure(fg_color=THEME["bg"])
        
        # 设为模态窗口
        t.transient(self)
        t.grab_set()
        
        container = CleanCard(t)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text=self.t["lang_sel"], font=FONTS["h3"], text_color=THEME["text_main"]).pack(anchor="w", padx=20, pady=(20, 10))
        
        # 语言选择
        current_display = "中文" if self.lang_code == "CN" else "English"
        self.lang_var = ctk.StringVar(value=current_display)
        combo = CleanCombo(container, values=["中文", "English"], variable=self.lang_var, width=200)
        combo.pack(padx=20, pady=10)
        
        def save_and_refresh():
            new_lang = "CN" if self.lang_var.get() == "中文" else "EN"
            if new_lang != self.lang_code:
                self.lang_code = new_lang
                self.config["language"] = new_lang
                self.save_json_async(CONFIG_FILE, self.config)
                self.rebuild_ui() # 调用重建UI的方法
            t.destroy()
            
        ctk.CTkButton(container, text=self.t["save_btn"], fg_color=THEME["primary"], height=36, command=save_and_refresh).pack(pady=20)

 # --- 批量更新窗口 ---
    def open_batch_update_window(self):
        t = ctk.CTkToplevel(self)
        t.geometry("600x500")
        t.title(self.t["p_batch_title"])
        t.configure(fg_color=THEME["bg"])
        t.transient(self)
        t.grab_set()
        
        top = ctk.CTkFrame(t, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(top, text=self.t["p_batch_title"], font=FONTS["h3"], text_color=THEME["text_main"]).pack(side="left")
        
        scroll = ctk.CTkScrollableFrame(t, fg_color=THEME["card"])
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        head = ctk.CTkFrame(scroll, fg_color="transparent")
        head.pack(fill="x", pady=5)
        headers = [self.t["f_ticker"], self.t["f_name"], self.t["p_price_col"], self.t["p_fx_col"]]
        widths = [60, 120, 100, 80]
        for txt, w in zip(headers, widths):
            ctk.CTkLabel(head, text=txt, width=w, font=FONTS["sub_bold"], text_color=THEME["text_sub"], anchor="w").pack(side="left", padx=5)
            
        self.batch_entries = [] 
        
        for idx, item in enumerate(self.portfolio_data):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=item.get("ticker", ""), width=60, anchor="w", font=FONTS["body_bold"]).pack(side="left", padx=5)
            name_txt = item.get("name", "")
            if len(name_txt) > 12: name_txt = name_txt[:12] + "..."
            ctk.CTkLabel(row, text=name_txt, width=120, anchor="w", font=FONTS["body"]).pack(side="left", padx=5)
            
            curr_p = item.get("last_price", 0)
            if curr_p == 0: curr_p = item.get("cost", 0) 
            
            e_price = CleanEntry(row, width=100)
            e_price.insert(0, str(curr_p))
            e_price.pack(side="left", padx=5)
            
            # Use stored FX or 1.0
            e_fx = CleanEntry(row, width=80)
            e_fx.insert(0, str(item.get("fx", 1.0)))
            e_fx.pack(side="left", padx=5)
            
            self.batch_entries.append((idx, e_price, e_fx))

        bot = ctk.CTkFrame(t, fg_color="transparent")
        bot.pack(fill="x", padx=20, pady=20)
        
        def run_fetch():
            if not YFINANCE_AVAILABLE:
                messagebox.showerror("Error", self.t["err_no_yf"])
                return
            
            btn_fetch.configure(state="disabled", text="⏳ Fetching...")
            t.configure(cursor="watch")
            
            def _thread_task():
                tickers = [self.portfolio_data[i]["ticker"] for i, _, _ in self.batch_entries]
                uniq_tickers = list(set([self.fix_ticker_for_yfinance(tik) for tik in tickers if tik]))
                
                currencies = list(set([self.portfolio_data[i].get("curr", "USD") for i, _, _ in self.batch_entries]))
                fx_tickers = [f"{c}=X" for c in currencies if c != "USD"]
                
                market_data = {}

                # 核心提取逻辑：兼容各种返回结构
                def extract_price(dataset, sym, is_single_request):
                    try:
                        val = None
                        # 路径 A: 多级索引 (最常见) -> dataset[sym]['Close']
                        # 探测 dataset 是否有 levels 属性
                        if hasattr(dataset.columns, 'levels') and sym in dataset.columns.levels[0]:
                            series = dataset[sym]['Close']
                            val = series.dropna().iloc[-1]
                        
                        # 路径 B: 单级索引 (只请求了1个代码时)
                        elif is_single_request and 'Close' in dataset.columns:
                            val = dataset['Close'].dropna().iloc[-1]
                            
                        if val is not None:
                            return float(val.item()) if hasattr(val, 'item') else float(val)
                    except: pass
                    return None

                def fetch_group(ticker_list):
                    if not ticker_list: return
                    try:
                        # 必须使用 group_by='ticker' 以获得相对稳定的结构
                        data = yf.download(ticker_list, period="5d", group_by='ticker', threads=True, progress=False, auto_adjust=False)
                        
                        if not data.empty:
                            is_single = len(ticker_list) == 1
                            for t in ticker_list:
                                price = extract_price(data, t, is_single)
                                if price and price > 0:
                                    market_data[t] = price
                    except Exception as e:
                        print(f"Fetch group error: {e}")

                # 分开下载股票和汇率，避免索引混乱
                fetch_group(uniq_tickers)
                fetch_group(fx_tickers)
                
                self.after(0, lambda: _update_ui(market_data))

            def _update_ui(data_map):
                count = 0
                for idx, e_p, e_fx in self.batch_entries:
                    item = self.portfolio_data[idx]
                    tik = self.fix_ticker_for_yfinance(item["ticker"])
                    
                    # Update Price
                    if tik in data_map:
                        e_p.delete(0, "end")
                        e_p.insert(0, f"{data_map[tik]:.2f}")
                        count += 1
                    
                    # Update FX
                    curr = item.get("curr", "USD")
                    if curr == "USD":
                         e_fx.delete(0, "end"); e_fx.insert(0, "1.0")
                    else:
                        fx_tik = f"{curr}=X"
                        if fx_tik in data_map:
                            e_fx.delete(0, "end"); e_fx.insert(0, f"{data_map[fx_tik]:.4f}")

                btn_fetch.configure(state="normal", text=self.t["p_fetch"], fg_color=THEME["primary"], text_color="white")
                t.configure(cursor="")
                
                if count == 0 and len(data_map) == 0:
                      messagebox.showinfo("Info", "No data updated. Check network/tickers.")
                
            threading.Thread(target=_thread_task, daemon=True).start()

        def save_batch():
            for idx, e_p, e_fx in self.batch_entries:
                try:
                    p_str = e_p.get().replace(",", "")
                    fx_str = e_fx.get().replace(",", "")
                    new_p = float(p_str)
                    new_fx = float(fx_str)
                    self.portfolio_data[idx]["last_price"] = new_p
                    self.portfolio_data[idx]["fx"] = new_fx
                except: pass
            
            self.save_json_async(PORTFOLIO_FILE, self.portfolio_data)
            self.refresh_port_view()
            t.destroy()

        btn_fetch = ctk.CTkButton(bot, text=self.t["p_fetch"],fg_color=THEME["primary"], text_color="white", command=run_fetch)
        btn_fetch.pack(side="left")
        
        ctk.CTkButton(bot, text=self.t["save_btn"], fg_color=THEME["primary"], width=120, command=save_batch).pack(side="right")

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- 核心优化: 创建持久化的视图框架 ---
        self.dcf_view_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.port_view_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        for frame in (self.dcf_view_frame, self.port_view_frame):
            frame.grid(row=0, column=0, sticky="nsew")
        
        # --- 一次性构建所有视图 ---
        self.create_dcf_ui(self.dcf_view_frame)
        self.create_port_ui(self.port_view_frame)

    def clear_main(self):
        # 这个方法现在不再需要，因为我们不再销毁视图
        pass

    # ==================================================================
    # 💎 Module 1: DCF Calculator
    # ==================================================================
    def show_dcf(self):
        self.set_active_nav("dcf")
        self.dcf_view_frame.tkraise() # --- 核心优化: 只需置顶，无需重建 ---
        
    def create_dcf_ui(self, parent_frame):
        # --- 这个方法包含了原来 show_dcf() 中所有创建UI的逻辑 ---
        self.dcf_grid = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.dcf_grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.wl_container = ctk.CTkFrame(self.dcf_grid, fg_color="transparent", width=self.watchlist_width)
        self.wl_container.pack(side="left", fill="y", padx=(0, 10))
        self.wl_container.pack_propagate(False) 
        
        self.btn_resize = ctk.CTkButton(self.dcf_grid, text="«", width=20, height=40, fg_color=THEME["card"], 
                                        text_color=THEME["text_sub"], hover_color=THEME["card_hover"],
                                        command=self.toggle_watchlist_width)
        self.btn_resize.pack(side="left", fill="y", padx=(0, 5))

        right_content = ctk.CTkFrame(self.dcf_grid, fg_color="transparent")
        right_content.pack(side="right", fill="both", expand=True)
        right_content.grid_columnconfigure(0, weight=3)
        right_content.grid_columnconfigure(1, weight=2)
        right_content.grid_rowconfigure(0, weight=1)

        self.build_watchlist_ui(self.wl_container)

        input_card = CleanCard(right_content)
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        in_head = ctk.CTkFrame(input_card, fg_color="transparent")
        in_head.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(in_head, text=self.t["dcf_title"], font=FONTS["h2"], text_color=THEME["text_main"]).pack(side="left")
        ctk.CTkButton(in_head, text="💾", width=36, height=28, fg_color=THEME["input_bg"], text_color=THEME["text_main"], command=self.save_to_wl).pack(side="right", padx=(5,0))
        ctk.CTkButton(in_head, text=self.t["btn_new_val"], width=36, height=28, fg_color=THEME["input_bg"], text_color=THEME["text_main"], command=self.reset_dcf_form).pack(side="left", padx=(5,0))

        self.grp_combo = CleanCombo(in_head, values=list(self.watchlist_data.keys()), width=120)
        self.grp_combo.pack(side="right")

        self.in_scroll = ctk.CTkScrollableFrame(input_card, fg_color="transparent")
        self.in_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 20))
        self.entries = {}
        self.init_dcf_inputs()

        ctk.CTkButton(input_card, text=self.t["btn_calc"], height=48, font=FONTS["h3"],
                      fg_color=THEME["primary"], hover_color=THEME["primary_hover"], corner_radius=24,
                      command=self.run_calculation).pack(fill="x", padx=40, pady=(30, 5))
                      
        self.lbl_status = ctk.CTkLabel(input_card, text="", font=FONTS["sub"], text_color=THEME["primary"])
        self.lbl_status.pack(pady=(0, 10))

        res_frame = ctk.CTkFrame(right_content, fg_color="transparent")
        res_frame.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(res_frame, text=self.t["res_title"], font=FONTS["h2"], text_color=THEME["text_main"]).pack(anchor="w", pady=(0, 15))
        
        hero_card = CleanCard(res_frame)
        hero_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(hero_card, text=self.t["iv_lbl"], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(pady=(25, 5))
        self.lbl_iv_big = ctk.CTkLabel(hero_card, text="---", font=FONTS["hero"], text_color=THEME["text_main"])
        self.lbl_iv_big.pack(pady=(0, 10))
        
        self.lbl_mos_badge = ctk.CTkButton(hero_card, text="---", height=32, corner_radius=16, 
                                            fg_color=THEME["input_bg"], text_color=THEME["text_main"], hover=False)
        self.lbl_mos_badge.pack(pady=(0, 25))

        self.txt_log = ctk.CTkTextbox(res_frame, fg_color=THEME["card"], text_color=THEME["text_sub"], 
                                      font=FONTS["mono"], corner_radius=10, border_width=1, border_color=THEME["border"])
        self.txt_log.pack(fill="both", expand=True)

    # --- 新增: 通用反馈 ---
    def show_feedback(self, msg, is_error=False):
        color = THEME["v_risk"] if is_error else THEME["v_deep_val"] 
        self.lbl_status.configure(text=msg, text_color=color)
        self.after(3000, lambda: self.lbl_status.configure(text=""))

    def run_calculation(self):
        # 执行计算
        gap, iv = self.calculate_dcf()
        # 如果 calculation 返回 0,0 可能是因为验证失败（已经弹窗警告），这里就不显示“计算完成”了
        if gap == 0 and iv == 0:
            return 
        self.show_feedback(self.t["msg_calc_done"])

    def toggle_watchlist_width(self):
        if self.watchlist_width > 100:
            self.watchlist_width = 0 
            self.btn_resize.configure(text="»")
        else:
            self.watchlist_width = 320 
            self.btn_resize.configure(text="«")
        
        if self.watchlist_width == 0:
            self.wl_container.pack_forget()
        else:
            self.wl_container.configure(width=self.watchlist_width)
            self.wl_container.pack(side="left", fill="y", padx=(0, 10), before=self.btn_resize)

    def build_watchlist_ui(self, parent):
        wl_frame = CleanCard(parent)
        wl_frame.pack(fill="both", expand=True)
        
        head = ctk.CTkFrame(wl_frame, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(head, text=self.t["wl_title"], font=FONTS["h3"], text_color=THEME["text_main"]).pack(side="left")
        
        tools = ctk.CTkFrame(head, fg_color="transparent")
        tools.pack(side="right")
        self.btn_refresh = ctk.CTkButton(tools, text="🔄", width=28, height=24, fg_color=THEME["input_bg"], 
                               text_color=THEME["primary"], hover_color=THEME["card_hover"],
                               command=self.refresh_all_prices_thread)
        self.btn_refresh.pack(side="left", padx=2)
        
        # --- 修改：增加编辑按钮 ---
        self.btn_edit_wl = ctk.CTkButton(tools, text="✎", width=28, height=24, fg_color=THEME["input_bg"], 
                                         text_color=THEME["primary"], hover_color=THEME["card_hover"],
                                         command=self.toggle_wl_edit_mode)
        self.btn_edit_wl.pack(side="left", padx=2)
        # ------------------------

        ctk.CTkButton(tools, text="+", width=28, height=24, fg_color=THEME["input_bg"], text_color=THEME    ["primary"], hover_color=THEME["card_hover"], command=self.add_wl_group).pack(side="left", padx=2)

        self.wl_scroll = ctk.CTkScrollableFrame(wl_frame, fg_color="transparent")
        self.wl_scroll.pack(fill="both", expand=True)
        self.render_watchlist()

    # --- 新增：切换编辑模式 ---
    def toggle_wl_edit_mode(self):
        self.wl_edit_mode = not self.wl_edit_mode
        # 更新按钮图标和颜色
        if self.wl_edit_mode:
            self.btn_edit_wl.configure(text="✓", fg_color=THEME["primary"], text_color="white",hover_color=THEME["primary_hover"])
        else:
            self.btn_edit_wl.configure(text="✎", fg_color=THEME["input_bg"], 
                                         text_color=THEME["primary"], hover_color=THEME["card_hover"])
        
        # 重新渲染列表以显示/隐藏控件
        self.render_watchlist()

    def fix_ticker_for_yfinance(self, symbol):
        s = symbol.strip().upper()
        if s.isdigit() and len(s) <= 5: 
            return f"{s.zfill(4)}.HK"
        if s.isdigit() and len(s) == 6:
            if s.startswith("6"): return f"{s}.SS" 
            if s.startswith("0") or s.startswith("3"): return f"{s}.SZ" 
            if s.startswith("8") or s.startswith("4"): return f"{s}.BJ" 
        return s 

    # --- 🚦 批量防限流更新 ---
    def refresh_all_prices_thread(self):
        threading.Thread(target=self.refresh_all_prices, daemon=True).start()

    def refresh_all_prices(self):
        if not YFINANCE_AVAILABLE:
            messagebox.showerror("Error", self.t["err_no_yf"])
            return

        self.btn_refresh.configure(state="disabled", text="⏳")
        self.configure(cursor="watch")
        
        all_items = []
        for group, items in self.watchlist_data.items():
            for item in items:
                sym = item.get("symbol")
                if sym: all_items.append((self.fix_ticker_for_yfinance(sym), item))
        
        tickers_list = [x[0] for x in all_items]
        
        if not self.winfo_exists(): return
        if not tickers_list:
            self.after(0, self.reset_refresh_state)
            return

        updated_count = 0
        try:
            # --- 核心修复: 适配新版 yfinance 的数据结构 ---
            # 1. 移除已过时的 group_by='ticker' 参数。
            # 2. 将周期设为 '2d' 以确保能取到最近的交易日数据。
            data = yf.download(tickers_list, period="2d", threads=True, progress=False, auto_adjust=False)
            
            if not data.empty:
                close_prices = data.get('Close')
                if close_prices is None:
                    raise ValueError("Could not retrieve 'Close' prices.")

                # 情况 1: 关注列表中只有一只股票
                if len(tickers_list) == 1:
                    if hasattr(close_prices, 'iloc') and not close_prices.dropna().empty:
                        price = float(close_prices.dropna().iloc[-1])
                        if price > 0:
                            item = all_items[0][1] # 获取唯一的项目
                            item["last_close"] = price
                            iv = item.get("last_iv", 0)
                            if iv > 0:
                                gap = (price - iv) / iv
                                item["last_gap"] = gap
                            updated_count += 1
                
                # 情况 2: 关注列表中有多只股票
                elif hasattr(close_prices, 'columns'):
                    for yf_sym, item in all_items:
                        try:
                            if yf_sym in close_prices.columns:
                                series = close_prices[yf_sym]
                                if not series.dropna().empty:
                                    price = float(series.dropna().iloc[-1])
                                    if price > 0:
                                        item["last_close"] = price
                                        iv = item.get("last_iv", 0)
                                        if iv > 0:
                                            gap = (price - iv) / iv
                                            item["last_gap"] = gap
                                        updated_count += 1
                        except Exception:
                            # 忽略处理单个股票时的错误，继续更新其他股票
                            pass
                    
        except Exception as e:
            print(f"Batch update failed: {e}")

        if not self.winfo_exists(): return

        self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
        self.after(0, lambda: self.finish_refresh(updated_count))

    def finish_refresh(self, count):
        # 安全检查：确保窗口还存在
        if not self.winfo_exists(): return
        
        self.render_watchlist()
        self.reset_refresh_state()
        messagebox.showinfo("Success", f"{self.t['msg_updated']} ({count})")

    def reset_refresh_state(self):
        if not self.winfo_exists(): return
        self.btn_refresh.configure(state="normal", text="🔄")
        self.configure(cursor="")

    def init_dcf_inputs(self):
        f = self.in_scroll
        def add_field(parent, key, default, r, c, is_combo=False, width=None):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            parent.columnconfigure(c, weight=1)
            
            ctk.CTkLabel(frame, text=self.t.get(key, key), font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w", pady=(0, 2))
            
            if is_combo:
                # --- 核心修改: 使用新的`methods`结构 ---
                # 1. 创建从显示名称到中性键的映射
                self.method_display_to_key_map = {v["name"]: k for k, v in self.t["methods"].items()}
                
                # 2. 获取要在下拉菜单中显示的名称列表
                options = list(self.method_display_to_key_map.keys())
                
                w = CleanCombo(frame, values=options, height=32, command=self.on_method_change)
                
                # 3. 设置默认值
                default_key = self.t.get("default_method_key", "ocf")
                default_display_name = self.t["methods"].get(default_key, {}).get("name", options[0])
                w.set(default_display_name)
            else:
                w = CleanEntry(frame)
                w.insert(0, str(default))
                if key in ["fin_curr", "list_curr", "rate"]:
                    w.bind("<KeyRelease>", self.update_rate_hint)
            w.pack(fill="x")
            self.entries[key] = w

        SectionHeader(f, self.t["grp_basic"]).grid(row=0, column=0, columnspan=2, pady=(10,5), sticky="w", padx=5)
        add_field(f, "symbol", "MSFT", 1, 0)
        add_field(f, "name", "Microsoft", 1, 1)
        
        # 修改：默认值传入空字符串，由 add_field 内部逻辑根据 default_method_idx 处理
        add_field(f, "method", "", 2, 0, is_combo=True)
        
        add_field(f, "curr_year", datetime.datetime.now().year, 2, 1)

        # --- 估值日期选择器 ---
        ds_frame = ctk.CTkFrame(f, fg_color="transparent")
        ds_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        f.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(ds_frame, text=self.t["val_date"], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w", pady=(0, 2))
        
        ds_box = ctk.CTkFrame(ds_frame, fg_color="transparent")
        ds_box.pack(fill="x")
        
        now = datetime.datetime.now()
        # 动态生成年份：当前年份的前3年到后3年
        years = [str(y) for y in range(now.year - 3, now.year + 3)]
        self.dcf_year = CleanCombo(ds_box, values=years, width=80, height=32)
        self.dcf_year.set(str(now.year))
        self.dcf_year.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        months = [f"{m:02d}" for m in range(1, 13)]
        self.dcf_month = CleanCombo(ds_box, values=months, width=60, height=32)
        self.dcf_month.set(f"{now.month:02d}")
        self.dcf_month.pack(side="left", fill="x", expand=True)
        # --- 修改结束 ---
        
        # 修正：初始化时设置标签文本
        # 获取当前选中的方法（add_field已设置默认值）
        current_method_display = self.entries["method"].get()
        current_method_key = self.method_display_to_key_map.get(current_method_display, "ocf")
        
        # 从配置中获取对应标签
        initial_label = self.t["methods"].get(current_method_key, {}).get("label", "Cash Flow")

        SectionHeader(f, self.t["grp_fin"]).grid(row=3, column=0, columnspan=2, pady=(20,5), sticky="w", padx=5)
        
        # 修正：使用获取到的 initial_label
        self.lbl_cf_dynamic = ctk.CTkLabel(f, text=initial_label, font=FONTS["sub"], text_color=THEME["text_sub"])
        self.lbl_cf_dynamic.grid(row=4, column=0, columnspan=2, sticky="w", padx=10)
        
        self.entry_cf = CleanEntry(f)
        self.entry_cf.insert(0, "70000")
        self.entry_cf.grid(row=5, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="ew")
        
        add_field(f, "debt", "60000", 6, 0)
        add_field(f, "cash", "80000", 6, 1)
        add_field(f, "shares", "7400", 7, 0)
        add_field(f, "close", "415.0", 7, 1)

        SectionHeader(f, self.t["grp_growth"]).grid(row=8, column=0, columnspan=2, pady=(20,5), sticky="w", padx=5)
        add_field(f, "g1", "15", 9, 0)
        add_field(f, "g2", "10", 9, 1)
        add_field(f, "g3", "5", 10, 0)
        add_field(f, "dr", "9", 10, 1)

        SectionHeader(f, self.t["grp_more"]).grid(row=11, column=0, columnspan=2, pady=(20,5), sticky="w", padx=5)
        add_field(f, "fin_curr", "USD", 12, 0)
        add_field(f, "rate", "1.0", 12, 1)
        add_field(f, "list_curr", "USD", 13, 0)
        
        self.lbl_rate_hint = ctk.CTkLabel(f, text="1 USD = ? USD", font=FONTS["sub"], text_color=THEME["primary"])
        self.lbl_rate_hint.grid(row=13, column=1, sticky="w", padx=5)

    def on_method_change(self, choice_display_name):
        # 通过显示名称反向查找到中性键
        method_key = self.method_display_to_key_map.get(choice_display_name, "ocf")
        # 使用中性键获取对应的标签文本
        label_text = self.t["methods"].get(method_key, {}).get("label", "Cash Flow")
        self.lbl_cf_dynamic.configure(text=label_text)

    def update_rate_hint(self, event=None):
        fin = self.entries["fin_curr"].get()
        lst = self.entries["list_curr"].get()
        rate = self.entries["rate"].get()
        hint = self.t["rate_hint"].format(fin, lst, rate)
        self.lbl_rate_hint.configure(text=hint)

    # --- 拖拽逻辑实现 ---
    def start_drag(self, event, group, index, item_data):
        self.drag_data = {"group": group, "index": index, "item": item_data}
        
        # 1. 高亮当前拖拽的行 (取代幽灵窗口)
        rows = self.group_row_widgets.get(group, [])
        if index < len(rows):
            active_row = rows[index]
            # 记录原始边框颜色以便恢复 (假设默认是透明或特定颜色)
            self.drag_active_row = active_row
            active_row.configure(border_color=THEME["primary"], border_width=2)
        
        # 2. 准备插入指示器 (不立即显示，motion中显示)
        # 这里我们不创建，在 motion 中按需创建
        
        return "break"

    def on_drag_motion(self, event):
        # 计算并显示插入指示器
        group = self.drag_data["group"]
        rows = self.group_row_widgets.get(group, [])
        if not rows: return

        # 核心逻辑：使用屏幕绝对坐标 (rootx/rooty) 计算插入点
        mouse_y = self.winfo_pointery()
        best_dist = float('inf')
        best_point = None

        # 遍历所有可能的插入缝隙
        if rows:
            r0 = rows[0]
            # 缝隙 0: 第0个元素上方
            screen_y = r0.winfo_rooty() - 3 
            dist = abs(mouse_y - screen_y)
            if dist < best_dist:
                best_dist = dist
                # 宽度缩减：使用 -8 
                best_point = (screen_y, 0, r0.winfo_width() - 80, r0.winfo_rootx() + 4)

            for i, row in enumerate(rows):
                # 缝隙 i+1: 当前元素下方
                screen_bottom = row.winfo_rooty() + row.winfo_height() + 3
                dist = abs(mouse_y - screen_bottom)
                if dist < best_dist:
                    best_dist = dist
                    # 宽度缩减：使用 -8 
                    best_point = (screen_bottom, i + 1, row.winfo_width() - 80, row.winfo_rootx() + 4)

        # 更新指示器位置 (使用 Toplevel Window 实现，避免坐标系错乱)
        if best_point:
            line_y, target_index, line_w, line_x = best_point
            
            # 如果指示器窗口不存在，创建它
            if not self.drag_indicator_window:
                self.drag_indicator_window = ctk.CTkToplevel(self)
                self.drag_indicator_window.overrideredirect(True) 
                self.drag_indicator_window.attributes('-topmost', True) 
                f = ctk.CTkFrame(self.drag_indicator_window, fg_color=THEME["primary"], corner_radius=2)
                f.pack(fill="both", expand=True)
            
            # 设置窗口几何位置: WxH+X+Y
            self.drag_indicator_window.geometry(f"{line_w}x4+{line_x}+{line_y}")
            self.drag_indicator_window.deiconify() 
            self.proposed_drop_index = target_index
        else:
            if self.drag_indicator_window:
                self.drag_indicator_window.withdraw()
            self.proposed_drop_index = None

    def stop_drag(self, event):
        if self.drag_indicator_window:
            self.drag_indicator_window.destroy()
            self.drag_indicator_window = None
        
        source_group = self.drag_data["group"]
        source_index = self.drag_data["index"]
        target_index = self.proposed_drop_index
        
        self.drag_data = {"group": None, "index": None, "item": None}
        self.drag_active_row = None
        self.proposed_drop_index = None
        
        if source_group is None or target_index is None: 
            # 如果没有移动，强制刷新以去除高亮
            self.render_watchlist()
            return

        # 只有位置真正改变时才处理
        if target_index != source_index and target_index != source_index + 1:
            # 调整索引: 如果在源下方插入，因为移除源会导致后面的索引前移，所以目标索引也要减1
            if target_index > source_index:
                target_index -= 1
            
            data_list = self.watchlist_data[source_group]
            item = data_list.pop(source_index)
            data_list.insert(target_index, item)
            
            self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
            self.render_watchlist()
        else:
            self.render_watchlist()

    def delete_wl_item(self, grp, item_to_delete):
        # --- 核心修复: 改为通过 item 对象引用来删除，避免索引问题 ---
        if messagebox.askyesno("Confirm Delete", f"Remove '{item_to_delete.get('symbol', 'N/A')}' from watchlist?"):
            try:
                # 使用 list.remove() 安全地移除对象
                self.watchlist_data[grp].remove(item_to_delete)
                self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
                # 成功删除数据后，立即刷新UI
                self.render_watchlist()
            except (ValueError, KeyError):
                # 如果组或项不存在 (例如，在快速点击中被重复删除), 仅刷新UI以同步状态
                print(f"Warning: Item to delete not found in group '{grp}'. Forcing a refresh.")
                self.render_watchlist()

    def render_watchlist(self):
        for w in self.wl_scroll.winfo_children(): w.destroy()
        
        # --- 新增: 空白状态引导 ---
        is_empty = not any(self.watchlist_data.values())
        if is_empty:
            welcome_frame = ctk.CTkFrame(self.wl_scroll, fg_color="transparent")
            welcome_frame.pack(pady=20, padx=10, fill="x")
            
            ctk.CTkLabel(welcome_frame, text=self.t.get("wl_welcome_title", "👋 Welcome!"), 
                         font=FONTS["h2"], text_color=THEME["text_main"]).pack(pady=(10, 15))
                         
            ctk.CTkLabel(welcome_frame, text=self.t.get("wl_welcome_msg", "Click [+ New] to start."),
                         font=FONTS["body"], text_color=THEME["text_sub"], wraplength=280, justify="center").pack(pady=(0, 20))
            
            # 添加一个示意图标
            ctk.CTkLabel(welcome_frame, text="📊", font=(UI_FONT, 60), text_color=THEME["border"]).pack()
            return # 结束函数，不渲染列表
        
        self.group_row_widgets = {}
        # --- 核心优化: 创建一个从 symbol 到 widget 的直接映射 ---
        self.watchlist_item_widgets = {}
        
        for group, items in self.watchlist_data.items():
            self.group_row_widgets[group] = []
            
            g_frame = ctk.CTkFrame(self.wl_scroll, fg_color="transparent")
            g_frame.pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(g_frame, text=group, font=FONTS["sub_bold"], text_color=THEME["text_sub"]).pack(side="left", padx=5)
            
            if self.wl_edit_mode:
                ctk.CTkButton(g_frame, text="Del Group", width=60, height=20, fg_color=THEME["input_bg"], text_color=THEME["v_risk"],
                              font=FONTS["tag"], command=lambda g=group: self.delete_wl_group(g)).pack(side="right")

            for idx, item in enumerate(items):
                gap = item.get("last_gap", 0)
                color_conf = self.get_valuation_config(gap)
                
                symbol = item.get('symbol')
                is_selected = (symbol == self.selected_wl_symbol)
                
                bg_color = THEME["list_selected"] if is_selected else color_conf["bg"]
                border_col = THEME["primary"] if is_selected else color_conf["border"]
                border_w = 2 if is_selected else 1
                
                row = ctk.CTkFrame(self.wl_scroll, fg_color=bg_color, corner_radius=6, border_width=border_w, border_color=border_col)
                row.pack(fill="x", pady=3, padx=2)
                
                # --- 核心优化: 存储 widget 引用 ---
                if symbol:
                    self.watchlist_item_widgets[symbol] = {
                        "widget": row,
                        "item_data": item # 存储item数据以便后续恢复颜色
                    }
                
                self.group_row_widgets[group].append(row)
                
                def bind_click(widget, item_data):
                    # 避免给按钮也绑定上 load 事件
                    if isinstance(widget, (ctk.CTkButton, ctk.CTkLabel)) and (widget.cget("text") in ["×", "⣿", "Del Group"]):
                        return
                        
                    widget.bind("<Button-1>", lambda e=None, i=item_data: self.load_wl_item(i))
                    for child in widget.winfo_children():
                        bind_click(child, item_data)
                
                pill = ctk.CTkFrame(row, width=4, height=28, fg_color=color_conf["text"], corner_radius=2)
                pill.pack(side="left", padx=(8, 5))
                
                if self.wl_edit_mode:
                    # --- 核心修复: lambda 捕捉 item 对象本身, 而不是不稳定的 idx ---
                    del_btn = ctk.CTkButton(row, text="×", width=24, height=24, fg_color="transparent", text_color=THEME["text_sub"],
                                            hover_color=THEME["v_risk"], command=lambda g=group, item_to_del=item: self.delete_wl_item(g, item_to_del))
                    del_btn.pack(side="left", padx=(0, 5))

                if self.wl_edit_mode:
                    drag_handle = ctk.CTkLabel(row, text="⣿", width=24, font=("Arial", 14), 
                                               text_color=THEME["text_sub"], cursor="fleur")
                    drag_handle.pack(side="right", padx=(0, 5))
                    
                    drag_handle.bind("<Button-1>", lambda e, g=group, i=idx, d=item: self.start_drag(e, g, i, d))
                    drag_handle.bind("<B1-Motion>", self.on_drag_motion)
                    drag_handle.bind("<ButtonRelease-1>", self.stop_drag)

                f_right = ctk.CTkFrame(row, fg_color="transparent")
                f_right.pack(side="right", padx=5, pady=5)
                
                gap_txt = f"{gap*100:+.1f}%"
                price = item.get("last_close", 0)
                iv = item.get("last_iv", 0)
                
                l1 = ctk.CTkLabel(f_right, text=f"{item.get('list_curr','')} {price:,.2f}  {gap_txt}", font=FONTS["body_bold"], text_color=color_conf["text"])
                l1.pack(anchor="e")
                l2 = ctk.CTkLabel(f_right, text=f"IV: {iv:,.2f}", font=FONTS["sub"], text_color=THEME["text_sub"])
                l2.pack(anchor="e")

                f_left = ctk.CTkFrame(row, fg_color="transparent")
                f_left.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                ctk.CTkLabel(f_left, text=item['symbol'], font=FONTS["body_bold"], text_color=THEME["text_main"]).pack(anchor="w")
                ctk.CTkLabel(f_left, text=item['name'], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w")

                bind_click(row, item)

    def get_valuation_config(self, gap):
        if gap < -0.3: return {"bg": THEME["bg_deep_val"], "border": THEME["v_deep_val"], "text": THEME["v_deep_val"]}
        if gap < -0.1: return {"bg": THEME["bg_val"], "border": THEME["v_val"], "text": THEME["v_val"]}
        if gap < 0.1:  return {"bg": THEME["bg_fair"], "border": "#CBD5E1", "text": THEME["text_sub"]}
        if gap < 0.3:  return {"bg": THEME["bg_over"], "border": THEME["v_over"], "text": THEME["v_over"]}
        return {"bg": THEME["bg_risk"], "border": THEME["v_risk"], "text": THEME["v_risk"]}

    def calculate_dcf(self):
        # 1. 验证必填项
        required_fields = ["g1", "g2", "g3", "dr", "debt", "cash", "shares", "rate", "close"]
        for k in required_fields:
            if not self.entries[k].get().strip():
                messagebox.showwarning("Input Missing", self.t["err_input_missing"])
                return 0, 0
        
        if not self.entry_cf.get().strip():
             messagebox.showwarning("Input Missing", self.t["err_cf_missing"])
             return 0, 0

        # 2. 验证数值格式
        try:
            cf = float(self.entry_cf.get())
            g1 = float(self.entries["g1"].get()) / 100
            g2 = float(self.entries["g2"].get()) / 100
            g3 = float(self.entries["g3"].get()) / 100
            dr = float(self.entries["dr"].get()) / 100
            debt = float(self.entries["debt"].get())
            cash = float(self.entries["cash"].get())
            shares = float(self.entries["shares"].get())
            rate = float(self.entries["rate"].get())
            close = float(self.entries["close"].get())
        except ValueError: 
            messagebox.showerror("Invalid Input", self.t["err_input_invalid"])
            return 0, 0

        total_pv = 0.0
        curr = cf
        log_lines = []
        for y in range(1, 21):
            g = g1 if y <= 5 else (g2 if y <= 10 else g3)
            curr *= (1 + g)
            pv = curr / ((1 + dr) ** y)
            total_pv += pv
            log_lines.append(f"Y{y:<2} | CF:{curr:,.0f} | PV:{pv:,.0f}")

        equity = total_pv + cash - debt
        iv = (equity / shares) * rate
        gap = (close - iv) / iv if iv else 0 

        sym = self.entries["list_curr"].get()
        self.lbl_iv_big.configure(text=f"{sym} {iv:,.2f}")
        
        col = self.get_valuation_config(gap)["text"] 
        
        if gap < -0.3: txt = self.t["r_v_und"]
        elif gap < -0.1: txt = self.t["r_und"]
        elif gap < 0.1: txt = self.t["r_fair"]
        elif gap < 0.3: txt = self.t["r_over"]
        else: txt = self.t["r_v_over"]

        self.lbl_iv_big.configure(text_color=col)
        self.lbl_mos_badge.configure(text=f"{gap*100:+.1f}%  {txt}", fg_color=col, text_color="#FFFFFF")

        rpt = f"Equity Val: {equity:,.0f}\nSum PV (20y): {total_pv:,.0f}\n\n" + "\n".join(log_lines)
        self.txt_log.delete("0.0", "end")
        self.txt_log.insert("0.0", rpt)
        return gap, iv

    def save_to_wl(self):
        grp = self.grp_combo.get()
        if not grp: return
        gap, iv = self.calculate_dcf()
        
        # 如果 calculation 返回 0,0 可能是因为验证失败（已经弹窗警告），这里就中断保存
        if gap == 0 and iv == 0:
            return

        try: close = float(self.entries["close"].get())
        except: close = 0

        val_date = f"{self.dcf_year.get()}-{self.dcf_month.get()}"
        params_dict = {k: v.get() for k, v in self.entries.items()}
        params_dict["val_date"] = val_date
        
        # --- 核心修改: 保存语言无关的 method_key ---
        current_method_display = self.entries["method"].get()
        method_key = self.method_display_to_key_map.get(current_method_display, "ocf")
        
        data = {
            "symbol": self.entries["symbol"].get(),
            "name": self.entries["name"].get(),
            "method_key": method_key, # 保存key
            "method": current_method_display, # 保留旧字段用于向后兼容显示
            "cf": self.entry_cf.get(),
            "last_gap": gap,
            "last_iv": iv,
            "last_close": close,
            "params": params_dict
        }
        lst = self.watchlist_data[grp]
        idx = next((i for i, x in enumerate(lst) if x["symbol"] == data["symbol"]), -1)
        if idx >= 0: lst[idx] = data
        else: lst.append(data)
        
        self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
        self.render_watchlist()
        self.load_wl_item(data)
        
        # --- 修改：增加反馈 ---
        self.show_feedback(self.t["msg_save_done"])
        # --------------------

    # --- 新增: 重置表单 ---
    def reset_dcf_form(self):
        self.selected_wl_symbol = None
        
        # 1. 清空所有输入框 (确保干净的状态)
        for k, widget in self.entries.items():
            if isinstance(widget, CleanEntry):
                widget.delete(0, "end")
        self.entry_cf.delete(0, "end")

        # 2. 设置合理的默认值 (加载范例)
        defaults = {
            "symbol": "MSFT(example)", "name": "Microsoft", "cf": "147039",
            "debt": "60556", "cash": "102005", "shares": "7434", "close": "483",
            "g1": "15", "g2": "10", "g3": "5", "dr": "9",
            "fin_curr": "USD", "list_curr": "USD", "rate": "1.0",
        }
        
        for key, value in defaults.items():
            if key == "cf":
                self.entry_cf.insert(0, value)
            elif key in self.entries:
                self.entries[key].insert(0, value)

        # 3. 重置下拉框和日期选择器
        default_method_key = self.t.get("default_method_key", "ocf")
        default_display_name = self.t["methods"].get(default_method_key, {}).get("name", "")
        self.entries["method"].set(default_display_name)
        self.on_method_change(default_display_name)

        now = datetime.datetime.now()
        self.entries["curr_year"].insert(0, str(now.year))
        self.dcf_year.set(str(now.year))
        self.dcf_month.set(f"{now.month:02d}")
        
        # 4. 重置计算结果显示
        self.lbl_iv_big.configure(text="---", text_color=THEME["text_main"])
        self.lbl_mos_badge.configure(text="---", fg_color=THEME["input_bg"], text_color=THEME["text_main"])
        self.txt_log.delete("0.0", "end")
        
        # 5. 更新UI状态
        self.update_rate_hint()
        self.render_watchlist()
        
        # 6. 显示反馈
        self.show_feedback(self.t["msg_new_ready"])
        # --------------------

    def add_wl_group(self):
        dialog = CleanInputDialog(self, title="New Group", prompt="Group Name:")
        name = dialog.show()
        
        if name and name not in self.watchlist_data:
            self.watchlist_data[name] = []
            self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
            self.grp_combo.configure(values=list(self.watchlist_data.keys()))
            self.grp_combo.set(name) # 自动选中新建的组
            self.render_watchlist()

    def delete_wl_group(self, grp):
        if messagebox.askyesno("Confirm", f"Delete group '{grp}'?"):
            del self.watchlist_data[grp]
            self.save_json_async(WATCHLIST_FILE, self.watchlist_data)
            self.grp_combo.configure(values=list(self.watchlist_data.keys()))
            self.render_watchlist()

    def load_wl_item(self, item):
        new_symbol = item.get('symbol')
        
        # --- 核心优化: 精确更新UI，避免全局刷新 ---
        # 1. 如果点击的是同一个项目，则不执行任何操作
        if self.selected_wl_symbol == new_symbol:
            return

        # 2. 取消旧项目的选中状态 (如果存在)
        if self.selected_wl_symbol and self.selected_wl_symbol in self.watchlist_item_widgets:
            old_widget_info = self.watchlist_item_widgets[self.selected_wl_symbol]
            old_widget = old_widget_info["widget"]
            old_item_data = old_widget_info["item_data"]
            
            # 恢复其基于估值区间的正常颜色
            gap = old_item_data.get("last_gap", 0)
            color_conf = self.get_valuation_config(gap)
            old_widget.configure(fg_color=color_conf["bg"], border_color=color_conf["border"], border_width=1)

        # 3. 设置新项目的选中状态
        if new_symbol and new_symbol in self.watchlist_item_widgets:
            new_widget_info = self.watchlist_item_widgets[new_symbol]
            new_widget = new_widget_info["widget"]
            
            # 设置为高亮颜色
            new_widget.configure(fg_color=THEME["list_selected"], border_color=THEME["primary"], border_width=2)

        # 4. 更新当前选中的 symbol
        self.selected_wl_symbol = new_symbol
        # ----------------------------------------------------
        
        # --- 以下是加载数据到右侧表单的逻辑 (保持不变) ---
        self.entries["symbol"].delete(0,"end"); self.entries["symbol"].insert(0, item.get("symbol", ""))
        self.entries["name"].delete(0,"end"); self.entries["name"].insert(0, item.get("name", ""))
        
        target_display_method = ""
        saved_method_key = item.get("method_key")
        if saved_method_key and saved_method_key in self.t["methods"]:
            target_display_method = self.t["methods"][saved_method_key]["name"]
        else:
            saved_display_text = item.get("method", "")
            for lang_data in LANG.values():
                if saved_display_text in [v['name'] for v in lang_data["methods"].values()]:
                    found_key = next((k for k, v in lang_data["methods"].items() if v['name'] == saved_display_text), None)
                    if found_key:
                        target_display_method = self.t["methods"].get(found_key, {}).get("name")
                        break
        
        if not target_display_method:
            default_key = self.t.get("default_method_key", "ocf")
            target_display_method = self.t["methods"].get(default_key, {}).get("name")

        if target_display_method:
            self.entries["method"].set(target_display_method)
            self.on_method_change(target_display_method)
        
        self.entry_cf.delete(0,"end"); self.entry_cf.insert(0, item.get("cf", "0"))
        
        params = item.get("params", {})
        
        val_date = params.get("val_date", "")
        if val_date and "-" in val_date:
            y, m = val_date.split("-")
            self.dcf_year.set(y)
            self.dcf_month.set(m)

        for k, v in params.items():
            if k in self.entries and k not in ["symbol", "name", "method", "val_date"]:
                if self.entries[k].get() != str(v):
                    self.entries[k].delete(0,"end")
                    self.entries[k].insert(0, v)
        
        if "last_close" in item and item["last_close"] > 0:
             if self.entries["close"].get() != f"{item['last_close']:.2f}":
                self.entries["close"].delete(0, "end")
                self.entries["close"].insert(0, f"{item['last_close']:.2f}")

        self.calculate_dcf()
        self.update_rate_hint()

    # ==================================================================
    # 📊 Module 2: Portfolio Pro
    # ==================================================================
    def show_port(self):
        self.set_active_nav("port")
        self.port_view_frame.tkraise() # --- 核心优化: 只需置顶 ---
        
        # 切换回来时刷新数据，确保数据是 актуально (up-to-date)
        # 注意：如果数据量特别大且不经常变动，可以考虑更懒惰的刷新策略
        self.refresh_port_view() 
        
    def create_port_ui(self, parent_frame):
        # --- 这个方法包含了原来 show_port() 中所有创建UI的逻辑 ---
        self.port_grid = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.port_grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- Top: Stats Dashboard ---
        stats_row = ctk.CTkFrame(self.port_grid, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 20))
        
        self.card_nw = StatsCard(stats_row, self.t["card_net_worth"], "$ 0.00", value_color=THEME["primary"])
        self.card_nw.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.card_cost = StatsCard(stats_row, self.t["card_cost"], "$ 0.00")
        self.card_cost.pack(side="left", fill="x", expand=True, padx=10)
        self.card_pl = StatsCard(stats_row, self.t["card_pl"], "$ 0.00 (+0.00%)")
        self.card_pl.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # --- 新增: 货币切换栏 ---
        ctrl_frame = ctk.CTkFrame(self.port_grid, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=(0, 10))

        # Currency
        ctk.CTkLabel(ctrl_frame, text=self.t["p_disp_curr"], font=FONTS["sub_bold"], text_color=THEME["text_sub"]).pack(side="left")
        self.display_curr_var = ctk.StringVar(value="USD")
        self.combo_display_curr = CleanCombo(ctrl_frame, values=["USD", "CNY", "HKD", "EUR", "JPY", "GBP", "AUD", "CAD", "SGD"], width=80, variable=self.display_curr_var, command=self.on_display_curr_change)
        self.combo_display_curr.pack(side="left", padx=(5, 15))
        
        # Global FX
        self.lbl_global_fx = ctk.CTkLabel(ctrl_frame, text=self.t["p_global_rate"], font=FONTS["sub"], text_color=THEME["text_sub"])
        self.lbl_global_fx.pack(side="left", padx=5)
        self.entry_global_fx = CleanEntry(ctrl_frame, width=70)
        self.entry_global_fx.insert(0, "1.0")
        self.entry_global_fx.pack(side="left", padx=5)

        # Separator
        ctk.CTkFrame(ctrl_frame, width=2, height=20, fg_color=THEME["border"]).pack(side="left", padx=15)

        # Sort
        ctk.CTkLabel(ctrl_frame, text=self.t["sort_lbl"], font=FONTS["sub_bold"], text_color=THEME["text_sub"]).pack(side="left")
        self.sort_var = ctk.StringVar(value=self.t["sort_opts"][0])
        self.combo_sort = CleanCombo(ctrl_frame, values=self.t["sort_opts"], width=120, variable=self.sort_var, command=lambda _: self.refresh_port_view())
        self.combo_sort.pack(side="left", padx=5)

        # Group
        ctk.CTkLabel(ctrl_frame, text=self.t["group_lbl"], font=FONTS["sub_bold"], text_color=THEME["text_sub"]).pack(side="left", padx=(10, 0))
        self.group_var = ctk.StringVar(value=self.t["group_opts"][0])
        self.combo_group = CleanCombo(ctrl_frame, values=self.t["group_opts"], width=110, variable=self.group_var, command=lambda _: self.refresh_port_view())
        self.combo_group.pack(side="left", padx=5)

        ctk.CTkButton(ctrl_frame, text="↻", width=30, fg_color=THEME["input_bg"], text_color=THEME["primary"], command=self.refresh_port_view).pack(side="right")

        # --- Content (修改布局为 Grid) ---
        content = ctk.CTkFrame(self.port_grid, fg_color="transparent")
        content.pack(fill="both", expand=True)
        # 配置列比例: List(4) : Chart(6)
        content.grid_columnconfigure(0, weight=4) 
        content.grid_columnconfigure(1, weight=6)
        content.grid_rowconfigure(0, weight=1)

        # Left: List
        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        action_bar = ctk.CTkFrame(left_col, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 10))
        self.btn_add = ctk.CTkButton(action_bar, text=self.t["p_add_btn"], height=36, fg_color=THEME["primary"], 
                                     command=self.toggle_input_panel)
        self.btn_add.pack(side="left")
        
        # --- 修改开始：新增批量更新按钮 ---
        ctk.CTkButton(action_bar, text=self.t["p_batch_btn"], height=36, fg_color=THEME["primary"],
                        command=self.open_batch_update_window).pack(side="left", padx=10)
        # --- 修改结束 ---
        
        self.input_panel = CleanCard(left_col) # Hidden by default
        
        head = ctk.CTkFrame(self.input_panel, fg_color="transparent")
        head.pack(fill="x", padx=15, pady=(15, 0))
        self.lbl_port_mode = ctk.CTkLabel(head, text=self.t["p_add"], font=FONTS["h3"], text_color=THEME["primary"])
        self.lbl_port_mode.pack(side="left")

        in_grid = ctk.CTkFrame(self.input_panel, fg_color="transparent")
        in_grid.pack(fill="x", padx=15, pady=15)
        self.p_entries = {}
        fields = [("ticker", 0, 0), ("name", 0, 1), ("curr", 0, 2), ("fx", 0, 3), ("qty", 1, 0), ("cost", 1, 1)]
        for k, r, c in fields:
            f = ctk.CTkFrame(in_grid, fg_color="transparent")
            f.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            in_grid.columnconfigure(c, weight=1)
            ctk.CTkLabel(f, text=self.t[f"f_{k}"], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w")
            # --- 修改 1: 将货币字段改为下拉框 ---
            if k == "curr":
                e = CleanCombo(f, values=["USD", "CNY", "HKD", "EUR", "JPY", "GBP", "AUD", "CAD", "SGD"])
                e.set("USD")
            else:
                e = CleanEntry(f)
            # ---------------------
            
            e.pack(fill="x")
            self.p_entries[k] = e
    
        f_sec = ctk.CTkFrame(in_grid, fg_color="transparent")
        f_sec.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(f_sec, text=self.t["f_sec"], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w")
        self.p_sector = CleanCombo(f_sec, values=["Technology", "Communication Services", "Consumer Discretionary", "Consumer Staples", "Diversified", "Finance", "Healthcare", "Energy", "Industrials", "Materials", "Real Estate", "Utilities", "Other"])
        self.p_sector.pack(fill="x")

        # 添加国家字段
        f_country = ctk.CTkFrame(in_grid, fg_color="transparent")
        f_country.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(f_country, text=self.t["f_country"], font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w")
        self.p_country = CleanCombo(f_country, values=["China/HK", "US", "Europe", "Singapore", "Canada", "Japan", "South Korea", "India", "Other"])
        self.p_country.pack(fill="x")
        
        act_row = ctk.CTkFrame(self.input_panel, fg_color="transparent")
        act_row.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(act_row, text=self.t["p_save"], height=32, fg_color=THEME["primary"], command=self.save_portfolio_item).pack(side="right")
        ctk.CTkButton(act_row, text=self.t["p_clear"], height=32, fg_color=THEME["input_bg"], text_color=THEME["text_main"], hover_color=THEME["border"], command=self.clear_port_inputs).pack(side="right", padx=10)

        # 移除旧表头，因为卡片式布局不需要对齐列
        # list_head = CleanCard(left_col, corner_radius=8, fg_color=THEME["bg"], border_width=0)
        # list_head.pack(fill="x", pady=5)

        self.port_scroll = ctk.CTkScrollableFrame(left_col, fg_color="transparent")
        self.port_scroll.pack(fill="both", expand=True)

        # Right: Charts (Modify layout)
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        
        chart_card = CleanCard(right_col)
        chart_card.pack(fill="both", expand=True)
        
        chart_tabs = ctk.CTkTabview(chart_card, fg_color="transparent", segmented_button_selected_color=THEME["primary"])
        chart_tabs.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_hold = chart_tabs.add(self.t["tab_holdings"])
        self.tab_sec = chart_tabs.add(self.t["tab_sectors"])
        self.tab_country = chart_tabs.add(self.t["tab_countries"])
        
        # 🚀 优化核心：初始化持久化图表对象 (Persistent Charts)
        self.chart_h = OptimizedChart(self.tab_hold)
        self.chart_h.pack(fill="both", expand=True)
        
        self.chart_s = OptimizedChart(self.tab_sec)
        self.chart_s.pack(fill="both", expand=True)

        # 添加国家图表
        self.chart_c = OptimizedChart(self.tab_country)
        self.chart_c.pack(fill="both", expand=True)

    def on_display_curr_change(self, choice):
        if choice == "USD":
            self.entry_global_fx.delete(0, "end"); self.entry_global_fx.insert(0, "1.0")
            self.refresh_port_view()
            return

        if not YFINANCE_AVAILABLE: return
        
        def _fetch():
            # 尝试获取 USD -> Target 汇率
            pair = f"{choice}=X" 
            try:
                # 修改 1: 添加 auto_adjust=False 以消除警告
                data = yf.download(pair, period="1d", progress=False, auto_adjust=False)
                if not data.empty:
                    # 修改 2: 使用 .item() 替代 float()，安全地从 Series/Numpy 对象中提取数值
                    # 兼容可能返回的 Series 或 Scalar 结构
                    close_val = data['Close'].iloc[-1]
                    rate = close_val.item() if hasattr(close_val, 'item') else float(close_val)
                    self.after(0, lambda: self._update_global_fx(rate))
            except: pass
            
        threading.Thread(target=_fetch, daemon=True).start()

    def _update_global_fx(self, rate):
        self.entry_global_fx.delete(0, "end")
        self.entry_global_fx.insert(0, f"{rate:.4f}")
        self.refresh_port_view()

    def toggle_input_panel(self):
        self.show_input_panel = not self.show_input_panel
        if self.show_input_panel:
            self.input_panel.pack(after=self.btn_add.master, fill="x", pady=(0, 15))
            self.btn_add.configure(text=self.t["p_close_btn"])
        else:
            self.input_panel.pack_forget()
            self.btn_add.configure(text=self.t["p_add_btn"])

    def clear_port_inputs(self):
        self.editing_port_idx = -1
        self.lbl_port_mode.configure(text=self.t["p_add"])
        # --- 修改 2: 区分处理 Entry 和 ComboBox 的重置 ---
        for k, e in self.p_entries.items():
            if isinstance(e, CleanCombo):
                e.set("USD")
            else:
                e.delete(0, "end")
        # -----------------------------------------------
        self.p_sector.set("")
        self.p_country.set("")


    def save_portfolio_item(self):
        try:
            data = {
                "ticker": self.p_entries["ticker"].get(),
                "name": self.p_entries["name"].get(),
                "curr": self.p_entries["curr"].get(),
                "fx": float(self.p_entries["fx"].get()),
                "qty": float(self.p_entries["qty"].get()),
                "cost": float(self.p_entries["cost"].get()),
                "sector": self.p_sector.get(),
                "country": self.p_country.get()
            }
            if self.editing_port_idx >= 0: self.portfolio_data[self.editing_port_idx] = data
            else: self.portfolio_data.append(data)
            
            self.save_json_async(PORTFOLIO_FILE, self.portfolio_data)
            self.clear_port_inputs()
            self.refresh_port_view()
        except ValueError: messagebox.showerror("Error", "Invalid Number")

    def edit_port_item(self, idx):
        if not self.show_input_panel: self.toggle_input_panel()
        self.editing_port_idx = idx
        item = self.portfolio_data[idx]
        # --- 修改 3: 区分处理 Entry 和 ComboBox 的数据回填 ---
        for k in ["ticker", "name", "curr", "fx", "qty", "cost"]:
            val = str(item.get(k, ""))
            widget = self.p_entries[k]
            
            if isinstance(widget, CleanCombo):
                widget.set(val)
            else:
                widget.delete(0, "end")
                widget.insert(0, val)
        # --------------------------------------------------
        self.p_sector.set(item.get("sector", ""))
        self.p_country.set(item.get("country", ""))
        self.lbl_port_mode.configure(text=self.t["p_edit_title"])

    def delete_port_item(self, idx):
        if messagebox.askyesno("Confirm", "Delete this position?"):
            del self.portfolio_data[idx]
            self.save_json_async(PORTFOLIO_FILE, self.portfolio_data)
            self.refresh_port_view()

    # --- 重构后的刷新逻辑 ---
    def refresh_port_view(self):
        for w in self.port_scroll.winfo_children(): 
            w.destroy()
        # --- 修改结束 ---

        disp_curr = self.display_curr_var.get()
        sym_char = CURRENCY_SYMBOLS.get(disp_curr, "$")
        try: global_fx = float(self.entry_global_fx.get())
        except: global_fx = 1.0

        # Phase 1: Pre-calculate & Enrich Data
        processed_data = []
        total_val_usd = 0
        total_cost_usd = 0
        holdings_map = {}
        sector_map = {}
        country_map = {}

        for idx, item in enumerate(self.portfolio_data):
            # Price Logic
            curr_price = item.get("last_price", 0)
            if curr_price <= 0:
                for grp, wl_items in self.watchlist_data.items():
                    found = next((x for x in wl_items if x["symbol"] == item["ticker"]), None)
                    if found and "last_close" in found:
                        curr_price = found["last_close"]
                        break
            if curr_price <= 0: curr_price = item.get("cost", 0)

            # Calc
            try:
                qty = float(item["qty"])
                cost = float(item["cost"])
                fx = float(item["fx"]) if item["fx"] != 0 else 1.0
                
                val_usd = (qty * curr_price) / fx
                cost_usd = (qty * cost) / fx
                
                pl_usd = val_usd - cost_usd
                pl_pct = pl_usd / cost_usd if cost_usd else 0
                
                # 2. 转换为显示货币
                val_disp = val_usd * global_fx
                pl_disp = pl_usd * global_fx
                
                total_val_usd += val_usd
                total_cost_usd += cost_usd

                # Maps for Charts
                holdings_map[item["ticker"]] = val_usd
                sec = item.get("sector", self.t["other_group"])
                cnt = item.get("country", self.t["other_group"])
                sector_map[sec] = sector_map.get(sec, 0) + val_usd
                country_map[cnt] = country_map.get(cnt, 0) + val_usd

                # Store enriched object
                processed_data.append({
                    "orig_idx": idx,
                    "item": item,
                    "val_usd": val_usd,
                    "pl_usd": pl_usd,
                    "pl_pct": pl_pct,
                    "val_disp": val_disp,
                    "pl_disp": pl_disp,
                    "curr_price": curr_price,
                    "qty": qty,
                    "sector": sec,
                    "country": cnt
                })
            except: pass

        # 2. 获取全局汇率并折算总值 (已在循环外处理，只需更新仪表盘)
        # ... (Dashboard 更新逻辑保持不变) ...
        # 折算
        final_net_worth = total_val_usd * global_fx
        final_cost = total_cost_usd * global_fx
        final_pl = final_net_worth - final_cost
        
        # 3. 更新仪表盘
        total_pl_pct = (final_pl / final_cost) if final_cost else 0
        
        self.card_nw.update_value(f"{sym_char} {final_net_worth:,.2f}")
        self.card_cost.update_value(f"{sym_char} {final_cost:,.2f}")
        
        pl_col = THEME["v_deep_val"] if final_pl >= 0 else THEME["v_risk"]
        self.card_pl.update_value(f"{final_pl:+,.2f} ({total_pl_pct:+.2%})", color=pl_col)

        if total_val_usd > 0:
            holdings_map = {k: v/total_val_usd*100 for k, v in holdings_map.items()}
            sector_map = {k: v/total_val_usd*100 for k, v in sector_map.items()}
            country_map = {k: v/total_val_usd*100 for k, v in country_map.items()}
        
        self.chart_h.update_data(holdings_map, is_donut=True)
        self.chart_s.update_data(sector_map, is_donut=True)
        self.chart_c.update_data(country_map, is_donut=True)

        # Phase 3: Sort & Group
        sort_opt = self.sort_var.get()
        group_opt = self.group_var.get()

        # Sorting
        # ["Value Desc", "Value Asc", "P&L Desc", "Ticker A-Z"] (Index mapped to LANG keys)
        # We check substring because language might change
        if "Value" in sort_opt or "市值" in sort_opt:
            reverse = "Desc" in sort_opt or "高→低" in sort_opt
            processed_data.sort(key=lambda x: x["val_usd"], reverse=reverse)
        elif "P&L" in sort_opt or "盈亏" in sort_opt:
            processed_data.sort(key=lambda x: x["pl_usd"], reverse=True)
        else: # Ticker
            processed_data.sort(key=lambda x: x["item"]["ticker"])

        # Grouping Pre-sort (Stability sort)
        if "Sector" in group_opt or "版块" in group_opt:
            processed_data.sort(key=lambda x: x["sector"])
            group_key = "sector"
        elif "Country" in group_opt or "地区" in group_opt:
            processed_data.sort(key=lambda x: x["country"])
            group_key = "country"
        else:
            group_key = None

        # Phase 4: Render List
        current_group_val = None
        
        for data in processed_data:
            item = data["item"]
            
            # Check Group Header
            if group_key:
                grp_val = data[group_key]
                if grp_val != current_group_val:
                    # Render Header
                    # Calculate group total stats for header
                    grp_items = [d for d in processed_data if d[group_key] == grp_val]
                    grp_total = sum(d["val_usd"] for d in grp_items)
                    grp_pct = (grp_total / total_val_usd * 100) if total_val_usd else 0
                    
                    header = ctk.CTkFrame(self.port_scroll, fg_color=THEME["header_bg"], height=30)
                    header.pack(fill="x", pady=(10, 2))
                    ctk.CTkLabel(header, text=f"{grp_val}", font=FONTS["body_bold"], text_color=THEME["text_main"]).pack(side="left", padx=10)
                    ctk.CTkLabel(header, text=f"{grp_pct:.1f}%", font=FONTS["body_bold"], text_color=THEME["primary"]).pack(side="right", padx=10)
                    current_group_val = grp_val

            # Render Card
            row = CleanCard(self.port_scroll, fg_color=THEME["card"], border_color=THEME["border"], corner_radius=8)
            row.pack(fill="x", pady=4)
            
            # Left: Info
            left_box = ctk.CTkFrame(row, fg_color="transparent")
            left_box.pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(left_box, text=item["ticker"], font=FONTS["body_bold"], text_color=THEME["text_main"]).pack(anchor="w")

            # 名称：字体更小，颜色更浅，营造层级感
            name_txt = item["name"]
            if len(name_txt) > 10: name_txt = name_txt[:9] + ".." # 稍微缩短截断长度以防换行
            ctk.CTkLabel(left_box, text=name_txt, font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="w", pady=(2, 0)) # 增加一点行间距
            
            # Tags Row
            tag_row = ctk.CTkFrame(left_box, fg_color="transparent")
            tag_row.pack(anchor="w", pady=(2, 0))
            
            # Helper to create tag
            def create_tag(parent, text):
                f = ctk.CTkFrame(parent, fg_color=THEME["tag_bg"], corner_radius=4, height=16)
                f.pack(side="left", padx=(0, 4))
                ctk.CTkLabel(f, text=text, font=FONTS["tag"], text_color=THEME["tag_text"]).pack(padx=4)
            
            if not group_key or group_key != "sector": create_tag(tag_row, data["sector"])
            if not group_key or group_key != "country": create_tag(tag_row, data["country"])

            # Right: Action Buttons
            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.pack(side="right", padx=5)
            ctk.CTkButton(btn_box, text="×", width=24, height=24, fg_color="transparent", text_color=THEME["text_sub"], hover_color=THEME["bg"], command=lambda i=data["orig_idx"]: self.delete_port_item(i)).pack(side="right")
            ctk.CTkButton(btn_box, text="✎", width=24, height=24, fg_color="transparent", text_color=THEME["text_main"], hover_color=THEME["bg"], command=lambda i=data["orig_idx"]: self.edit_port_item(i)).pack(side="right")

            # Mid-Right: Value & P&L
            right_info_box = ctk.CTkFrame(row, fg_color="transparent")
            right_info_box.pack(side="right", padx=(5, 10), pady=5)
            
            # Value + Pct
            val_frame = ctk.CTkFrame(right_info_box, fg_color="transparent")
            val_frame.pack(anchor="e")
            port_pct = (data["val_usd"] / total_val_usd * 100) if total_val_usd else 0
            ctk.CTkLabel(val_frame, text=f"{sym_char} {data['val_disp']:,.0f}", font=FONTS["body_bold"], text_color=THEME["text_main"]).pack(side="left")

            
            ctk.CTkLabel(val_frame, text=f" ({port_pct:.1f}%)", font= FONTS["sub"], text_color=THEME["text_sub"]).pack(side="left")
            
            # P&L Pill
            pl_col = THEME["profit_bg"] if data["pl_disp"] >= 0 else THEME["loss_bg"]
            pl_txt = THEME["profit_text"] if data["pl_disp"] >= 0 else THEME["loss_text"]
            pl_str = f"{data['pl_disp']:+,.0f} ({data['pl_pct']:+.1%})"
            pill = ctk.CTkFrame(right_info_box, fg_color=pl_col, corner_radius=4, height=18)
            pill.pack(anchor="e", pady=(2,0))
            ctk.CTkLabel(pill, text=pl_str, font=FONTS["tag"], text_color=pl_txt).pack(padx=6, pady=1)

            # Mid: Price & Qty
            mid_box = ctk.CTkFrame(row, fg_color="transparent")
            mid_box.pack(side="right", padx=(5, 15), pady=5)
            asset_curr = item.get("curr", "USD")
            asset_sym = CURRENCY_SYMBOLS.get(asset_curr, asset_curr)
            ctk.CTkLabel(mid_box, text=f"{asset_sym} {data['curr_price']:,.2f}", font=FONTS["body_bold"], text_color=THEME["text_main"]).pack(anchor="e")
            ctk.CTkLabel(mid_box, text=f"{data['qty']:,.0f} shares", font=FONTS["sub"], text_color=THEME["text_sub"]).pack(anchor="e")

if __name__ == "__main__":
    app = StockSifuUltimate()
    app.mainloop()