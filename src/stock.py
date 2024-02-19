# main.py

from profile import get_real_time_data, get_multi_symbol_data

def get_lot_size():
    while True:
        try:
            lot_size = int(input("Enter lot size for trading (Example, 10): "))
            if lot_size <= 0:
                raise ValueError("Lot size must be a positive integer.")
            return lot_size
        except ValueError:
            print("Invalid input. Please enter a valid positive integer for lot size.")

if __name__ == "__main__":
    symbols_input = input("Enter stock symbol (e.g BBCA.JK) or multiple symbols separated by commas (e.g., BBCA.JK,BBRI.JK,XXXX.JK,ZZZZ.JK): ")
    symbols = [symbol.strip() for symbol in symbols_input.split(',')]

    if len(symbols) == 1:
        symbol = symbols[0]
        lot_size = get_lot_size()
        get_real_time_data(symbol, lot_size)
    elif len(symbols) > 1:
        lot_size_multi = get_lot_size()
        get_multi_symbol_data(symbols, lot_size_multi)
    else:
        print("No symbols entered. Exiting.")
