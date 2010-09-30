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
Requires:   python26-tw-forms
Requires:   mod_wsgi-python26

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
make install \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
	PYTHON=%{__python}

# %find_lang %{name} # ne fonctionne qu'avec les fichiers dans /usr/share/locale/


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
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
