from dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
from my_program.monte_carlo_dynamic import travellers_modelisation
import math
import random as rdm

class OneLevelSearch:

    @staticmethod
    def search(graph_path, generate_branch):
        APSP = Dynamic_APSP(graph_path)
        metric = travellers_modelisation(PATH.TRAVEL, APSP.distance, 100)     #todo check if correct
        best = None
        minimum = math.inf
        branch = generate_branch()
        for b_modif in branch:
            APSP.save()
            metric.save()

            b_modif(APSP)
            metric.update(APSP.get_changes())

            value = metric.todo  # todo monte_Carlo_dynamic
            if value < minimum:
                best = b_modif
                minimum = value
            APSP.restore()
        return best, minimum

    @staticmethod
    def generate_branch_rdm():
        branch = []
        rdm.seed(12121214)

        def my_funct(APSP):
            i = 10
            is_new_name1 = rdm.randint(0, 3)
            if is_new_name1 == 0:
                name1 = str(i)
                i += 1
                time1 = rdm.randint(0, APSP.max_time - 1)
            else:
                name1 = rdm.sample(APSP.idx_to_name, 1).pop()
                is_new_time = rdm.randint(0, 3)
                if is_new_time == 0:
                    time1 = rdm.randint(0, APSP.max_time - 1)
                else:
                    time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()

            is_new_name2 = rdm.randint(0, 3)
            if is_new_name2 == 0:
                name2 = str(i)
                i += 1
                time2 = rdm.randint(time1, APSP.max_time - 1)
            else:
                name2 = rdm.sample(APSP.idx_to_name, 1).pop()
                is_new_time = rdm.randint(0, 3)
                if is_new_time == 0:
                    time2 = rdm.randint(time1, APSP.max_time - 1)
                else:
                    possible_time = []
                    for t in APSP.used_time[APSP.name_to_idx[name2]]:
                        if t >= time1:
                            possible_time.append(t)
                    if len(possible_time) > 0:
                        time2 = rdm.sample(possible_time, 1).pop()
                    else:
                        time2 = rdm.randint(time1, APSP.max_time - 1)
            print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))

        for _ in range(10):
            branch.append(my_funct)
            #branch.append(lambda APSP : APSP.add_edge(name1, time1, name2, time2))

            #APSP.add_edge(name1, time1, name2, time2)
        return branch

if __name__ == '__main__':
    graph_path = "Test/mini.json"
    OneLevelSearch.search(graph_path, OneLevelSearch.generate_branch_rdm)



class Search:
    #todo s'inspiree du cours de constraint programming
    # je me suis un peu inspiree du cours de constraint programming

    #def search(self, APSP, branching_genrator, limit = None):
    pass