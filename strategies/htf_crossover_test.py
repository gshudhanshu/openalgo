"""
HTF Crossover Options Strategy - Test Script
Use this script to verify your setup before running the live strategy
"""

from openalgo import api
import pandas as pd
from datetime import datetime, timedelta, date

# Configuration (same as main strategy)
api_key = '9e660e71b2db4b839225acd6432352aa0bcc1e5a341a87f526d90dafee1eb72d'
htf_interval = "1h"

symbols_config = {
    "NIFTY": {
        "index_symbol": "NIFTY",
        "exchange": "NSE_INDEX", 
        "options_exchange": "NFO",
        "strike_step": 50,
        "lot_size": 75
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
        quote = client.quotes(symbol="NIFTY", exchange="NSE_INDEX")
        
        if quote.get("status") == "success":
            print("✅ API Connection: SUCCESS")
            print(f"   Current NIFTY: {quote['data']['ltp']}")
            return client
        else:
            print("❌ API Connection: FAILED")
            print(f"   Error: {quote}")
            return None
    except Exception as e:
        print("❌ API Connection: ERROR")
        print(f"   Exception: {e}")
        return None

def test_data_fetch(client):
    """Test historical data fetching"""
    print("\n" + "="*50)
    print("Testing Data Fetching...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            df = client.history(
                symbol=symbol_config["index_symbol"],
                exchange=symbol_config["exchange"],
                interval=htf_interval,
                start_date=start_date,
                end_date=end_date
            )
            
            # Check if df is a dictionary (error response) or DataFrame
            if isinstance(df, dict):
                print(f"❌ {symbol_name} Data: ERROR")
                print(f"   Response: {df}")
            elif hasattr(df, 'empty') and not df.empty and len(df) >= 2:
                print(f"✅ {symbol_name} Data: SUCCESS")
                print(f"   Records: {len(df)}")
                print(f"   Latest Close: {df['close'].iloc[-1]}")
                print(f"   Latest Open: {df['open'].iloc[-1]}")
            else:
                print(f"❌ {symbol_name} Data: INSUFFICIENT")
                print(f"   Type: {type(df)}")
                print(f"   Content: {df}")
                
        except Exception as e:
            print(f"❌ {symbol_name} Data: ERROR")
            print(f"   Exception: {e}")

def test_atm_calculation(client):
    """Test ATM strike calculation"""
    print("\n" + "="*50)
    print("Testing ATM Strike Calculation...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            quote = client.quotes(
                symbol=symbol_config["index_symbol"], 
                exchange=symbol_config["exchange"]
            )
            
            if quote.get("status") == "success":
                ltp = quote["data"]["ltp"]
                step = symbol_config["strike_step"]
                atm_strike = int(round(ltp / step) * step)
                
                print(f"✅ {symbol_name} ATM Calculation: SUCCESS")
                print(f"   Current Price: {ltp}")
                print(f"   ATM Strike: {atm_strike}")
                print(f"   Strike Step: {step}")
                print(f"   Spread Distance: 200 points")
                print(f"   Call Spread: {atm_strike}CE / {atm_strike + 200}CE")
                print(f"   Put Spread: {atm_strike}PE / {atm_strike - 200}PE")
            else:
                print(f"❌ {symbol_name} ATM Calculation: FAILED")
                print(f"   Quote Error: {quote}")
                
        except Exception as e:
            print(f"❌ {symbol_name} ATM Calculation: ERROR")
            print(f"   Exception: {e}")

def test_expiry_calculation():
    """Test expiry date calculation"""
    print("\n" + "="*50)
    print("Testing Expiry Calculation...")
    print("="*50)
    
    try:
        today = date.today()
        days_ahead = 3 - today.weekday()  # Thursday is weekday 3
        if days_ahead <= 0:
            days_ahead += 7
        
        expiry_date = today + timedelta(days_ahead)
        expiry_string = expiry_date.strftime("%d%b%y").upper()
        
        print("✅ Expiry Calculation: SUCCESS")
        print(f"   Today: {today}")
        print(f"   Next Thursday: {expiry_date}")
        print(f"   Expiry String: {expiry_string}")
        
    except Exception as e:
        print("❌ Expiry Calculation: ERROR")
        print(f"   Exception: {e}")

def test_signal_logic(client):
    """Test signal generation logic"""
    print("\n" + "="*50)
    print("Testing Signal Logic...")
    print("="*50)
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            df = client.history(
                symbol=symbol_config["index_symbol"],
                exchange=symbol_config["exchange"],
                interval=htf_interval,
                start_date=start_date,
                end_date=end_date
            )
            
            # Check if df is a dictionary (error response) or DataFrame
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
                print(f"   Previous: O={prev_open} C={prev_close}")
                print(f"   Current:  O={current_open} C={current_close}")
                print(f"   Long Signal: {long_signal}")
                print(f"   Short Signal: {short_signal}")
            else:
                print(f"❌ {symbol_name} Signal Logic: INSUFFICIENT DATA")
                print(f"   Data type: {type(df)}")
                print(f"   Data content: {df}")
                
        except Exception as e:
            print(f"❌ {symbol_name} Signal Logic: ERROR")
            print(f"   Exception: {e}")

def test_option_symbols(client):
    """Test option symbol formation and availability"""
    print("\n" + "="*50)
    print("Testing Option Symbols...")
    print("="*50)
    
    # Get expiry
    today = date.today()
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    expiry_date = today + timedelta(days_ahead)
    expiry = expiry_date.strftime("%d%b%y").upper()
    
    for symbol_name, symbol_config in symbols_config.items():
        try:
            # Get ATM strike
            quote = client.quotes(
                symbol=symbol_config["index_symbol"], 
                exchange=symbol_config["exchange"]
            )
            
            if quote.get("status") == "success":
                ltp = quote["data"]["ltp"]
                step = symbol_config["strike_step"]
                atm_strike = int(round(ltp / step) * step)
                
                # Test option symbols with 200 point spread
                ce_symbol = f"{symbol_name}{expiry}{atm_strike}CE"
                pe_symbol = f"{symbol_name}{expiry}{atm_strike}PE"
                ce_sell_symbol = f"{symbol_name}{expiry}{atm_strike + 200}CE"
                pe_sell_symbol = f"{symbol_name}{expiry}{atm_strike - 200}PE"
                
                print(f"✅ {symbol_name} Option Symbols: GENERATED")
                print(f"   Bull Call Spread:")
                print(f"     Buy: {ce_symbol}")
                print(f"     Sell: {ce_sell_symbol}")
                print(f"   Bear Put Spread:")
                print(f"     Buy: {pe_symbol}")
                print(f"     Sell: {pe_sell_symbol}")
                
                # Try to get quotes for these symbols (optional)
                try:
                    ce_quote = client.quotes(symbol=ce_symbol, exchange=symbol_config["options_exchange"])
                    if ce_quote.get("status") == "success":
                        print(f"   ATM CE Quote: ₹{ce_quote['data']['ltp']}")
                    else:
                        print(f"   ATM CE Quote: {ce_quote}")
                except Exception as e:
                    print(f"   ATM CE Quote: Error - {e}")
                    
            else:
                print(f"❌ {symbol_name} Option Symbols: FAILED")
                print(f"   Quote Error: {quote}")
                
        except Exception as e:
            print(f"❌ {symbol_name} Option Symbols: ERROR")
            print(f"   Exception: {e}")

def run_all_tests():
    """Run all tests"""
    print("HTF Crossover Options Strategy - Setup Test")
    print("="*60)
    print("Configuration:")
    print(f"  Symbols: {list(symbols_config.keys())}")
    print(f"  HTF Interval: {htf_interval}")
    print(f"  Spread Distance: 200 points")
    print(f"  NIFTY Lot Size: 75")
    print("="*60)
    
    # Test 1: API Connection
    client = test_api_connection()
    if not client:
        print("\n❌ Setup test failed at API connection. Please check your API key and server.")
        return False
    
    # Test 2: Data Fetching
    test_data_fetch(client)
    
    # Test 3: ATM Calculation
    test_atm_calculation(client)
    
    # Test 4: Expiry Calculation
    test_expiry_calculation()
    
    # Test 5: Signal Logic
    test_signal_logic(client)
    
    # Test 6: Option Symbols
    test_option_symbols(client)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("✅ If all tests show SUCCESS, your setup is ready")
    print("❌ If any tests show ERROR/FAILED, please fix before running live strategy")
    print("\nNext Steps:")
    print("1. Review any failed tests and fix issues")
    print("2. If tests pass, run: python htf_crossover_options.py")
    print("\n⚠️  Important: Start with small position sizes for testing!")

if __name__ == "__main__":
    run_all_tests() 