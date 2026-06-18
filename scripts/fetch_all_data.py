import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEFRAMES = {'3mo': 63, '6mo': 126, '9mo': 189, '1y': 252, '2y': 504}
FRICTION = 0.15

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PORTFOLIOS = {
    'semi': ({
        'HCL Tech': 'HCLTECH.NS', 'Tata Elxsi': 'TATAELXSI.NS', 'Dixon Technologies': 'DIXON.NS',
        'CG Power': 'CGPOWER.NS', 'Kaynes Technology': 'KAYNES.NS', 'Vedanta': 'VEDL.NS',
        'BEL': 'BEL.NS', 'Data Patterns': 'DATAPATTNS.NS', 'Syrma SGS': 'SYRMA.NS',
        'Cyient DLM': 'CYIENTDLM.NS', 'PG Electroplast': 'PGEL.NS', 'Avalon Technologies': 'AVALON.NS',
        'MosChip Tech': 'MOSCHIP.NS', 'Paras Defence': 'PARAS.NS'
    }, 'semi_data.json', 'SEMICONDUCTORS', 'Aggressive Trend Follow'),
    
    'ancillary': ({
        'ASM Tech (Equip)': 'ASMTEC.NS', 'RIR Power (SiC)': 'RIR.NS', 'SPEL Semi (OSAT)': 'SPEL.NS',
        'Linde India (Gases)': 'LINDEINDIA.NS', 'Navin Fluorine (Chems)': 'NAVINFLUOR.NS',
        'Archean Chem (Chems)': 'ACI.NS', 'Stallion India (Chems)': 'STALLION.BO',
        'Amber Ent (PCB)': 'AMBER.NS', 'Hitachi Energy (Power)': 'POWERINDIA.NS',
        'L&T Tech (Design)': 'LTTS.NS', 'Tata Chemicals (Silica)': 'TATACHEM.NS'
    }, 'data.json', 'ANCILLARY ECOSYSTEM', 'Aggressive Trend Follow'),

    'nuclear': ({
        'BHEL (Main)': 'BHEL.NS', 'L&T (Main)': 'LT.NS', 'Walchandnagar (Main)': 'WALCHANNAG.NS',
        'Godrej Ind (Main)': 'GODREJIND.NS', 'Thermax (Ancillary)': 'THERMAX.NS',
        'KSB Ltd (Ancillary)': 'KSB.NS', 'GMM Pfaudler (Ancillary)': 'GMMPFAUDL.NS',
        'Apar Ind (Ancillary)': 'APARINDS.NS', 'Graphite India (Ancillary)': 'GRAPHITE.NS',
        'MTAR Tech (Ancillary)': 'MTARTECH.NS'
    }, 'nuclear_data.json', 'NUCLEAR ENERGY', 'Aggressive Trend Follow'),

    'water': ({
        'VA Tech Wabag (Main)': 'WABAG.NS', 'Ion Exchange (Main)': 'IONEXCHANG.NS',
        'EMS Ltd (Main)': 'EMSLIMITED.NS', 'Enviro Infra (Main)': 'ENVIROINFRA.NS',
        'Supreme Ind (Ancillary)': 'SUPREMEIND.NS', 'Astral (Ancillary)': 'ASTRAL.NS',
        'Prince Pipes (Ancillary)': 'PRINCEPIPE.NS', 'Finolex Ind (Ancillary)': 'FINPIPE.NS',
        'Kirloskar Bros (Ancillary)': 'KIRLOSBROS.NS', 'Shakti Pumps (Ancillary)': 'SHAKTIPUMP.NS'
    }, 'water_data.json', 'WATER INFRASTRUCTURE', 'Aggressive Trend Follow'),

    'drone': ({
        'ideaForge (Main)': 'IDEAFORGE.NS', 'Zen Tech (Main)': 'ZENTEC.NS',
        'Paras Defence (Main)': 'PARAS.NS', 'Data Patterns (Main)': 'DATAPATTNS.NS',
        'BEL (Ancillary)': 'BEL.NS', 'Astra Microwave (Ancillary)': 'ASTRAMC.NS',
        'Solar Ind (Ancillary)': 'SOLARINDS.NS', 'HAL (Ancillary)': 'HAL.NS',
        'Laurus Labs (Ancillary)': 'LAURUSLABS.NS', 'Cyient (Ancillary)': 'CYIENT.NS'
    }, 'drone_data.json', 'DRONE & UAV', 'Aggressive Trend Follow'),

    'datacenter': ({
        'Anant Raj (Main)': 'ANANTRAJ.NS', 'Netweb Tech (Main)': 'NETWEB.NS',
        'RateGain (Main)': 'RATEGAIN.NS', 'Blue Star (Ancillary)': 'BLUESTARCO.NS',
        'Voltas (Ancillary)': 'VOLTAS.NS', 'ABB India (Ancillary)': 'ABB.NS',
        'Siemens India (Ancillary)': 'SIEMENS.NS', 'Polycab (Ancillary)': 'POLYCAB.NS',
        'Sterlite Tech (Ancillary)': 'STLTECH.NS', 'HFCL (Ancillary)': 'HFCL.NS',
        'Schneider India (Ancillary)': 'SCHNEIDER.NS'
    }, 'datacenter_data.json', 'DATA CENTER & AI INFRA', 'Aggressive Trend Follow'),

    'hydrogen': ({
        'L&T (Main)': 'LT.NS', 'NTPC (Main)': 'NTPC.NS', 'Indian Oil (Main)': 'IOC.NS',
        'GAIL (Main)': 'GAIL.NS', 'Thermax (Ancillary)': 'THERMAX.NS',
        'Praj Ind (Ancillary)': 'PRAJ.NS', 'Kirloskar Oil (Ancillary)': 'KIRLOSENG.NS',
        'Gujarat Fluoro (Ancillary)': 'FLUOROCHEM.NS', 'Sterling & Wilson (Ancillary)': 'SWSOLAR.NS',
        'Deepak Fertilisers (Ancillary)': 'DEEPAKFERT.NS'
    }, 'hydrogen_data.json', 'GREEN HYDROGEN', 'Aggressive Trend Follow'),
    
    'rare_earth': ({
        'NMDC (Main)': 'NMDC.NS', 'Hindustan Copper (Main)': 'HINDCOPPER.NS', 'GMDC (Main)': 'GMDCLTD.NS',
        'MOIL (Main)': 'MOIL.NS', 'Mishra Dhatu Nigam (Main)': 'MIDHANI.NS',
        'Exide Industries (Ancillary)': 'EXIDEIND.NS', 'Amara Raja (Ancillary)': 'ARE&M.NS',
        'Neogen Chemicals (Ancillary)': 'NEOGEN.NS', 'Himadri Speciality (Ancillary)': 'HSCL.NS',
        'Tata Chemicals (Ancillary)': 'TATACHEM.NS'
    }, 'rare_earth_data.json', 'RARE EARTHS & METALS', 'Aggressive Trend Follow'),
    
    'green_energy': ({
        'Tata Power (Main)': 'TATAPOWER.NS', 'Adani Green (Main)': 'ADANIGREEN.NS', 'Suzlon Energy (Main)': 'SUZLON.NS',
        'JSW Energy (Main)': 'JSWENERGY.NS', 'Waaree Renewables (Main)': 'WAAREERTL.NS',
        'Borosil Renewables (Ancillary)': 'BORORENEW.NS', 'Sterling and Wilson (Ancillary)': 'SWSOLAR.NS',
        'Genus Power (Ancillary)': 'GENUSPOWER.NS', 'Olectra Greentech (Ancillary)': 'OLECTRA.NS',
        'Servotech Power (Ancillary)': 'SERVOTECH.NS'
    }, 'green_energy_data.json', 'GREEN ENERGY & INFRA', 'Aggressive Trend Follow'),
    
    'it_services': ({
        'TCS (Main)': 'TCS.NS', 'Infosys (Main)': 'INFY.NS', 'HCL Tech (Main)': 'HCLTECH.NS',
        'LTIMindtree (Main)': 'LTIM.NS', 'Persistent Systems (Main)': 'PERSISTENT.NS',
        'KPIT Technologies (Ancillary)': 'KPITTECH.NS', 'Tata Elxsi (Ancillary)': 'TATAELXSI.NS',
        'RateGain (Ancillary)': 'RATEGAIN.NS', 'Cyient (Ancillary)': 'CYIENT.NS',
        'MapmyIndia (Ancillary)': 'MAPMYINDIA.NS'
    }, 'it_services_data.json', 'IT SERVICES & ER&D', 'Aggressive Trend Follow')
}

