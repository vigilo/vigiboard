��    �      <              \     ]     n     {     �  3   �  2   �  H     0   P  x   �  �   �  S  �  �    $     �   '  
    R        j     w  
   ~     �  &   �     �     �     �     �  i        m     s     �     �     �     �  .   �     �       -   $  !   R  �  t               0     ?     R     g     o     x     �  �   �     (     @  I   ]     �  &   �     �     �  
             "     5     A     [     s     �     �     �     �     �     �  �   �     _     }     �     �     �  7   �  =   �     <  
   B     M     T     `     f     x     ~     �     �  	   �     �     �     �     �    �       ,        L  Q   `     �     �  	   �     �     �     �     
  /        H     O     \     s     �     �     �     �  
   �     �     �     �     �     
         C   /      s   "   x      �      �   M   �   P   !  �   ]!     W"  �  l"  �   E%  �   	&     �&  N   �&     �&     �&  
   '  \   '  t   j'     �'  7   �'     (     1(  	   6(     @(  	   F(     P(     i(     q(     �(  M   �(  '   �(  R   )     d)    v)     �*     �*  �   �*  :   [+  �   �+     j,     q,     �,     �,  >   �,  #   �,     �,      -     -  	   .-     8-     D-  �   P-    :.     R/     a/     x/  ^  �/     �0     �0     �0     �0      1  	   '1     11  K  81     �2     �2     �2     �2     �2    �2     �3     �3     �3     �3  �  
4     �5     �5     �5     �5  3   �5  2   6  H   D6  0   �6  x   �6  �   77  S  �7  �  J9  $   ?;  �   d;  
  I<  R   T=     �=     �=  
   �=     �=  &   �=     �=     >     >     !>  i   @>     �>     �>     �>     �>     �>  	   ?  .   ?     ;?     Y?  -   j?  !   �?  �  �?     NA     hA     zA     �A     �A     �A     �A     �A     �A  �   �A     ~B     �B  I   �B  *   �B  -   (C     VC     eC     yC     �C     �C     �C     �C     �C     �C     D     *D  
   GD     RD     WD     ]D  �   `D     �D     
E     E     !E     7E  7   SE  =   �E     �E     �E     �E     �E     �E     �E     F     F     /F  !   NF     pF     �F     �F     �F     �F    �F     �G  7   �G     H  Q   &H     xH     �H     �H     �H     �H     �H     �H  /   �H  
   I     %I     >I     [I     rI     zI  #   �I     �I  	   �I     �I     �I     �I     �I     �I     
J  C   J     bJ  "   gJ     �J     �J  M   �J  P   �J  �   LK     FL  �  `L  �   9O  �   �O     �P  N   �P     �P     �P  
    Q  \   Q  t   hQ     �Q  7   �Q     R     0R     <R     NR  	   UR  ,   _R     �R     �R     �R  M   �R  '   S  R   /S     �S    �S     �T     �T  �   �T  :   U  �   �U     �V     �V     �V     �V  >   �V  #   �V     W     $W     8W  	   RW     \W     hW  �   tW    ^X     vY     �Y     �Y  ^  �Y     [     [     [     [      +[  	   L[     V[  K  ][     �\     �\     �\     �\     �\    �\     �]     �]     ^     ^   " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under About About this page Admin All objects from locals(): Another protected resource is Apply Architectural basics of a quickstart TG2 site. Aucun évènement disponible. Authentication Authentication & Authorization in a TG2 site. Back to your Quickstart Home page But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Change to Acknowledged Change to Closed Change to None Code my data model Code your data model Contact Critical Current State: Date<br />[Duration] Decide your URLs, Program your controller methods, Design your 
            templates, and place some static files (CSS and/or JavaScript). Design my URL structure Design your URL architecture Design your data model, Create the database, and Add some bootstrap data. Detailed history for this event Detailed history for this host/service Developing TG2 Distribute your app Edit Event Error Error has Occurred Error in DB Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! History Home Host ID If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Initial Initial State: Join the TG Mail List Join the TG-Trunk Mail List Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Login Login Form Logout Maintenance Major Metrology details Minor More TG2 Documents Nagios host details No access to this event No change None Now Viewing: Now try to visiting the OK Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Only for managers Only for people with the "manage" permission Only for the editor Only managers are authorized to visit this method. You will need to log-in using: Output Pages Password: Powered by TurboGears 2 Presentation Reuse the web page elements SHNs impacté Sample Template, for looking at template locals Search Search Event Secure Controller here Security details Service Service Type Service Type<br />Service Name Showing rows Suppressed TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Test your source, Generate project documents, Build a distribution. Text Thank you for choosing TurboGears. The " The Python web metaframework The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: There is no history. There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). Time To change the comportement of this setup-app command you just need to edit the Touble Ticket Trouble Ticket TurboGears TurboGears 2 is rapid web application development toolkit designed to make your life easier. TurboGears is a open source front-to-back web development
      framework written in Python. Copyright (c) 2005-2008 Type URL. You will be challenged with a login/password form. Updated successfully User Username: Value Vigiboard We hope to see you soon! Welcome Welcome back, %s! Welcome to TurboGears 2 Welcome to TurboGears 2.0, standing on the 
  shoulders of giants, since 2007 What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the Wrong credentials You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. You need to be authenticated about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. of or password: managepass paster setup-app development.ini py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: to to be able to access it. websetup.py with a password of Project-Id-Version: vigiboard 0.1
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2009-07-06 11:19+0200
PO-Revision-Date: 2009-07-06 11:45+0200
Last-Translator: Thomas ANDREJAK <thomas.andrejak@c-s.fr>
Language-Team: fr_FR <LL@li.org>
Plural-Forms: nplurals=2; plural=(n > 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.4
 " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under A propos About this page Admin All objects from locals(): Another protected resource is Appliquer Architectural basics of a quickstart TG2 site. Aucun évènement disponible. Authentification Authentication & Authorization in a TG2 site. Back to your Quickstart Home page But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Changer en Pris en compte Changer en Fermé Changer en Non pris en compte Code my data model Code your data model Contact Critique Statu actuel: Date<br />[Durée] Decide your URLs, Program your controller methods, Design your 
            templates, and place some static files (CSS and/or JavaScript). Design my URL structure Design your URL architecture Design your data model, Create the database, and Add some bootstrap data. Historique détaillé pour cet évènement Historique détaillé pour ce hôte / service Developing TG2 Distribute your app Edition d'évènements Erreur Error has Occurred Erreur dans la base de données Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! Historique Home Hôte ID If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Initial Statu initial: Join the TG Mail List Join the TG-Trunk Mail List Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Login Formulaire de login Logout Maintenance Majeur Détails de métrologie Mineur More TG2 Documents Détails de l'hôte par Nagios Accès à cet évènement refusé Sans changement Aucun Page: Now try to visiting the OK Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Réservé aux Managers Réservé aux utilisateurs ayant la permission "manage" Réservé aux Editeurs Only managers are authorized to visit this method. You will need to log-in using: Sortie d'erreur Pages Mot de passe Powered by TurboGears 2 Presentation Reuse the web page elements SHNs impacté Sample Template, for looking at template locals Rechercher Recherche d'évènements Ici : Controlleur sécurisé Détails de sécurité Service Type de service Type de service<br />Nom du service Lignes Supprimé TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Test your source, Generate project documents, Build a distribution. Text Thank you for choosing TurboGears. The " The Python web metaframework The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: Il n'y a pas d'historique There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). Temps To change the comportement of this setup-app command you just need to edit the Ticket d'incidence Ticket d'incidence TurboGears TurboGears 2 is rapid web application development toolkit designed to make your life easier. TurboGears is a open source front-to-back web development
      framework written in Python. Copyright (c) 2005-2008 Type URL. You will be challenged with a login/password form. Mise à jour réussie Utilisateur Nom d'utilisateur Valeur Vigiboard Nous espérons vous revoir très rapidement! Bonjour Bienvenu %s! Welcome to TurboGears 2 Welcome to TurboGears 2.0, standing on the 
  shoulders of giants, since 2007 What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the Paramètres incorrects You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. Vous devez être authentifié about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. sur or password: managepass paster setup-app development.ini py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: à to be able to access it. websetup.py with a password of 