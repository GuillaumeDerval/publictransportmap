#Monte carlo

################################## Pick a rdm travel ##################################################


# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

# dynamic :
# 0) mettre ajours les structure : class stop_munty
# 1) trouver la liste des pt(resid/work) potentiellement affecte
#           => avoir une liste de pt utilise
#           => permettre une recherche efficace parmis ces points
# 2) mettre ajour les temps de parcours


# reversible 2 choix:
# sauvegarder l'etat antérieur ou
# chaque action a sont inverse (=> supppression d'un aret , augmentationn de la duree d'un trajet)


# function of cumulative distribution =  function of repartition
import random
import math


from shapely.geometry import Point

from Program.distance_and_conversion import *
from Program.Data_manager.path_data import PATH
from Program.Data_manager.main import Parameters

#MAX_WALKING_TIME = 60 # in min
#SPEED = WALKING_SPEED /0.06 #in m/min
#SPEED = 1000/20
#WALKING_SPEED = WALKING_SPEED/0.06
#mapmap = my_map.get_map(path_shape=PATH.MAP_SHAPE, path_pop=PATH.MAP_POP)


# ################################# Monte Carlo #########################################################
class TravellersModelisation:

    def __init__(self,param:Parameters, distance_oracle, reducing_factor: int, travel_path: str = PATH.TRAVEL,
                 mapmap=None, my_seed = None):

        assert reducing_factor > 0
        if mapmap is None:
            from Program.General.map import my_map
            mapmap = my_map.get_map(param, path_shape=PATH.MAP_SHAPE, path_pop=PATH.MAP_POP,
                                    stop_list_path=PATH.STOP_POSITION_LAMBERT)

        if my_seed is not None:
            random.seed(my_seed)

        self.map = mapmap
        self.speed = param.WALKING_SPEED()
        self.max_walk_time = param.MAX_WALKING_TIME()
        # virtual traveller generation
        self.reducing_factor = reducing_factor
        # travel_loc :  dico {(munty_rsd, munty_work): [(pt_rsd, pt_work,(best_rsd_stop, best_work_stop), best_TC),...]}
        self.traveller_locations = {}
        self.__generate_virtual_travellers(travel_path)

        # access to distance
        self.distance = distance_oracle

        # min/max_time bound
        self.__min_max_time = {}  # store min and max time for each couple of munty orgin -> munty dest

        # computation
        self.all_results = {}           # contains result for each munty
        self.total_results = Result()   # Result for the country
        self.__estimate_travel_time()

        # reversible structure
        self.__change_log = {"all_results_save": {}, "travellers": {}}
        self.__stack_log = []  # permet de faire une recherche sur plusieur etage

    # ##################################### Virtual traveller generation ###############################################
    def __generate_virtual_travellers(self, travel_path):
        map = self.map
        def get_n_rdm_point(n, munty):
            """pick a rdm point in the shape, the probability of select a point depend on the number of people in the sector"""

            def rdm_point_shape(shape):
                """pick uniformaly at rdm a point in the shape"""
                assert shape.area > 0

                minx, miny, maxx, maxy = shape.bounds
                x = random.randint(math.ceil(minx), math.floor(maxx))
                y = random.randint(math.ceil(miny), math.floor(maxy))
                p = (x, y)  # Point(x, y)
                if shape.contains(Point(x, y)):
                    return p
                else:
                    return rdm_point_shape(shape)

            def get_n_rdm_sector(n, sect_ids):
                sect_pop = [int(map.get_pop_sector(id)) for id in sect_ids]
                tot_pop = map.get_pop_refnis(munty)

                sect_cumul_pop = [sect_pop[0] / tot_pop]
                for i in range(1, len(sect_pop)):
                    sect_cumul_pop.append(sect_pop[i] / tot_pop + sect_cumul_pop[i - 1])

                # select a sector depending of the number of person in this sector
                for _ in range(n):
                    rdm = random.random()

                    def bin_search_le(arr, value):
                        # return the max index i such that l[i] <= value
                        l = 0
                        r = len(arr) - 1
                        mid = 0
                        while l <= r:

                            mid = l + (r - l) // 2

                            # Check if x is present at mid
                            if arr[mid] == value:
                                return mid

                                # If x is greater, ignore left half
                            elif arr[mid] < value:
                                l = mid + 1

                            # If x is smaller, ignore right half
                            else:
                                r = mid - 1

                        if arr[mid] < value: return mid + 1
                        return mid

                    i = bin_search_le(sect_cumul_pop, rdm)
                    yield sect_ids[i]

            sect_ids = map.get_sector_ids(munty)
            rdm_sectors = get_n_rdm_sector(n, sect_ids)

            out = []
            for id in rdm_sectors:
                shape = map.get_shape_sector(id)
                out.append(rdm_point_shape(shape))
            return out

        def __iter_by_pop(pop, reducing_factor):
            iteration = pop // reducing_factor
            # avoid bias
            remaining = (pop % reducing_factor) / reducing_factor
            if random.random() < remaining:
                iteration += 1
            return iteration

        with open(travel_path) as file :
            travel = json.load(file)["travel"]
        assert len(travel) > 0
        travel.sort(key=(lambda x: x["residence"][1]))

        for trav in travel:
            rsd_munty = str(trav["residence"][1])
            work_munty = str(trav["work"][1])
            n = int(trav["n"])

            iters = __iter_by_pop(n, self.reducing_factor)
            #print("travellers generation: ", trav, "iteration :", iters)
            resid_list = get_n_rdm_point(iters, rsd_munty)
            work_list = get_n_rdm_point(iters, work_munty)
            self.traveller_locations[(rsd_munty, work_munty)] = list(zip(resid_list, work_list))



    # ###################################### Min/Max Time   ############################################################
    # Effectuer de manière parresseuse vu que plein de paire de commune ne seront potentiellement pas consideree

    def get_min_time(self, munty_org, munty_dest):
        if munty_org not in self.__min_max_time or munty_dest not in self.__min_max_time[munty_org]:
            self.__compute_min_max_time(munty_org, munty_dest)  # trigger min/max time computation

        return self.__min_max_time[munty_org][munty_dest][0]

    def get_max_time(self, munty_org, munty_dest):
        if munty_org not in self.__min_max_time or munty_dest not in self.__min_max_time[munty_org]:
            self.__compute_min_max_time(munty_org, munty_dest)  # trigger min/max time computation

        return self.__min_max_time[munty_org][munty_dest][1]

    def update_travel_time(self, stop_name_org, stop_name_dest, new_distance, old_distance):
        munty_org_list = self.map.reachable_munty_from_stop.get(stop_name_org,[])
        munty_dest_list = self.map.reachable_munty_from_stop.get(stop_name_dest,[])

        for munty_org in munty_org_list:
            for munty_dest in munty_dest_list:

                if new_distance == -1 or new_distance > old_distance:  # network deterioration
                    self.__compute_min_max_time(munty_org, munty_dest)
                else:  # network improvement
                    # simply update min/max
                    old_min_time = self.get_min_time(munty_org, munty_dest)  # trigger computation if not already done
                    old_max_time = self.get_max_time(munty_org, munty_dest)
                    mini = min(new_distance, old_min_time)
                    maxi = max(new_distance, old_max_time)
                    self.__min_max_time[munty_org][munty_dest] = (mini,maxi)

    def __compute_min_max_time(self, munty_org, munty_dest):
        """
        Calcul le temps de trajet minimal et maximal entre  les stop de munty_org et munty_dest
        """
        min_time = math.inf
        max_time = -1
        for org, _ in self.map.get_reachable_stop_from_munty(munty_org):
            TC_travel_array, name_to_idx = self.distance.dist_from(org)
            for dest, _ in self.map.get_reachable_stop_from_munty(munty_dest):
                time = TC_travel_array[name_to_idx[dest]]
                if time >= 0:
                    min_time = min(min_time, time)
                    max_time = max(max_time, time)

        # save result
        if munty_org not in self.__min_max_time:
            self.__min_max_time[munty_org] = {}
        self.__min_max_time[munty_org][munty_dest] = (min_time, max_time)

    # #################################### Computations ################################################################
    def __estimate_travel_time(self):
        for rsd_munty, work_munty in self.traveller_locations.keys():
            travellers = list(self.traveller_locations[(rsd_munty, work_munty)])
            #print("travels estimation: from ", rsd_munty, " to ", work_munty, "iteration :", len(travellers))
            res = self.all_results.get(rsd_munty, Result())
            for i in range(len(travellers)):
                rsd, work = travellers[i]
                opti_path, opti_time = self.optimal_travel_time(rsd, rsd_munty, work, work_munty)
                (time, walk1, walk2, TC, dist, unreachable) = opti_time
                travellers[i] = (rsd, work, opti_path, TC)
                res.add(time, walk1, walk2, TC, dist, 1, unreachable)
                self.total_results.add(time, walk1, walk2, TC, dist, 1, unreachable)

            self.traveller_locations[(rsd_munty, work_munty)] = travellers
            self.all_results[rsd_munty] = res

            # number of worker
            w = self.all_results.get(work_munty, Result())
            self.all_results[work_munty] = w

    def optimal_travel_time(self,resid_pt, munty_rsd, work_pt, munty_work):
        stop_list_rsd = self.map.get_reachable_stop_pt(resid_pt, munty_rsd)
        stop_list_work = self.map.get_reachable_stop_pt(work_pt, munty_work)

        dist = distance_Eucli(resid_pt, work_pt)
        time_without_TC = dist / self.speed  # without Tc
        # opti time : (time, walk1, walk2, TC,dist, unreachable)
        if time_without_TC > (2 * self.max_walk_time):
            unreachable = 1
        else:
            unreachable = 0

        opti_time = (time_without_TC, time_without_TC / 2, time_without_TC / 2, 0, dist, unreachable)
        opti_path = (None, None)



        if len(stop_list_rsd) == 0 or len(stop_list_work) == 0: return opti_path, opti_time

        stop_list_rsd.sort(key=lambda x: distance_Eucli(x[1], resid_pt))
        stop_list_work.sort(key=lambda x: distance_Eucli(x[1], work_pt))
        min_walk2 = distance_Eucli(stop_list_work[0][1], work_pt) / self.speed
        min_trav = self.get_min_time(munty_rsd, munty_work)

        for stop_rsd in stop_list_rsd:
            walk1 = distance_Eucli(resid_pt, stop_rsd[1]) / self.speed  # walking time
            if walk1 + min_walk2 + min_trav >= opti_time[0]:
                return opti_path, opti_time
            TC_travel_array, name_to_idx = self.distance.dist_from(stop_rsd[0])
            for stop_work in stop_list_work:
                walk2 = distance_Eucli(work_pt, stop_work[1]) / self.speed
                if walk1 + walk2 + min_trav >= opti_time[0]: break
                TC = TC_travel_array[name_to_idx[stop_work[0]]]
                if TC > 0:
                    time = walk1 + walk2 + TC
                    if opti_time[0] > time:
                        opti_time = (time, walk1, walk2, TC, dist, 0)
                        opti_path = (stop_rsd, stop_work)


        return opti_path, opti_time

    # #################################### Dynamic part ################################################################
    def update(self, changes):
        """
        Met a jour la mesure de temps de trajet en fonciton des changement apporter au reseau.
        :param changes: A dictionnary : {"size": (new_number_of_stop, old_number of stop),
                                  "change_distance": {org_name : {dest_name : (new_dist, old_dist)}}
        """

        for org_name_ch, dico in changes["change_distance"].items():
            for dest_name_ch, (new_value, old_value) in dico.items():
                self.update_travel_time(org_name_ch, dest_name_ch, new_distance=new_value,
                                                     old_distance=old_value)  # update used structure
                assert new_value <= old_value or old_value == -1
                org_ch_pos = self.map.stop_position_dico[org_name_ch]
                dest_ch_pos = self.map.stop_position_dico[dest_name_ch]

                #todo improve : ne parcourir que le stop concerner et pas tout ceux des commune affectee
                for rsd_munty in self.map.reachable_munty_from_stop[org_name_ch]:
                    for work_munty in self.map.reachable_munty_from_stop[dest_name_ch]:
                        travellers = self.traveller_locations.get((rsd_munty, work_munty),[])
                        for i in range(len(travellers)):   # find all potentially affected stop
                            rsd_pt, work_pt, (old_org_stop, old_dest_stop), old_TC = travellers[i]
                            if (old_org_stop, old_dest_stop) == (None, None):
                                old_unreach = 1
                                old_time = distance_Eucli(rsd_pt, work_pt)/self.speed
                                old_walk1 = old_time/2
                                old_walk2 = old_time / 2
                                old_TC = 0

                            else:
                                old_unreach = 0
                                old_walk1 = distance_Eucli(rsd_pt,old_org_stop[1]) / self.speed # walking time
                                old_walk2 = distance_Eucli(work_pt, old_dest_stop[1]) / self.speed  # walking time
                                # old_TC = old_TC
                                old_time = old_walk1 + old_TC + old_walk2

                            new_walk1 = distance_Eucli(rsd_pt, org_ch_pos) / self.speed  # walking time
                            new_walk2 = distance_Eucli(work_pt, dest_ch_pos) / self.speed  # walking time
                            new_TC = self.distance.dist(org_name_ch, dest_name_ch)
                            assert new_TC >= 0
                            new_time = new_walk1 + new_TC + new_walk2

                            if new_time < old_time and new_walk1 < self.max_walk_time and new_walk2 < self.max_walk_time:
                                #record old state
                                if rsd_munty not in self.__change_log["all_results_save"]:
                                    self.__change_log["travellers"][i] = travellers[i]
                                    self.__change_log["all_results_save"][rsd_munty]= self.all_results[rsd_munty].__copy__()
                                if "total_result" not in self.__change_log:
                                    self.__change_log["total_result"] = self.total_results.__copy__()
                                travellers[i] = rsd_pt, work_pt, ((org_name_ch,org_ch_pos), (dest_name_ch,dest_ch_pos)),new_TC
                                self.all_results[rsd_munty].remove(old_time, old_walk1, old_walk2, old_TC, unreachable=old_unreach)
                                self.all_results[rsd_munty].add(new_time, new_walk1, new_walk2, new_TC, unreachable=0)
                                self.total_results.remove(old_time, old_walk1, old_walk2, old_TC, unreachable=old_unreach)
                                self.total_results.add(new_time, new_walk1, new_walk2, new_TC, unreachable=0)

    # #################################### Reversible part
    def save(self):
        self.__stack_log.append(self.__change_log)
        self.__change_log = {"all_results_save": {}, "travellers": {}}

    def restore(self):
        changes = self.__change_log
        for i in changes["travellers"].keys():
            self.traveller_locations[i]= changes["travellers"][i]

        for munty in changes["all_results_save"].keys():
            self.all_results[munty]= changes["all_results_save"][munty]

        if "total_result" in self.__change_log:
            self.total_results = self.__change_log["total_result"]

        self.__change_log = self.__stack_log.pop()



