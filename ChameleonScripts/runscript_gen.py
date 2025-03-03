import os

#TODO: make the script to copy over from spec build to bench_exe
#TODO: decide if I want to copy w the spec genereated name or the shorter names as seen here

bench = {
    "505.mcf_r": { #mine
        "cmd": "./mcf_r_base.init_test-m64",
        "input": "inp.in",
        "output": "inp.out",
        "err": "inp.err",
        "args": "",
    }
    "500.perlbench_r": { #below this are ai generated
        "cmd": "./perlbench_r_base.init_test-m64 -I. -I./lib",
        "input": "makerand.pl",
        "output": "makerand.out",
        "err": "makerand.err",
        "args": ""
    },
    "502.gcc_r": {
        "cmd": "./cpugcc_r_base.init_test-m64 -O3 -finline-limit=50000 -o t1.opts-O3_-finline-limit_50000.s",
        "input": "t1.c",
        "output": "t1.opts-O3_-finline-limit_50000.out",
        "err": "t1.opts-O3_-finline-limit_50000.err",
        "args": ""
    },
    "520.omnetpp_r": {
        "cmd": "./omnetpp_r_base.init_test-m64 -c -r 0",
        "input": "control",
        "output": "omnetpp.General-0.out",
        "err": "omnetpp.General-0.err",
        "args": ""
    },
    "523.xalancbmk_r": {
        "cmd": "./cpuxalan_r_base.init_test-m64 -v",
        "input": ["test.xml", "xalanc.xsl"],
        "output": "test-test.out",
        "err": "test-test.err",
        "args": ""
    },
    # "525.x264_r": {
    #     "cmd": "./x264 --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720",
    #     "input": "",
    #     "output": "run_000-156_x264.out",
    #     "err": "run_000-156_x264.err",
    #     "args": ""
    # },
    "531.deepsjeng_r": {
        "cmd": "./deepsjeng_r_base.init_test-m64",
        "input": ["test.txt"],
        "output": "test.out",
        "err": "test.err",
        "args": ""
    }
}

for key, value in bench.items():
    script_content = f"""#!/bin/bash
cd ~/bench_exe/{key}
{value['cmd']} {value['args']} {"test/input/" + inp for inp in value['input']} > test/output/{value['output']} 2>> test/{value['err']}
"""
    script_path = os.path.join(os.path.expanduser("~/bench_exe"), key, f"{key}.sh")
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    os.chmod(script_path, 0o755)

