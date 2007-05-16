# TODO
# - ac that i don't know how to fix:
#+ autoconf
#configure.in:51: error: possibly undefined macro: AC_FUNC_SNPRINTF
#      If this token and others are legitimate, please use m4_pattern_allow.
#      See the Autoconf documentation.
#
#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
%bcond_without	supervise	# install initscript instead of supervise
#
%include	/usr/lib/rpm/macros.perl
%define		pnam	OPM
Summary:	Open proxy monitor and blocker, designed for use with ircds
Summary(pl.UTF-8):	Monitorowanie i blokowanie otwartych proxy do używania z ircd
Name:		bopm
Version:	3.1.3
Release:	0.1
License:	GPL
Group:		Applications/Communications
Source0:	http://static.blitzed.org/www.blitzed.org/bopm/files/%{name}-%{version}.tar.gz
# Source0-md5:	643c7090b32dfe09a38b5440b2c480e3
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-supervise.tar.bz2
# Source3-md5:	247c0438a5e2860097d09a374a521151
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-shared.patch
Patch2:		%{name}-cr-connect.patch
Patch3:		http://www.nedworks.org/bopm/%{name}.whitelists.3.1.2.diff
Patch4:		http://dgl.cx/2006/09/bopm-conf-cmd.diff
URL:		http://wiki.blitzed.org/BOPM
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.268
%{!?with_supervise:Requires(post,preun):	/sbin/chkconfig}
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
%{!?with_supervise:Requires:	rc-scripts >= 0.4.0.17}
%{?with_supervise:Requires:	daemontools >= 0.76-5}
Provides:	group(%{name})
Provides:	user(%{name})
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_supervise	/etc/supervise/%{name}

%description
The Blitzed Open Proxy Monitor is designed to connect to an IRC server
and become an IRC operator. It then watches connect notices in order
to scan all connecting clients for open (insecure) proxies. Such
insecure proxies are commonly used for spamming, floods and other
abusive activities.

BOPM can detect WinGates, HTTP proxies, SOCKS 4/5 proxies and Cisco
routers with default passwords. BOPM also has support for checking
against a DNS-Based Blacklist (similar to MAPS RBL) and can be
configured to report new proxies back to the Blitzed Open Proxy
Monitoring project.

%description -l pl.UTF-8
Blitzed Open Proxy Monitor jest zaprojektowany tak, że łączy się z
serwerem IRC i staje operatorem. Następnie ogląda informacje o
połączeniach w celu skanowania wszystkich klientów pod kątem otwartych
(niebezpiecznych) proxy. Takie niebezpieczne proxy zwykle są używane
do spamowania, floodowania i innych nadużyć.

BOPM jest w stanie wykryć WinGates, proxy HTTP, proxy SOCKS 4/5 oraz
routery Cisco z domyślnymi hasłami. BOPM obsługuje także sprawdzanie
czarnych list opartych na DNS (takich jak MAPS RBL) i może być
skonfigurowany do zgłaszania nowych proxy z powrotem do projektu
Blitzed Open Proxy Monitoring.

%package libs
Summary:	libopm open proxy scanning library
Summary(pl.UTF-8):	Biblioteka libopm do szukania otwartych proxy
Group:		Libraries

%description libs
libopm open proxy scanning library.

%description libs -l pl.UTF-8
Biblioteka libopm do szukania otwartych proxy.

%package devel
Summary:	Header files for libopm library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libopm
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This is the package containing the header files for libopm library.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe biblioteki libopm.

%package static
Summary:	Static libopm library
Summary(pl.UTF-8):	Statyczna biblioteka libopm
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libopm library.

%description static -l pl.UTF-8
Statyczna biblioteka libopm.

%package -n perl-%{pnam}
Summary:	OPM - Perl interface to libopm open proxy scanning library
Summary(pl.UTF-8):	OPM - perlowy interfejs do biblioteki libopm szukającej otwartych proxy
Group:		Development/Languages/Perl
Requires:	%{name}-libs = %{version}-%{release}
# should here be Version: 0.01 due to "Provides: OPM.so perl(OPM) = 0.01"?

%description -n perl-%{pnam}
OPM - Perl interface to libopm open proxy scanning library.

