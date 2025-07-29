"""
HTF Crossover Options Strategy
Converted from Pine Script "GetTrendStrategy with Accurate HTF and Stop Loss"

Strategy Logic:
- Uses higher timeframe (60m) to determine trend direction
- Long signal: HTF close crosses above HTF open -> Bull Call Spread
- Short signal: HTF close crosses below HTF open -> Bear Put Spread
- Stop loss based on percentage from entry price
"""

from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, date
import calendar

def log_with_time(message):
    """Print message with timestamp for important events"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def log_section(section_name):
    """Print section header with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] {section_name}")
    print("="*50)

# Get API key from openalgo portal
api_key = '9e660e71b2db4b839225acd6432352aa0bcc1e5a341a87f526d90dafee1eb72d'

# Strategy configuration
strategy = "HTF Crossover Options Strategy"
htf_interval = "5m"  # Higher timeframe (1 hour)
stop_loss_perc = 0.25  # Stop loss percentage
spread_distance = 200  # Distance between strikes for spreads

# Trading symbols
symbols_config = {
    "NIFTY": {
        "index_symbol": "NIFTY",
        "exchange": "NSE_INDEX", 
        "options_exchange": "NFO",
        "strike_step": 50,
        "lot_size": 75
    }
}

# Initialize OpenAlgo client
client = api(api_key=api_key, host='http://127.0.0.1:5000')

def get_current_expiry():
    """Get current week's Thursday expiry for options"""
    today = date.today()
    
    # Find this week's Thursday
    days_ahead = 3 - today.weekday()  # Thursday is weekday 3
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    expiry_date = today + timedelta(days_ahead)
    
    # Format as DDMMMYY (e.g., 30JAN25)
    return expiry_date.strftime("%d%b%y").upper()

def get_atm_strike(symbol_config):
    """Get at-the-money strike for options"""
    try:
        quote = client.quotes(
            symbol=symbol_config["index_symbol"], 
            exchange=symbol_config["exchange"]
        )
        
        if quote.get("status") == "success":
            ltp = quote["data"]["ltp"]
            step = symbol_config["strike_step"]
            return int(round(ltp / step) * step)
        else:
            print(f"Error getting quote: {quote}")
            return None
    except Exception as e:
        log_with_time(f"❌ Error getting ATM strike: {e}")
        return None

