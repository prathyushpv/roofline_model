from roofline import Roofline
from logger import create_logger

logger = create_logger()
r = Roofline(64, 15)

benchmarks = ['607.cactuBSSN_s', 
            '619.lbm_s', 
            '621.wrf_s', 
            '627.cam4_s', 
            '628.pop2_s', 
            '638.imagick_s', 
            '644.nab_s', 
            '649.fotonik3d_s', 
            '654.roms_s']
for benchmark in benchmarks:
    r.add_prereq("/home/ppv/cpu2017/bin/runcpu --config=config1.cfg --action=build %s" % benchmark)
    r.add_command("/home/ppv/cpu2017/bin/runcpu --config=config1.cfg --nobuild --threads 1 %s" % benchmark, benchmark)

    r.run()
    r.dump_data()

