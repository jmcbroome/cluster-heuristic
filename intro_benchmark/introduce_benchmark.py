import subprocess
import time
proportion_in = .25
tout = open("introduce_times.txt","w+")
print("\t".join(["SCount\tPerm\tPropIn\tTime"]),file=tout)
for s in [100,1000,10000,50000,100000,500000,1000000,2500000]:
    for p in range(1,5):
        #first, subset the public tree.
        subprocess.check_call(["matUtils","extract",'-i','public-2021-11-08.all.masked.pb','-z',str(s),'-o','public_subset_' + str(s) + '_' + str(p) + '.pb'])
        #call summary and store the results.
        subprocess.check_call(["matUtils","summary",'-i','public_subset_' + str(s) + '_' + str(p) + '.pb','>','public_subset_' + str(s) + '_' + str(p) + '.summary'])
        #then extract another set of samples from that tree to treat as in-region.
        subprocess.check_call(["matUtils","extract",'-i','public_subset_' + str(s) + '_' + str(p) + '.pb','-z',str(int(s*proportion_in)),'-u','public_subset_' + str(s) + '_' + str(p) + '_in.txt'])
        #then call introduce. Time it.
        start = time.time()
        subprocess.check_call(["matUtils","introduce",'-i','public_subset_' + str(s) + '_' + str(p) + '.pb','-s','public_subset_' + str(s) + '_' + str(p) + '_in.txt','-o','public_subset_' + str(s) + '_' + str(p) + '_intros.txt'])
        end = time.time()
        print("\t".join([str(v) for v in [s,p,str(int(s*proportion_in)),end-start]]),file=tout)
tout.close()