import matplotlib.pyplot as plt
import numpy as np


def make_spider_plot(dataframe, ndvi_range, all_pct, temps, fig_path=None, show=False):
    disp_pct = [(int(x)) for x in np.add(np.multiply(all_pct, 100.0), -100)]
    xx = 1
    for index, row in dataframe.iterrows():
        fig = plt.figure(xx, figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twiny()
        ax3 = ax1.twiny()
        fig.subplots_adjust(bottom=0.2)
        ax2.plot(temps, row[0], 'black', label='Temperature (+/- 5 deg C)')
        ax1.plot(disp_pct, row[1], 'blue', label='Precipitation (+/- 50%)')
        ax1.plot(disp_pct, row[2], 'purple', label='Reference Evapotranspiration (+/- 50%)')
        ax1.plot(disp_pct, row[3], 'brown', label='Total Available Water (+/- 50%)')
        ax3.plot(ndvi_range, row[4], 'green', linestyle='-.', label='Normalized Density Vegetation\n'
                                                                    ' Index Conversion Factor (0.9 - 1.8)')
        ax1.plot(disp_pct, row[5], 'red', label='Soil Hydraulic Conductivity (+/- 50%)')
        ax1.set_xlabel(r"Parameter Change (%)", fontsize=16)
        ax1.set_ylabel(r"Total Recharge per Year (mm)", fontsize=16)

        ax2.set_xlabel(r"Temperature Change (C)", fontsize=16)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("axes", -0.15))
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        for sp in ax2.spines.itervalues():
            sp.set_visible(False)
        ax2.spines['bottom'].set_visible(True)

        ax3.set_xlabel(r"NDVI to Crop Coefficient Conversion Factor", fontsize=16)
        ax3.xaxis.set_ticks_position("top")
        ax3.xaxis.set_label_position("top")
        # ax3.spines["top"].set_position(("axes", 1.0))
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False)
        for sp in ax3.spines.itervalues():
            sp.set_visible(False)
        ax3.spines['top'].set_visible(True)
        plt.title('Variation of ETRM Pysical Parameters at {}'.format(index), y=1.08, fontsize=20)
        handle1, label1 = ax1.get_legend_handles_labels()
        handle2, label2 = ax2.get_legend_handles_labels()
        handle3, label3 = ax3.get_legend_handles_labels()
        handles, labels = handle1 + handle2 + handle3, label1 + label2 + label3
        ax1.legend(handles, labels, loc=0)
        if show:
            plt.show()
        if fig_path:
            plt.savefig('{}_spider'.format(index), fig_path, ext='jpg', dpi=500, close=True, verbose=True)
        plt.close(fig)
