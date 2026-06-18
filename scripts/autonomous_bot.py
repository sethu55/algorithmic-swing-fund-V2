import os
import json
import math
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO_FILE = os.path.join(ROOT_DIR, 'portfolio.json')
LEDGER_FILE = os.path.join(ROOT_DIR, 'paper_trades.md')
FUNDAMENTALS_FILE = os.path.join(ROOT_DIR, 'fundamentals.json')

SECTORS = {
    'Nuclear': 'nuclear_data.json',
    'Water': 'water_data.json',
    'Drone': 'drone_data.json',
    'DataCenter': 'datacenter_data.json',
    'Hydrogen': 'hydrogen_data.json',
    'Semiconductors': 'semi_data.json',
    'Ancillary': 'data.json',
    'Rare Earths': 'rare_earth_data.json',
    'Green Energy': 'green_energy_data.json',
    'IT Services': 'it_services_data.json'
}

MAX_POSITIONS = 4
CAPITAL_PER_TRADE = 25000.0
INITIAL_STOP_PCT = 0.15
TRAILING_STOP_PCT = 0.20
FRICTION_PCT = 0.0015
STCG_TAX_RATE = 0.20

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_market_data():
    market = {}
    for sector, file in SECTORS.items():
        path = os.path.join(ROOT_DIR, file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                if '1y' in data:
                    for comp, d in data['1y'].items():
                        market[comp] = d
    return market

def calculate_portfolio_value(pf, market_data):
    val = pf['cash']
    for comp, pos in pf['active_positions'].items():
        if comp in market_data:
            val += pos.get('shares', 0) * market_data[comp]['current_price']
        else:
            val += pos.get('capital_deployed', 0)
    return val

def render_ledger(pf, market_data):
    md = [
        "# Aggressive Mega-Bull: V2 Paper Trading Ledger",
        "> [!IMPORTANT]",
        "> **Portfolio Objective:** Aggressively maximize absolute returns in a Mega-Bull Market.",
        "> **Exit Strategy:** Let winners run indefinitely. No take-profits. Ride the trend until a -20% trailing stop or structural break.",
        "> **Position Sizing:** Concentrated Momentum (Max 4 Positions at ₹25,000 each) to minimize friction.",
        "",
        "## Account Overview",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Starting Balance** | INR {pf['starting_balance']:,.2f} |"
    ]
    
    current_value = calculate_portfolio_value(pf, market_data)
    total_tax = max(0, pf['realized_pnl'] * STCG_TAX_RATE)
            
    md.append(f"| **Current Portfolio Value** | **INR {current_value:,.2f}** |")
    md.append(f"| **Available Cash** | INR {pf['cash']:,.2f} |")
    
    pnl_pct = (pf['realized_pnl'] / pf['starting_balance']) * 100
    md.append(f"| **Total Realized P&L** | INR {pf['realized_pnl']:,.2f} ({pnl_pct:.2f}%) |")
    md.append(f"| **Estimated STCG Tax** | INR {total_tax:,.2f} |")
    
    total_trades = pf['trades_won'] + pf['trades_lost']
    win_rate = (pf['trades_won'] / total_trades * 100) if total_trades > 0 else 0
    md.append(f"| **Win Rate** | {win_rate:.1f}% ({total_trades} Trades) |")
    md.append("")
    
    md.append("## Active Positions")
    if not pf['active_positions']:
        md.append("*Currently holding 100% Cash. Waiting for aggressive momentum triggers.*")
    else:
        md.append("| Date | Company | Shares | Entry Price | Trailing Stop | Current Price | Unrealized P&L |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for comp, pos in pf['active_positions'].items():
            curr_p = market_data[comp]['current_price'] if comp in market_data else pos['entry_price']
            unrealized_val = (curr_p - pos['entry_price']) * pos.get('shares', 0)
            unrealized_pct = (curr_p - pos['entry_price']) / pos['entry_price'] * 100
            
            md.append(f"| {pos['entry_date']} | **{comp}** | {pos.get('shares', 0)} | INR {pos['entry_price']:.2f} | INR {pos['stop']:.2f} | INR {curr_p:.2f} | {unrealized_pct:.2f}% (INR {unrealized_val:,.2f}) |")
            
    md.append("")
    md.append("## Closed Trade History")
    if not pf['closed_trades']:
        md.append("*No closed trades yet.*")
    else:
        md.append("| Entry | Exit | Company | Entry Price | Exit Price | Shares Sold | Realized P&L | Reason |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for t in reversed(pf['closed_trades'][-15:]): 
            md.append(f"| {t['entry_date']} | {t['exit_date']} | **{t['comp']}** | INR {t['entry_price']:.2f} | INR {t['exit_price']:.2f} | {t.get('shares_sold', 0)} | INR {t['pnl']:,.2f} | {t['reason']} |")
            
    with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))

def run_bot():
    default_pf = {
        'starting_balance': 100000.0, 'cash': 100000.0, 'realized_pnl': 0.0,
        'trades_won': 0, 'trades_lost': 0, 'active_positions': {}, 'closed_trades': []
    }
    pf = load_json(PORTFOLIO_FILE, default_pf)
    
    # Check if this is old V1 portfolio being loaded by accident and reset it if so
    if pf['starting_balance'] != 100000.0:
        print("V1 Portfolio detected. Resetting to 1 Lakh V2 Logic.")
        pf = default_pf
        
    market = load_market_data()
    fundamentals = load_json(FUNDAMENTALS_FILE, {})
    
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    to_close = []
    for comp, pos in pf['active_positions'].items():
        if comp not in market: continue
        curr_p = market[comp]['current_price']
        
        # Update Highest Peak and Trailing Stop
        if curr_p > pos['highest']:
            pos['highest'] = curr_p
            pos['stop'] = max(pos['stop'], curr_p * (1.0 - TRAILING_STOP_PCT))
            
        reason = None
        
        # Structural Stop (Close < 50 DMA) is managed by buy_zone_status "NEUTRAL - BEARISH" 
        # But we also have hard trailing stops.
        status = market[comp].get('buy_zone_status', 'NEUTRAL')
        if 'BEARISH' in status:
            reason = "Structural Trend Broken (Below 50 DMA)"
        elif curr_p <= pos['stop']:
            reason = "Trailing Stop Triggered"
            
        if reason:
            shares_to_sell = pos['shares']
            
            gross_val = curr_p * shares_to_sell
            sell_friction = gross_val * FRICTION_PCT
            net_val = gross_val - sell_friction
            
            buy_val = pos['entry_price'] * shares_to_sell
            buy_friction = buy_val * FRICTION_PCT
            net_cost = buy_val + buy_friction
            
            net_pnl = net_val - net_cost
            
            to_close.append({
                'comp': comp, 'entry_date': pos['entry_date'], 'exit_date': today,
                'entry_price': pos['entry_price'], 'exit_price': curr_p,
                'shares_sold': shares_to_sell, 'pnl': net_pnl, 
                'reason': reason
            })
            
    for t in to_close:
        pf['cash'] += (t['shares_sold'] * t['exit_price']) - (t['shares_sold'] * t['exit_price'] * FRICTION_PCT)
        pf['realized_pnl'] += t['pnl']
        if t['pnl'] > 0: pf['trades_won'] += 1
        else: pf['trades_lost'] += 1
        
        pf['closed_trades'].append(t)
        del pf['active_positions'][t['comp']]
        print(f"CLOSED: {t['comp']} | {t['reason']} | PnL: {t['pnl']:.2f}")

    # BUY LOGIC
    for comp, d in market.items():
        status = d.get('buy_zone_status', '')
        if 'BREAKOUT ACTIVE' in status or 'BUY' in status:
            if comp not in pf['active_positions'] and len(pf['active_positions']) < MAX_POSITIONS:
                
                # Check fundamental score
                fund_score = fundamentals.get(comp, 0)
                if fund_score >= 50:
                    curr_p = d['current_price']
                    shares_to_buy = math.floor(CAPITAL_PER_TRADE / curr_p)
                    
                    if shares_to_buy > 0:
                        gross_cost = shares_to_buy * curr_p
                        friction = gross_cost * FRICTION_PCT
                        net_cost = gross_cost + friction
                        
                        if pf['cash'] >= net_cost:
                            pf['cash'] -= net_cost
                            pf['active_positions'][comp] = {
                                'entry_date': today,
                                'entry_price': curr_p,
                                'highest': curr_p,
                                'stop': curr_p * (1.0 - INITIAL_STOP_PCT),
                                'shares': shares_to_buy,
                                'capital_deployed': net_cost
                            }
                            print(f"BOUGHT: {comp} | Shares: {shares_to_buy} | Capital: {net_cost:,.2f} | Score: {fund_score}")

    save_json(PORTFOLIO_FILE, pf)
    render_ledger(pf, market)
    print("Bot execution complete.")

if __name__ == "__main__":
    run_bot()
