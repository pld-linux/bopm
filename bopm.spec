%include	/usr/lib/rpm/macros.perl
Summary:	Open proxy monitor and blocker, designed for use with ircds
Summary(pl):	Monitorowanie i blokowanie otwartych proxy do u¿ywania z ircd
Name:		bopm
Version:	3.1.2
Release:	0.17
License:	GPL
Group:		Applications/Communications
Source0:	http://static.blitzed.org/www.blitzed.org/bopm/files/%{name}-%{version}.tar.gz
# Source0-md5:	ab1b7494c4242eef957b5fca61c92b18
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-shared.patch
URL:		http://www.blitzed.org/bopm/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts >= 0.4.0.17
Provides:	group(%{name})
Provides:	user(%{name})
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%description -l pl
Blitzed Open Proxy Monitor jest zaprojektowany tak, ¿e ³±czy siê z
serwerem IRC i staje operatorem. Nastêpnie ogl±da informacje o
po³±czeniach w celu skanowania wszystkich klientów pod k±tem otwartych
(niebezpiecznych) proxy. Takie niebezpieczne proxy zwykle s± u¿ywane
do spamowania, floodowania i innych nadu¿yæ.

BOPM jest w stanie wykryæ WinGates, proxy HTTP, proxy SOCKS 4/5 oraz
routery Cisco z domy¶lnymi has³ami. BOPM obs³uguje tak¿e sprawdzanie
czarnych list opartych na DNS (takich jak MAPS RBL) i mo¿e byæ
skonfigurowany do zg³aszania nowych proxy z powrotem do projektu
Blitzed Open Proxy Monitoring.

%package libs
Summary:	libopm open proxy scanning library
Group:		Libraries

%description libs
libopm open proxy scanning library.

%package devel
Summary:	Header files for libopm library
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This is the package containing the header files for libopm library.

%package static
Summary:	Static ... library
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libopm library.

%package -n perl-OPM
Summary:	OPM - Perl interface to libopm open proxy scanning library
Group:		Development/Languages/Perl
Requires:	%{name}-libs = %{version}-%{release}
# should here be Version: 0.01 due to "Provides: OPM.so perl(OPM) = 0.01"?

%description -n perl-OPM
OPM - Perl interface to libopm open proxy scanning library.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

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

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/{run,log}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
> $RPM_BUILD_ROOT/var/log/%{name}/bopm.log
> $RPM_BUILD_ROOT/var/log/%{name}/scan.log

cd src/libopm/OPM
%{__make} pure_install \
	DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{perl_vendorarch}/auto/OPM/.packlist
install -d $RPM_BUILD_ROOT%{_examplesdir}/perl-OPM-%{version}
mv $RPM_BUILD_ROOT{%{perl_vendorarch},%{_examplesdir}/perl-OPM-%{version}}/bopchecker.pl

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 151 %{name}
%useradd -u 151 -c "BOPM Daemon" -g %{name} %{name}

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "BOPM daemon"

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
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
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/%{name}

%attr(770,root,bopm) %dir /var/run/%{name}
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

%files -n perl-OPM
%defattr(644,root,root,755)
%{perl_vendorarch}/OPM.pm
%dir %{perl_vendorarch}/auto/OPM
%{perl_vendorarch}/auto/OPM/OPM.bs
%attr(755,root,root) %{perl_vendorarch}/auto/OPM/OPM.so
%{_examplesdir}/perl-OPM-%{version}
%{_mandir}/man3/OPM.3pm*
