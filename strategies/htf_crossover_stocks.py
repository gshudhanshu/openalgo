"""
HTF Crossover Intraday Stock Strategy
Converted from options strategy to direct stock trading with short selling capability

Strategy Logic:
- Uses higher timeframe (15m) to determine trend direction
- Long signal: HTF close crosses above HTF open → Buy Stock
- Short signal: HTF close crosses below HTF open → Sell Short
- Stop loss: 0.5% below entry for long, 0.5% above entry for short
- Reversal exits: Exit long on short signal, exit short on long signal
"""

from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, date

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
strategy = "HTF Crossover Intraday Stock Strategy"
htf_interval = "15m"  # Higher timeframe (5 minutes)
stop_loss_perc = 0.5  # Stop loss percentage (0.5% for stocks)
position_size = 4000  # Position size in rupees per stock

# Trading symbols configuration
symbols_config = {
    "BAJFINANCE": {
        "symbol": "BAJFINANCE",
        "exchange": "NSE",
        "lot_size": 1,  # Stocks trade in single shares
        "tick_size": 0.05
    },
    "PAYTM": {
        "symbol": "PAYTM",
        "exchange": "NSE",
        "lot_size": 1,  # Stocks trade in single shares
        "tick_size": 0.05
    },
}

# Initialize OpenAlgo client
client = api(api_key=api_key, host='http://127.0.0.1:5000')

