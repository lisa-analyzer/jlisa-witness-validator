import os
import csv
import subprocess

results = {}

top_level = {
    "VALID_ASSERT": "SV-COMP26_valid-assert",
    "NO_RUNTIME": "SV-COMP26_no-runtime-exception",
}

env = os.environ.copy()
env['JAVA_HOME'] = '/usr/lib/jvm/java-26-openjdk'

cmd = [
    "./build/install/jlisa-witness-validator/bin/jlisa-witness-validator",
    "--witness", 
    "svcomp-26/results-verified/jbmc.2025-12-09_16-35-43.files/TOP_LEVEL/BENCHMARK/witness.graphml",
    "--benchmark-dir",
    "svcomp-26/benchmarks/java/", # jbmc-regression/CharSequenceBug
    "--extra-sources", 
    "svcomp-26/benchmarks/java/common"       , '--verbose' 
]

with open('svcomp-26/benchmark_tasks_1.csv') as f:
    reader = csv.reader(f) #, delimiter=' ', quotechar='|')

    for i, row in enumerate(reader):
        if i == 0:
            continue

        _, bench, _, tp, _ = row

        local = cmd.copy()


        if tp == 'valid-assert':
            local[2] = local[2].replace('TOP_LEVEL', top_level['VALID_ASSERT']) 
        elif tp == 'no-runtime-exception':
            continue
            local[2] = local[2].replace('TOP_LEVEL', top_level['NO_RUNTIME']) 

        local[2] = local[2].replace('BENCHMARK', bench.split('/')[1]) 
        local[4] = local[4] + bench.split('.')[0]
       
        out = subprocess.run(local, env=env, capture_output=True) 

        result = out.stdout.decode().strip()

        results[bench] = [result, out.stderr]

        if result == 'Witness Correct':
            print(0)
        else:
            print(1)
            print(bench)
            print(result)
            print(out.stderr)
            print()
        


with open('report.csv', 'w') as o:
    spamwriter = csv.writer(o)
    for r in results.items():
        spamwriter.writerow(r)
