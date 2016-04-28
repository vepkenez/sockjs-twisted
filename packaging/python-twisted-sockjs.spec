Name:		python-twisted-sockjs
Version:	%{_iv_pkg_version}
Release:	%{_iv_pkg_release}%{?dist}
Summary:	A simple library for adding SockJS support to your twisted application.

%define		_package_	%{name}-%{version}
%define		_sources_	txsockjs-%{version}

Group:		Applications/System
License:	BSD
URL:		https://pypi.python.org/pypi/txsockjs
Source0:	%{_sources_}.tar.gz
BuildRoot:	%{_tmppath}/%{_package_}-%{release}-root-%(%{__id_u} -n)

BuildArch:		noarch

BuildRequires:	python-devel python-setuptools
BuildRequires:	python-twisted >= 13.2.0-1

Requires:	python
Requires:	python-twisted >= 13.2.0-1

%description
A simple library for adding SockJS support to your twisted application.

%prep
%setup -q -n %{_sources_}


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
# Ensure root is clean
rm -rf %{buildroot}

# Run install script
%{__python} setup.py install \
	--skip-build \
	--root $RPM_BUILD_ROOT \
	--prefix /usr

%post
# Regenerate Twisted plugin cache
%{__python} -c 'from twisted.plugin import IPlugin, getPlugins; list(getPlugins(IPlugin))'

%clean
rm -rf $RPM_BUILD_ROOT

%files
/usr/lib/python2.6/site-packages

%changelog
* Thu Apr 28 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.2
- Added reason to timeout related disconnections.

* Wed Apr 13 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.1-9
- Fixed connection close reason not being forwarded.

* Wed Nov 19 2014 Julien Tagneres <jtag@interact-iv.com> 1.2.1-8
- Fixed connection loss not being detected.

* Mon Oct 27 2014 Julien Tagneres <jtag@interact-iv.com> 1.2.1-1
- First attempt at building python-twisted-sockjs.
- Merged pull request #15 from frog32 (websocket Heartbeat).
