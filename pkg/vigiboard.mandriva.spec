%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    1%{?svn}%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-setuptools
BuildRequires:   python-babel

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   vigilo-turbogears
Requires:   python-tw.forms
Requires:   apache-mod_wsgi
######### Dependance from python dependance tree ########
Requires:   vigilo-common
Requires:   vigilo-models
Requires:   vigilo-themes-default
Requires:   vigilo-turbogears
Requires:   python-addons
Requires:   python-babel
Requires:   python-beaker
Requires:   python-bytecodeassembler
Requires:   python-configobj
Requires:   python-decorator
Requires:   python-decoratortools
Requires:   python-EggTranslations
Requires:   python-extremes
Requires:   python-formencode
Requires:   python-genshi
Requires:   python-mako
Requires:   python-nose
Requires:   python-paste
Requires:   python-pastedeploy
Requires:   python-pastescript
Requires:   python-peak-rules
Requires:   python-prioritized_methods
Requires:   python-psycopg2
Requires:   python-pygments
Requires:   python-pylons
Requires:   python-dateutil
Requires:   python-repoze.tm2
Requires:   python-repoze.what
Requires:   python-repoze.what.plugins.sql
Requires:   python-repoze.what-pylons
Requires:   python-repoze.what-quickstart
Requires:   python-repoze.who
Requires:   python-repoze.who-friendlyform
Requires:   python-repoze.who.plugins.sa
Requires:   python-repoze.who-testutil
Requires:   python-routes
Requires:   python-rum
Requires:   python-RumAlchemy
Requires:   python-setuptools
Requires:   python-simplejson
Requires:   python-sqlalchemy
Requires:   python-sqlalchemy-migrate
Requires:   python-symboltype
Requires:   python-tempita
Requires:   python-tg.devtools
Requires:   python-TgRum
Requires:   python-toscawidgets
Requires:   python-transaction
Requires:   python-turbogears2
Requires:   python-turbojson
Requires:   python-tw.dojo
Requires:   python-tw.forms
Requires:   python-tw.rum
Requires:   python-weberror
Requires:   python-webflash
Requires:   python-webhelpers
Requires:   python-webob
Requires:   python-webtest
Requires:   python-zope-interface
Requires:   python-zope.sqlalchemy


%description
@DESCRIPTION@
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
make install_pkg \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
	LOCALSTATEDIR=%{_localstatedir} \
	PYTHON=%{__python}

%find_lang %{name}


%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%config(noreplace) /etc/httpd/conf/webapps.d/%{module}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) /etc/logrotate.d/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python_sitelib}/*

