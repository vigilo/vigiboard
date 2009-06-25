########################
#    Désactiver l'environement virtuel
########################

Editer le fichier apache/dashboard.wsgi et commenter la section 3

########################
#    Configuration de l'application
########################

Les variables de configuration de l'application (par exemple les liens externes)
sont dans le fichier dashboard/config/dashboard_config.py

########################
#    Installation des Eggs
########################

Installer la liste des Eggs du fichier README_Eggs_Requis.txt en utilisant easy_install

Pour JQuery, pour avoir UI.Dialog, il faut :

1 ) Ajouter la ligne suivante au fichier /path/to/lib/python2.6/site-packages/tw.jquery-0.9.4.5-py2.6.egg/tw/jquery/__init__.py
from tw.jquery.ui_dialog import JQueryUIDialog
2 ) Copier le fichier README_jquery/ui_dialog.py vers /path/to/lib/python2.6/site-packages/tw.jquery-0.9.4.5-py2.6.egg/tw/jquery/ui_dialog.py
3 ) Copier les fichiers README_jquery/static/css vers /path/to/lib/python2.6/site-packages/tw.jquery-0.9.4.5-py2.6.egg/tw/jquery/static/css

