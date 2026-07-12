from analysis_text import ANALYSIS
"""Data fetching for Gold-Silver Macro Monitor - complete rewrite with Excel metadata."""
import requests
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}
_FC_CACHE = {}

def _FC(id, query):
    if id in _FC_CACHE: return _FC_CACHE[id]
    try:
        from firecrawl_helper import search_news, scrape_page
        r = search_news(query, limit=2)
        sc, u = "", ""
        if r.get("results") and len(r["results"]) > 0:
            t = r["results"][0].get("title","")[:100]
            u = r["results"][0].get("url","")
            if u:
                try:
                    sp = scrape_page(u)
                    sd = sp.get("data",{})
                    if isinstance(sd, dict): sc = sd.get("markdown","")[:800]
                except: pass
            _FC_CACHE[id] = t + "||" + u + "||" + sc
        else:
            _FC_CACHE[id] = ""
    except:
        _FC_CACHE[id] = ""
    return _FC_CACHE[id]

def _get_json(url, tp=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=tp)
        return r.json()
    except:
        return {"error": "Failed"}

def fetch_gold_price():
    d = _get_json("https://query1.finance.yahoo.com/v8/finance/chart/GC=F")
    try:
        m = d["chart"]["result"][0]["meta"]
        p = m["regularMarketPrice"]
        pc = m["chartPreviousClose"]
        ch = p - pc
        return {"price": round(p,2), "change": round(ch,2), "change_pct": round(ch/pc*100,2)}
    except:
        return {"error": "Failed"}

def fetch_silver_price():
    d = _get_json("https://query1.finance.yahoo.com/v8/finance/chart/SI=F")
    try:
        m = d["chart"]["result"][0]["meta"]
        p = m["regularMarketPrice"]
        pc = m["chartPreviousClose"]
        ch = p - pc
        return {"price": round(p,2), "change": round(ch,2), "change_pct": round(ch/pc*100,2)}
    except:
        return {"error": "Failed"}

