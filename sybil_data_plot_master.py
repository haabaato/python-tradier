# sybil_data_plot_master.py
# Script Created by Teddy Rowan for MySybil.com
# Last Modified: March 10, 2020
# Description: This script handles all the plotting for driver_sybil_data.py

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime
import time

tickfont = {'fontname':'Futura', 'fontsize':8}
titlefont = {'fontname':'Futura', 'fontsize':11}

# Should we plot /timesales/ or /history/
def plot_data(data, should_use_history_endpoint, data_title, settings):
    if (should_use_history_endpoint):
        plot_history(data, data_title, settings)
    else:
        plot_timesales(data, data_title, settings)
    return 0

# Shared default plot settings between /history/ and /timesales/ plots.
def default_plot_settings(settings):
    plt.rcParams['figure.figsize'] = (7.9, 4.6)
    if (settings['darkMode']):
        plt.rcParams['savefig.facecolor']=(0.04, 0.04, 0.04)
    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))
    if (settings['darkMode']):
        ax1.set_facecolor((0.04, 0.04, 0.04))
        fig.set_facecolor((0.04, 0.04, 0.04))
        ax1.tick_params(colors='white')
        ax1.yaxis.label.set_color('white')

    ax1.grid(False)
    plt.subplots_adjust(left=0.10, bottom=0.20, right=0.95, top=0.90, wspace=0.2, hspace=0)
    labelfont = {'fontname':'Futura', 'fontsize':10}
    plt.ylabel("Option Price ($)", **labelfont)    

    if (settings['grid']):
        ax1.minorticks_on()
        if (settings['darkMode']):
            ax1.grid(which='major', color='#ffffff', linestyle='--', linewidth=0.75, alpha=0.35)
        else:
            ax1.grid(which='major', color='#000000', linestyle='--', linewidth=0.75, alpha=0.35)
        ax1.grid(b=True, which='minor', color='#999999', linestyle='--', linewidth=0.5, alpha=0.15)    
    
    if (settings['watermark']):
        textstr = settings['branding']
        props = dict(boxstyle='square', facecolor='none', alpha=0, edgecolor='none')
        brandColor = 'black'
        if (settings['darkMode']):
            brandColor = 'white'
        ax1.text(0.87, 0.06, textstr, transform=ax1.transAxes, verticalalignment='top', bbox=props, **labelfont, color=brandColor)
    
    return plt, fig, ax1

# Take in the formatted data and settings, and plot the corresponding chart.
def plot_history(data, data_title, settings):
    ohlc = [] # list of candlestick chart data
    t1 = 0 # first timestamp in the data
    
    for quote in data:
        t_current = convert_string_to_date(quote['date'])
        if (t1 == 0): # set t1 equal to midnight on the day of the first data point.
            t1 = t_current - (t_current % 24*60*60)
                    
        t_current = convert_timestamp_to_binning(t_current, 24*60*60, t1)
        
        quote_data = t_current, quote['open'], quote['high'], quote['low'], quote['close'], quote['volume']       
        ohlc.append(quote_data)
    
    # If there is data, create a figure and plot it.
    if (len(ohlc)): #if there is any data
        plt, fig, ax1 = default_plot_settings(settings)
        
        candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#57b859', colordown='#db3f3f')
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        # these are assigned so that we can use them when we re-grab the axes when xlims change
        plt.t1 = t1
        plt.binning = 24*60*60

        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1), **tickfont)
        ax1.callbacks.connect('xlim_changed', on_xlims_change) #live update the xlabels
                
        title_obj = plt.title(data_title, **titlefont)
        if (settings['darkMode']):
            plt.setp(title_obj, color='white')
        
        plt.show()
    else:
        print("No option trades during period.")
    
    return

# Take in the formatted data and settings, and plot the corresponding time/sales chart.
def plot_timesales(data, data_title, settings):    
    ohlc = [] # candlestick chart data
    t1 = 0 #midnight timestamp for first day in data.
    t_current = 0;
    plt_binning = settings['binning'] #in minutes
    
    # Loop through all the data and set candles for each data point
    for quote in data:                        
        if (t1 == 0): # set t1 equal to midnight on the day of the first data point.
            t1 = quote['timestamp'] - (quote['timestamp'] % 24*60*60)
            
        t_current = convert_timestamp_to_binning(quote['timestamp'], plt_binning*60, t1)
        
        quote_data = t_current, quote['open'], quote['high'], quote['low'], quote['close'], quote['volume']
        ohlc.append(quote_data)
        
    # If there is data, create a figure and plot it.
    if (len(ohlc)): 
        plt, fig, ax1 = default_plot_settings(settings)
        
        candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#57b859', colordown='#db3f3f')
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.binning = plt_binning*60 #seconds to minutes * plt_binning
        plt.t1 = t1
                
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1), **tickfont)
        ax1.callbacks.connect('xlim_changed', on_xlims_change) #live update the xlabels

        title_obj = plt.title(data_title, **titlefont)
        if (settings['darkMode']):
            plt.setp(title_obj, color='white')        
        
        plt.show()
    else:
        print("No option trades during period.")
    return

# Whenever the x-axis changes, redo the xtick labels 
def on_xlims_change(axes):
    ax1 = plt.gca()
    ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1))

    
# Return the secondsSince1970 for a generic date string
def convert_string_to_date(datestr):
    datenum = datetime.strptime(datestr, "%Y-%m-%d")
    return time.mktime(datenum.timetuple())


####### Clean up everything below me.     

# this should at least put it to 1 per then just need to scale and shit or something
def convert_timestamp_to_binning(timestamp, binning, t0):
    tconvert = (timestamp-t0)/binning #binning from first data point being 0
    tdays = (int)(tconvert/(24*60*60/binning)) #how many days have passed.
    tadjust = tconvert - tdays*(17.5*60*60/binning - 1) #remove after hours binning
    # w/out -1 it was doubling up a data point on the day crossover. double negative. 

    # i need to handle daily binning different than binning when we need to deal with after-hours
    if (binning == 24*60*60):
        tadjust = tconvert
    
    return tadjust # ok perfect (well perfectly awful)
        
def convert_xticks_to_dates(xticks, binning, t0):
    output = []
    for x in xticks:
            date_str = datetime.fromtimestamp(convert_binning_to_timestamp(x, binning, t0))
            if (binning < 24*60*60):
                output.append(date_str.strftime("%m/%d, %H:%M"))
            else:
                output.append(date_str.strftime("%m/%d/%Y"))

    return output

# just need to do the opposite of convert_timestamp_to_binning    
def convert_binning_to_timestamp(bin_number, binning, t0):
    tdays = (int)((bin_number*binning)/(6.5*60*60 + binning)) # + binning b/c of the -1.
    tadjust = bin_number + tdays*(17.5*60*60/binning - 1) #restored to full bin since zero-point
    
    # i need to handle daily binning different than binning when we need to deal with after-hours
    if (binning == 24*60*60):
        tadjust = bin_number

    return (tadjust*binning + t0)
        
    