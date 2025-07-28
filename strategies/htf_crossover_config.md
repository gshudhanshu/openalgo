# HTF Crossover Options Strategy - Configuration Guide

## Overview
This strategy converts the Pine Script "GetTrendStrategy with Accurate HTF and Stop Loss" to work with NIFTY and BANK NIFTY options using spreads.

## Strategy Logic
- **Higher Timeframe**: Uses 60-minute candles for trend detection
- **Long Signal**: When HTF close crosses above HTF open → Places Bull Call Spread
- **Short Signal**: When HTF close crosses below HTF open → Places Bear Put Spread
- **Stop Loss**: Percentage-based stop loss from entry price

## Options Spreads Used

### Bull Call Spread (Bullish Signal)
- **Buy**: ATM Call Option
- **Sell**: OTM Call Option (+100 points)
- **Maximum Profit**: Limited to spread width minus premium paid
- **Risk**: Limited to premium paid

### Bear Put Spread (Bearish Signal)  
- **Buy**: ATM Put Option
- **Sell**: OTM Put Option (-100 points)
- **Maximum Profit**: Limited to spread width minus premium paid
- **Risk**: Limited to premium paid

## Configuration Parameters

### Basic Settings
```python
# API Configuration
api_key = 'your-openalgo-api-key'  # Replace with your OpenAlgo API key

# Strategy Parameters
htf_interval = "60m"        # Higher timeframe (60 minutes)
stop_loss_perc = 1.5        # Stop loss percentage (1.5%)
spread_distance = 100       # Distance between strikes (100 points)
```

### Symbol Configuration
```python
symbols_config = {
    "NIFTY": {
        "index_symbol": "NIFTY",
        "exchange": "NSE_INDEX", 
        "options_exchange": "NFO",
        "strike_step": 50,      # NIFTY strike step
        "lot_size": 50          # NIFTY lot size
    },
    "BANKNIFTY": {
        "index_symbol": "BANKNIFTY", 
        "exchange": "NSE_INDEX",
        "options_exchange": "NFO", 
        "strike_step": 100,     # BANK NIFTY strike step
        "lot_size": 15          # BANK NIFTY lot size
    }
}
```

## Customization Options

### 1. Change Higher Timeframe
```python
htf_interval = "30m"  # For 30-minute timeframe
htf_interval = "1h"   # For 1-hour timeframe
htf_interval = "4h"   # For 4-hour timeframe
```

### 2. Adjust Stop Loss
```python
stop_loss_perc = 2.0   # For 2% stop loss
stop_loss_perc = 1.0   # For 1% stop loss
```

### 3. Modify Spread Distance
```python
spread_distance = 50   # Tighter spreads (less premium, less profit)
spread_distance = 150  # Wider spreads (more premium, more profit)
```

### 4. Add More Symbols
```python
symbols_config["SENSEX"] = {
    "index_symbol": "SENSEX",
    "exchange": "BSE_INDEX",
    "options_exchange": "BFO",
    "strike_step": 100,
    "lot_size": 10
}
```

### 5. Change Lot Sizes
```python
# For smaller position sizes
"lot_size": 25  # Half lot for NIFTY
"lot_size": 8   # Half lot for BANK NIFTY

# For larger position sizes  
"lot_size": 100 # Double lot for NIFTY
"lot_size": 30  # Double lot for BANK NIFTY
```

## Setup Instructions

### 1. Prerequisites
- OpenAlgo server running
- Valid API key from OpenAlgo portal
- Broker account with options trading enabled
- Python environment with required packages

### 2. Installation
```bash
# Install required packages (if not already installed)
pip install pandas numpy openalgo
```

### 3. Configuration
1. Replace `'your-openalgo-api-key'` with your actual API key
2. Ensure OpenAlgo server is running on `http://127.0.0.1:5000`
3. Verify broker connection in OpenAlgo
4. Check that options symbols are available

### 4. Running the Strategy
```bash
python htf_crossover_options.py
```

## Risk Management Features

### 1. Position Tracking
- Only one position per symbol at a time
- Automatic position tracking and management
- Entry price and stop loss monitoring

### 2. Stop Loss
- Percentage-based stop loss from entry price
- Automatic position closure on stop loss hit
- Separate stop loss logic for bull and bear spreads

### 3. Error Handling
- Connection error recovery
- Data validation
- Order placement error handling

## Important Notes

### 1. Expiry Management
- Strategy automatically uses current week's Thursday expiry
- Manually adjust `get_current_expiry()` for specific expiries
- Consider weekly vs monthly expiries based on strategy needs

### 2. Market Hours
- Strategy runs during market hours
- Consider adding market hour checks
- Handle pre-market and after-market scenarios

### 3. Liquidity Considerations
- Ensure sufficient liquidity in selected strikes
- Monitor bid-ask spreads before placing orders
- Consider using limit orders instead of market orders for better fills

### 4. Capital Requirements
- Each spread requires margin for short leg
- Calculate total margin requirements before running
- Consider position sizing based on account size

## Monitoring and Alerts

### Strategy Output
The strategy provides detailed logging:
- Signal detection
- Order placement confirmations  
- Position status updates
- Stop loss triggers
- Error messages

### Key Metrics to Monitor
- Win rate of signals
- Average profit/loss per trade
- Maximum drawdown
- Time in position
- Slippage on entries/exits

## Troubleshooting

### Common Issues
1. **API Key Error**: Verify API key is correct and active
2. **Symbol Not Found**: Check option symbol format and availability
3. **Insufficient Margin**: Ensure adequate account balance
4. **Network Issues**: Verify OpenAlgo server connectivity

### Testing Recommendations
1. Start with paper trading or small position sizes
2. Monitor for at least a week before full deployment
3. Backtest the logic on historical data
4. Verify signal accuracy during different market conditions

## Disclaimer
This strategy is for educational purposes. Always:
- Understand the risks involved
- Test thoroughly before live trading
- Consider market conditions and volatility
- Consult with financial advisors if needed
- Use appropriate position sizing 