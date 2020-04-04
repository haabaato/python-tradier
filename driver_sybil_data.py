# driver_sybil_data.py
# Created by: Teddy Rowan @ MySybil.com
# Last Modified: January 8, 2020
# Description: This script is designed as a free and open-source tool to help retail investors get and analyze historic options data.

import datetime

import sybil_data_grab
import sybil_data_plot_master
import sybil_data_ui_helper

# TODO: add setting for weekly/monthly binning on /history/ plots

def check_sentinel(input): # Check if the user wants to exit the program everytime they input anything
    if (input.lower() == "exit"): print("User Requested Program Termination."); exit()


# Settings can also be modified at runtime (non-persistent)
settings = {'shouldPrintData'   : False,
            'API_KEY'           : 'Bearer UNAGUmPNt1GPXWwWUxUGi4ekynpj', #public key
            'darkMode'          : True, 
            'watermark'         : False, 
            'branding'          : "MySybil.com",
            'grid'              : True,
            'historyLimit'      : 10,             #when we switch form /timesales to /history endpoint(days)
            'binning'           : 15}             #1/5/15 for time/sales. (time/sales < 35 days.)

sybil_data_ui_helper.intro_screen(); # just some printing / instructions to introduce the program

symbol = input("Type 'settings', enter a ticker, or enter entire option symbol (e.g. SPY 4/17 200.0 C): ").upper(); check_sentinel(symbol)
if (symbol == "SETTINGS"): # Does the user want to change the settings
    settings = sybil_data_grab.modify_settings(settings) #settings editting superloop
    symbol = input("Enter a symbol to proceed: ").upper(); check_sentinel(symbol) # prompt for symbol after settings optimized

date = None
selectedPrice = None
optionType = None

parts = symbol.split(' ')
if (len(parts) == 4):
    # User inputted entire symbol: <ticker> <date> <strike price> <call|put>
    symbol = parts[0]
    date = parts[1]
    selectedPrice = parts[2]
    optionType = parts[3].upper()

    # Determine date format
    if ('/' in date):
        date = date.replace('/', '-')
    elif ('-' in date):
        pass
    else:
        print('Date separator not found. Please use format like 4/20 or 2021-04-20. Terminating.'); exit()

    dateSeparator = '-'
    dateParts = date.split(dateSeparator)
    dateParts = ['{0:02d}'.format(int(part)) for part in dateParts] # zero-pad each date part

    # Determine year and then reorganize date such that year is in front
    year = None
    if (date.count(dateSeparator) == 1):
        print('No year entered, assuming current year...')
        year = str(datetime.datetime.today().year)
        dateParts.insert(0, year)
    else:
        year = next(filter(lambda x: len(x) == 4, parts))
        if (year is None):
            print('Could not determine year from input. Please enter 4 digits for the year.'); exit()
        dateParts.remove(year).insert(0, year)

    date = dateSeparator.join(dateParts)

    format_date = date.replace(dateSeparator, "").replace(year, '') # strip out the dashes from the selected date
    format_date = year[2:] + format_date

description = sybil_data_grab.background_info(symbol, settings['API_KEY']) # Display some info about the underlying
if (optionType is None):
    optionType = sybil_data_grab.option_type(symbol) # Does the user want to look at call options or put options

print("\nList of expiration dates:")
dateList = sybil_data_grab.get_expiry_dates(symbol, settings['API_KEY']) # Download a list of all the expiry dates available

if (date is None):
    # Prompt the user to pick one of the expiry dates
    date = input("Select an expiry date from the list above: "); check_sentinel(date)

    # Format the date string for Tradier's API formatting
    format_date = date.replace("-", "") # strip out the dashes from the selected date
    format_date = format_date[2:len(format_date)] # strip the 20 off the front of 2020

if (date not in dateList):
    print("The date: " + date + " is not valid. Terminating Program."); exit()
else:
    print('You selected date: ' + date + '\n')

strikeList = sybil_data_grab.get_strike_list(symbol, date, settings['API_KEY'])

if (selectedPrice is None):
    selectedPrice = input("Select a strike from the list above: "); check_sentinel(selectedPrice)
else:
    print('You selected strike: ' + str(float(selectedPrice)) + '\n')

if not (float(selectedPrice) in strikeList):
    print("No strike available for input price. Terminating Program."); exit()

selectedPrice = '{0:08d}'.format(int(float(selectedPrice)*1000)) #format the price string for Tradier

startDate, should_use_history_endpoint = sybil_data_grab.get_start_date(int(settings['historyLimit'])) #prompt user for date range
option_symbol = symbol + format_date + optionType + selectedPrice #full Tradier-formatted symbol for the option

print('\nOption symbol for Tradier: ' + option_symbol + '\n')

data_name = symbol + " $" + str(float(selectedPrice)/1000)  + " Put data expiring " + date
if (optionType == "C"):
    data_name = symbol + " $" + str(float(selectedPrice)/1000)  + " Call data expiring " + date
print("Now grabbing " + data_name)


# Download the trade data and plot it
trade_data = sybil_data_grab.get_trade_data(option_symbol, startDate, settings['binning'], should_use_history_endpoint, settings['API_KEY'])
sybil_data_plot_master.plot_data(trade_data, should_use_history_endpoint, data_name, settings)

if (settings['shouldPrintData']):
    print(trade_data)
    
print("Program Reached End Of Execution."); exit()