def add_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['High_20'] = df['High'].rolling(20).max()
    df['High_52w'] = df['High'].rolling(252).max()
    df['Vol_MA20'] = df['Volume'].rolling(20).mean()
    
    delta = df['Close'].diff(1)
    gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    ema_fast = df['Close'].ewm(span=12, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    df.bfill(inplace=True)
    return df

def run_backtest_and_status(df, strategy_name):
    buy_signals = []; sell_signals = []; trades = []
    in_position = 0.0 # 0.0 (Flat), 1.0 (Full)
    entry_price = 0.0; highest = 0.0; stop_loss = 0.0
    status = 'NEUTRAL'
    
    close = float(df['Close'].iloc[-1])
    vol = df['Volume'].iloc[-1]
    vol_ma = df['Vol_MA20'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    ema10 = df['EMA_10'].iloc[-1]
    sma20 = df['SMA_20'].iloc[-1]
    sma50 = df['SMA_50'].iloc[-1]
    sma200 = df['SMA_200'].iloc[-1]
    high_52w = df['High_52w'].iloc[-1]

    for i in range(252, len(df)):
        c = float(df['Close'].iloc[i])
        e10 = df['EMA_10'].iloc[i]
        s20 = df['SMA_20'].iloc[i]
        s50 = df['SMA_50'].iloc[i]
        h52w = df['High_52w'].iloc[i-1]
        v = df['Volume'].iloc[i]
        vma = df['Vol_MA20'].iloc[i]
        d_str = df.index[i].strftime('%Y-%m-%d')
        
        # AGGRESSIVE MEGA-BULL ENTRY: Breakout near 52w High or EMA10 > SMA20 in uptrend
        buy_trigger = (e10 > s20 and df['EMA_10'].iloc[i-1] <= df['SMA_20'].iloc[i-1] and c > s50) or (c > h52w * 0.95 and v > vma * 1.5)
        
        # AGGRESSIVE EXIT: Let winners run indefinitely. Only exit if price closes below SMA_50 or trailing stop hits -20%
        strategy_exit = c < s50
        
        if in_position == 0.0 and buy_trigger:
            in_position = 1.0; entry_price = c; highest = c
            stop_loss = c * 0.85 # 15% Initial Hard Stop
            buy_signals.append({'date': d_str, 'price': round(c, 2), 'note': 'Aggressive Momentum Entry'})
        
        elif in_position == 1.0:
            highest = max(highest, c)
            # Wide trailing stop of -20% from peak to allow normal bull market pullbacks
            stop_loss = max(stop_loss, highest * 0.80) 
            
            if c <= stop_loss:
                in_position = 0.0
                trades.append(((c - entry_price) / entry_price * 100 * 1.0) - FRICTION)
                sell_signals.append({'date': d_str, 'price': round(c, 2), 'note': 'Trailing Stop (-20%)'})
            elif strategy_exit:
                in_position = 0.0
                trades.append(((c - entry_price) / entry_price * 100 * 1.0) - FRICTION)
                sell_signals.append({'date': d_str, 'price': round(c, 2), 'note': 'Trend Broken (Close < 50 DMA)'})

    # CURRENT STATUS
    if ema10 > sma20 and close > sma50 and close > high_52w * 0.90:
        status = 'BREAKOUT ACTIVE — BUY'
    elif close > sma50 and close <= high_52w * 0.90:
        status = 'APPROACHING BREAKOUT'
    elif close < sma50 and close > sma200:
        status = 'NEUTRAL — BULLISH'
    else:
        status = 'NEUTRAL — BEARISH'

    if in_position > 0.0:
        close_final = float(df['Close'].iloc[-1])
        ret = ((close_final - entry_price) / entry_price * 100 * in_position) - FRICTION
        trades.append(ret)
        sell_signals.append({'date': df.index[-1].strftime('%Y-%m-%d'), 'price': round(close_final, 2), 'note': 'End'})

    total_return = sum(trades) if trades else 0
    wins = [t for t in trades if t > 0]
    bt = {
        'strategy_name': strategy_name,
        'buy_signals': buy_signals, 'sell_signals': sell_signals,
        'individual_trades_pct': [round(t, 2) for t in trades],
        'total_return_pct': round(total_return, 2),
        'win_rate_pct': round(len(wins)/len(trades)*100, 2) if trades else 0,
        'total_trades': len(trades),
        'max_drawdown_pct': round(min(trades), 2) if trades else 0,
    }
    return bt, status

def get_yfinance_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    return session

def process_portfolio(tickers, output_file, label, strategy_name):
    output_path = os.path.join(ROOT_DIR, output_file)
    print(f"PROCESSING: {label} [{strategy_name}]")
    multi_tf_data = {tf: {} for tf in TIMEFRAMES}
    
    session = get_yfinance_session()
    successful_downloads = 0
    
    for name, symbol in tickers.items():
        try:
            df = yf.download(symbol, period='3y', progress=False, session=session) # Needs 3y because 52w high takes 252 days
            if df.empty: 
                df = yf.download(symbol.replace('.NS', '.BO'), period='3y', progress=False, session=session)
            if df.empty: 
                print(f"Failed to fetch data for {symbol}")
                continue
                
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            df.dropna(inplace=True)
            total_days = len(df)
            if total_days < 252:
                continue
                
            successful_downloads += 1
            
            for tf_name, tf_days in TIMEFRAMES.items():
                if total_days < tf_days + 150: continue # Changed from 252 to 150 to ensure we have enough data but don't drop everyone
                
                # We need up to 252 days for the 52w high, but if we don't have it, we just use the max available
                lookback = min(total_days, tf_days + 252)
                sliced = df.iloc[-lookback:].copy()
                sliced = add_indicators(sliced)
                bt, zone = run_backtest_and_status(sliced, strategy_name)
                
                sliced_indexed = sliced.iloc[-tf_days:].copy()
                sliced_indexed.index = sliced_indexed.index.strftime('%Y-%m-%d')
                chart_data = []
                for date, row in sliced_indexed.iterrows():
                    chart_data.append({
                        'time': date, 'open': round(float(row['Open']), 2), 'high': round(float(row['High']), 2),
                        'low': round(float(row['Low']), 2), 'close': round(float(row['Close']), 2),
                        'sma_50': round(float(row['SMA_50']), 2) if not np.isnan(row['SMA_50']) else None,
                        'sma_200': round(float(row['SMA_200']), 2) if not np.isnan(row['SMA_200']) else None,
                        'rsi': round(float(row['RSI']), 2) if not np.isnan(row['RSI']) else None,
                    })
                
                bh = round((chart_data[-1]['close'] - chart_data[0]['close']) / chart_data[0]['close'] * 100, 2)
                multi_tf_data[tf_name][name] = {
                    'chart_data': chart_data, 'backtest': bt,
                    'current_price': chart_data[-1]['close'], 'current_rsi': chart_data[-1]['rsi'],
                    'buy_zone_status': zone, 'buy_hold_return_pct': bh,
                    'strategy_name': strategy_name,
                }
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            pass
            
    if successful_downloads == 0:
        raise Exception(f"CRITICAL ERROR: Failed to download any data for {label}.")
        
    with open(output_path, 'w') as f: 
        json.dump(multi_tf_data, f)
    print(f"Successfully wrote {output_path}")

if __name__ == "__main__":
    for key, (tickers, outfile, label, strategy) in PORTFOLIOS.items():
        process_portfolio(tickers, outfile, label, strategy)
    print("Market Data Sync Complete.")
