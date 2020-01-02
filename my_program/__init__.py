"""import random

def get_n_rdm_sector(n, sect_ids, all_sector_pop):
    sect_pop = [all_sector_pop[id] for id in sect_ids]
    tot_pop = sum(sect_pop)

    sect_cumul_pop = [sect_pop[0] / tot_pop]
    for i in range(1,len(sect_pop)):
        sect_cumul_pop.append(sect_pop[i] / tot_pop + sect_cumul_pop[i - 1])

    # select a sector depending of the number of person in ths sector
    for _ in range(n):
        rdm = random.random()
        # todo improve binary search
        i = 0
        while i < len(sect_cumul_pop) and rdm > sect_cumul_pop[i]:
            i += 1
        yield sect_ids[i]


n = 100

sect_ids = [c for c in range(0, 20)]
all_sector_pop = {}

i = 1
for id in sect_ids:
    all_sector_pop[id] = i*10
rdm_sectors = get_n_rdm_sector(n, sect_ids, all_sector_pop)

for id in rdm_sectors:
    print(id)"""
