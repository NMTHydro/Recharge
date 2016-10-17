import matplotlib.pyplot as plt
import numpy as np


def make_tornado_plot(dataframe, factors, show=False, fig_path=None):
    fig_path = 'C:\Users\David\Documents\ArcGIS\results\Sensitivity_analysis\\normalized'
    for index, row in dataframe.iterrows():
        print index, row
        base = row[0][5]
        lows = []
        for fact in row:
            lows.append(min(fact))
        lows = np.array(lows)
        values = []
        for fact in row:
            values.append(max(fact))

        # The y position for each variable
        ys = range(len(values))[::-1]  # top to bottom

        # Plot the bars, one by one
        for y, low, value in zip(ys, lows, values):
            # The width of the 'low' and 'high' pieces
            low_width = base - low
            high_width = value - base
            # Each bar is a "broken" horizontal bar chart
            plt.broken_barh(
                [(low, low_width), (base, high_width)],
                (y - 0.4, 0.8),
                facecolors=['white', 'white'],  # Try different colors if you like
                edgecolors=['black', 'black'],
                linewidth=1)
            plt.subplots_adjust(left=0.32)

            # Display the value as text. It should be positioned in the center of
            # the 'high' bar, except if there isn't any room there, then it should be
            # next to bar instead.
            x = base + high_width / 2
            if x <= base:
                x = base + high_width
            plt.text(x, y, str(round(value - low, 1)) + 'mm', va='center', ha='center')

        # Draw a vertical line down the middle
        plt.axvline(base, color='black')

        # Position the x-axis on the top, hide all the other spines (=axis lines)
        axes = plt.gca()  # (gca = get current axes)
        axes.spines['left'].set_visible(False)
        axes.spines['right'].set_visible(False)
        axes.spines['bottom'].set_visible(False)
        axes.xaxis.set_ticks_position('top')

        # Make the y-axis display the factors
        plt.yticks(ys, factors)
        plt.title('Calculated Recharge Ranges at {} (mm)'.format(index.replace('_', ' ')), y=1.05)
        # Set the portion of the x- and y-axes to show
        plt.xlim(min(-20, 1.2 * min(lows)), base + 1.1 * max(values))
        plt.ylim(-1, len(factors))
        # plt.show()
        if show:
            plt.show()
        if fig_path:
            plt.savefig('{}_spider'.format(index), fig_path, ext='jpg', dpi=500, close=True, verbose=True)
        plt.close()
