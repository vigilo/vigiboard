VigiBoard
=========

VigiBoard est l'interface web de Vigilo_ orientée "bac à évènements". Les
évènements du parc supervisé sont présentés sous la forme d'un tableau, triés
par priorité.

VigiBoard est à destination de l'exploitant niveau 1, pour qui il constitue
une sorte de "liste des tâches" à traiter dans l'ordre.

Pour les détails du fonctionnement de VigiBoard, se reporter à la
`documentation officielle`_.


Dépendances
-----------
Vigilo nécessite une version de Python supérieure ou égale à 2.5. Le chemin de
l'exécutable python peut être passé en paramètre du ``make install`` de la
façon suivante::

    make install PYTHON=/usr/bin/python2.6

VigiBoard a besoin des modules Python suivants :

- setuptools (ou distribute)
- vigilo-turbogears
- tw.forms


Installation
------------
L'installation se fait par la commande ``make install`` (à exécuter en
``root``).

Après avoir configuré VigiBoard dans le fichier
``/etc/vigilo/vigiboard/settings.ini``, il faut initialiser la base de données
par la commande ``vigilo-updatedb``. Enfin, il faut redémarrer Apache pour
qu'il prenne en compte le nouveau fichier de configuration de VigiBoard.

L'accès à l'interface se fait avec les identifiants suivants :

 - login : ``manager``
 - mot de passe : ``iddad``


License
-------
VigiBoard est sous licence `GPL v2`_.


.. _documentation officielle: Vigilo_
.. _Vigilo: http://www.vigilo-nms.com
.. _GPL v2: http://www.gnu.org/licenses/gpl-2.0.html

.. vim: set syntax=rst fileencoding=utf-8 tw=78 :


