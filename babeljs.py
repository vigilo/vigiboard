# -*- coding: utf-8 -*-
"""
Provides a class derived from Babel's compile_catalog
which automatically creates JavaScript files compatible
with Babel's JavaScript frontend.

This code was taken from:
http://svn.python.org/projects/doctools/trunk/setup.py

And generates files for use with:
http://babel.edgewall.org/browser/trunk/contrib/babel.js
"""
try:
    from babel.messages.pofile import read_po
    from babel.messages.frontend import compile_catalog
    try:
        from simplejson import dump
    except ImportError:
        from json import dump
except ImportError:
    pass
else:
    import os
    from distutils import log

    class compile_catalog_plusjs(compile_catalog):
        """
        An extended command that writes all message strings that occur in
        JavaScript files to a JavaScript file along with the .mo file.

        Unfortunately, babel's setup command isn't built very extensible, so
        most of the run() code is duplicated here.
        """

        def run(self):
            compile_catalog.run(self)

            po_files = []
            js_files = []

            if isinstance(self.domain, list):
                domains = self.domain
            else:
                domains = [self.domain]

            if not self.input_file:
                if self.locale:
                    for domain in domains:
                        basename = os.path.join(self.directory, self.locale,
                                                'LC_MESSAGES', domain)
                        po_files.append( (self.locale, basename + '.po') )
                        js_files.append( basename + '.js')
                else:
                    for locale in os.listdir(self.directory):
                        for domain in domains:
                            basename = os.path.join(self.directory, locale,
                                                    'LC_MESSAGES', domain)
                            if os.path.exists(basename + '.po'):
                                po_files.append( (locale, basename + '.po') )
                                js_files.append(basename + '.js')
            else:
                po_files.append( (self.locale, self.input_file) )
                if self.output_file:
                    js_files.append(self.output_file)
                else:
                    for domain in domains:
                        js_files.append(os.path.join(
                            self.directory,
                            self.locale,
                            'LC_MESSAGES',
                            domain + '.js'
                         ))

            for js_file, (locale, po_file) in zip(js_files, po_files):
                infile = open(po_file, 'r')
                try:
                    catalog = read_po(infile, locale)
                finally:
                    infile.close()

                if catalog.fuzzy and not self.use_fuzzy:
                    continue

                log.info('writing JavaScript strings in catalog %r to %r',
                         po_file, js_file)

                jscatalog = {}
                for message in catalog:
                    # Si le message n'a pas encore été traduit,
                    # on ne l'ajoute pas. Le message d'origine
                    # (non traduit) sera renvoyé.
                    if not message.string:
                        continue

                    # On n'ajoute le message au fichier de traduction JS
                    # auto-généré que si le message est utilisé dans du
                    # code JavaScript.
                    if any(x[0].endswith('.js') for x in message.locations):
                        msgid = message.id
                        if isinstance(msgid, (list, tuple)):
                            msgid = msgid[0]
                        jscatalog[msgid] = message.string

                outfile = open(js_file, 'wb')
                try:
                    outfile.write('babel.Translations.load(');
                    dump(dict(
                        messages=jscatalog,
                        plural_expr=catalog.plural_expr,
                        locale=str(catalog.locale)
                        ), outfile)
                    outfile.write(').install();')
                finally:
                    outfile.close()