%description -n perl-%{pnam} -l pl.UTF-8
OPM - perlowy interfejs do biblioteki libopm szukającej otwartych
proxy.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p0
cd src
%patch4 -p0

# we include contrib in %doc. cleanup it
find -name CVS | xargs -r rm -rf
rm -f contrib/bopm.spec

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--localstatedir=/var/log/%{name} \
	--bindir=%{_sbindir}

%{__make}

cd src/libopm/OPM
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make} \
	OPTIMIZE="%{rpmcflags}"
%{?with_tests:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/log/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with supervise}
install -d $RPM_BUILD_ROOT%{_supervise}
tar xf %{SOURCE3} -C $RPM_BUILD_ROOT%{_supervise}

install -d $RPM_BUILD_ROOT%{_supervise}/{,log/}supervise
touch $RPM_BUILD_ROOT%{_supervise}/{,log/}supervise/lock
touch $RPM_BUILD_ROOT%{_supervise}/{,log/}supervise/status
mkfifo $RPM_BUILD_ROOT%{_supervise}/{,log/}supervise/control
mkfifo $RPM_BUILD_ROOT%{_supervise}/{,log/}supervise/ok

%else
install -D %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -d $RPM_BUILD_ROOT/var/run/%{name}
%endif

install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
> $RPM_BUILD_ROOT/var/log/%{name}/bopm.log
> $RPM_BUILD_ROOT/var/log/%{name}/scan.log

# Perl module
cd src/libopm/OPM
%{__make} pure_install \
	DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{perl_vendorarch}/auto/%{pnam}/.packlist
install -d $RPM_BUILD_ROOT%{_examplesdir}/perl-%{pnam}-%{version}
mv $RPM_BUILD_ROOT{%{perl_vendorarch},%{_examplesdir}/perl-%{pnam}-%{version}}/bopchecker.pl

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 151 %{name}
%useradd -u 151 -c "BOPM Daemon" -g %{name} %{name}

%post
%if %{with supervise}
if [ -d /service/%{name}/supervise ]; then
	svc -t /service/%{name} /service/%{name}/log
fi
if [ "$1" = 1 ]; then
	ln -snf %{_supervise} /service/%{name}
fi
%else
/sbin/chkconfig --add %{name}
%service %{name} restart "BOPM daemon"
%endif

%preun
if [ "$1" = "0" ]; then
%if %{with supervise}
	if [ -d /service/%{name}/supervise ]; then
		cd /service/%{name}
		rm /service/%{name}
		svc -dx . log
	fi
%else
	%service %{name} stop
	/sbin/chkconfig --del %{name}
%endif
fi

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog INSTALL README bopm.conf.sample
%doc contrib/ network-bopm/
%attr(640,root,bopm) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf
%attr(755,root,root) %{_sbindir}/%{name}

%if %{with supervise}
%attr(1755,root,root) %dir %{_supervise}
%attr(755,root,root) %{_supervise}/run
%attr(700,root,root) %dir %{_supervise}/supervise

%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %ghost %{_supervise}/supervise/*
%attr(1755,root,root) %dir %{_supervise}/log
%attr(755,root,root) %{_supervise}/log/run
%attr(700,root,root) %dir %{_supervise}/log/supervise
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %ghost %{_supervise}/log/supervise/*
%else
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(770,root,bopm) %dir /var/run/%{name}
%endif

%attr(770,root,bopm) %dir /var/log/%{name}
%attr(640,bopm,bopm) %ghost /var/log/%{name}/bopm.log
%attr(640,bopm,bopm) %ghost /var/log/%{name}/scan.log

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopm.so.*.*.*

%files devel
%defattr(644,root,root,755)
%{_includedir}/opm.h
%{_includedir}/opm_common.h
%{_includedir}/opm_error.h
%{_includedir}/opm_types.h
%{_libdir}/libopm.la

%files static
%defattr(644,root,root,755)
%{_libdir}/libopm.a

%files -n perl-%{pnam}
%defattr(644,root,root,755)
%{perl_vendorarch}/OPM.pm
%dir %{perl_vendorarch}/auto/OPM
%{perl_vendorarch}/auto/OPM/OPM.bs
%attr(755,root,root) %{perl_vendorarch}/auto/OPM/OPM.so
%{_examplesdir}/perl-OPM-%{version}
%{_mandir}/man3/OPM.3pm*
