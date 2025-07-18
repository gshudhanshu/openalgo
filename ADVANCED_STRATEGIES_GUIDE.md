# Advanced Options & Multi-Symbol Strategies with OpenAlgo

Your OpenAlgo application has **enterprise-grade infrastructure** for sophisticated trading strategies! Here's what you can build with your existing system.

## 🏗️ **Your Current Capabilities**

### **Multi-Exchange Support**
- ✅ **NSE/NFO** - Equity & Index Options (NIFTY, BANKNIFTY, FINNIFTY)  
- ✅ **BSE/BFO** - BSE Options (SENSEX, BANKEX)
- ✅ **CDS/BCD** - Currency Options (USDINR, EURINR)
- ✅ **MCX** - Commodity Options (GOLD, SILVER, CRUDE)
- ✅ **Multi-broker** - 25+ brokers with different capability levels

### **Options Instrument Types** (Already Supported)
- **Index Options**: `NIFTY23DEC21000CE`, `BANKNIFTY24JAN44000PE`
- **Stock Options**: `RELIANCE24FEB2500CE`, `TCS24MAR3000PE`  
- **Currency Options**: `USDINR24JAN83CE`, `EURINR24FEB88PE`
- **Commodity Options**: `GOLD24FEB62000CE`, `SILVER24MAR74000PE`

### **Real-time Data Streaming**
- **WebSocket Support** - Live LTP, Quote, Market Depth (5-50 levels)
- **Rate Handling** - 10 orders/sec regular, 1 order/sec smart orders
- **Multi-symbol** - Unlimited symbol monitoring across exchanges

## 🚀 **Complex Strategy Examples**

### **1. Iron Condor Strategy (4-Leg Options)**

