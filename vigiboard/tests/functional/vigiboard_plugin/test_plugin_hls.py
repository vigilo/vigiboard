# -*- coding: utf-8 -*-
""" Test du plugin listant les services de haut niveau impactés. """

from datetime import datetime
import transaction
from vigiboard.tests import TestController
from nose.tools import assert_equal
from vigilo.models import Permission, StateName, \
                            HostGroup, Host, HighLevelService, \
                            Event, CorrEvent, ImpactedPath, ImpactedHLS
from vigilo.models.configure import DBSession

def populate_DB():
    """ Peuple la base de données. """

    # On ajoute un groupe d'hôtes
    hostmanagers = HostGroup(name = u'managersgroup')
    DBSession.add(hostmanagers)
    DBSession.flush()

    # On lui octroie les permissions
    manage_perm = Permission.by_permission_name(u'manage')
    hostmanagers.permissions.append(manage_perm)
    DBSession.flush()

    # On crée un hôte de test.
    host = Host(
        name = u'host', 
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        mainip = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
        )
    DBSession.add(host)

    # On affecte cet hôte au groupe précédemment créé.
    hostmanagers.hosts.append(host)
    DBSession.flush()

    # On ajoute un évènement causé par cet hôte.
    event1 = Event(
        supitem = host,
        message = u'foo',
        current_state = StateName.statename_to_value(u'WARNING'))
    DBSession.add(event1)
    DBSession.flush()

    # On ajoute un évènement corrélé causé par cet évènement 'brut'.
    aggregate = CorrEvent(
        idcause = event1.idevent, 
        timestamp_active = datetime.now(),
        priority = 1,
        status = u'None')
    aggregate.events.append(event1)
    DBSession.add(aggregate)
    DBSession.flush()
    
    transaction.commit()

    return aggregate

def add_paths(path_number, path_length, idsupitem):
    """ 
    Ajoute path_number chemins de services de haut niveau impactés
    dans la base de donnée. Leur longeur sera égale à path_length.
    La 3ème valeur passée en paramètre est l'id du supitem impactant.
     
    path_number * path_length services de 
    haut niveau sont créés dans l'opération.
    """

    # Création de services de haut niveau dans la BDD.
    hls_template = {
        'op_dep': u'&',
        'message': u'Bar',
        'warning_threshold': 60,
        'critical_threshold': 80,
        'weight': None,
        'priority': 2,
    }

    # Création des chemins de services de haut niveau impactés.
    for j in range(path_number):
        
        # On crée le chemin en lui-même
        path = ImpactedPath(idsupitem = idsupitem)
        DBSession.add(path)
        DBSession.flush()
        
        # Pour chaque étage du chemin,
        for i in range(path_length):
            # on ajoute un service de haut niveau dans la BDD,
            hls = HighLevelService(
                servicename = u'HLS' + str(j + 1) + str(i + 1), 
                **hls_template)
            DBSession.add(hls)
            # et on ajoute un étage au chemin contenant ce service. 
            DBSession.add(
                ImpactedHLS(
                    path = path,
                    hls = hls,
                    distance = i + 1,
                    ))
    
    DBSession.flush()
    transaction.commit()


class TestHLSPlugin(TestController):
    """
    Classe de test du contrôleur listant les services 
    de haut niveau impactés par un évènement corrélé.
    """
    
    def test_no_impacted_hls(self):
        """
        Retour du plugin SHN pour 0 SHN impacté
        Teste la valeur de retour du plugin lorsque
        aucun service de haut niveau n'est impacté.
        """
        
        # On peuple la base de données avant le test.
        aggregate = populate_DB()
        DBSession.add(aggregate)
        add_paths(0, 0, aggregate.events[0].idsupitem)
        DBSession.add(aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 404.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les
        ### droits sur l'hôte ayant causé le correvent.
        # On vérifie que le plugin retourne bien une erreur 404.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 404,
            extra_environ={'REMOTE_USER': 'editor'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.        
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            extra_environ={'REMOTE_USER': 'manager'})
        # On vérifie que le plugin ne retourne toujours rien.
        assert_equal(resp.json, {"services": []})
    
    def test_1_impacted_hls_path(self):
        """
        Retour du plugin SHN pour 1 chemin impacté
        Teste la valeur de retour du plugin lorsqu'un
        chemin de services de haut niveau est impacté.
        """
        
        # On peuple la base de données avant le test.
        aggregate = populate_DB()
        DBSession.add(aggregate)
        add_paths(1, 2, aggregate.events[0].idsupitem)
        DBSession.add(aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 404.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les
        ### droits sur l'hôte ayant causé le correvent.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 404,
            extra_environ={'REMOTE_USER': 'editor'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.        
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            extra_environ={'REMOTE_USER': 'manager'})
        # On vérifie que le plugin retourne bien les 2 SHN impactés..
        assert_equal(resp.json, {"services": ['HLS12']})
    
    def test_2_impacted_hls_path(self):
        """
        Retour du plugin SHN pour 2 chemins impactés
        Teste la valeur de retour du plugin lorsque deux
        chemins de services de haut niveau sont impactés.
        """
        
        # On peuple la base de données avant le test.
        aggregate = populate_DB()
        DBSession.add(aggregate)
        add_paths(2, 2, aggregate.events[0].idsupitem)
        DBSession.add(aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 404.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les
        ### droits sur l'hôte ayant causé le correvent.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            status = 404,
            extra_environ={'REMOTE_USER': 'editor'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.        
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(aggregate.idcorrevent),
             "plugin_name" : "shn"},
            extra_environ={'REMOTE_USER': 'manager'})
        # On vérifie que le plugin retourne bien les 4 SHN impactés..
        assert_equal(resp.json, {"services": ['HLS12', 'HLS22']})
        
