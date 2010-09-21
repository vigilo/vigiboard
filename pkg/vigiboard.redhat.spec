%define module  vigiboard
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}%{?dist}

%define pyver 26
%define pybasever 2.6
%define __python /usr/bin/python%{pybasever}
%define __os_install_post %{__python26_os_install_post}
%{!?python26_sitelib: %define python26_sitelib %(python26 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       %{name}
Summary:    Vigilo event board
Version:    %{version}
Release:    %{release}
Source0:    %{module}-%{version}.tar.gz
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python26-distribute
BuildRequires:   python26-babel

Requires:   python26-distribute
Requires:   vigilo-turbogears
Requires:   python26-tw.forms
Requires:   apache-mod_wsgi
######### Dependance from python dependance tree ########
Requires:   vigilo-vigiboard
Requires:   vigilo-common
Requires:   vigilo-models
Requires:   vigilo-themes-default
Requires:   vigilo-turbogears
Requires:   python26-addons
Requires:   python26-babel
Requires:   python26-beaker
Requires:   python26-bytecodeassembler
Requires:   python26-configobj
Requires:   python26-decorator
Requires:   python26-decoratortools
Requires:   python26-EggTranslations
Requires:   python26-extremes
Requires:   python26-formencode
Requires:   python26-genshi
Requires:   python26-mako
Requires:   python26-nose
Requires:   python26-paste
Requires:   python26-pastedeploy
Requires:   python26-pastescript
Requires:   python26-peak-rules
Requires:   python26-prioritized_methods
Requires:   python26-psycopg2
Requires:   python26-pygments
Requires:   python26-pylons
Requires:   python26-dateutil
Requires:   python26-repoze.tm2
Requires:   python26-repoze.what
Requires:   python26-repoze.what.plugins.sql
Requires:   python26-repoze.what-pylons
Requires:   python26-repoze.what-quickstart
Requires:   python26-repoze.who
Requires:   python26-repoze.who-friendlyform
Requires:   python26-repoze.who.plugins.sa
Requires:   python26-repoze.who-testutil
Requires:   python26-routes
Requires:   python26-rum
Requires:   python26-RumAlchemy
Requires:   python26-distribute
Requires:   python26-simplejson
Requires:   python26-sqlalchemy
Requires:   python26-sqlalchemy-migrate
Requires:   python26-symboltype
Requires:   python26-tempita
Requires:   python26-tg.devtools
Requires:   python26-TgRum
Requires:   python26-toscawidgets
Requires:   python26-transaction
Requires:   python26-turbogears2
Requires:   python26-turbojson
Requires:   python26-tw.dojo
Requires:   python26-tw.forms
Requires:   python26-tw.rum
Requires:   python26-weberror
Requires:   python26-webflash
Requires:   python26-webhelpers
Requires:   python26-webob
Requires:   python26-webtest
Requires:   python26-zope-interface
Requires:   python26-zope.sqlalchemy

# Renommage
Obsoletes: vigiboard < 1.0-1
Provides:  vigiboard = %{version}-%{release}


%description
Vigilo event board.
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q -n %{module}-%{version}

%build
make PYTHON=%{__python} SYSCONFDIR=%{_sysconfdir}

%install
rm -rf $RPM_BUILD_ROOT
make install_files \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
	PYTHON=%{__python}

# %find_lang %{name} # ne fonctionne qu'avec les fichiers dans /usr/share/locale/


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyo
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyc
%{_sysconfdir}/httpd/conf.d/%{module}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python26_sitelib}/*