```python
#!/usr/bin/env python3
"""
Iron Condor Strategy - Automated 4-leg options strategy
"""

from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class IronCondorStrategy:
    """
    Iron Condor: Sell OTM Call + Put, Buy further OTM Call + Put
    Max profit when underlying stays between short strikes
    """
    
    def __init__(self, config: Dict):
        self.client = api(api_key=config['api_key'], host=config['host'])
        self.strategy_name = "Iron_Condor_NIFTY"
        
        # Strategy parameters
        self.underlying = config.get('underlying', 'NIFTY')
        self.lots = config.get('lots', 1)
        self.expiry_date = config.get('expiry_date', '24DEC')
        
        # Iron Condor parameters
        self.short_call_distance = config.get('short_call_distance', 200)  # Points from ATM
        self.short_put_distance = config.get('short_put_distance', 200)
        self.long_call_distance = config.get('long_call_distance', 300)
        self.long_put_distance = config.get('long_put_distance', 300)
        
        # Risk management
        self.max_loss = config.get('max_loss', 5000)
        self.target_profit = config.get('target_profit', 2000)
        self.dte_exit = config.get('dte_exit', 5)  # Days to expiry exit
        
        # Position tracking
        self.positions = {}
        self.entry_time = None
        self.total_premium = 0
        
    def get_atm_strike(self) -> int:
        """Get current ATM strike for the underlying"""
        try:
            response = self.client.get_quotes(
                symbol=self.underlying,
                exchange='NSE'
            )
            if response.get('status') == 'success':
                ltp = float(response['data']['ltp'])
                # Round to nearest 50 for NIFTY
                return int(round(ltp / 50) * 50)
        except Exception as e:
            print(f"Error getting ATM strike: {e}")
        return 21000  # Fallback
    
    def build_option_symbol(self, strike: int, option_type: str) -> str:
        """Build option symbol: NIFTY24DEC21000CE"""
        return f"{self.underlying}{self.expiry_date}{strike}{option_type}"
    
    def place_iron_condor(self) -> bool:
        """
        Place all 4 legs of Iron Condor simultaneously
        
        Legs:
        1. Sell Call (Short Call) - Collect premium
        2. Buy Call (Long Call) - Limit risk  
        3. Sell Put (Short Put) - Collect premium
        4. Buy Put (Long Put) - Limit risk
        """
        try:
            atm_strike = self.get_atm_strike()
            print(f"ATM Strike: {atm_strike}")
            
            # Calculate strikes for all 4 legs
            short_call_strike = atm_strike + self.short_call_distance
            long_call_strike = atm_strike + self.long_call_distance
            short_put_strike = atm_strike - self.short_put_distance
            long_put_strike = atm_strike - self.long_put_distance
            
            # Build option symbols
            short_call = self.build_option_symbol(short_call_strike, 'CE')
            long_call = self.build_option_symbol(long_call_strike, 'CE')
            short_put = self.build_option_symbol(short_put_strike, 'PE')
            long_put = self.build_option_symbol(long_put_strike, 'PE')
            
            # Iron Condor legs configuration
            legs = [
                {'symbol': short_call, 'action': 'SELL', 'type': 'short_call'},
                {'symbol': long_call, 'action': 'BUY', 'type': 'long_call'},
                {'symbol': short_put, 'action': 'SELL', 'type': 'short_put'}, 
                {'symbol': long_put, 'action': 'BUY', 'type': 'long_put'}
            ]
            
            print(f"Placing Iron Condor:")
            print(f"Short Call: SELL {short_call}")
            print(f"Long Call: BUY {long_call}")
            print(f"Short Put: SELL {short_put}")
            print(f"Long Put: BUY {long_put}")
            
            # Place all legs
            order_ids = []
            for leg in legs:
                try:
                    response = self.client.placeorder(
                        strategy=self.strategy_name,
                        symbol=leg['symbol'],
                        exchange='NFO',
                        action=leg['action'],
                        product='NRML',
                        price_type='MARKET',
                        quantity=25 * self.lots  # NIFTY lot size = 25
                    )
                    
                    if response.get('status') == 'success':
                        order_id = response['orderid']
                        order_ids.append(order_id)
                        self.positions[leg['type']] = {
                            'symbol': leg['symbol'],
                            'action': leg['action'],
                            'order_id': order_id,
                            'strike': leg['symbol'][-7:-2],
                            'option_type': leg['symbol'][-2:]
                        }
                        print(f"✅ {leg['type']}: Order {order_id}")
                        
                        # Wait 1 second between orders (rate limiting)
                        time.sleep(1)
                    else:
                        print(f"❌ Failed to place {leg['type']}: {response}")
                        return False
                        
                except Exception as e:
                    print(f"Error placing {leg['type']}: {e}")
                    return False
            
            self.entry_time = datetime.now()
            print(f"🎯 Iron Condor placed successfully! {len(order_ids)} orders")
            return True
            
        except Exception as e:
            print(f"Error placing Iron Condor: {e}")
            return False
    
    def monitor_positions(self) -> Dict:
        """Monitor all positions and calculate P&L"""
        try:
            response = self.client.positions()
            if response.get('status') == 'success':
                positions_data = response.get('data', [])
                
                total_pnl = 0
                position_summary = {}
                
                for pos in positions_data:
                    symbol = pos.get('symbol', '')
                    if self.underlying in symbol and self.expiry_date in symbol:
                        pnl = float(pos.get('pnl', 0))
                        total_pnl += pnl
                        
                        position_summary[symbol] = {
                            'quantity': pos.get('netqty', 0),
                            'avg_price': pos.get('avgprice', 0),
                            'ltp': pos.get('ltp', 0),
                            'pnl': pnl
                        }
                
                return {
                    'total_pnl': total_pnl,
                    'positions': position_summary,
                    'status': 'active' if position_summary else 'closed'
                }
                
        except Exception as e:
            print(f"Error monitoring positions: {e}")
        
        return {'total_pnl': 0, 'positions': {}, 'status': 'unknown'}
    
    def should_exit(self, monitor_data: Dict) -> Tuple[bool, str]:
        """Check if strategy should exit based on conditions"""
        total_pnl = monitor_data.get('total_pnl', 0)
        
        # Profit target hit
        if total_pnl >= self.target_profit:
            return True, f"Profit target hit: ₹{total_pnl}"
        
        # Max loss hit
        if total_pnl <= -self.max_loss:
            return True, f"Stop loss hit: ₹{total_pnl}"
        
        # Days to expiry check
        if self.entry_time:
            days_held = (datetime.now() - self.entry_time).days
            if days_held >= (30 - self.dte_exit):  # Assuming monthly expiry
                return True, f"DTE exit: {days_held} days held"
        
        return False, "Continue monitoring"
    
    def close_all_positions(self) -> bool:
        """Close all Iron Condor positions"""
        try:
            print("🔄 Closing all Iron Condor positions...")
            
            response = self.client.positions()
            if response.get('status') == 'success':
                positions_data = response.get('data', [])
                
                for pos in positions_data:
                    symbol = pos.get('symbol', '')
                    if self.underlying in symbol and self.expiry_date in symbol:
                        quantity = int(pos.get('netqty', 0))
                        if quantity != 0:
                            # Reverse the position
                            action = 'SELL' if quantity > 0 else 'BUY'
                            
                            close_response = self.client.placeorder(
                                strategy=self.strategy_name,
                                symbol=symbol,
                                exchange='NFO',
                                action=action,
                                product='NRML',
                                price_type='MARKET',
                                quantity=abs(quantity)
                            )
                            
                            if close_response.get('status') == 'success':
                                print(f"✅ Closed {symbol}: {action} {abs(quantity)}")
                            else:
                                print(f"❌ Failed to close {symbol}")
                            
                            time.sleep(1)  # Rate limiting
                
                return True
                
        except Exception as e:
            print(f"Error closing positions: {e}")
        
        return False
    
    def run_strategy(self):
        """Main strategy execution loop"""
        print("🚀 Starting Iron Condor Strategy")
        
        # Check market hours
        now = datetime.now()
        if now.hour < 9 or now.hour >= 15:
            print("❌ Market closed")
            return
        
        # Place Iron Condor
        if not self.place_iron_condor():
            print("❌ Failed to place Iron Condor")
            return
        
        print("⏰ Starting monitoring loop...")
        
        # Monitor positions
        while True:
            try:
                monitor_data = self.monitor_positions()
                
                if monitor_data['status'] == 'closed':
                    print("✅ All positions closed")
                    break
                
                total_pnl = monitor_data['total_pnl']
                print(f"💰 Current P&L: ₹{total_pnl:.2f}")
                
                # Check exit conditions
                should_exit, reason = self.should_exit(monitor_data)
                if should_exit:
                    print(f"🛑 Exit condition: {reason}")
                    self.close_all_positions()
                    break
                
                # Wait 30 seconds before next check
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Manual exit requested")
                self.close_all_positions()
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(10)


### **2. Multi-Symbol Momentum Strategy**

class MultiSymbolMomentumStrategy:
    """
    Monitor multiple symbols and trade based on momentum signals
    Supports stocks, futures, and options across exchanges
    """
    
    def __init__(self, config: Dict):
        self.client = api(api_key=config['api_key'], host=config['host'])
        self.strategy_name = "Multi_Symbol_Momentum"
        
        # Multi-symbol configuration
        self.watchlist = config.get('watchlist', [
            {'symbol': 'RELIANCE', 'exchange': 'NSE', 'quantity': 10},
            {'symbol': 'TCS', 'exchange': 'NSE', 'quantity': 5},
            {'symbol': 'NIFTY24DEC21000CE', 'exchange': 'NFO', 'quantity': 25},
            {'symbol': 'BANKNIFTY24DEC44000PE', 'exchange': 'NFO', 'quantity': 15},
            {'symbol': 'GOLD24FEBFUT', 'exchange': 'MCX', 'quantity': 1}
        ])
        
        # Momentum parameters
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.volume_threshold = config.get('volume_threshold', 1.5)  # 1.5x avg volume
        
        # Risk management
        self.max_positions = config.get('max_positions', 5)
        self.position_size_pct = config.get('position_size_pct', 0.2)  # 20% of capital per position
        
        # State tracking
        self.active_positions = {}
        self.signal_history = {}
    
    def calculate_momentum_signals(self, symbol: str, exchange: str) -> Dict:
        """Calculate momentum indicators for a symbol"""
        try:
            # Get historical data (last 50 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=50)
            
            response = self.client.history(
                symbol=symbol,
                exchange=exchange,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='D'
            )
            
            if response.get('status') == 'success':
                data = response.get('data', [])
                df = pd.DataFrame(data)
                
                if len(df) >= 20:  # Need minimum data for indicators
                    # Calculate RSI
                    df['rsi'] = self.calculate_rsi(df['close'], 14)
                    
                    # Calculate volume ratio
                    df['avg_volume'] = df['volume'].rolling(20).mean()
                    df['volume_ratio'] = df['volume'] / df['avg_volume']
                    
                    # Get latest values
                    latest = df.iloc[-1]
                    
                    return {
                        'rsi': latest['rsi'],
                        'volume_ratio': latest['volume_ratio'],
                        'close': latest['close'],
                        'signal': self.generate_signal(latest['rsi'], latest['volume_ratio'])
                    }
            
        except Exception as e:
            print(f"Error calculating signals for {symbol}: {e}")
        
        return {'rsi': 50, 'volume_ratio': 1, 'close': 0, 'signal': 'HOLD'}
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def generate_signal(self, rsi: float, volume_ratio: float) -> str:
        """Generate trading signal based on indicators"""
        # Strong buy signal: RSI oversold + high volume
        if rsi < self.rsi_oversold and volume_ratio > self.volume_threshold:
            return 'STRONG_BUY'
        
        # Buy signal: RSI oversold
        elif rsi < self.rsi_oversold:
            return 'BUY'
        
        # Strong sell signal: RSI overbought + high volume  
        elif rsi > self.rsi_overbought and volume_ratio > self.volume_threshold:
            return 'STRONG_SELL'
        
        # Sell signal: RSI overbought
        elif rsi > self.rsi_overbought:
            return 'SELL'
        
        return 'HOLD'
    
    def execute_signal(self, watchlist_item: Dict, signal_data: Dict):
        """Execute trading signal for a symbol"""
        symbol = watchlist_item['symbol']
        exchange = watchlist_item['exchange']
        quantity = watchlist_item['quantity']
        signal = signal_data['signal']
        
        try:
            # Check if we already have a position
            current_position = self.active_positions.get(symbol, {'quantity': 0})
            current_qty = current_position['quantity']
            
            # Check position limits
            if len(self.active_positions) >= self.max_positions and current_qty == 0:
                print(f"⚠️ Max positions reached, skipping {symbol}")
                return
            
            action = None
            target_qty = quantity
            
            # Determine action based on signal
            if signal in ['STRONG_BUY', 'BUY'] and current_qty <= 0:
                action = 'BUY'
                if current_qty < 0:  # Cover short first
                    target_qty = abs(current_qty) + quantity
            
            elif signal in ['STRONG_SELL', 'SELL'] and current_qty >= 0:
                action = 'SELL'
                if current_qty > 0:  # Sell long first
                    target_qty = current_qty + quantity
            
            if action:
                # Determine product type based on exchange
                product = 'NRML' if exchange in ['NFO', 'BFO', 'MCX', 'CDS'] else 'MIS'
                
                response = self.client.placeorder(
                    strategy=self.strategy_name,
                    symbol=symbol,
                    exchange=exchange,
                    action=action,
                    product=product,
                    price_type='MARKET',
                    quantity=target_qty
                )
                
                if response.get('status') == 'success':
                    order_id = response['orderid']
                    
                    # Update position tracking
                    new_qty = target_qty if action == 'BUY' else -target_qty
                    if current_qty != 0:
                        new_qty = current_qty + (target_qty if action == 'BUY' else -target_qty)
                    
                    self.active_positions[symbol] = {
                        'quantity': new_qty,
                        'exchange': exchange,
                        'signal': signal,
                        'entry_time': datetime.now(),
                        'order_id': order_id
                    }
                    
                    print(f"✅ {signal}: {action} {target_qty} {symbol} @ {exchange}")
                else:
                    print(f"❌ Failed to place order for {symbol}: {response}")
            
        except Exception as e:
            print(f"Error executing signal for {symbol}: {e}")
    
    def monitor_and_execute(self):
        """Monitor all symbols and execute signals"""
        print(f"📊 Monitoring {len(self.watchlist)} symbols...")
        
        for watchlist_item in self.watchlist:
            symbol = watchlist_item['symbol']
            exchange = watchlist_item['exchange']
            
            try:
                # Calculate signals
                signal_data = self.calculate_momentum_signals(symbol, exchange)
                
                print(f"{symbol}: RSI={signal_data['rsi']:.1f}, "
                      f"Vol={signal_data['volume_ratio']:.1f}x, "
                      f"Signal={signal_data['signal']}")
                
                # Store signal history
                self.signal_history[symbol] = signal_data
                
                # Execute signal if not HOLD
                if signal_data['signal'] != 'HOLD':
                    self.execute_signal(watchlist_item, signal_data)
                
                # Rate limiting between symbols
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
    
    def run_strategy(self):
        """Main strategy execution"""
        print("🚀 Starting Multi-Symbol Momentum Strategy")
        
        while True:
            try:
                # Check market hours
                now = datetime.now()
                if 9 <= now.hour < 15:  # Market hours
                    self.monitor_and_execute()
                    
                    # Show current positions
                    if self.active_positions:
                        print(f"\n💼 Active Positions: {len(self.active_positions)}")
                        for symbol, pos in self.active_positions.items():
                            print(f"  {symbol}: {pos['quantity']} ({pos['signal']})")
                    
                    # Wait 5 minutes before next scan
                    print("⏰ Waiting 5 minutes for next scan...\n")
                    time.sleep(300)
                else:
                    print("💤 Market closed, waiting...")
                    time.sleep(3600)  # Wait 1 hour
                
            except KeyboardInterrupt:
                print("\n🛑 Strategy stopped")
                break
            except Exception as e:
                print(f"Error in strategy loop: {e}")
                time.sleep(60)


### **3. Options Delta Neutral Strategy**

class DeltaNeutralStrategy:
    """
    Maintain delta-neutral portfolio using options
    Dynamically hedge using futures/options
    """
    
    def __init__(self, config: Dict):
        self.client = api(api_key=config['api_key'], host=config['host'])
        self.strategy_name = "Delta_Neutral_Portfolio"
        
        # Strategy configuration
        self.underlying = config.get('underlying', 'NIFTY')
        self.target_delta = config.get('target_delta', 0)  # Neutral
        self.delta_tolerance = config.get('delta_tolerance', 10)  # ±10 delta tolerance
        self.rebalance_frequency = config.get('rebalance_frequency', 300)  # 5 minutes
        
        # Position tracking
        self.portfolio = {}
        self.total_delta = 0
        self.last_rebalance = None
    
    def calculate_option_greeks(self, symbol: str, spot: float) -> Dict:
        """
        Calculate option Greeks (simplified Black-Scholes)
        In production, use proper Greeks calculation library
        """
        try:
            # Extract strike and option type from symbol
            # Example: NIFTY24DEC21000CE -> strike=21000, type=CE
            if symbol.endswith('CE') or symbol.endswith('PE'):
                option_type = symbol[-2:]
                strike = int(symbol[-7:-2])
                
                # Simplified delta calculation
                moneyness = spot / strike
                
                if option_type == 'CE':  # Call option
                    if moneyness > 1.05:
                        delta = 0.8  # Deep ITM
                    elif moneyness > 0.95:
                        delta = 0.5  # ATM
                    else:
                        delta = 0.2  # OTM
                else:  # Put option
                    if moneyness < 0.95:
                        delta = -0.8  # Deep ITM
                    elif moneyness < 1.05:
                        delta = -0.5  # ATM
                    else:
                        delta = -0.2  # OTM
                
                return {'delta': delta, 'strike': strike, 'type': option_type}
            
        except Exception as e:
            print(f"Error calculating Greeks for {symbol}: {e}")
        
        return {'delta': 0, 'strike': 0, 'type': 'UNKNOWN'}
    
    def get_portfolio_delta(self) -> float:
        """Calculate total portfolio delta"""
        try:
            response = self.client.positions()
            if response.get('status') == 'success':
                positions_data = response.get('data', [])
                
                # Get current spot price
                spot_response = self.client.get_quotes(symbol=self.underlying, exchange='NSE')
                spot = float(spot_response['data']['ltp']) if spot_response.get('status') == 'success' else 21000
                
                total_delta = 0
                self.portfolio = {}
                
                for pos in positions_data:
                    symbol = pos.get('symbol', '')
                    quantity = int(pos.get('netqty', 0))
                    
                    if quantity != 0 and self.underlying in symbol:
                        greeks = self.calculate_option_greeks(symbol, spot)
                        position_delta = quantity * greeks['delta']
                        total_delta += position_delta
                        
                        self.portfolio[symbol] = {
                            'quantity': quantity,
                            'delta': greeks['delta'],
                            'position_delta': position_delta,
                            'strike': greeks['strike'],
                            'type': greeks['type']
                        }
                
                self.total_delta = total_delta
                return total_delta
                
        except Exception as e:
            print(f"Error calculating portfolio delta: {e}")
        
        return 0
    
    def hedge_delta_imbalance(self, current_delta: float):
        """Hedge delta imbalance using futures or options"""
        delta_imbalance = current_delta - self.target_delta
        
        if abs(delta_imbalance) > self.delta_tolerance:
            print(f"🔄 Rebalancing: Current delta={current_delta:.1f}, Target={self.target_delta}")
            
            # Use futures for hedging (delta = 1 for long, -1 for short)
            futures_symbol = f"{self.underlying}24DECFUT"  # Current month futures
            
            # Calculate required futures quantity
            # If delta is too positive, sell futures (negative delta)
            # If delta is too negative, buy futures (positive delta)
            hedge_quantity = abs(int(delta_imbalance / 25))  # NIFTY lot size = 25
            
            if hedge_quantity > 0:
                action = 'SELL' if delta_imbalance > 0 else 'BUY'
                
                try:
                    response = self.client.placeorder(
                        strategy=self.strategy_name,
                        symbol=futures_symbol,
                        exchange='NFO',
                        action=action,
                        product='NRML',
                        price_type='MARKET',
                        quantity=hedge_quantity * 25
                    )
                    
                    if response.get('status') == 'success':
                        print(f"✅ Hedge: {action} {hedge_quantity} lots {futures_symbol}")
                        self.last_rebalance = datetime.now()
                    else:
                        print(f"❌ Hedge failed: {response}")
                        
                except Exception as e:
                    print(f"Error placing hedge order: {e}")
    
    def run_strategy(self):
        """Main delta neutral strategy loop"""
        print("🚀 Starting Delta Neutral Strategy")
        
        while True:
            try:
                # Calculate current portfolio delta
                current_delta = self.get_portfolio_delta()
                
                print(f"\n📊 Portfolio Status:")
                print(f"Total Delta: {current_delta:.1f}")
                print(f"Target Delta: {self.target_delta}")
                print(f"Delta Tolerance: ±{self.delta_tolerance}")
                
                # Show individual positions
                if self.portfolio:
                    print(f"\n💼 Positions ({len(self.portfolio)}):")
                    for symbol, pos in self.portfolio.items():
                        print(f"  {symbol}: {pos['quantity']} (Δ={pos['position_delta']:.1f})")
                
                # Check if rebalancing is needed
                should_rebalance = (
                    abs(current_delta - self.target_delta) > self.delta_tolerance and
                    (self.last_rebalance is None or 
                     (datetime.now() - self.last_rebalance).seconds > self.rebalance_frequency)
                )
                
                if should_rebalance:
                    self.hedge_delta_imbalance(current_delta)
                else:
                    print("✅ Portfolio within delta tolerance")
                
                # Wait before next check
                print(f"⏰ Next check in {self.rebalance_frequency} seconds...")
                time.sleep(self.rebalance_frequency)
                
            except KeyboardInterrupt:
                print("\n🛑 Strategy stopped")
                break
            except Exception as e:
                print(f"Error in delta neutral loop: {e}")
                time.sleep(60)


# Usage Examples
if __name__ == "__main__":
    
    # Configuration
    config = {
        'api_key': 'your-openalgo-api-key',
        'host': 'http://127.0.0.1:5000'
    }
    
    # Example 1: Iron Condor Strategy
    print("=== Iron Condor Strategy ===")
    iron_condor_config = {
        **config,
        'underlying': 'NIFTY',
        'lots': 1,
        'expiry_date': '24DEC',
        'short_call_distance': 200,
        'short_put_distance': 200,
        'long_call_distance': 300,
        'long_put_distance': 300,
        'max_loss': 5000,
        'target_profit': 2000
    }
    
    # iron_condor = IronCondorStrategy(iron_condor_config)
    # iron_condor.run_strategy()
    
    # Example 2: Multi-Symbol Momentum
    print("\n=== Multi-Symbol Momentum Strategy ===")
    momentum_config = {
        **config,
        'watchlist': [
            {'symbol': 'RELIANCE', 'exchange': 'NSE', 'quantity': 10},
            {'symbol': 'TCS', 'exchange': 'NSE', 'quantity': 5},
            {'symbol': 'NIFTY24DEC21000CE', 'exchange': 'NFO', 'quantity': 25},
            {'symbol': 'BANKNIFTY24DEC44000PE', 'exchange': 'NFO', 'quantity': 15}
        ],
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'max_positions': 5
    }
    
    # momentum = MultiSymbolMomentumStrategy(momentum_config)
    # momentum.run_strategy()
    
    # Example 3: Delta Neutral
    print("\n=== Delta Neutral Strategy ===")
    delta_neutral_config = {
        **config,
        'underlying': 'NIFTY',
        'target_delta': 0,
        'delta_tolerance': 10,
        'rebalance_frequency': 300
    }
    
    # delta_neutral = DeltaNeutralStrategy(delta_neutral_config)
    # delta_neutral.run_strategy()
    
    print("🎯 Choose and uncomment the strategy you want to run!") 