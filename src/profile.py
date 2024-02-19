
import yfinance as yf
import time
import requests
from colorama import Fore, Style, init

init()

def check_internet_connection():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def get_company_info(symbol):
    stock = yf.Ticker(symbol)
    company_profile = stock.info
    company_name = (company_profile.get('shortName', company_profile.get('longName', 'N/A')))[:25]
    country_of_origin = company_profile.get('country', 'N/A')
    currency = company_profile.get('currency', 'N/A')
    return company_name, country_of_origin, currency,symbol

def validate_symbol(symbol):
    # Add your own validation logic here
    return len(symbol) > 0

def validate_lot_size(lot_size):
    # Add your own validation logic here
    return lot_size > 0

def format_price(price):
    return '{:.10f}'.format(price)

def format_absolute_unit(absolute_value, unit, color):
    return f"{color}{unit} {absolute_value:.2f}{Style.RESET_ALL}"

def format_relative_unit(relative_value, unit, color):
    return f"{color}{unit} {relative_value:.2f}{Style.RESET_ALL}"

def format_percentage(value, color):
    return f"{color}{value:.2f} % {Style.RESET_ALL}"

def calculate_profit_loss(opening_price, current_price, lot_size):
    absolute_profit_loss = (current_price - opening_price) * lot_size
    relative_profit_loss = current_price - opening_price
    profit_ratio = (relative_profit_loss / opening_price) * 100 if opening_price != 0 else 0

    return absolute_profit_loss, relative_profit_loss, profit_ratio

def format_company_info(company_info):
    return f"{Fore.CYAN}Company Name: {company_info[0]} | Country of Origin: {company_info[1]} | Currency: {company_info[2]}{Style.RESET_ALL}"

def format_table_header(symbols):
    header = " | ".join(f"{symbol}".ljust(39) for symbol in symbols)
    return header

def format_table_row(data, colors):
    return " | ".join(f"{color}{value}".ljust(25) + Style.RESET_ALL for value, color in zip(data, colors))


def get_real_time_data(stock_symbol, lot_size, max_retries=3):
    while not check_internet_connection():
        print(f"{Fore.RED}Error: Internet connection failed. Retrying...{Style.RESET_ALL}")
        time.sleep(5)

    stock = yf.Ticker(stock_symbol)

    try:
        company_profile = stock.info
        company_name = company_profile.get('longName', 'N/A')
        country_of_origin = company_profile.get('country', 'N/A')
        currency = company_profile.get('currency', 'N/A')
        unit = currency
        print(f"{Fore.CYAN}Company Name: {company_name} | Country of Origin: {country_of_origin} | Currency: {currency}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Lot Size: {lot_size}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error fetching company profile: {e}{Style.RESET_ALL}")
        return

    opening_price_set = False
    opening_price = 0.0
    retries = 0

    while True:
        try:
            data = stock.history(period='1d', interval='1m')

            if data.empty:
                raise ValueError(f"{Fore.RED}Price data not available. Retrying...{Style.RESET_ALL}")

            latest_data = data.tail(1)

            if not opening_price_set:
                opening_price = latest_data['Open'].values[0]
                opening_price_set = True
                print(f"{Fore.YELLOW}First Opening Price: {format_price(opening_price)}{Style.RESET_ALL}")

            current_price = latest_data['Close'].values[0]

            absolute_profit_loss, relative_profit_loss, profit_ratio = calculate_profit_loss(opening_price, current_price, lot_size)

            color = Fore.GREEN if all(value >= 0 for value in (absolute_profit_loss, relative_profit_loss, profit_ratio)) else Fore.YELLOW

            print(f"{Fore.WHITE}Current Price: {format_price(current_price)}{Style.RESET_ALL} | Absolute Profit/Loss: {format_absolute_unit(absolute_profit_loss, unit, color)} | Relative Profit/Loss: {format_relative_unit(relative_profit_loss, unit, color)} | Profit Ratio: {format_percentage(profit_ratio, color)}")

            time.sleep(10)

        except Exception as e:
            print(f"{Fore.RED}Error fetching real-time data: {e}{Style.RESET_ALL}")

            retries += 1
            if retries > max_retries:
                print(f"{Fore.RED}Max retries reached. Exiting.{Style.RESET_ALL}")
                break

            print(f"{Fore.YELLOW}Retrying in 10 seconds (Retry {retries}/{max_retries})...{Style.RESET_ALL}")
            time.sleep(5)

def get_multi_symbol_data(symbols, lot_size):
    while not check_internet_connection():
        print(f"{Fore.RED}Error: Internet connection failed. Retrying...{Style.RESET_ALL}")
        time.sleep(5)

    stocks = [yf.Ticker(symbol) for symbol in symbols]

    try:
        company_info = [get_company_info(symbol) for symbol in symbols]
        company_names = [info[0] for info in company_info]
        countries_of_origin = [info[1] for info in company_info]
        currencies = [info[2] for info in company_info]
        units = currencies

        # Add the first opening price to the table header
        opening_prices = [None] * len(stocks)
        header_row = ["\nStock Data"]
        for i, stock in enumerate(stocks):
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                opening_price = data['Open'].values[-1]  # Get the last available opening price
                opening_prices[i] = f"{units[i]} {opening_price:.2f}" 
            else:
                header_row.append(f"{symbols[i]}\nN/A")


        print(format_table_header(header_row))
        print(format_table_header(company_names))
        print(format_table_header(countries_of_origin))
        print("\nOpened Value")
        print(format_table_header(opening_prices))
        print("")
        print("PROFIT %".ljust(14), end='')
        print("ABSOLUTE P/L".ljust(14),end='')
        print("CURNT PRICE".ljust(1))

    except Exception as e:
        print(f"{Fore.RED}Error fetching company profiles: {e}{Style.RESET_ALL}")
        return

    opening_prices_set = [False] * len(stocks)
    opening_prices = [0.0] * len(stocks)
    retries = 0

    while True:
        try:
            for i, stock in enumerate(stocks):
                data = stock.history(period='1d', interval='1m')

                if data.empty:
                    raise ValueError(f"{Fore.RED}{symbols[i]}: Price data not available. Retrying...{Style.RESET_ALL}")

                latest_data = data.tail(1)

                if not opening_prices_set[i]:
                    opening_prices[i] = latest_data['Open'].values[0]
                    opening_prices_set[i] = True

                current_price = latest_data['Close'].values[0]

                absolute_profit_loss, relative_profit_loss, profit_ratio = calculate_profit_loss(opening_prices[i], current_price, lot_size)

                colors = [Fore.GREEN if value >= 0 else Fore.RED for value in (profit_ratio, absolute_profit_loss, current_price)]
                data = [f"{format_percentage(profit_ratio, colors[0])}", f"{format_absolute_unit(absolute_profit_loss, units[i], colors[1])}", f"{format_absolute_unit(current_price, units[i], colors[1])}"]

                print(format_table_row(data, colors), end=' | ')

            print("")  # Move to the next line after printing data for all symbols

            time.sleep(10)

        except Exception as e:
            print(f"{Fore.RED}Error fetching real-time data: {e}{Style.RESET_ALL}")

            retries += 1
            if retries > 3:
                print(f"{Fore.RED}Max retries reached. Exiting.{Style.RESET_ALL}")
                break

            print(f"{Fore.YELLOW}Retrying in 10 seconds (Retry {retries}/3)...{Style.RESET_ALL}")
            time.sleep(5)
if __name__ == "__main__":
    pass  # You can leave this empty if you're using this module as a library
