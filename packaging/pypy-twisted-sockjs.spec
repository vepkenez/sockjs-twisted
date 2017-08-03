Name:		pypy-twisted-sockjs
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

BuildRequires:	pypy-portable

Requires:	pypy-portable
Requires:	pypy-twisted

%description
A simple library for adding SockJS support to your twisted application.

%prep
%setup -q -n %{_sources_}

%build
CFLAGS="$RPM_OPT_FLAGS" pypy setup.py build

%install
# Ensure root is clean
rm -rf %{buildroot}

# Run install script
pypy setup.py install \
	--skip-build \
	--root $RPM_BUILD_ROOT

%post
# Regenerate Twisted plugin cache
pypy -c 'from twisted.plugin import IPlugin, getPlugins; list(getPlugins(IPlugin))'

%clean
rm -rf $RPM_BUILD_ROOT

%files
/usr/lib/python2.6/site-packages

%changelog
* Thu Aug 03 2017 Julien Tagneres <jtag@interact-iv.com> 1.2.2-5
- First attempt at packaging with pypy.
- Fixed compatibility issues with pypy.

* Wed Nov 30 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.2-4
- Fixed hardcoded 5 seconds timeout.

* Mon Sep 12 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.2-3
- Fixed default sockjs_url value for python2.6 (incompatibility with format).
- Fixed issue in writeSequence (attempt to modify a tuple).

* Mon Jul 11 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.2-2
- Changed default sockjs_url value and made sure an url is inserted even if
the option is missing (different class).

* Thu Apr 28 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.2
- Added reason to timeout related disconnections.

* Wed Apr 13 2016 Julien Tagneres <jtag@interact-iv.com> 1.2.1-9
- Fixed connection close reason not being forwarded.

* Wed Nov 19 2014 Julien Tagneres <jtag@interact-iv.com> 1.2.1-8
- Fixed connection loss not being detected.

* Mon Oct 27 2014 Julien Tagneres <jtag@interact-iv.com> 1.2.1-1
- First attempt at building python-twisted-sockjs.
- Merged pull request #15 from frog32 (websocket Heartbeat).
