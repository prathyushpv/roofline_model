import matplotlib.pyplot as plt
import pylab
import numpy as np
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker

# https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting

class Roofline:
    def __init__(self, peak_flops, peak_bandwidth):
        self.peak_flops = peak_flops
        self.peak_bandwidth = peak_bandwidth

        # plt.plot([self.peak_flops/self.peak_bandwidth, 10],[self.peak_flops, self.peak_flops])
        # plt.ylabel('some numbers')

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale('log', basey=2)
        ax.set_xscale('log', basex=2)
        

        ax.axis([0.25, 16, 0.5, 128])
        for axis in [ax.xaxis, ax.yaxis]:
            formatter = ScalarFormatter()
            formatter.set_scientific(False)
            axis.set_major_formatter(formatter)


        ax.yaxis.grid()
        ax.plot([self.peak_flops/self.peak_bandwidth, 16],[self.peak_flops, self.peak_flops], color='red', lw=2)
        # TODO Memory line correction
        ax.plot([0, self.peak_flops/self.peak_bandwidth],[0, self.peak_flops], color='red', lw=2)

    def show(self):
        plt.show()
    


r = Roofline(17.6, 15)
r.show()