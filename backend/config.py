"""Configuration and indicator definitions for Gold-Silver Monitor."""

import os
from dotenv import load_dotenv

load_dotenv()

# Firecrawl
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev")

# Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5100"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Schedule
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "09:00")


# Indicator definitions: each indicator has:
#   id, name, dimension, priority, threshold, bullish_text, bearish_text
INDICATORS = {
    "fed_meeting": {
        "name": "下次议息会议",
        "dimension": "美联储与宏观",
        "priority": "最高",
        "unit": "",
    },
    "core_pce": {
        "name": "核心 PCE",
        "dimension": "美联储与宏观",
        "priority": "最高",
        "unit": "%",
    },
    "dxy": {
        "name": "美元指数 DXY",
        "dimension": "美联储与宏观",
        "priority": "最高",
        "unit": "",
    },
    "real_yield": {
        "name": "10Y 美债实际利率",
        "dimension": "美联储与宏观",
        "priority": "最高",
        "unit": "%",
    },
    "slv_holdings": {
        "name": "SLV 白银 ETF 持仓",
        "dimension": "资金流向与持仓",
        "priority": "次高",
        "unit": "吨",
    },
    "comex_net_long": {
        "name": "COMEX 白银期货净多",
        "dimension": "资金流向与持仓",
        "priority": "次高",
        "unit": "万手",
    },
    "comex_inventory": {
        "name": "COMEX 白银库存",
        "dimension": "资金流向与持仓",
        "priority": "次高",
        "unit": "万吨",
    },
    "supply_gap": {
        "name": "全球白银供需缺口",
        "dimension": "供需与产业",
        "priority": "中",
        "unit": "万吨",
    },
    "solar_pv": {
        "name": "光伏装机同比增长",
        "dimension": "供需与产业",
        "priority": "中",
        "unit": "%",
    },
    "china_export": {
        "name": "中国白银月度出口量",
        "dimension": "供需与产业",
        "priority": "中",
        "unit": "吨",
    },
    "gold_silver_ratio": {
        "name": "金银价格比",
        "dimension": "金银比与技术面",
        "priority": "低",
        "unit": "",
    },
    "gold_support": {
        "name": "伦敦现货黄金支撑位",
        "dimension": "金银比与技术面",
        "priority": "低",
        "unit": "美元",
    },
    "gold_resistance": {
        "name": "伦敦现货黄金阻力位",
        "dimension": "金银比与技术面",
        "priority": "低",
        "unit": "美元",
    },
    "supply_disruption": {
        "name": "白银主产国供应扰动",
        "dimension": "地缘与政策风险",
        "priority": "低",
        "unit": "",
    },
    "geopolitics": {
        "name": "地缘冲突",
        "dimension": "地缘与政策风险",
        "priority": "低",
        "unit": "",
    },
    "margin_change": {
        "name": "COMEX 期货保证金调整",
        "dimension": "地缘与政策风险",
        "priority": "低",
        "unit": "",
    },
}

DIMENSION_ORDER = [
    "美联储与宏观",
    "资金流向与持仓",
    "供需与产业",
    "金银比与技术面",
    "地缘与政策风险",
]
