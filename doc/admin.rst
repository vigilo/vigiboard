**********************
Guide d'administration
**********************


Installation
============

Pré-requis logiciels
--------------------
Afin de pouvoir faire fonctionner VigiBoard, l'installation préalable des
logiciels suivants est requise :

* python (>= 2.5), sur la machine où VigiBoard est installé
* Apache (>= 2.2.0), sur la machine où VigiBoard est installé
* mod_wsgi (>= 2.3), sur la machine où VigiBoard est installé
* PostgreSQL (>= 8.3), éventuellement sur une machine distante


.. Installation du RPM
.. include:: ../buildenv/doc/package.rst


Démarrage et arrêt
==================

VigiBoard fonctionne comme un site Web standard. À ce titre, il n'est pas
nécessaire d'exécuter une commande spécifique pour démarrer VigiBoard, dès lors
que le serveur Web qui l'héberge a été lancé, à l'aide de la commande::

    service httpd start

De la même manière, il n'y a pas de commande spécifique pour arrêter VigiBoard.
L'application est arrêtée en même temps que le serveur Web, à l'aide de la
commande::

    service httpd stop



Configuration
=============

La configuration initialement fournie avec VigiBoard est très rudimentaire.
Elle est décomposée en deux fichiers :

- le fichier ``settings.ini`` d'une part, qui contient la majorité des options
  de configuration ;
- et le fichier ``app_cfg.py`` qui contient des options de configuration plus
  complexes, nécessitant l'utilisation d'un langage plus complet (Python).

Ce chapitre a pour but de présenter les différentes options de configuration
disponibles afin de configurer VigiBoard en fonction de vos besoins. Les
chapitres :ref:`confbdd` à :ref:`confproxy` reprennent l'ordre de la
configuration utilisé dans le fichier ``settings.ini`` de l'application. Toutes
les options de configuration citées ici se trouvent sous la section
``[app:main]`` du fichier ``settings.ini``.

Le chapitre :ref:`confappcfg` quant à lui décrit certaines options de
configuration fournies par le fichier ``app_cfg.py``.

Enfin, le chapitre :ref:`confmodwsgi` donne des informations quant à la méthode
utilisée pour intégrer VigiBoard sur un serveur Web de type Apache, grâce au
module mod_wsgi.

La configuration de la journalisation des événements se fait également au
travers du fichier ``settings.ini``. Néanmoins, comme ce procédé se fait de la
même manière dans les différents composants de Vigilo, celui-ci fait l'objet
d'une documentation séparée dans le document *Vigilo - Journaux d'événements*.

.. _confbdd:

Base de données
---------------

Pour fonctionner, VigiBoard nécessite qu'une base de données soit accessible.
Ce chapitre décrit les options de configuration se rapportant à la base de
données.

Connexion
^^^^^^^^^
La configuration de la connexion à la base de base de données se fait en
modifiant la valeur de la clé ``sqlalchemy.url`` sous la section
``[app:main]``.

Cette clé contient une URL qui contient tous les paramètres nécessaires pour
pouvoir se connecter à la base de données. Le format de cette URL est le
suivant::

    sgbd://utilisateur:mot_de_passe@serveur:port/base_de_donnees

Le champ ``:port`` est optionnel et peut être omis si vous utilisez le port
par défaut d'installation du SGBD choisi.

Par exemple, voici la valeur correspondant à une installation mono-poste par
défaut de VigiBoard::

    postgressql://vigilo:vigilo@localhost/vigilo

..  warning::
    À l'heure actuelle, seul PostgreSQL a fait l'objet de tests intensifs.
    D'autres SGBD peuvent également fonctionner, mais aucun support ne
    sera fourni pour ces SGBD.

Choix d'un préfixe pour les tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous pouvez choisir un préfixe qui sera appliqué aux noms des tables de la base
de données en indiquant ce préfixe dans la clé ``db_basename`` sous la section
``[app:main]``. Par défaut, la configuration suppose que les tables de Vigilo
porteront le préfixe ``vigilo_``.

Si vous optez pour l'utilisation d'un préfixe, veillez à ce que celui-ci ne
contiennent que des caractères alpha-numériques (a-zA-Z0-9) ou le caractère
``_``.

Si vous décidez de ne pas utiliser de préfixe, veillez à ce que la base de
données configurée ne doit utilisée que par Vigilo, au risque d'un conflit avec
une éventuelle application tierce.

