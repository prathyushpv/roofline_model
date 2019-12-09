from perf import Perf
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from logger import create_logger

if __name__ == "__main__":
    logger = create_logger()
    cmd = "/home/prathyushpv/work/cpu2017/bin/runcpu --config=config1.cfg --nobuild --threads 1 --size train 628.pop2_s"
    p = Perf(['LLC-load-misses',
              'LLC-store-misses'], cmd)
    result = p.run_continuous()
    size = min(len(result["LLC-store-misses"]), len(result["LLC-load-misses"]))
    y = [(result["LLC-load-misses"][i] + result["LLC-store-misses"][i]) * 64 for i in range(size)]
    x = range(1, size + 1)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, title="Memory Bandwidth Usage",
                         xlabel="Time", ylabel="Bandwidth",)

    def numfmt(x, pos):
        s = '{}'.format(x / 10**9)
        return s

    yfmt = tkr.FuncFormatter(numfmt)
    ax.yaxis.set_major_formatter(yfmt)
    ax.plot(x, y)

    plt.show()
    print(result)
