%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    @RELEASE@%{?dist}
Source0:    %{name}-%{version}@PREVERSION@.tar.gz
URL:        @URL@
Group:      Applications/System
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-distribute
BuildRequires:   python-babel

Requires:   python-distribute
Requires:   vigilo-turbogears
Requires:   python-tw-forms

%description
@DESCRIPTION@
This application is part of the Vigilo Project <https://www.vigilo-nms.com>

%prep
%setup -q -n %{name}-%{version}@PREVERSION@

%build

%install
rm -rf $RPM_BUILD_ROOT
make install_pkg \
    DESTDIR=$RPM_BUILD_ROOT \
    SYSCONFDIR=%{_sysconfdir} \
    LOCALSTATEDIR=%{_localstatedir} \
    PYTHON=%{__python}


%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%exclude %{_sysconfdir}/vigilo/%{module}/*.pyc
%exclude %{_sysconfdir}/vigilo/%{module}/*.pyo
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python_sitelib}/*
%attr(755,root,root) %{_sysconfdir}/cron.daily/*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