Optimisation de la couche d'abstraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'option ``sqlalchemy.echo`` permet de forcer l'affichage des requêtes SQL. En
production, cette valeur doit être positionnée à ``False``. Elle est redondante
avec la configuration des journaux d'événements (voir le document intitulé
Vigilo - Journaux d'événements pour plus d'information).

L'option ``sqlalchemy.echo_pool`` permet d'activer le mode de débogage du
gestionnaire de connexions à la base de données. De même que pour l'option
``sqlalchemy.echo`` ci-dessus, elle doit être positionnée à ``False`` en
production.

L'option ``sqlalchemy.pool_recycle`` permet de définir la durée après laquelle
une connexion est « recyclée » (recréée).

L'option ``sqlalchemy.pool_size`` permet de configurer le nombre de connexions
gérées simultanément par le gestionnaire de connexions à la base de données. La
valeur recommandée est 20.

L'option ``sqlalchemy.max_overflow`` permet de limiter le nombre maximales de
connexions simultanées à la base de données. La limite correspond à la somme de
``sqlalchemy.pool_size`` et ``sqlalchemy.max_overflow``. Une valeur de 100
convient généralement.

La documentation d'API de SQLAlchemy (la bibliothèque d'abstraction de la base
de données utilisée par Vigilo) donne quelques informations supplémentaires sur
le rôle de ces différents paramètres. Cette documentation est accessible `sur
le site du projet
<http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/pooling.html>`_.

Éléments de sécurité
--------------------

Ce chapitre décrit les options relatives à la gestion des données de sécurité
(clés de chiffrements, etc.) utilisées par VigiBoard.

Choix de la méthode de hachage des mots de passe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Lorsque l'authentification de Vigilo se base sur les comptes contenus dans la
base de données, les mots de passe des utilisateurs sont stockés sous forme
hachée afin de rendre plus difficile le cassage de ces mots de passe.

La méthode de hachage sélectionnée peut être configurée en modifiant la valeur
de la clé ``password_hashing_function`` sous la section ``[app:main]``. Les
méthodes de hachage disponibles sont variées. Les fonctions de hachage
suivantes sont notamment disponibles : md5, sha1, sha224, sha256, sha384 et
sha512. D'autres fonctions peuvent être disponibles en fonction de votre
installation de Python.

..  warning::
    En cas d'absence d'une valeur pour cette option ou si la fonction
    de hachage indiquée n'existe pas, les mots de passe sont stockés
    en clair. Vérifiez donc la valeur indiquée.

..  warning::
    Cette option ne doit être modifiée qu'au moment de l'installation.
    Si vous modifiez la méthode utilisée ultérieurement, les comptes
    précédemment enregistrés ne seront plus utilisables.
    En particulier, le compte d'administration créé par défaut.

Clé de chiffrement / déchiffrement des sessions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Afin de ne pas dévoiler certains paramètres associés à un utilisateur, le
fichier de session qui contient ces paramètres est chiffré à l'aide d'une clé
symétrique, utilisée à la fois pour le chiffrement et le déchiffrement des
sessions de tous les utilisateurs de VigiBoard.

