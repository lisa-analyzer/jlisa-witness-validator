import os
import csv
import subprocess
import pandas as pd

benchmark_path = 'data/svcomp-26/benchmark_tasks_1.csv'

df = pd.read_csv(benchmark_path, index_col=False)

print(df)


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


tools = df['tool'].unique()

#print(df['category'].unique())
for t in tools:
    if t != 'jbmc':
        continue

    tool_mask = (df['tool'] == t)
    assert_mask = (df['properties'] == 'valid-assert')
    status_mask = (df['status'] == 'false')
    category_mask = (df['category'] == 'correct')

    mask = tool_mask & assert_mask & status_mask & category_mask

    for r in df[mask].iterrows():
        index, bench = r

        break
    break

exit(0)

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


        if result == 'Witness Correct':
            print(0)
        else:
            results[bench] = [result, out.stderr]
            print(1)
            print(bench)
            print(result)
            print(out.stderr)
            print()
        

with open('report.csv', 'w') as o:
    spamwriter = csv.writer(o)
    for r in results.items():
        spamwriter.writerow(r)
