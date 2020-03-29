from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
from Program.metric.monte_carlo_dynamic import TravellersModelisation
import math
import random as rdm
from Program.path import PATH

class Search:

    @staticmethod
    def one_level_search(graph_path, branch_genration_function,  mmap=None, reducing_pop_factor = 100, initial_state = None):
        APSP = Dynamic_APSP(graph_path, mmap)

        metric = TravellersModelisation(PATH.TRAVEL, APSP.distance, reducing_pop_factor)     #todo check if correct
        print("initialisation done")
        best = None
        minimum = math.inf
        branch = branch_genration_function(APSP, metric, initial_state)
        for b_modif in branch:
            APSP.save()
            metric.save()

            b_modif(APSP)
            metric.update(APSP.get_changes())

            value = metric.total_results.mean()
            if value < minimum:
                best = b_modif
                minimum = value
            APSP.restore()
        return best, minimum

    @staticmethod
    def multi_level_search(graph_path, branch_genration_function, mmap=None, reducing_pop_factor = 100, initial_state = None, max_dept = None,metric_on_leaf= False):
        """

        Note : L'evaluation de la metric ne sera calculee qu'aux feuille.
                                La valeur optimal ne sera donc elle aussi calculée qu'au feuilles

        :param graph_path:
        :param branch_generation_function:
            Fonction(APSP, metric, initial_state) ->  [ f_1(APSP), ...] ou f_i sont de fonctions modifiant le reseau
                                                                            et renvoyant un nouvel etat
        :param mmap: carte contenant les stopn
        :param reducing_pop_factor: lors du calcul de la metric, le nbre habitant virtuel =nbre habitant/reducing factor
        :param initial_state: Etat (structure au choix) qui sera transfere a branch_generation_function.
                              %Peut être None, si la branch_generation_function n'utilise pas d'etat
        :param max_dept: Profondeur maximal pour la recherche
        :return: (best_modif, minimum value)
                ou best _modif est une liste des fonction a appliquer pour reobtenir la solution optimal et
                minimu_value est la valeur optimale
        """
        def recursive_search(APSP, metric,branch_generation_function, state=None, max_dept=None, curr_dept=0):
            if curr_dept < max_dept:
                branch = branch_genration_function(APSP, metric, state)
            else:
                branch = []

            if len(branch) == 0 :
                metric.update(APSP.get_changes())
                value = metric.total_results.mean()
                return [], value
            else:
                best_modif = []
                minimum_value = math.inf
                for br_modif in branch:
                    APSP.save()
                    metric.save()

                    new_state = br_modif(APSP, metric)

                    modif, value = recursive_search(branch_generation_function, new_state, max_dept, curr_dept + 1)
                    if value < minimum_value:
                        best_modif= modif.append(br_modif)
                        minimum_value = value

                    APSP.restore()
                return best_modif, minimum_value

        APSP = Dynamic_APSP(graph_path, mmap)
        metric = TravellersModelisation(PATH.TRAVEL, APSP.distance, reducing_pop_factor)
        best_modif, minimum_value =recursive_search(APSP,metric, branch_genration_function, initial_state,max_dept, 0)
        return best_modif.reverse(), minimum_value


class BranchGeneration:

    @staticmethod
    def generate_random_edge(APSP, metric, state):
        """
        :param APSP:
        :param metric:
        :param state: (min_lat, max_lat, min_lon, max_lon)
        :return:
        """
        (min_lat, max_lat, min_lon, max_lon) = state
        is_new_name1 = rdm.randint(0, 3)
        if is_new_name1 == 0:
            name1 = str(rdm.random())  # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
            time1 = rdm.randint(0, APSP.max_time - 1)
            pos1 = (rdm.random() * (max_lat - min_lat) + min_lat, rdm.random() * (max_lon - min_lon) + min_lon)
        else:
            name1 = rdm.sample(APSP.idx_to_name, 1).pop()
            pos1 = None
            is_new_time = rdm.randint(0, 3)
            if is_new_time == 0 or len(APSP.used_time[APSP.name_to_idx[name1]]) == 0:
                time1 = rdm.randint(0, APSP.max_time - 1)
            else:
                time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()

        is_new_name2 = rdm.randint(0, 3)
        if is_new_name2 == 0:
            name2 = str(rdm.random())
            time2 = rdm.randint(time1, APSP.max_time - 1)
            pos2 = (rdm.random() * (max_lat - min_lat) + min_lat, rdm.random() * (max_lon - min_lon) + min_lon)
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
            pos2 = None
        # print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
        APSP.add_edge(name1, time1, name2, time2, u_position=pos1, v_position=pos2)

    @staticmethod
    def generate_branch_rdm(APSP, metric, state):
        branch = []
        rdm.seed(1212)

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

        for _ in range(100):
            branch.append(my_funct)
            #branch.append(lambda APSP : APSP.add_edge(name1, time1, name2, time2))

            #APSP.add_edge(name1, time1, name2, time2)
        return branch

if __name__ == '__main__':
    opti, val = Search.one_level_search(PATH.GRAPH_TC_WALK,BranchGeneration.generate_branch_rdm)
    print("best value = ", val)