class Result:
    def __init__(self):
        self.tot_time = 0.
        self.tot_time2 = 0.  # sum of squared(time)
        self.tot_walk1 = 0.
        self.tot_walk2 = 0.
        self.tot_TC = 0.
        self.tot_TC_user_only = 0.
        self.tot_dist = 0.
        self.iteration = 0
        self.unreachable = 0
        self.TC_user = 0.
        #self.pop = 0  # nb resident according to sector pop
        #self.resid = 0  # nb resident  according to travel
        #self.work = 0  # nb workers  according to travel

    def __copy__(self):
        new = Result
        new.tot_time = self.tot_time
        new.tot_time2 = self.tot_time2
        new.tot_walk1 = self.tot_walk1
        new.tot_walk2 = self.tot_walk2
        new.tot_TC = self.tot_TC
        new.tot_TC_user_only = self.tot_TC_user_only
        new.tot_dist = self.tot_dist
        new.iteration = self.iteration
        new.unreachable = self.unreachable
        new.TC_user = self.TC_user
        #new.pop = self.pop  # nb resident according to sector pop
        #new.resid = self.resid  # nb resident  according to travel
        #new.work = self.work  # nb workers  according to travel
        return new

    def __eq__(self, other):
        if not isinstance(other, Result): return False
        return self.tot_time == other.tot_time and self.tot_time2 == other.tot_time2 \
               and self.tot_walk1 == other.tot_walk1 and self.tot_walk2 == other.tot_walk2 \
               and self.tot_TC == other.tot_TC and self.tot_TC_user_only == other.tot_TC_user_only \
               and self.tot_dist == other.tot_dist and self.iteration == other.iteration \
               and self.unreachable == other.unreachable and self.TC_user == other.TC_user

    def add(self, time, walk1=0., walk2=0., TC=0.0, dist=0., iter=1, unreachable=0):
        self.unreachable += unreachable
        self.iteration += iter
        if unreachable == 0:
            self.tot_time += time
            self.tot_time2 += time ** 2
            self.tot_walk1 += walk1
            self.tot_walk2 += walk2
            self.tot_TC += TC
            self.tot_dist += dist
            if TC > 0:
                self.TC_user += 1
                self.tot_TC_user_only += TC

    def remove(self, time, walk1=0, walk2=0, TC=0, dist=0, iter=1, unreachable=0):
        self.unreachable -= unreachable
        self.iteration -= iter
        if unreachable == 0:
            self.tot_time -= time
            self.tot_time2 -= time ** 2
            self.tot_walk1 -= walk1
            self.tot_walk2 -= walk2
            self.tot_TC -= TC
            self.tot_dist -= dist
        if TC > 0:
            self.TC_user -= 1
            self.tot_TC_user_only -= TC

    def __str__(self):
        "(mean time {}, var {},mean_dist {}, iteration {})".format(self.tot_time / self.iteration,
                                                                   self.tot_time2 / self.iteration - 1,
                                                                   self.tot_dist / self.iteration,
                                                                   self.iteration)

    def mean(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.tot_time / n
        else:
            return None

    def walk1(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.tot_walk1 / n
        else:
            return None

    def walk2(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.tot_walk2 / n
        else:
            return None

    def TC(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.tot_TC / n
        else:
            return None

    def TC_user_only(self):
        n = self.TC_user
        if n > 0:
            return self.tot_TC_user_only / n
        else:
            return None

    def mean_dist(self):
        n = self.iteration
        if n > 0:
            return self.tot_dist / n
        else:
            return None

    def mean_dist_reachable(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.tot_dist / n
        else:
            return None

    def var(self):
        n = self.iteration - self.unreachable - 1  # todo check unbiased var
        if n > 0:
            return self.tot_time2 / n
        else:
            return None

    def prop_unreachable(self):
        n = self.iteration
        if n > 0:
            return self.unreachable / n
        else:
            return None

    def prop_TC_users(self):
        n = self.iteration - self.unreachable
        if n > 0:
            return self.TC_user / n
        else:
            return None

