"""
HTF Crossover Intraday Stock Strategy - Test Script
Use this script to verify your setup before running the live strategy
"""

from openalgo import api
import pandas as pd
from datetime import datetime, timedelta

# Configuration (same as main strategy)
api_key = '9e660e71b2db4b839225acd6432352aa0bcc1e5a341a87f526d90dafee1eb72d'
htf_interval = "5m"
position_size = 10000

symbols_config = {
    "RELIANCE": {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "lot_size": 1,
        "tick_size": 0.05
    },
    "TCS": {
        "symbol": "TCS", 
        "exchange": "NSE",
        "lot_size": 1,
        "tick_size": 0.05
    },
    "INFY": {
        "symbol": "INFY",
        "exchange": "NSE", 
        "lot_size": 1,
        "tick_size": 0.05
    },
    "HDFCBANK": {
        "symbol": "HDFCBANK",
        "exchange": "NSE",
        "lot_size": 1,
        "tick_size": 0.05
    },
    "ICICIBANK": {
        "symbol": "ICICIBANK",
        "exchange": "NSE",
        "lot_size": 1,
        "tick_size": 0.05
    }
}

def test_api_connection():
    """Test OpenAlgo API connection"""
    print("="*50)
    print("Testing API Connection...")
    print("="*50)
    
    try:
        client = api(api_key=api_key, host='http://127.0.0.1:5000')
        # Test with a simple quotes call
        quote = client.quotes(symbol="RELIANCE", exchange="NSE")
        
        if quote.get("status") == "success":
            print("✅ API Connection: SUCCESS")
            print(f"   Current RELIANCE: ₹{quote['data']['ltp']}")
            return client
        else:
            print("❌ API Connection: FAILED")
            print(f"   Error: {quote}")
            return None
    except Exception as e:
        print("❌ API Connection: ERROR")
        print(f"   Exception: {e}")
        return None

def test_stock_quotes(client):
    """Test stock quote fetching"""
    print("\n" + "="*50)
    print("Testing Stock Quotes...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            quote = client.quotes(
                symbol=symbol_config["symbol"], 
                exchange=symbol_config["exchange"]
            )
            
            if quote.get("status") == "success":
                ltp = quote["data"]["ltp"]
                quantity = int(position_size / ltp)
                position_value = quantity * ltp
                
                print(f"✅ {symbol_name}: SUCCESS")
                print(f"   Current Price: ₹{ltp}")
                print(f"   Calculated Qty: {quantity} shares")
                print(f"   Position Value: ₹{position_value:,.2f}")
            else:
                print(f"❌ {symbol_name}: FAILED")
                print(f"   Error: {quote}")
                
        except Exception as e:
            print(f"❌ {symbol_name}: ERROR")
            print(f"   Exception: {e}")

def test_data_fetch(client):
    """Test historical data fetching"""
    print("\n" + "="*50)
    print("Testing Historical Data...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            df = client.history(
                symbol=symbol_config["symbol"],
                exchange=symbol_config["exchange"],
                interval=htf_interval,
                start_date=start_date,
                end_date=end_date
            )
            
            if isinstance(df, dict):
                print(f"❌ {symbol_name} Data: ERROR")
                print(f"   Response: {df}")
            elif hasattr(df, 'empty') and not df.empty and len(df) >= 2:
                print(f"✅ {symbol_name} Data: SUCCESS")
                print(f"   Records: {len(df)}")
                print(f"   Latest Close: ₹{df['close'].iloc[-1]}")
                print(f"   Latest Open: ₹{df['open'].iloc[-1]}")
            else:
                print(f"❌ {symbol_name} Data: INSUFFICIENT")
                print(f"   Type: {type(df)}")
                
        except Exception as e:
            print(f"❌ {symbol_name} Data: ERROR")
            print(f"   Exception: {e}")

def test_signal_logic(client):
    """Test signal generation logic"""
    print("\n" + "="*50)
    print("Testing Signal Logic...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            df = client.history(
                symbol=symbol_config["symbol"],
                exchange=symbol_config["exchange"],
                interval=htf_interval,
                start_date=start_date,
                end_date=end_date
            )
            
            if isinstance(df, dict):
                print(f"❌ {symbol_name} Signal Logic: ERROR")
                print(f"   Response: {df}")
            elif hasattr(df, '__len__') and len(df) >= 2:
                # Test signal logic
                current_open = df['open'].iloc[-1]
                current_close = df['close'].iloc[-1]
                prev_open = df['open'].iloc[-2]
                prev_close = df['close'].iloc[-2]
                
                long_signal = (prev_close <= prev_open) and (current_close > current_open)
                short_signal = (prev_close >= prev_open) and (current_close < current_open)
                
                print(f"✅ {symbol_name} Signal Logic: SUCCESS")
                print(f"   Previous: O=₹{prev_open} C=₹{prev_close}")
                print(f"   Current:  O=₹{current_open} C=₹{current_close}")
                print(f"   Long Signal: {long_signal}")
                print(f"   Short Signal: {short_signal}")
            else:
                print(f"❌ {symbol_name} Signal Logic: INSUFFICIENT DATA")
                
        except Exception as e:
            print(f"❌ {symbol_name} Signal Logic: ERROR")
            print(f"   Exception: {e}")

def test_position_sizing():
    """Test position sizing calculations"""
    print("\n" + "="*50)
    print("Testing Position Sizing...")
    print("="*50)
    
    test_prices = [1500, 3000, 4500, 1800, 1200]  # Sample prices
    
    for i, (symbol_name, _) in enumerate(symbols_config.items()):
        if i < len(test_prices):
            price = test_prices[i]
            quantity = int(position_size / price)
            actual_value = quantity * price
            
            print(f"✅ {symbol_name} Position Sizing:")
            print(f"   Target: ₹{position_size:,}")
            print(f"   Price: ₹{price}")
            print(f"   Quantity: {quantity} shares")
            print(f"   Actual Value: ₹{actual_value:,}")
            print(f"   Difference: ₹{actual_value - position_size:+,}")

def run_all_tests():
    """Run all tests"""
    print("HTF Crossover Intraday Stock Strategy - Setup Test")
    print("="*60)
    print("Configuration:")
    print(f"  Symbols: {list(symbols_config.keys())}")
    print(f"  HTF Interval: {htf_interval}")
    print(f"  Position Size: ₹{position_size:,} per stock")
    print(f"  Stop Loss: 0.5%")
    print("="*60)
    
    # Test 1: API Connection
    client = test_api_connection()
    if not client:
        print("\n❌ Setup test failed at API connection. Please check your API key and server.")
        return False
    
    # Test 2: Stock Quotes
    test_stock_quotes(client)
    
    # Test 3: Data Fetching
    test_data_fetch(client)
    
    # Test 4: Signal Logic
    test_signal_logic(client)
    
    # Test 5: Position Sizing
    test_position_sizing()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("✅ If all tests show SUCCESS, your setup is ready")
    print("❌ If any tests show ERROR/FAILED, please fix before running live strategy")
    print("\nNext Steps:")
    print("1. Review any failed tests and fix issues")
    print("2. Adjust position size if needed in htf_crossover_stocks.py")
    print("3. Add/remove stocks from symbols_config as desired")
    print("4. Run: python strategies/htf_crossover_stocks.py")
    print("\n⚠️  Important: Start with smaller position sizes for testing!")
    print("💡 Tip: Consider paper trading first to validate signals")

if __name__ == "__main__":
    run_all_tests() 