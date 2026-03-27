import requests
import yfinance as yf
from langchain.tools import tool

MAIN_SERVICE = "http://main_service:8000"
NOTIF_SERVICE = "http://notification_service:8001"

WATCHLIST = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","TSLA","META","NFLX",
    "AMD","INTC","ORCL","CRM","UBER","LYFT","SHOP","SNAP",
    "TWTR","BABA","TSM","ASML"
]

@tool
def get_stock_price(symbol: str) -> str:
    """查询股票的最新价格和技术指标。输入股票代码如 AAPL。"""
    try:
        r1 = requests.get(f"{MAIN_SERVICE}/stocks/{symbol.upper()}", timeout=15)
        r2 = requests.get(f"{MAIN_SERVICE}/stocks/{symbol.upper()}/analysis", timeout=15)
        price_data = r1.json()
        analysis_data = r2.json()
        return f"""
{symbol.upper()} 股票信息：
- 最新价格：${price_data['latest_price']:.2f}
- SMA5：${analysis_data['sma_5']:.2f}
- SMA20：${analysis_data['sma_20']:.2f}
- 日收益率：{analysis_data['daily_return']*100:.3f}%
- Alert 触发：{'是 ⚡ ' + price_data['alert']['message'] if price_data['alert_triggered'] else '否'}
"""
    except Exception as e:
        return f"查询失败：{str(e)}"


@tool
def get_top_movers(direction: str = "both") -> str:
    """查找今日涨幅或跌幅最大的股票。direction 可以是 up（涨）、down（跌）、both（两者）。"""
    results = []
    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                continue
            prev_close = hist["Close"].iloc[-2]
            last_close = hist["Close"].iloc[-1]
            change_pct = (last_close - prev_close) / prev_close * 100
            results.append({
                "symbol": symbol,
                "price": round(float(last_close), 2),
                "change_pct": round(float(change_pct), 2)
            })
        except:
            continue

    results.sort(key=lambda x: x["change_pct"], reverse=True)

    if direction == "up":
        top = results[:10]
        label = "涨幅最大"
    elif direction == "down":
        top = results[-10:][::-1]
        label = "跌幅最大"
    else:
        top_up = results[:5]
        top_down = results[-5:][::-1]
        top = top_up + top_down
        label = "涨跌幅最大"

    lines = [f"今日{label}股票：\n"]
    for r in top:
        arrow = "▲" if r["change_pct"] >= 0 else "▼"
        lines.append(f"  {arrow} {r['symbol']}: ${r['price']} ({r['change_pct']:+.2f}%)")
    return "\n".join(lines)


@tool
def get_notifications(symbol: str = "") -> str:
    """查询 Alert 通知记录。可以指定股票代码，留空则返回所有记录。"""
    try:
        r = requests.get(f"{NOTIF_SERVICE}/notifications", timeout=10)
        data = r.json()
        items = data.get("items", [])
        if symbol:
            items = [i for i in items if i["symbol"] == symbol.upper()]
        if not items:
            return f"没有找到{'关于 ' + symbol.upper() + ' 的' if symbol else ''}Alert 记录。"
        lines = [f"共 {len(items)} 条 Alert 记录：\n"]
        for item in items[:10]:
            lines.append(
                f"  [{item['event_timestamp'][:16]}] {item['symbol']} "
                f"{item['condition']} ${item['threshold']} — {item['message']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"查询失败：{str(e)}"


def get_tools():
    return [get_stock_price, get_top_movers, get_notifications]