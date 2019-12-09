from perf import Perf
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from logger import create_logger

if __name__ == "__main__":
    logger = create_logger()
    cmd = "/home/prathyushpv/work/cpu2017/bin/runcpu --config=config1.cfg --threads 1 "
    benchmarks = ['607.cactuBSSN_s'
                  '619.lbm_s',
                  '621.wrf_s',
                  '627.cam4_s',
                  '628.pop2_s',
                  '638.imagick_s',
                  '644.nab_s',
                  '649.fotonik3d_s',
                  '654.roms_s']
    counters = ['LLC-load-misses',
                'LLC-store-misses',
                'instructions',
                'L1-dcache-loads',
                'L1-dcache-stores']
    for benchmark in benchmarks:
        p = Perf(counters, cmd + benchmark)
        result = p.run_continuous()
        size = min([len(counter_values) for counter_values in result.values()])
        y_mem = [(result["LLC-load-misses"][i] + result["LLC-store-misses"][i]) for i in range(size)]
        y_cpu = [(result["instructions"][i] - result["L1-dcache-loads"][i] - result["L1-dcache-stores"][i]) / 1000 for i
                 in range(size)]
        x = range(size)

        print(y_mem)
        print(y_cpu)
        fig = plt.figure()

        ax = fig.add_subplot(1, 1, 1, title="CPU Usage",
                             xlabel="Time", ylabel="Operations",)
        # def numfmt(x, pos):
        #     s = '{}'.format(x / 10**9)
        #     return s
        # yfmt = tkr.FuncFormatter(numfmt)
        # ax.yaxis.set_major_formatter(yfmt)

        ax.plot(x, y_mem, label="Memory Operations")
        ax.plot(x, y_cpu, label="kilo CPU Operations")
        ax.legend()

    plt.show()
