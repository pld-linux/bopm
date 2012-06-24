# TODO: user/group removal
Summary:	Open proxy monitor and blocker, designed for use with ircds
Summary(pl):	Monitorowanie i blokowanie otwartych proxy do u�ywania z ircd
Name:		bopm
Version:	3.1.2
Release:	0.10
Epoch:		0
License:	GPL
Group:		Applications/Communications
Source0:	http://static.blitzed.org/www.blitzed.org/bopm/files/%{name}-%{version}.tar.gz
# Source0-md5:	ab1b7494c4242eef957b5fca61c92b18
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-DESTDIR.patch
URL:		http://www.blitzed.org/bopm/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	rpmbuild(macros) >= 1.202
PreReq:		rc-scripts >= 0.4.0.17
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
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
Blitzed Open Proxy Monitor jest zaprojektowany tak, �e ��czy si� z
serwerem IRC i staje operatorem. Nast�pnie ogl�da informacje o
po��czeniach w celu skanowania wszystkich klient�w pod k�tem otwartych
(niebezpiecznych) proxy. Takie niebezpieczne proxy zwykle s� u�ywane
do spamowania, floodowania i innych nadu�y�.

BOPM jest w stanie wykry� WinGates, proxy HTTP, proxy SOCKS 4/5 oraz
routery Cisco z domy�lnymi has�ami. BOPM obs�uguje tak�e sprawdzanie
czarnych list opartych na DNS (takich jak MAPS RBL) i mo�e by�
skonfigurowany do zg�aszania nowych proxy z powrotem do projektu
Blitzed Open Proxy Monitoring. 

%prep
%setup -q
%patch0 -p1

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

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/{run,log}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
> $RPM_BUILD_ROOT/var/log/%{name}/bopm.log
> $RPM_BUILD_ROOT/var/log/%{name}/scan.log

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 151 %{name}
%useradd -u 151 -c "BOPM Daemon" -g %{name} %{name}

%post
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start BOPM daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

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