def get_htf_data(symbol_config, days_back=3):
    """Fetch higher timeframe data"""
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        df = client.history(
            symbol=symbol_config["symbol"],
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

def calculate_quantity(symbol_config, current_price):
    """Calculate quantity based on position size"""
    try:
        # Calculate quantity based on position size in rupees
        quantity = int(position_size / current_price)
        
        # Ensure minimum quantity of 1
        if quantity < 1:
            quantity = 1
            
        return quantity
    except Exception as e:
        log_with_time(f"❌ Error calculating quantity: {e}")
        return 1

def buy_stock(symbol_name, symbol_config, current_price):
    """Buy stock"""
    try:
        quantity = calculate_quantity(symbol_config, current_price)
        
        buy_response = client.placeorder(
            strategy=strategy,
            symbol=symbol_config["symbol"],
            exchange=symbol_config["exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",  # Intraday
            quantity=quantity
        )
        
        log_with_time(f"✅ Stock bought:")
        print(f"  Symbol: {symbol_name}")
        print(f"  Quantity: {quantity}")
        print(f"  Price: ₹{current_price}")
        print(f"  Response: {buy_response}")
        
        return buy_response, quantity
        
    except Exception as e:
        log_with_time(f"❌ Error buying stock: {e}")
        return None, 0

def sell_stock(symbol_name, symbol_config, quantity):
    """Sell stock (exit long position)"""
    try:
        sell_response = client.placeorder(
            strategy=strategy,
            symbol=symbol_config["symbol"],
            exchange=symbol_config["exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",  # Intraday
            quantity=quantity
        )
        
        log_with_time(f"🔄 Stock sold (exit long):")
        print(f"  Symbol: {symbol_name}")
        print(f"  Quantity: {quantity}")
        print(f"  Response: {sell_response}")
        
        return sell_response
        
    except Exception as e:
        log_with_time(f"❌ Error selling stock: {e}")
        return None

def sell_short(symbol_name, symbol_config, current_price):
    """Sell short (enter short position)"""
    try:
        quantity = calculate_quantity(symbol_config, current_price)
        
        short_response = client.placeorder(
            strategy=strategy,
            symbol=symbol_config["symbol"],
            exchange=symbol_config["exchange"],
            action="SELL",
            price_type="MARKET",
            product="MIS",  # Intraday
            quantity=quantity
        )
        
        log_with_time(f"📉 Stock sold short:")
        print(f"  Symbol: {symbol_name}")
        print(f"  Quantity: {quantity}")
        print(f"  Price: ₹{current_price}")
        print(f"  Response: {short_response}")
        
        return short_response, quantity
        
    except Exception as e:
        log_with_time(f"❌ Error selling short: {e}")
        return None, 0

def buy_to_cover(symbol_name, symbol_config, quantity):
    """Buy to cover (exit short position)"""
    try:
        cover_response = client.placeorder(
            strategy=strategy,
            symbol=symbol_config["symbol"],
            exchange=symbol_config["exchange"],
            action="BUY",
            price_type="MARKET",
            product="MIS",  # Intraday
            quantity=quantity
        )
        
        log_with_time(f"🔄 Stock covered (exit short):")
        print(f"  Symbol: {symbol_name}")
        print(f"  Quantity: {quantity}")
        print(f"  Response: {cover_response}")
        
        return cover_response
        
    except Exception as e:
        log_with_time(f"❌ Error buying to cover: {e}")
        return None

def htf_crossover_stock_strategy():
    """Main strategy function for stock trading"""
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
                
                print(f"Current Price: ₹{current_price}")
                print(f"Long Signal: {long_signal}")
                print(f"Short Signal: {short_signal}")
                
                # Entry logic (only if no existing position)
                if long_signal and symbol_name not in positions:
                    log_with_time(f"🟢 LONG SIGNAL for {symbol_name} - Buying Stock")
                    
                    buy_resp, quantity = buy_stock(symbol_name, symbol_config, current_price)
                    
                    if buy_resp and quantity > 0:
                        entry_time = datetime.now()
                        positions[symbol_name] = {
                            'type': 'long',
                            'entry_price': current_price,
                            'quantity': quantity,
                            'stop_loss': current_price * (1 - stop_loss_perc / 100),
                            'entry_time': entry_time
                        }
                        print(f"✅ Long position entered at {entry_time.strftime('%H:%M:%S')} - "
                              f"Entry: ₹{current_price}, Stop: ₹{current_price * (1 - stop_loss_perc / 100):.2f}, Qty: {quantity}")
                
                elif short_signal and symbol_name not in positions:
                    log_with_time(f"🔴 SHORT SIGNAL for {symbol_name} - Selling Short")
                    
                    short_resp, quantity = sell_short(symbol_name, symbol_config, current_price)
                    
                    if short_resp and quantity > 0:
                        entry_time = datetime.now()
                        positions[symbol_name] = {
                            'type': 'short',
                            'entry_price': current_price,
                            'quantity': quantity,
                            'stop_loss': current_price * (1 + stop_loss_perc / 100),  # Stop loss above entry for shorts
                            'entry_time': entry_time
                        }
                        print(f"✅ Short position entered at {entry_time.strftime('%H:%M:%S')} - "
                              f"Entry: ₹{current_price}, Stop: ₹{current_price * (1 + stop_loss_perc / 100):.2f}, Qty: {quantity}")
                
                # Exit logic for existing positions
                if symbol_name in positions:
                    position = positions[symbol_name]
                    exit_hit = False
                    exit_reason = ""
                    
                    # Reversal exit logic - exit long on short signal, exit short on long signal
                    if position['type'] == 'long' and short_signal:
                        log_with_time(f"🔄 REVERSAL EXIT for {symbol_name} - Short signal detected (exit long)")
                        sell_resp = sell_stock(symbol_name, symbol_config, position['quantity'])
                        if sell_resp:
                            exit_hit = True
                            exit_reason = "Signal Reversal"
                    
                    elif position['type'] == 'short' and long_signal:
                        log_with_time(f"🔄 REVERSAL EXIT for {symbol_name} - Long signal detected (exit short)")
                        cover_resp = buy_to_cover(symbol_name, symbol_config, position['quantity'])
                        if cover_resp:
                            exit_hit = True
                            exit_reason = "Signal Reversal"
                    
                    # Stop loss logic - different for long vs short
                    elif position['type'] == 'long' and current_price <= position['stop_loss']:
                        log_with_time(f"🛑 STOP LOSS HIT for {symbol_name} (long position)")
                        sell_resp = sell_stock(symbol_name, symbol_config, position['quantity'])
                        if sell_resp:
                            exit_hit = True
                            exit_reason = "Stop Loss"
                    
                    elif position['type'] == 'short' and current_price >= position['stop_loss']:
                        log_with_time(f"🛑 STOP LOSS HIT for {symbol_name} (short position)")
                        cover_resp = buy_to_cover(symbol_name, symbol_config, position['quantity'])
                        if cover_resp:
                            exit_hit = True
                            exit_reason = "Stop Loss"
                    
                    if exit_hit:
                        # Calculate position hold time
                        time_held = datetime.now() - position['entry_time']
                        hours = int(time_held.total_seconds() // 3600)
                        minutes = int((time_held.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        
                        # Calculate P&L (different for long vs short)
                        entry_value = position['entry_price'] * position['quantity']
                        exit_value = current_price * position['quantity']
                        
                        if position['type'] == 'long':
                            pnl = exit_value - entry_value  # Profit when price goes up
                        else:  # short position
                            pnl = entry_value - exit_value  # Profit when price goes down
                            
                        pnl_perc = (pnl / entry_value) * 100
                        
                        del positions[symbol_name]
                        print(f"🔄 {position['type'].title()} position closed for {symbol_name} - "
                              f"Held for {time_str} (Entry: {position['entry_time'].strftime('%H:%M:%S')}) - "
                              f"Reason: {exit_reason}")
                        print(f"📊 P&L: ₹{pnl:.2f} ({pnl_perc:+.2f}%) - "
                              f"Entry: ₹{position['entry_price']:.2f}, Exit: ₹{current_price:.2f}")
                    else:
                        # Calculate time since entry and unrealized P&L
                        time_held = datetime.now() - position['entry_time']
                        hours = int(time_held.total_seconds() // 3600)
                        minutes = int((time_held.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        
                        # Calculate unrealized P&L (different for long vs short)
                        if position['type'] == 'long':
                            unrealized_pnl = (current_price - position['entry_price']) * position['quantity']
                            unrealized_perc = ((current_price - position['entry_price']) / position['entry_price']) * 100
                        else:  # short position
                            unrealized_pnl = (position['entry_price'] - current_price) * position['quantity']
                            unrealized_perc = ((position['entry_price'] - current_price) / position['entry_price']) * 100
                        
                        position_icon = "📈" if position['type'] == 'long' else "📉"
                        print(f"{position['type'].title()} Position Status - Entry: ₹{position['entry_price']:.2f} ({position['entry_time'].strftime('%H:%M:%S')}), "
                              f"Current: ₹{current_price:.2f}, Stop: ₹{position['stop_loss']:.2f}, "
                              f"Time Held: {time_str}, Qty: {position['quantity']}")
                        print(f"{position_icon} Unrealized P&L: ₹{unrealized_pnl:.2f} ({unrealized_perc:+.2f}%)")
                
                print(f"Active positions: {len(positions)}")
        
        except Exception as e:
            log_with_time(f"❌ Error in strategy loop: {e}")
            time.sleep(30)
            continue
        
        # Wait before next cycle (60 seconds for HTF strategy)
        print(f"Waiting 60 seconds before next analysis...")
        time.sleep(60)

if __name__ == "__main__":
    log_with_time("🚀 Starting HTF Crossover Intraday Stock Strategy")
    print("="*60)
    print(f"Strategy: {strategy}")
    print(f"HTF Interval: {htf_interval}")
    print(f"Stop Loss: {stop_loss_perc}%")
    print(f"Position Size: ₹{position_size:,} per stock")
    print(f"Symbols: {list(symbols_config.keys())}")
    print("="*60)
    print("📈 STOCK TRADING MODE:")
    print("   🟢 Long Signal → Buy Stock")
    print("   🔴 Short Signal → Sell Short")
    print("   🔄 Reversal Exit → Exit on opposite signal")
    print("   🛑 Stop Loss → 0.5% (below entry for long, above entry for short)")
    print("   💰 Position Size → ₹4,000 per stock")
    print("="*60)
    
    htf_crossover_stock_strategy() 