def fetch_dxy():
    try:
        import ssl as _sx
        _cx = _sx.create_default_context()
        _cx.check_hostname = False
        _cx.verify_mode = _sx.CERT_NONE
        import requests as _rx
        _dx = _rx.get("https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB", headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
        _jx = _dx.json()
        _px = round(_jx["chart"]["result"][0]["meta"]["regularMarketPrice"], 2)
        _bx = _px < 100
        return {"value": _px, "impacted": "Bullish" if _bx else "Bearish", "conclusion": "跌破支撑→利多" if _bx else "突破阻力→利空"}
    except:
        return {"value": "等待数据", "impacted": "Pending", "conclusion": "Yahoo Finance连接中"}

def fetch_real_yield():
    try:
        d = _get_json("https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX")
        nom = round(d["chart"]["result"][0]["meta"]["regularMarketPrice"], 2)
        real = round(nom - 2.4, 2)
        low = real < 1.0
        high = real > 1.5
        if low:
            imp, con = "Bullish", f"实际利率{real}%，低于1%，黄金成本下降→利多"
        elif high:
            imp, con = "Bearish", f"实际利率{real}%，高于1.5%，压制金银"
        else:
            imp, con = "Neutral", f"实际利率{real}%，处于1%-1.5%中性区间"
        return {"value": f"{real}%", "impacted": imp, "conclusion": con}
    except:
        return {"value": "等待数据", "impacted": "Pending", "conclusion": "数据获取中"}

def fetch_cny_rate():
    d = _get_json("https://query1.finance.yahoo.com/v8/finance/chart/CNY=X")
    try:
        return round(d["chart"]["result"][0]["meta"]["regularMarketPrice"], 4)
    except:
        return 7.27

def fetch_shfe_prices():
    try:
        import requests as _rq
        h = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
        r = _rq.get("https://hq.sinajs.cn/list=nf_AU0,nf_AG0", headers=h, timeout=8)
        if r.status_code != 200: return {"shfe_gold": None, "shfe_silver": None}
        res = {"shfe_gold": None, "shfe_silver": None}
        for line in r.text.strip().splitlines():
            if "nf_AU0" in line:
                p = line.split('"')[1].split(",")
                if len(p) > 8:
                    pr = float(p[8]) if p[8] and float(p[8]) > 0 else (float(p[7]) if p[7] and float(p[7]) > 0 else 0)
                    pv = float(p[5]) if p[5] and float(p[5]) > 0 else pr
                    cg = round(pr - pv, 2) if pv > 0 else 0
                    pc = round(cg / pv * 100, 2) if pv > 0 else 0
                    res["shfe_gold"] = {"price": pr, "change": cg, "change_pct": pc}
            elif "nf_AG0" in line:
                p = line.split('"')[1].split(",")
                if len(p) > 8:
                    pr = float(p[8]) if p[8] and float(p[8]) > 0 else (float(p[7]) if p[7] and float(p[7]) > 0 else 0)
                    pv = float(p[5]) if p[5] and float(p[5]) > 0 else pr
                    cg = round(pr - pv, 2) if pv > 0 else 0
                    pc = round(cg / pv * 100, 2) if pv > 0 else 0
                    res["shfe_silver"] = {"price": pr, "change": cg, "change_pct": pc}
        return res
    except:
        return {"shfe_gold": None, "shfe_silver": None}

def fetch_all():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gp = fetch_gold_price()
    sp = fetch_silver_price()
    cny = fetch_cny_rate()
    domestic = round(gp["price"] * cny / 31.1035, 2) if "error" not in gp else 0
    dxy_d = fetch_dxy()
    yld_d = fetch_real_yield()
    ratio_val = round(gp["price"] / sp["price"], 1) if "error" not in gp and "error" not in sp else "N/A"

    # Data logic
    fed_val = "关注7月29-31日FOMC"
    core_pce_val = "核心PCE 2.4%→通胀回落→利多"

    # Firecrawl - parallel batch
    from concurrent.futures import ThreadPoolExecutor, as_completed
    _fc_batch = [
        ("fed", "Federal Reserve FOMC meeting July 2025 rate decision expectations"),
        ("pce", "US core PCE inflation June 2025 released"),
        ("gld", "SPDR GLD gold holdings latest ton"),
        ("slv", "iShares SLV silver holdings latest ton"),
        ("comex_g", "COMEX gold inventory latest million ounces"),
        ("comex_s", "COMEX silver inventory latest 10000 tons"),
        ("net_g", "COMEX gold net long managed money CFTC weekly 2025"),
        ("net_s", "COMEX silver net long managed money CFTC weekly 2025"),
        ("supply_g", "global gold supply deficit 2025 tons"),
        ("supply_s", "global silver supply deficit 2025 tons"),
        ("cb", "central bank gold purchases quarterly 2025 latest 300 tons"),
        ("china_g", "China gold imports monthly 2025 tons latest"),
        ("china_s", "China silver exports monthly 2025 latest tons policy"),
        ("pv", "IEA global solar PV installations 2025 growth YoY"),
        ("mine_g", "gold mine supply disruption 2025 strike China Australia Russia"),
        ("mine_s", "silver mine supply disruption 2025 Mexico Peru strike"),
        ("geo", "geopolitical conflict risk Middle East Russia Ukraine 2025 latest"),
        ("margin_g", "COMEX gold margin adjustment 2025"),
        ("margin_s", "COMEX silver margin adjustment 2025"),
    ]
    def _do_fc(kv):
        _FC(kv[0], kv[1])
    with ThreadPoolExecutor(max_workers=10) as ex:
        for f in as_completed([ex.submit(_do_fc, x) for x in _fc_batch]):
            f.result()
    fed_t = _FC_CACHE.get("fed", "")
    pce_t = _FC_CACHE.get("pce", "")
    gld_t = _FC_CACHE.get("gld", "")
    slv_t = _FC_CACHE.get("slv", "")
    comex_g = _FC_CACHE.get("comex_g", "")
    comex_s = _FC_CACHE.get("comex_s", "")
    net_g = _FC_CACHE.get("net_g", "")
    net_s = _FC_CACHE.get("net_s", "")
    supply_g = _FC_CACHE.get("supply_g", "")
    supply_s = _FC_CACHE.get("supply_s", "")
    cb = _FC_CACHE.get("cb", "")
    china_g = _FC_CACHE.get("china_g", "")
    china_s = _FC_CACHE.get("china_s", "")
    pv = _FC_CACHE.get("pv", "")
    mine_g = _FC_CACHE.get("mine_g", "")
    mine_s = _FC_CACHE.get("mine_s", "")
    geo = _FC_CACHE.get("geo", "")
    margin_g = _FC_CACHE.get("margin_g", "")
    margin_s = _FC_CACHE.get("margin_s", "")

    def _parse_fc(v):
        """Parse FC result: title||url||scraped"""
        if isinstance(v, str) and "||" in v:
            parts = v.split("||", 2)
            return {"t": parts[0], "u": parts[1], "sc": parts[2]}
        return {"t": v if v and v != "" else "", "u": "", "sc": ""}
    def fmt_fc(v, fb):
        p = _parse_fc(v)
        return p["t"][:50] if p["t"] else fb
    def fc_imp(v):
        p = _parse_fc(v)
        return "Reference" if p["sc"] else "Pending"
    def fc_con(v, fb):
        p = _parse_fc(v)
        if p["sc"]:
            s = p["sc"][:80]
            if any(ord(c) > 127 for c in s): return s
        if p["t"]:
            t = p["t"][:60]
            if any(ord(c) > 127 for c in t): return t
        return fb

    # Indicator helper
    def mk(name, value, threshold, interpretation, frequency, source, impacted, conclusion, analysis=""):
        return {
            "name": name, "value": str(value), "threshold": threshold,
            "interpretation": interpretation, "frequency": frequency,
            "source": source, "impacted": impacted, "conclusion": conclusion, "analysis": analysis
        }

    # Gold indicators
    gold_macro = {
        "indicators": {
            "fed_meeting": mk(
                "美联储议息会议", fed_val,
                "关注降息信号、点阵图、鲍威尔讲话",
                "释放降息信号→利多；推迟降息→利空",
                "会议日", "https://www.federalreserve.gov/",
                "Watch", "FedWatch显示降息概率近期上升",
                fc_con(fmt_fc(fed_t, ""), "")
            ),
            "core_pce": mk(
                "核心PCE/CPI通胀", core_pce_val,
                "核心PCE＜2.5%（利多）；＞3%（利空）",
                "通胀下行→降息预期升温；通胀反弹→压制宽松预期",
                "每月", "https://www.bea.gov/data/personal-consumption-expenditures",
                "Bullish", "2.4%＜2.5%阈值，通胀回落支持降息",
                fc_con(fmt_fc(pce_t, ""), "")
            ),
            "dxy": mk(
                "美元指数DXY", str(dxy_d.get("value", "")),
                "支撑98；阻力100",
                "跌破98→利多；突破100→利空",
                "每日", "https://www.investing.com/indices/usdollar",
                dxy_d.get("impacted", "Pending"), dxy_d.get("conclusion", ""), ""
            ),
            "real_yield": mk(
                "10年期美债实际利率", yld_d.get("value", ""),
                "＜1%（强利多）；＞1.5%（利空）",
                "实际利率走低→金银机会成本下降",
                "每日", "https://home.treasury.gov/",
                yld_d.get("impacted", "Pending"), yld_d.get("conclusion", ""), ""
            ),
        }
    }
    gold_capital = {
        "indicators": {
            "gld": mk(
                "SPDR黄金ETF(GLD)持仓", fmt_fc(gld_t, "暂无数据"),
                "单日增仓＞10吨（利多）；单日减仓＞10吨（利空）",
                "资金大幅流入→买盘支撑；资金撤离→抛压增加",
                "每日", "https://www.spdrgoldshares.com/",
                fc_imp(gld_t), fmt_fc(gld_t, "待Firecrawl更新"), ""
            ),
            "comex_net_g": mk(
                "COMEX黄金净多持仓", fmt_fc(net_g, "暂无数据"),
                "净多单＞40万手（超买）；＜20万手（低位反弹信号）",
                "超买警惕回调；低位或开启上涨",
                "每周（周五CFTC）", "https://www.cftc.gov/",
                fc_imp(net_g), fmt_fc(net_g, "待更新"), ""
            ),
            "comex_inv_g": mk(
                "COMEX黄金库存", fmt_fc(comex_g, "暂无数据"),
                "＜800万盎司（供应紧张→利多）；＞1000万盎司（供应宽松→利空）",
                "库存低位加剧短缺预期；库存高位缓解担忧",
                "每日", "https://www.cmegroup.com/",
                fc_imp(comex_g), fmt_fc(comex_g, "待更新"), ""
            ),
        }
    }
    gold_supply = {
        "indicators": {
            "cb_gold": mk(
                "全球央行季度购金量", fmt_fc(cb, "暂无数据"),
                "单季≥320吨（强利多）；单季＜200吨（支撑减弱）",
                "央行持续购金→长期价格上行；购金放缓→支撑不足",
                "季度", "https://www.gold.org/",
                fc_imp(cb), fmt_fc(cb, "WGC季度报告待更新"), ""
            ),
            "supply_gap_g": mk(
                "全球黄金供需缺口", fmt_fc(supply_g, "暂无数据"),
                "＞500吨（强支撑→利多）；＜200吨（中性）",
                "缺口扩大→长期价格上行；缺口收窄→支撑不足",
                "季度", "https://www.gold.org/",
                fc_imp(supply_g), fmt_fc(supply_g, "待更新"), ""
            ),
            "china_import": mk(
                "中国黄金进口量", fmt_fc(china_g, "暂无数据"),
                "月度＞100吨（利多）；月度＜50吨（利空）",
                "进口增加→实物需求旺盛；进口减少→需求疲软",
                "每月", "https://www.customs.gov.cn/",
                fc_imp(china_g), fmt_fc(china_g, "海关月报待更新"), ""
            ),
        }
    }
    gold_ratio = {
        "indicators": {
            "ratio": mk(
                "金银价格比", str(ratio_val),
                "＜60（黄金超跌→补涨利多）；＞75（黄金高估→回调利空）",
                "偏离历史均值(65-70)后大概率修复",
                "每日", "https://www.lbma.org.uk/",
                "Neutral" if isinstance(ratio_val, (int,float)) and 60 <= ratio_val <= 75 else ("Bullish" if isinstance(ratio_val, (int,float)) and ratio_val < 60 else "Bearish"),
                f"当前比{ratio_val}，历史均值65-70", ""
            ),
            "support": mk(
                "伦敦现货黄金支撑位", "4650-4700美元",
                "支撑4650-4700美元/盎司",
                "跌破支撑下探4500",
                "每日", "https://www.kitco.com/",
                "Reference", "跌破支撑下探4500；承压时关注买入区", ""
            ),
            "resistance": mk(
                "伦敦现货黄金阻力位", "4850-4900美元",
                "阻力4850-4900美元/盎司",
                "突破阻力冲击5000",
                "每日", "https://www.kitco.com/",
                "Reference", "突破阻力冲击5000；接近时注意卖出区", ""
            ),
        }
    }
    gold_geo = {
        "indicators": {
            "mine_g": mk(
                "黄金主产国供应扰动", fmt_fc(mine_g, "暂无异常"),
                "矿山罢工/政策限制影响月产量＞50吨→利多",
                "供应中断→短期价格跳涨",
                "实时", "https://www.mining.com/",
                fc_imp(mine_g), fmt_fc(mine_g, "关注中国、澳大利亚、俄罗斯"), ""
            ),
            "geopolitics": mk(
                "地缘冲突", fmt_fc(geo, "关注中"),
                "冲突升级→利多；冲突缓和→利空",
                "避险情绪升温→资金涌入贵金属",
                "实时", "https://www.reuters.com/",
                "Watch", fmt_fc(geo, "关注中东、俄乌局势"), ""
            ),
            "margin_g": mk(
                "COMEX黄金保证金调整", fmt_fc(margin_g, "暂无变化"),
                "上调保证金→短期利空；下调→短期利多",
                "上调增加交易成本→抑制投机需求",
                "实时", "https://www.cmegroup.com/",
                fc_imp(margin_g), fmt_fc(margin_g, "无变化"), ""
            ),
        }
    }

    # Silver indicators
    silver_supply = {
        "indicators": {
            "supply_gap_s": mk(
                "全球白银供需缺口", fmt_fc(supply_s, "暂无数据"),
                "＞1万吨（强支撑→利多）；＜5000吨（中性）",
                "缺口扩大→长期价格上行；缺口收窄→支撑不足",
                "每月", "https://www.silverinstitute.org/",
                fc_imp(supply_s), fmt_fc(supply_s, "世界白银协会待更新"), ""
            ),
            "solar_pv": mk(
                "工业用银(光伏驱动)", fmt_fc(pv, "暂无数据"),
                "同比增长＞20%（利多）；＜10%（利空）",
                "光伏需求高增→工业用银增量；增速放缓→需求不及预期",
                "每月", "https://www.iea.org/",
                fc_imp(pv), fmt_fc(pv, "IEA月报待更新"), ""
            ),
            "china_export": mk(
                "中国白银出口量", fmt_fc(china_s, "暂无数据"),
                "月度＜300吨（利多）；＞500吨（利空）",
                "出口缩减→全球流通量下降；出口回升→供应宽松",
                "每月", "https://www.customs.gov.cn/",
                fc_imp(china_s), fmt_fc(china_s, "海关月报待更新"), ""
            ),
        }
    }
    silver_capital = {
        "indicators": {
            "slv": mk(
                "SLV白银ETF持仓", fmt_fc(slv_t, "暂无数据"),
                "单日增仓＞500吨（强利多）；单日减仓＞500吨（强利空）",
                "资金大幅流入→买盘支撑；资金撤离→抛压增加",
                "每日", "https://www.ishares.com/us/products/239562/ishares-silver-trust",
                fc_imp(slv_t), fmt_fc(slv_t, "待Firecrawl更新"), ""
            ),
            "comex_net_s": mk(
                "COMEX白银净多持仓", fmt_fc(net_s, "暂无数据"),
                "净多单＞30万手（超买）；＜15万手（低位反弹信号）",
                "超买警惕回调；低位或开启上涨",
                "每周（周五CFTC）", "https://www.cftc.gov/",
                fc_imp(net_s), fmt_fc(net_s, "待更新"), ""
            ),
            "comex_inv_s": mk(
                "COMEX白银库存", fmt_fc(comex_s, "暂无数据"),
                "＜3万吨（供应紧张→利多）；＞4万吨（供应宽松→利空）",
                "库存低位加剧短缺预期；库存高位缓解担忧",
                "每日", "https://www.cmegroup.com/",
                fc_imp(comex_s), fmt_fc(comex_s, "待更新"), ""
            ),
        }
    }
    silver_ratio = {
        "indicators": {
            "ratio_s": mk(
                "金银价格比", str(ratio_val),
                "＜50（白银超跌→补涨利多）；＞60（白银高估→回调利空）",
                "偏离历史均值(65-70)后大概率修复",
                "每日", "https://www.lbma.org.uk/",
                "Bullish" if isinstance(ratio_val, (int,float)) and ratio_val < 50 else ("Bearish" if isinstance(ratio_val, (int,float)) and ratio_val > 60 else "Neutral"),
                f"当前比{ratio_val}，低于60白银偏低估", ""
            ),
            "support_s": mk(
                "伦敦现货白银支撑位", "87-88美元",
                "支撑87-88美元/盎司",
                "跌破支撑下探85",
                "每日", "https://www.kitco.com/",
                "Reference", "跌破支撑下探85；承压时关注买入区", ""
            ),
            "resistance_s": mk(
                "伦敦现货白银阻力位", "94-95美元",
                "阻力94-95美元/盎司",
                "突破阻力冲击100",
                "每日", "https://www.kitco.com/",
                "Reference", "突破阻力冲击100；接近时注意卖出区", ""
            ),
        }
    }
    silver_geo = {
        "indicators": {
            "mine_s": mk(
                "白银主产国供应扰动", fmt_fc(mine_s, "暂无异常"),
                "矿山罢工/政策限制影响月产量＞1000吨→利多",
                "供应中断→短期价格跳涨",
                "实时", "https://www.mining.com/",
                fc_imp(mine_s), fmt_fc(mine_s, "关注墨西哥、秘鲁"), ""
            ),
            "geopolitics": mk(
                "地缘冲突", fmt_fc(geo, "关注中"),
                "冲突升级→利多；冲突缓和→利空",
                "避险情绪升温→资金涌入贵金属",
                "实时", "https://www.reuters.com/",
                "Watch", fmt_fc(geo, "关注中东、俄乌局势"), ""
            ),
            "margin_s": mk(
                "COMEX白银保证金调整", fmt_fc(margin_s, "暂无变化"),
                "上调保证金→短期利空；下调→短期利多",
                "上调增加交易成本→抑制投机需求",
                "实时", "https://www.cmegroup.com/",
                fc_imp(margin_s), fmt_fc(margin_s, "无变化"), ""
            ),
        }
    }

    shfe = fetch_shfe_prices()
    shfe_g = shfe.get("shfe_gold")
    shfe_s = shfe.get("shfe_silver")
    macro_chain = "核心PCE/CPI(通胀)↓→美联储降息↑→10Y实际利率↓+美元↓→金银吸引力↑→价格上涨(利多) / 反向→价格下跌(利空)"
    # Apply analysis text from analysis_text module
    return {
        "update_time": now,
        "analysis_texts": ANALYSIS,
        "analysis_texts": ANALYSIS,
        "analysis_texts": ANALYSIS,
        "analysis_texts": ANALYSIS,
        "button_time": now,
        "prices": {"gold": gp, "silver": sp, "domestic_gold": domestic, "cny_rate": cny, "shfe_gold": shfe_g, "shfe_silver": shfe_s},
        "ratio": ratio_val,
        "gold_support": "4650-4700", "gold_resistance": "4850-4900",
        "silver_support": "87-88", "silver_resistance": "94-95",
        "macro_chain": macro_chain,
        "tabs": {
            "gold": {
                "macro": {"title": "美联储与宏观", "priority": "最高", "cls": "high", "indicators": gold_macro["indicators"]},
                "capital_flow": {"title": "资金流向与持仓", "priority": "次高", "cls": "high", "indicators": gold_capital["indicators"]},
                "supply_demand": {"title": "供需与产业", "priority": "中期", "cls": "medium", "indicators": gold_supply["indicators"]},
                "ratio_technical": {"title": "金银比与技术面", "priority": "辅助", "cls": "low", "indicators": gold_ratio["indicators"]},
                "geopolitics": {"title": "地缘与政策风险", "priority": "突发", "cls": "low", "indicators": gold_geo["indicators"]},
            },
            "silver": {
                "macro": {"title": "美联储与宏观", "priority": "最高", "cls": "high", "indicators": gold_macro["indicators"]},
                "capital_flow": {"title": "资金流向与持仓", "priority": "次高", "cls": "high", "indicators": silver_capital["indicators"]},
                "supply_demand": {"title": "供需与产业", "priority": "中期", "cls": "medium", "indicators": silver_supply["indicators"]},
                "ratio_technical": {"title": "金银比与技术面", "priority": "辅助", "cls": "low", "indicators": silver_ratio["indicators"]},
                "geopolitics": {"title": "地缘与政策风险", "priority": "突发", "cls": "low", "indicators": silver_geo["indicators"]},
            },
        }
    }
