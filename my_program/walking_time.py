
# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

def walking_time_distrib(stop, munty, max_walking_time):
    """
    the distribution of the walking_time to go to stop for people in munty

    :param stop: (stop_id, (coord_x, coord_y))
    :param munty: refnis of munty
    :param max_walking_time: maximum walking distance to reach the stop
    :return: (prop_0_min, prop_1_min ,..., prop_max_time_min, prop_stop_unreached)
    """


def get_reachable_stop(stop_list, munty, max_walking_time):
    """
    Compute a list containing every reachable stop_id in a walking_time < max_walking_time for a given munty

    :param stop_list:
    :param munty:
    :param max_walking_time:
    :return:
    """

def get_all_walking_time_distrib(stop_list, munty_list, max_walking_time):
    """
    Build a dictionnary containing the distribution of the walking_time
            for each stop,munty where min_dist(stop, munty) < max_walking_time
    :param stop_list:
    :param munty_list:
    :param max_walking_time:
    :return: dictionnary : {(stop_id,munty_refnis) : (prop_0_min, prop_1_min ,..., prop_max_time_min, prop_not_counted)}
    """
    pass
    #for : walking_time_distrib(...)