L'option ``beaker.session.secret`` permet de choisir la clé utilisée pour
chiffrer et déchiffrer le contenu des sessions. Cette clé peut être la même que
celle configurée pour le chiffrement / déchiffrement des cookies (voir le
chapitre suivant), mais ceci est déconseillé afin d'éviter que la compromission
de l'une des deux clés n'entraine la compromission de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques de
Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des clés
différentes (là encore, pour éviter la propagation d'une compromission).

Clé de chiffrement / déchiffrement des cookies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'association entre un utilisateur et sa session se fait à l'aide d'un cookie
de session enregistré sur le navigateur de l'utilisateur. De la même manière
que les sessions sont chiffrés afin de garantir la confidentialité de leur
contenu, le cookie de session est également chiffré afin de protéger son
contenu.

L'option ``sa_auth.cookie_secret`` permet de choisir la clé utilisée pour
chiffrer et déchiffrer le contenu du cookie. Cette clé peut être la même que
celle configurée pour le chiffrement / déchiffrement des sessions (voir le
chapitre ), mais ceci est déconseillé afin d'éviter que la compromission de
l'une des deux clés n'entraine la compromission de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques de
Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des clés
différentes (là encore, pour éviter la propagation d'une compromission).


Emplacement de la configuration d'authentification/autorisation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
La directive ``auth.config`` de la section ``[app:main]`` permet d'indiquer
l'emplacement du fichier contenant la configuration de la couche
d'authentification/autorisation de Vigilo.

Il n'est généralement pas nécessaire de modifier cette valeur. La configuration
de cette couche d'abstraction est détaillée dans le document *Vigilo -
Authentification et autorisation*.

Configuration de l'interface
----------------------------

Ce chapitre décrit les options qui modifient l'apparence de l'interface
graphique de VigiBoard.

Langue par défaut de VigiBoard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Au sein de son interface, VigiBoard tente de s'adapter au navigateur de
l'utilisateur pour afficher les pages dans sa langue. Toutefois, si
l'utilisateur n'a pas paramétré sa langue ou bien si aucune traduction n'est
disponible qui soit en accord avec les paramètres du navigateur de
l'utilisateur, une langue par défaut est utilisée (dans l'installation par
défaut de VigiBoard, cette langue est le Français ``fr``).

Vous pouvez modifier la langue utilisée par défaut en changeant la valeur de la
clé ``lang`` sous la section ``[app:main]``. La valeur de cette clé est le code
de la langue à utiliser, sur deux caractères et en minuscules (format ISO
3166-1 ``alpha 2``). Exemples de codes valides : fr, en, de, ...

La liste complète des codes possibles est disponible sur
http://fr.wikipedia.org/wiki/ISO_3166-1.
La langue retenue doit être disponible parmi les traductions fournies
avec VigiBoard.

Emplacement de la documentation en ligne
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Il est possible d'ajouter un lien dans l'interface graphique qui redirige
l'utilisateur vers la documentation en ligne de l'application. Ceci se fait en
assignant une URL à l'option ``help_link``.

Si cette option est renseignée, une icône en forme de bouée de sauvetage
|imghelp| apparaît dans l'interface graphique qui permet à l'utilisateur
d'accéder à l'URL indiquée.

.. |imghelp| image:: img/help.png

Délai de rafraîchissement automatique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le bac à événements de VigiBoard peut être actualisé automatiquement à
intervalle régulier afin de donner une vue à jour de l'état du parc aux
veilleurs. L'option ``refresh_delay`` permet de choisir le délai, en secondes,
entre deux rafraîchissements automatiques de la page.

..  note::
    Les veilleurs ont la possibilité de désactiver le rafraîchissement
    automatique durant leur session. Dans tous les cas, si une boîte
    de dialogue de VigiBoard est affichée à l'écran, le rafraîchissement
    automatique est mis en pause afin de ne pas perturber les opérations
    en cours.

État initial du rafraîchissement automatique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous avez la possibilité d'activer par défaut le rafraîchissement automatique
du bac à événements pour les veilleurs, en positionnant l'option
``refresh_enabled`` à ``True``.

..  note::
    Les veilleurs ont la possibilité de désactiver le rafraîchissement
    automatique durant leur session. Leur choix (rafraîchissement automatique
    actif ou non) est conservé en session durant un certain temps.

Configuration du nombre d'événements affichés par page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le nombre d'événements affichés par page peut être configuré en changeant la
valeur de la clé ``vigiboard_items_per_page`` sous la section ``[app:main]``.

Configuration du lien d'accueil
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous avez la possibilité de rediriger l'utilisateur vers une page de votre
choix lorsque celui-ci clique sur le logo en forme de maison |imghome|
dans l'interface graphique de VigiBoard.
Ceci se fait en modifiant l'URL associée à l'option ``home_link``.

.. |imghome| image:: img/home.png

Ordre de tri de la priorité des événements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
VigiBoard prend en compte la priorité des événements pour les triers dans son
interface graphique. Néanmoins, chaque système à sa propre définition de la
priorité d'un événement. Généralement, plus la priorité d'un événement est
élevée, plus cet événement doit être traité en premier. Cependant il se peut
que cet ordre de tri soit inversé sur votre parc (c'est-à-dire qu'un événement
très prioritaire est représenté par une priorité dont la valeur est très
basse).

L'ordre de tri de la priorité est défini grâce à la clé de configuration
``vigiboard_priority_order``, sous la section ``[app:main]``. Cette clé accepte
deux valeurs : ``asc`` (nombre peu élevé = priorité importante) ou ``desc``
(nombre élevé = priorité importante).

Choix du critère de tri prioritaire
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
En fonction de votre parc informatique, il peut être intéressant de trier les
événements reçus dans le bac à événements par état Nagios puis par horodatage,
ou bien l'inverse.

L'option ``state_first`` est un booléen qui permet de choisir si le tri se fait
d'abord par l'état (``True``), ou d'abord par l'horodatage (``False``).

.. _confproxy:

Configuration de l'auto-supervision
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
VigiBoard affiche un message d'alerte à l'utilisateur dès lors qu'un des
collecteurs Vigilo n'a pas donné signe de vie depuis plus d'une certaine durée.
Cette durée-seuil, exprimée en secondes, est configurable à l'aide de l'option
« freshness_threshold » .
Une valeur négative ou nulle désactive complètement cette fonctionnalité.

Configuration du serveur mandataire
-----------------------------------
VigiBoard permet d'accéder à la page d'état Nagios d'un hôte ou d'un service,
et ce malgré le fait que ces hôtes/services sont supervisés par des serveurs
Nagios différents. Ceci est rendu possible par l'existence d'un serveur
mandataire (proxy) qui relaye les requêtes au serveur Nagios concerné.

Le chapitre  présente tout d'abord les options communes à tous les types de
serveurs mandataires de Vigilo. Puis, le chapitre  détaille les options
spécifiques au serveur mandataire pour Nagios intégré à VigiBoard.

Options communes à tous les serveurs mandataires de Vigilo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les options communes à tous les serveurs mandataires de Vigilo concernent
l'authentification auprès d'un serveur mandataire intermédiaire. Elles sont au
nombre de trois :

- ``app_proxy_auth_method`` indique la méthode d'authentification à utiliser et
  peut valoir ``basic`` ou ``digest``

- ``app_proxy_auth_username`` indique le nom d'utilisateur à utiliser pour se
  connecter au serveur mandataire intermédiaire

- ``app_proxy_auth_password`` indique le mot de passe associé à ce nom
  d'utilisateur.

Ces trois options doivent être renseignées pour que l'authentification auprès
du serveur mandataire intermédiaire soit effective.

Options spécifiques au serveur mandataire Nagios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'option ``app_path.nagios`` indique l'emplacement de l'installation de Nagios
sur le serveur Web distant, à partir de la racine du serveur Web. Généralement,
il s'agit de ``/nagios/`` (emplacement par défaut lors d'une nouvelle
installation de l'interface graphique CGI de Nagios).

L'option ``app_scheme.nagios`` indique le protocole à utiliser pour communiquer
avec le serveur Web distant. Pour le moment, seuls les protocoles ``http`` et
``https`` sont supportés.

L'option ``app_port.nagios`` permet d'indiquer le port à utiliser pour se
connecter, dans le cas où il ne s'agit pas du port standard. Par défaut, le
serveur mandataire Nagios utilise le port standard associé au protocole donné
par ``app_scheme.nagios`` (80 pour HTTP, 443 pour HTTPS).

L'option ``app_redirect.nagios`` permet de modifier le comportement du serveur
mandataire. Lorsque cette option vaut ``True``, le serveur mandataire agit
comme un simple redirecteur de requêtes. Dans ce mode, les options
d'authentification liées au serveur mandataire sont ignorées. Ce mode de
fonctionnement est utile afin de tester la configuration mais n'est pas
recommandé en production.

Les options ``app_auth_method.nagios``, ``app_auth_username.nagios`` et
``app_auth_password.nagios`` permettent d'indiquer la méthode
d'authentification, le nom d'utilisateur et le mot de passe pour accéder à
l'interface CGI de Nagios. Ces options sont similaires à celles décrites au
chapitre .

Configuration des sessions
--------------------------
Chaque fois qu'un utilisateur se connecte à VigiBoard, un fichier de session
est créé permettant de sauvegarder certaines préférences de cet utilisateur
(par exemple, le thème de l'application, la taille de la police de caractères,
etc.).

Ce chapitre décrit les options relatives à la gestion des sessions.

Emplacement des fichiers de session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le dossier dans lequel les fichiers de session seront stockés est indiqué par
l'option ``cache_dir``.

Nom du cookie de session
^^^^^^^^^^^^^^^^^^^^^^^^
Afin d'associer un utilisateur au fichier de session qui lui correspond, un
cookie de session est créé sur le navigateur de l'utilisateur. L'option
``beaker.session.key`` permet de choisir le nom du cookie créé. Le nom doit
être composé de caractères alphanumériques (a-zA-Z0-9) et commencer par une
lettre (a-zA-Z).

.. _confappcfg:

Options du fichier ``app_cfg.py``
---------------------------------
Le fichier ``app_cfg.py`` contient des réglages spécifiques à VigiBoard plus
complexes à représenter que par l'usage du fichier ``settings.ini``. Ce
chapitre décrit ces réglages.

La modification de ces réglages nécessite une connaissance rudimentaire du
langage de programmation Python.

Choix des colonnes affichées dans VigiBoard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous avez la possibilité de configurer les colonnes à afficher dans VigiBoard
ainsi que leur ordre. VigiBoard est fourni avec un ensemble de colonnes
prédéfinies. La liste complète des colonnes disponibles peut être obtenue à
l'aide de la commande suivante::

    vigilo-plugins vigiboard.columns

L'option ``base_config['vigiboard_plugins']`` du fichier ``app_cfg.py``
contient un tuple des noms des colonnes à afficher (dans leur ordre
d'affichage, de gauche à droite sur un navigateur configuré pour un utilisateur
français, et de droite à gauche pour un utilisateur hébreu).

Exemple de configuration possible :

..  sourcecode:: python

    base_config['vigiboard_plugins'] = (
        'details',
        'date',
        'priority',
        'occurrences',
        'hostname',
        'servicename',
        'output',
        'hls',
        'status',
    )

Configuration des liens externes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'option ``base_config['vigiboard_links.eventdetails']`` contient la liste des
liens externes configurés, c'est-à-dire les liens qui seront affichés dans le
dialogue de détail d'un événement (figure ).

La configuration des liens externes est donnée sous la forme d'un tuple de
tuples, de la forme ::

    (libellé du lien, URL cible)

L'URL peut être relative ou absolue. Dans le cas d'une URL relative, celle-ci
est relative à l'emplacement de la racine de VigiBoard sur le serveur Web.

L'URL peut contenir des paramètres qui seront transmis tel quel. De plus, les
variables de substitution suivantes sont disponibles :

- ``%(idcorrevent)d`` est remplacé par l'identifiant (unique) de l'événement
  corrélé dans Vigilo,
- ``%(host)s`` est remplacé par le nom de l'hôte impacté par l'événement
  corrélé,
- ``%(service)s`` est remplacé par le nom du service impacté ou ``None`` si
  l'événement concernant directement l'hôte,
- ``%(message)s`` est remplacé par le message de supervision remonté par
  Nagios.

Exemple de configuration possible :

..  sourcecode:: python

    base_config['vigiboard_links.eventdetails'] = (
        (
            u'Détail de l\'hôte dans Nagios',
            '/nagios/%(host)s/cgi-bin/status.cgi?host=%(host)s'
        ), (
            u'Détail de la métrologie',
            'http://vigilo.example.com/vigigraph/rpc/fullHostPage?host=%(host)s'
        ), (
            u'Détail de la sécurité',
            'http://security.example.com/?host=%(host)s'
        ), (
            'Inventaire',
            'http://cmdb.example.com/?host=%(host)s'
        ), (
            'Documentation',
            'http://doc.example.com/?q=%(message)s'
        ),
    )

Cet exemple correspond à la liste de liens suivante :

.. figure:: img/liens.png

   Liens externes d'un événement


Emplacement du gestionnaire de tickets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Un ticket d'incident peut être associé à un ou plusieurs événements corrélés
apparaissant dans VigiBoard. L'adresse du gestionnaire de ticket est
paramétrable à l'aide de l'option ``base_config['vigiboard_links.tt']``.

Il s'agit d'une URL absolue, dans laquelle les variables de substitution
suivantes sont disponibles :

- ``%(idcorrevent)d`` est remplacé par l'identifiant (unique) de l'événement
  corrélé dans Vigilo,
- ``%(host)s`` est remplacé par le nom de l'hôte impacté par l'événement
  corrélé,
- ``%(service)s`` est remplacé par le nom du service impacté ou ``None`` si
  l'événement concernant directement l'hôte,
- ``%(tt)s`` est remplacé par la référence du ticket d'incident, telle que
  saisie par un utilisateur.

Exemple de configuration possible :

    ..  sourcecode:: python

        base_config['vigiboard_links.tt'] = \
            'http://bugs.example.com/?ticket_id=%(tt)s'


.. _confmodwsgi:

Intégration de VigiBoard avec Apache / mod_wsgi
-----------------------------------------------

VigiBoard a été testé avec le serveur libre Apache. L'application utilise en
outre le module Apache ``mod_wsgi`` pour communiquer avec le serveur. Ce module
implémente un modèle de communication basé sur l'interface WSGI. Le reste de ce
chapitre décrit la configuration utilisée pour réaliser cette intégration.

Fichier de configuration pour Apache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le fichier de configuration pour l'intégration de VigiBoard dans Apache se
trouve généralement dans ``/etc/vigilo/vigiboard/vigiboard.conf`` (un lien
symbolique vers ce fichier est créé dans le dossier de configuration d'Apache,
généralement dans ``/etc/httpd/conf.d/vigiboard.conf``).

En général, il n'est pas nécessaire de modifier le contenu de ce fichier. Ce
chapitre vise toutefois à fournir quelques informations sur le fonctionnement
de ce fichier, afin de permettre d'éventuelles personnalisations de ce
comportement.

Ce fichier tente tout d'abord de charger le module ``mod_wsgi`` (directive
LoadModule) puis ajoute les directives de configuration nécessaire à Apache
pour faire fonctionner VigiBoard, reprises partiellement ci-dessous::

    WSGIRestrictStdout off
    WSGIPassAuthorization on
    WSGIDaemonProcess vigiboard user=apache group=apache threads=2
    WSGIScriptAlias /vigilo/vigiboard "/etc/vigilo/vigiboard/vigiboard.wsgi"

    KeepAlive Off

    <Directory "/etc/vigilo/vigiboard/">
    <Files "vigiboard.wsgi">
    WSGIProcessGroup vigiboard
    WSGIApplicationGroup %{GLOBAL}

    Order deny,allow
    Allow from all
    </Files>
    </Directory>

