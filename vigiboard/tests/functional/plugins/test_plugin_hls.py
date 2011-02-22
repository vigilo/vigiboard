# -*- coding: utf-8 -*-
""" Test du plugin listant les services de haut niveau impactés. """

from datetime import datetime
import transaction
from nose.tools import assert_equal

from vigilo.models.session import DBSession
from vigilo.models.tables import Permission, DataPermission, StateName, \
                            SupItemGroup, Host, HighLevelService, \
                            Event, CorrEvent, ImpactedPath, ImpactedHLS, \
                            User, UserGroup
from vigiboard.tests import TestController

def populate_DB():
    """ Peuple la base de données. """

    # On ajoute un groupe d'hôtes
    hostmanagers = SupItemGroup(name=u'managersgroup')
    DBSession.add(hostmanagers)
    DBSession.flush()

    # On lui octroie les permissions
    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        group=hostmanagers,
        usergroup=usergroup,
        access=u'r',
    ))
    DBSession.flush()

    # On crée un hôte de test.
    host = Host(
        name = u'host', 
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        address = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
        )
    DBSession.add(host)

    # On affecte cet hôte au groupe précédemment créé.
    hostmanagers.supitems.append(host)
    DBSession.flush()

    # On ajoute un évènement causé par cet hôte.
    event1 = Event(
        supitem = host,
        message = u'foo',
        current_state = StateName.statename_to_value(u'WARNING'),
        timestamp = datetime.now(),
    )
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
    def setUp(self):
        super(TestHLSPlugin, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')

        user = User(
            user_name=u'access',
            fullname=u'',
            email=u'user.has@access',
        )
        usergroup = UserGroup(
            group_name=u'users_with_access',
        )
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        user = User(
            user_name=u'no_access',
            fullname=u'',
            email=u'user.has.no@access',
        )
        usergroup = UserGroup(
            group_name=u'users_without_access',
        )
        usergroup.permissions.append(perm)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        self.aggregate = populate_DB()

    def test_no_impacted_hls(self):
        """
        Retour du plugin HLS pour 0 HLS impacté
        Teste la valeur de retour du plugin lorsque
        aucun service de haut niveau n'est impacté.
        """
        
        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(0, 0, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les
        ### droits sur l'hôte ayant causé le correvent.
        # On vérifie que le plugin retourne bien une erreur 404.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 404,
            extra_environ={'REMOTE_USER': 'no_access'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            extra_environ={'REMOTE_USER': 'access'})
        # On vérifie que le plugin ne retourne toujours rien.
        assert_equal(resp.json, {"services": []})
    
    def test_1_impacted_hls_path(self):
        """
        Retour du plugin HLS pour 1 chemin impacté
        Teste la valeur de retour du plugin lorsqu'un
        chemin de services de haut niveau est impacté.
        """
        
        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(1, 2, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les droits
        ### sur l'hôte ayant causé le correvent, on doit
        ### obtenir une erreur 404 (pas d'événement trouvé
        ### avec les informations liées à cet utilisateur).
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 404,
            extra_environ={'REMOTE_USER': 'no_access'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            extra_environ={'REMOTE_USER': 'access'})
        # On vérifie que le plugin retourne bien les 2 HLS impactés.
        assert_equal(resp.json, {"services": ['HLS12']})
    
    def test_2_impacted_hls_path(self):
        """
        Retour du plugin HLS pour 2 chemins impactés
        Teste la valeur de retour du plugin lorsque deux
        chemins de services de haut niveau sont impactés.
        """
        
        # On peuple la base de données avant le test.
        DBSession.add(self.aggregate)
        add_paths(2, 2, self.aggregate.events[0].idsupitem)
        DBSession.add(self.aggregate)
        
        ### 1er cas : l'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 401,)
        
        ### 2ème cas : l'utilisateur n'a pas les
        ### droits sur l'hôte ayant causé le correvent.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            status = 404,
            extra_environ={'REMOTE_USER': 'no_access'})
        
        ### 3ème cas : l'utilisateur a cette fois les droits.
        resp = self.app.post(
            '/get_plugin_value', 
            {"idcorrevent" : str(self.aggregate.idcorrevent),
             "plugin_name" : "hls"},
            extra_environ={'REMOTE_USER': 'access'})
        # On vérifie que le plugin retourne bien les 4 HLS impactés.
        assert_equal(resp.json, {"services": ['HLS12', 'HLS22']})