def get_htf_data(symbol_config, days_back=4):
    """Fetch higher timeframe data"""
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        df = client.history(
            symbol=symbol_config["index_symbol"],
            exchange=symbol_config["exchange"],
            interval=htf_interval,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check if response is a dictionary (error) or DataFrame
        if isinstance(df, dict):
            log_with_time(f"❌ Error in history API response: {df}")
            return pd.DataFrame()
        
        # Check if DataFrame is valid and not empty
        if hasattr(df, 'empty') and not df.empty:
            df['close'] = df['close'].round(2)
            df['open'] = df['open'].round(2)
            return df
        else:
            print(f"Empty or invalid DataFrame received: {type(df)}")
            return pd.DataFrame()
            
    except Exception as e:
        log_with_time(f"❌ Error fetching HTF data: {e}")
        return pd.DataFrame()

def check_crossover_signals(df):
    """Check for HTF open/close crossover signals"""
    if len(df) < 2:
        return False, False, None
    
    # Current and previous HTF candles
    current_open = df['open'].iloc[-1]
    current_close = df['close'].iloc[-1]
    prev_open = df['open'].iloc[-2]
    prev_close = df['close'].iloc[-2]
    
    # Crossover conditions (similar to Pine Script logic)
    long_signal = (prev_close <= prev_open) and (current_close > current_open)
    short_signal = (prev_close >= prev_open) and (current_close < current_open)
    
    current_price = current_close
    
    return long_signal, short_signal, current_price

def place_bull_call_spread(symbol_name, symbol_config, atm_strike):
    """Place bull call spread (buy lower call + sell higher call)"""
    try:
        expiry = get_current_expiry()
        lot_size = symbol_config["lot_size"]
        
        # Buy ATM call
        buy_symbol = f"{symbol_name}{expiry}{atm_strike}CE"
        buy_response = client.placeorder(
            strategy=strategy,
            symbol=buy_symbol,
            exchange=symbol_config["options_exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        # Sell OTM call
        sell_symbol = f"{symbol_name}{expiry}{atm_strike + spread_distance}CE"
        sell_response = client.placeorder(
            strategy=strategy,
            symbol=sell_symbol,
            exchange=symbol_config["options_exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        log_with_time(f"✅ Bull Call Spread placed:")
        print(f"  Buy: {buy_symbol} - {buy_response}")
        print(f"  Sell: {sell_symbol} - {sell_response}")
        
        return buy_response, sell_response
        
    except Exception as e:
        log_with_time(f"❌ Error placing bull call spread: {e}")
        return None, None

def place_bear_put_spread(symbol_name, symbol_config, atm_strike):
    """Place bear put spread (buy higher put + sell lower put)"""
    try:
        expiry = get_current_expiry()
        lot_size = symbol_config["lot_size"]
        
        # Buy ATM put
        buy_symbol = f"{symbol_name}{expiry}{atm_strike}PE"
        buy_response = client.placeorder(
            strategy=strategy,
            symbol=buy_symbol,
            exchange=symbol_config["options_exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        # Sell OTM put
        sell_symbol = f"{symbol_name}{expiry}{atm_strike - spread_distance}PE"
        sell_response = client.placeorder(
            strategy=strategy,
            symbol=sell_symbol,
            exchange=symbol_config["options_exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        log_with_time(f"✅ Bear Put Spread placed:")
        print(f"  Buy: {buy_symbol} - {buy_response}")
        print(f"  Sell: {sell_symbol} - {sell_response}")
        
        return buy_response, sell_response
        
    except Exception as e:
        log_with_time(f"❌ Error placing bear put spread: {e}")
        return None, None

def close_bull_call_spread(symbol_name, symbol_config, atm_strike):
    """Close bull call spread by reversing the trades"""
    try:
        expiry = get_current_expiry()
        lot_size = symbol_config["lot_size"]
        
        # Sell the bought call
        sell_symbol = f"{symbol_name}{expiry}{atm_strike}CE"
        sell_response = client.placeorder(
            strategy=strategy,
            symbol=sell_symbol,
            exchange=symbol_config["options_exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        # Buy back the sold call
        buy_symbol = f"{symbol_name}{expiry}{atm_strike + spread_distance}CE"
        buy_response = client.placeorder(
            strategy=strategy,
            symbol=buy_symbol,
            exchange=symbol_config["options_exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        log_with_time(f"🔄 Bull Call Spread closed:")
        print(f"  Sell: {sell_symbol} - {sell_response}")
        print(f"  Buy: {buy_symbol} - {buy_response}")
        
        return sell_response, buy_response
        
    except Exception as e:
        log_with_time(f"❌ Error closing bull call spread: {e}")
        return None, None

def close_bear_put_spread(symbol_name, symbol_config, atm_strike):
    """Close bear put spread by reversing the trades"""
    try:
        expiry = get_current_expiry()
        lot_size = symbol_config["lot_size"]
        
        # Sell the bought put
        sell_symbol = f"{symbol_name}{expiry}{atm_strike}PE"
        sell_response = client.placeorder(
            strategy=strategy,
            symbol=sell_symbol,
            exchange=symbol_config["options_exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        # Buy back the sold put
        buy_symbol = f"{symbol_name}{expiry}{atm_strike - spread_distance}PE"
        buy_response = client.placeorder(
            strategy=strategy,
            symbol=buy_symbol,
            exchange=symbol_config["options_exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",
            quantity=lot_size
        )
        
        log_with_time(f"🔄 Bear Put Spread closed:")
        print(f"  Sell: {sell_symbol} - {sell_response}")
        print(f"  Buy: {buy_symbol} - {buy_response}")
        
        return sell_response, buy_response
        
    except Exception as e:
        log_with_time(f"❌ Error closing bear put spread: {e}")
        return None, None

def htf_crossover_strategy():
    """Main strategy function"""
    positions = {}  # Track positions for each symbol
    
    while True:
        try:
            for symbol_name, symbol_config in symbols_config.items():
                log_section(f"Analyzing {symbol_name}...")
                
                # Get HTF data
                df = get_htf_data(symbol_config)
                if df.empty:
                    print(f"No data for {symbol_name}, skipping...")
                    continue
                
                # Check for crossover signals
                long_signal, short_signal, current_price = check_crossover_signals(df)
                
                print(f"Current Price: {current_price}")
                print(f"Long Signal: {long_signal}")
                print(f"Short Signal: {short_signal}")
                
                # Entry logic (only if no existing position)
                if long_signal and symbol_name not in positions:
                    log_with_time(f"🟢 LONG SIGNAL for {symbol_name} - Placing Bull Call Spread")
                    atm_strike = get_atm_strike(symbol_config)
                    
                    if atm_strike:
                        buy_resp, sell_resp = place_bull_call_spread(symbol_name, symbol_config, atm_strike)
                        
                        if buy_resp and sell_resp:
                            entry_time = datetime.now()
                            positions[symbol_name] = {
                                'type': 'bull_call',
                                'entry_price': current_price,
                                'atm_strike': atm_strike,
                                'stop_loss': current_price * (1 - stop_loss_perc / 100),
                                'entry_time': entry_time
                            }
                            print(f"✅ Position entered at {entry_time.strftime('%H:%M:%S')} - "
                                  f"Entry: ₹{current_price}, Stop: ₹{current_price * (1 - stop_loss_perc / 100):.2f}")
                
                elif short_signal and symbol_name not in positions:
                    log_with_time(f"🔴 SHORT SIGNAL for {symbol_name} - Placing Bear Put Spread")
                    atm_strike = get_atm_strike(symbol_config)
                    
                    if atm_strike:
                        buy_resp, sell_resp = place_bear_put_spread(symbol_name, symbol_config, atm_strike)
                        
                        if buy_resp and sell_resp:
                            entry_time = datetime.now()
                            positions[symbol_name] = {
                                'type': 'bear_put',
                                'entry_price': current_price,
                                'atm_strike': atm_strike,
                                'stop_loss': current_price * (1 + stop_loss_perc / 100),
                                'entry_time': entry_time
                            }
                            print(f"✅ Position entered at {entry_time.strftime('%H:%M:%S')} - "
                                  f"Entry: ₹{current_price}, Stop: ₹{current_price * (1 + stop_loss_perc / 100):.2f}")
                
                # Exit logic for existing positions
                if symbol_name in positions:
                    position = positions[symbol_name]
                    exit_hit = False
                    exit_reason = ""
                    
                    # Reversal exit logic - exit on opposite signal
                    if position['type'] == 'bull_call' and short_signal:
                        log_with_time(f"🔄 REVERSAL EXIT for {symbol_name} Bull Call Spread - Short signal detected")
                        close_bull_call_spread(symbol_name, symbol_config, position['atm_strike'])
                        exit_hit = True
                        exit_reason = "Signal Reversal"
                        
                    elif position['type'] == 'bear_put' and long_signal:
                        log_with_time(f"🔄 REVERSAL EXIT for {symbol_name} Bear Put Spread - Long signal detected")
                        close_bear_put_spread(symbol_name, symbol_config, position['atm_strike'])
                        exit_hit = True
                        exit_reason = "Signal Reversal"
                    
                    # Stop loss logic
                    elif position['type'] == 'bull_call' and current_price <= position['stop_loss']:
                        log_with_time(f"🛑 STOP LOSS HIT for {symbol_name} Bull Call Spread")
                        close_bull_call_spread(symbol_name, symbol_config, position['atm_strike'])
                        exit_hit = True
                        exit_reason = "Stop Loss"
                        
                    elif position['type'] == 'bear_put' and current_price >= position['stop_loss']:
                        log_with_time(f"🛑 STOP LOSS HIT for {symbol_name} Bear Put Spread")
                        close_bear_put_spread(symbol_name, symbol_config, position['atm_strike'])
                        exit_hit = True
                        exit_reason = "Stop Loss"
                    
                    if exit_hit:
                        # Calculate position hold time
                        time_held = datetime.now() - position['entry_time']
                        hours = int(time_held.total_seconds() // 3600)
                        minutes = int((time_held.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        
                        del positions[symbol_name]
                        print(f"🔄 Position closed for {symbol_name} - "
                              f"Held for {time_str} (Entry: {position['entry_time'].strftime('%H:%M:%S')}) - Reason: {exit_reason}")
                    else:
                        # Calculate time since entry
                        time_held = datetime.now() - position['entry_time']
                        hours = int(time_held.total_seconds() // 3600)
                        minutes = int((time_held.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        
                        print(f"Position Status - Entry: {position['entry_price']} ({position['entry_time'].strftime('%H:%M:%S')}), "
                              f"Current: {current_price}, Stop: {position['stop_loss']:.2f}, "
                              f"Time Held: {time_str}, Type: {position['type'].replace('_', ' ').title()}")
                
                print(f"Active positions: {len(positions)}")
        
        except Exception as e:
            log_with_time(f"❌ Error in strategy loop: {e}")
            time.sleep(30)
            continue
        
        # Wait before next cycle (60 seconds for HTF strategy)
        print(f"Waiting 60 seconds before next analysis...")
        time.sleep(60)

if __name__ == "__main__":
    log_with_time("🚀 Starting HTF Crossover Options Strategy")
    print("="*60)
    print(f"Strategy: {strategy}")
    print(f"HTF Interval: {htf_interval}")
    print(f"Stop Loss: {stop_loss_perc}%")
    print(f"Spread Distance: {spread_distance} points")
    print(f"Symbols: {list(symbols_config.keys())}")
    print(f"Current Expiry: {get_current_expiry()}")
    print("="*60)
    
    htf_crossover_strategy() 