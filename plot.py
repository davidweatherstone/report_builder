import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib.dates import DateFormatter, MonthLocator
import matplotlib.dates as mdates

import pandas as pd


def create_fig(df, brand_colour = '#00205B', colours=None, output_folder=None, source=None, type=None, interval=None, width=8, legend_loc="top"):
    """
    Create and save a figure for each unique visual in the pandas DataFrame.

    Parameters:
    df (DataFrame): pandas DataFrame containing the data to plot. Must include the following columns:
        - Index (str): Name of index, e.g., commodity name, or location. Used as plot line(s).
        - Unique_Visual (str): Name of visual to display the Index against. Used as plot title.
        - Date (DateTime): Date of a value for a given index. X-Axis value.
        - Value (float): Value of the index for a given date. Y-Axis value.
        - OPTIONAL - Units (str): To be included in title, legend and file name.
        
    brand_colour (str): Hex code for the brand colour. Default is '#00205B'.
    colours (dict): Dictionary mapping indices to colours. Default is None.
    output_folder (str): Folder to save files to. File names default to the Unique_Visual name.
    source (str): Source link for the data. Default is None. Appears as footnote in the figure.
    interval (int): Interval for the x-axis date ticks. With default as None, every month is displayed.
    width (int): Width of the figure. Default is 8.

    Returns:
    None
    """
    
    # Default font and colours   
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = brand_colour
    plt.rcParams['axes.labelcolor'] = brand_colour
    plt.rcParams['xtick.color'] = brand_colour
    plt.rcParams['ytick.color'] = brand_colour
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)
    
    # Loop through the Unique Visuals in each DataFrame
    
    # Calculate the number of unique indexes
    index_length = len(df["Index"].unique())
    title = df["Visual"].iloc[0]
    
    # Define a unit, only if one exists
    unit = df["Units"].drop_duplicates().iloc[0] if "Units" in df.columns else None
    
    # Define the source, only if one exists
    if not source:
        source = df["Source Link"].drop_duplicates().iloc[0] if "Source Link" in df.columns else None
        
    # Create a single subplot for each unique visual
    fig, ax = plt.subplots(figsize=(width, 3))

    if type == None:
        # Create a DateFormatter object
        date_formatter = mdates.DateFormatter('%b-%y')
        
        # Collect all unique dates from the 'Date' column
        unique_dates = mdates.date2num(df['Date'].drop_duplicates())
            
        # Set the x-axis major locator based on the interval   
        if interval == None:
            ax.xaxis.set_major_locator(FixedLocator(unique_dates))
        else:
            ax.xaxis.set_major_locator(MonthLocator(interval=interval))

        ax.xaxis.set_major_formatter(date_formatter)
    
    # Set the y-axis major locator
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))

    # Plot each group of data (each index)
    for index, group in df.groupby('Index'):
        color = colours.get(index, 'black') if colours else None
        ax.plot(group['Date'], group['Value'], label=index, marker="o", markersize="4", color=color)
            
    # Customize the grid and ticks
    ax.grid(axis="y", linestyle="dotted", color='gray', linewidth=0.5)
    ax.tick_params(axis="both", labelsize=10, colors=brand_colour)
    ax.tick_params(axis="x", rotation=45)
    
    # Customize the spines    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(brand_colour)
    ax.spines['left'].set_color(brand_colour)
        
    # Add a title, legend and adjust the layout
    title = f"{title}, Unit: {unit}" if unit else title
    
    if legend_loc == "right":
        ax.set_title(title, fontsize=14)
        ax.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
            
        # Add the source details as a footnote
        if source:
            plt.figtext(0.02, 0, 
                    f"Data source: {source}",
                    fontsize=8, ha='left')
    else:
        if index_length <= 4:
            ax.set_title(title, fontsize=14)
            ax.legend(fontsize=10)
            plt.tight_layout()
            
            # Add the source details as a footnote
            if source:
                plt.figtext(0.02, 0, 
                        f"Data source: {source}",
                        fontsize=8, ha='left')
                
        elif index_length <= 6:
            plt.figtext(0.5, 1.18, 
                        title,
                        fontsize=14, ha="center")
            ax.legend(ncols=2, loc="upper center", bbox_to_anchor=(0.5, 1.34))
            
            # Add the source details as a footnote            
            if source:
                plt.figtext(0.085, -0.12, 
                        f"Data source: {source}",
                        fontsize=8, ha='left')
            
        elif index_length >= 7:
            plt.figtext(0.5, 1.18, 
                        title,
                        fontsize=14, ha="center")
            ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.34))
            
            # Add the source details as a footnote            
            if source:
                plt.figtext(0.085, -0.12, 
                        f"Data source: {source}",
                        fontsize=8, ha='left')

            
    return fig