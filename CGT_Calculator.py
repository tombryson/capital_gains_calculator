from datetime import datetime
import csv

def parse_data(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    content = content.decode('utf-8-sig')  # Decode and remove BOM if present

    trades = [line.strip().split(',') for line in content.strip().split('\n')]
    stock_data = {}

    for trade in trades:
        date, _, _, stock, direction, units, price, currency, total, fee1, fee2, net_total, _, _, _, _, _, _ = trade
        units = abs(int(units))
        price = abs(float(price))
        net_total = abs(float(net_total))
        
        if stock not in stock_data:
            stock_data[stock] = []

        stock_data[stock].append((date, direction, units, price, net_total))
    
    return stock_data

def calculate_gains(stock_data):
    analyzed_stocks = set()
    total_gain = 0
    total_discount = 0

    for stock, transactions in stock_data.items():
        if stock not in analyzed_stocks:
            analyzed_stocks.add(stock)
            buy_list = []
            stock_gain = 0
            stock_discount = 0
            print(f"\nStock: {stock}")
            
            transactions_sorted = sorted(transactions, key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"))

            for transaction in transactions_sorted:
                date_str, direction, units, price, net_total = transaction
                date = datetime.strptime(date_str, "%d-%m-%Y")
                print(f"{date_str} - {direction} {units} units at {price}, for {net_total} total.")
                
                if direction == "BUY":
                    buy_list.append((date, units, price))
                else:  # SELL
                    sell_units = units
                    while sell_units > 0 and buy_list:
                        purchase_date, purchase_units, purchase_price = buy_list[0]
                        holding_period = (date - purchase_date).days
                        cg_per_share = price - purchase_price
                        shares_sold = min(sell_units, purchase_units)
                        gain = cg_per_share * shares_sold
                        discount = 0.5 * gain if holding_period > 365 else 0
                        stock_gain += gain
                        stock_discount += discount
                        total_gain += gain
                        total_discount += discount
                        print(f"  Sold {shares_sold} shares bought on {purchase_date.strftime('%d-%m-%Y')} after holding for {holding_period} days: gain {gain}, discount {discount}")

                        sell_units -= shares_sold
                        if shares_sold == purchase_units:
                            buy_list.pop(0)
                        else:
                            buy_list[0] = (purchase_date, purchase_units - shares_sold, purchase_price)
            
            print(f"Total gain for {stock}: {stock_gain}, Total discount for {stock}: {stock_discount}")
    print(f"\nOverall Total gain: {total_gain}, Overall Total discount: {total_discount}")

def main(file_path):
    stock_data = parse_data(file_path)
    calculate_gains(stock_data)

if __name__ == "__main__":
    file_path = './TradeHistory-BTPYQ-(01-06-2022)-(30-06-2024).csv'
    main(file_path)
