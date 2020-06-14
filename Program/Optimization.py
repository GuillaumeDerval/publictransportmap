from Program.NetworkEfficiency import NetworkEfficiency
import math

def find_best_modification(network : NetworkEfficiency, modifications: list):
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
        print(network.get_value())
        network.save()
        value = network.modify(modif)
        print("\n\n\nmodif value", value)
        if value < min_value:
            best = modif
            min_value = value
        network.restore()
        print(network.get_value())
    return best, min_value


def find_best_Duo_modification(network : NetworkEfficiency, modifications: list):
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
        print(network.get_value())
        network.save()
        value = network.modify(modifications[i])
        print("modif1 value", value)
        for j in range(i+1, len(modifications)):
            network.save()
            value = network.modify(modifications[j])
            print("modif2 value", value)
            if value < min_value:
                best = (modifications[i], modifications[j])
                min_value = value
            network.restore()
            print("modif1 value", value)
        network.restore()
        print(network.get_value())
    return best, min_value
