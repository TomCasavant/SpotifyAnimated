from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation

from src.spotify import get_playlist_data

def gen_plot(token, playlist_id, background_color, title, text_color, freq):
    ''' Creates an animated plot and returns an HTML5 video to be embedded in page'''
    df = get_playlist_data(token, playlist_id) # Get a dataframe full of playlist data

    fig, ax = plt.subplots(figsize=(18, 8)) # Create figure

    r = range(0, len(df)-1, freq)
    # Iterate over create_chart for each week between the beginning and end of the playlist
    animator = animation.FuncAnimation(fig, create_chart, frames=r, fargs=[ax, df, background_color, title, text_color])
    #animator.save("video.mp4")
    return animator.to_html5_video() # Create HTML5 video from animation

def to_color(id):
    ''' Converts a spotify ID into a color to be used in the graph '''
    new_id = ""
    for char in id:
        new_id += str(ord(char)) # Convert each character into a number
    id = int(new_id) # Convert the newly edited id into a integer
    color = "%06x" % (id % 0xFFFFFF) # Convert the id into a hex number
    return "#" + color # Return hex number with color format

def setup_labels(ax, song_num, title, text_color, comparison_date):
    ''' Creates all of the labels for the plot '''
    ax.text(1, 0.4, comparison_date.to_period("D"), transform=ax.transAxes, color=text_color, size=45, ha='right', weight=800) # Display date
    ax.text(1, 0.3, str(song_num) + " songs", transform=ax.transAxes, color=text_color, size=30, ha='right', weight=800)
    # Title and Subtitle
    ax.text(0, 1.05, '% Of Playlist', transform=ax.transAxes, size=11, color='gray')
    ax.text(0, 1.09, title,
            transform=ax.transAxes, size=24, weight=600, ha='left')

    # Display my name
    ax.text(1, 0, 'Tom Casavant - @MrPresidentTom', transform=ax.transAxes, ha='right',
            color='white', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))

def setup_axis(ax, color):
    ''' Setup the axis tick marks and color '''
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.2f}')) # Limit percentages to 2 decimal places
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=10)
    ax.set_yticks([]) # Disable the y tick marks
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-') # Setup grid lines
    ax.set_axisbelow(True)
    ax.set_facecolor(color) # Setup color of plot

    # Incremement the last xtick mark (Makes it easier to see percentage of largest value)
    locs, labels = plt.xticks()
    locs[-1] += 1
    ax.set_xticks(locs, labels)

    remove_frame(ax) # Remove the frame around the plot


def remove_frame(ax):
    ''' Disables the frame around the plot'''

    # Doesn't use plt.box(False) because that would disable the background color
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

def prepare_data(df, song_num):
    ''' Setup the necessary data for the plot '''
    dff = df.sort_values(by='date_added', ascending=True) # Only use values before given date, sort by count
    comparison_date = dff.iloc[song_num-1]['date_added']
    dff = dff[dff['date_added'] <= comparison_date].tail(song_num)
    dff = dff.drop_duplicates(subset='artist', keep='last') # Get rid of duplicate artists (saves the most recent one)
    dff = dff.sort_values(by=["count", "date_added"], ascending=True)
    #print(dff)
    dff['percentage'] = (dff['count'] / dff['count'].sum())*100 # Calculate the percentage of each count
    dff = dff.tail(10) # Take the top 15 values
    return dff, comparison_date

def setup_bars(ax, dff, text_color):
    ''' Create the bars and attach labels to each one '''
    ax.clear()
    ax.barh(dff['artist'], dff['percentage'], height=0.8, color=[to_color(x) for x in dff['id']]) # Colorize each bar with to_color(id)

    for i, (percentage, artist, count) in enumerate(zip(dff['percentage'], dff['artist'], dff['count'])):
        ax.text(percentage, i,     artist,           size=14, weight=600, ha='right', va='center', color=text_color) # The artist name
        ax.text(percentage, i,     f'{percentage:,.2f}% ({count})',  size=14, ha='left',  va='center', color=text_color) # The percentage and count of each artist

def create_chart(song_num, ax, df, background_color, title, text_color):
    ''' Handles creating the entire chart '''
    dff, comparison_date = prepare_data(df, song_num)
    setup_bars(ax, dff, text_color)
    setup_axis(ax, background_color)
    setup_labels(ax, song_num, title, text_color, comparison_date)
