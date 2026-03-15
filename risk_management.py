def calculate_position_size(account_balance, entry_price, stop_loss_price, max_risk_pct=0.02):
    turn: position_size_btc (How much crypto to actually buy)
    # 1. Calculate how many actual dollars we are willing to lose on this trade
    capital_at_risk = account_balance * max_risk_pct
    
    # 2. Calculate the distance from our entry to our stop loss
    # (Using absolute value in case we add shorting later)
    stop_loss_distance = abs(entry_price - stop_loss_price)
    
    # Safety check to avoid division by zero
    if stop_loss_distance == 0:
        return 0
        
    # 3. Calculate exact BTC position size
    position_size_btc = capital_at_risk / stop_loss_distance
    
    return round(position_size_btc, 5)

def calculate_trade_metrics(account_balance, entry_price, atr):
    """
    Returns the complete risk profile for a potential trade.
    """
    # Widen SL to 1.5x ATR to avoid whipsaws, TP to 3x ATR for 1:2 Risk/Reward
    stop_loss_price = entry_price - (1.5 * atr)
    take_profit_price = entry_price + (3.0 * atr)
    
    # Get exact position size for a $100 account
    size_btc = calculate_position_size(account_balance, entry_price, stop_loss_price)
    
    # Calculate the total USD value of the position we are taking
    notional_value_usd = size_btc * entry_price
    
    # Calculate required leverage (Delta Exchange handles this natively)
    required_leverage = notional_value_usd / account_balance if account_balance > 0 else 0
    
    return {
        "stop_loss": round(stop_loss_price, 2),
        "take_profit": round(take_profit_price, 2),
        "size_btc": size_btc,
        "notional_value": round(notional_value_usd, 2),
        "required_leverage": round(required_leverage, 2)
    }

# --- Quick Test ---
if __name__ == "__main__":
    print("Testing Risk Manager for $100 Account...")
    metrics = calculate_trade_metrics(account_balance=100, entry_price=65000, atr=300)
    print(f"Stop Loss: ${metrics['stop_loss']}")
    print(f"Take Profit: ${metrics['take_profit']}")
    print(f"Position Size to Buy: {metrics['size_btc']} BTC")
    print(f"Total Trade Value: ${metrics['notional_value']}")
    print(f"Leverage Needed: {metrics['required_leverage']}x")