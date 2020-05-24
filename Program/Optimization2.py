import Program.NetworkEfficiency as NE
import math

def find_best_modification(network : NE.NetworkEfficiency, modifications: list):
    """
    Trouve la meilleur modification du reseau de Transport en commun possible parmis celles proposée.
    Cette fonction ne modifie pas l'état final du réseau
    :param network: NetworkEfficency, reseau surlequel les modification seront testée
    :param modifications: Une liste de  NetworkModification
    :return: best, min_value ; la meilleur modificaion suivie de la valeur de la métrique obtenue
    """
    best = None
    min_value = math.inf
    for modif in modifications:
        network.save()
        value = network.modify(modif)
        if value < min_value:
            best = modif
            min_value = value
        network.restore()
    return best, min_value


def find_best_Duo_modification(network : NE.NetworkEfficiency, modifications: list):
    """
    Trouve la meilleur modification du reseau de Transport en commun possible parmis celles proposée.
    Cette fonction ne modifie pas l'état final du réseau
    :param network: NetworkEfficency, reseau surlequel les modification seront testée
    :param modifications: Une liste de  NetworkModification
    :return: best, min_value ; liste reprenant le meilleur duo de modificaion , valeur de la métrique obtenue
    """
    best = None
    min_value = math.inf
    for i in range(len(modifications)):
        network.save()
        network.modify(modifications[i])
        for j in range(i+1, len(modifications)):
            network.save()
            value = network.modify(modifications[j])
            if value < min_value:
                best = (modifications[i], modifications[j])
                min_value = value
            network.restore()
        network.restore()
    return best, min_value

def find_best_combination_of_modifications(network : NE.NetworkEfficiency, modifications: list, weight: list, max_weight):
    """
    Trouve la meilleur combinaison de modification tel que la somme des poids qui leur son attribuée est inféreiur a max_weight
    :param network: NetworkEfficency, reseau surlequel les modification seront testée
    :param Modifications: Une liste de  NetworkModification
    :param weight: Une liste de poids associé respectivement à chaque modifications
    :param max_weight: valeur maximal de la somme de poids d'une combinaison de modifications
    :return: best_combi, min_value ; liste reprenant la meilleur combinaion modificaion , valeur de la métrique obtenue
    """

    # Cette methode de recherche n'a pas été optimisé

    best = None
    min_value = math.inf
    curr_value = 0
    for i in range(len(modifications)):
        if curr_value+ weight[i] < max_weight:
            modif = modifications[i]
            other_modif = modifications.copy()
            other_modif.remove(i)
            network.save()
            #todo recursive