L'option ``WSGIRestrictStdout`` est positionnée à ``off`` afin d'éviter
qu'Apache ne tue le processus de l'application lorsque des données sont
envoyées sur la sortie standard. Ceci permet de récupérer les erreurs critiques
pouvant être émises par l'application. Ces erreurs apparaissent alors dans le
journal des événements d'Apache (configuré par la directive ``error_log``).

L'option ``WSGIPassAuthorization`` positionnée à ``on`` indique à Apache et
mod_wsgi que les informations d'authentification éventuellement transmises par
l'utilisateur doivent être transmises à VigiBoard. En effet, Vigilo utilise son
propre mécanisme de gestion de l'authentification et des autorisations (voir la
documentation intitulée Vigilo - Authentification et autorisation) et utilise
donc ces informations.

L'option ``WSGIDaemonProcess`` permet de créer un groupe de processus affecté
au traitement des requêtes HTTP destinées à VigiBoard. Il permet d'utiliser un
nom d'utilisateur et un groupe prédéfini (afin de réduire les privilèges
nécessaires), ainsi que le nombre de processus légers à utiliser pour traiter
les requêtes (ici, 2).

L'option ``WSGIScriptAlias`` indique l'emplacement à partir duquel VigiBoard
sera accessible (ici, ``http://example.com/vigilo/vigiboard`` si le serveur
Apache est configuré pour le domaine ``example.com``) et l'emplacement du script
WSGI nécessaire au lancement de l'application (voir le chapitre suivant).

L'option ``KeepAlive`` positionnée à ``off`` est nécessaire afin de contourner
un problème dans le module ``mod_wsgi`` d'Apache.

Les autres options permettent d'exécuter le script WSGI de VigiBoard à l'aide
du groupe de processus défini précédemment.

La liste complète des directives de configuration supportées par le module
``mod_wsgi`` d'Apache est disponible `dans la documentation officielle
<http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives>`_.

Script WSGI de VigiBoard
^^^^^^^^^^^^^^^^^^^^^^^^
Le script WSGI de VigiBoard est un script Python très simple qui a pour but de
démarrer l'exécution de VigiBoard à partir du fichier de configuration associé
(``/etc/vigilo/vigiboard/settings.ini``).

Vous n'avez généralement pas besoin de modifier son contenu, sauf
éventuellement pour adapter l'emplacement du fichier de configuration en
fonction de votre installation.



Annexes
=======

.. include:: ../../turbogears/doc/glossaire.rst


.. vim: set tw=79 :
