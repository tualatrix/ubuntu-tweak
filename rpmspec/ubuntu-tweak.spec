%define ver %{?minor_version:.%{minor_version}}
%define tarball_suffix %{?minor_version:-%{minor_version}}
%define rel %{?snapshot:.%{snapshot}}
%define build_number 3

Name:		ubuntu-tweak
Version:	0.4.3
Release:	%{?snapshot:0.}%{build_number}%{?ver}%{?rel}
Summary:	A tweak software for ubuntu and other distributions based on GNOME desktop.

Group:		System Environment/Base
License:	GPLv2
URL:		http://code.google.com/p/ubuntu-tweak
Source0:	http://ubuntu-tweak.googlecode.com/files/%{name}_%{version}.orig.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch
BuildRequires:	gtk2-devel pygtk2-devel gnome-python2-devel
BuildRequires:	desktop-file-utils
Requires:	pyxdg pygtk2 gnome-python2 gnome-python2-gnome gnome-python2-gnomedesktop gnome-python2-gconf

%description
Ubuntu-tweak is a tweak software for ubuntu.

It can be used for Fedora desktop too, most function still work fine.


%prep
%setup -q


%build
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT


%post
update-desktop-database %{_datadir}/applications &>/dev/null || :


%postun
update-desktop-database %{_datadir}/applications &>/dev/null || :


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%{_sbindir}/*
%{_bindir}/*
%{_datadir}/*
%{_sysconfdir}/*


%changelog
* Sat Dec 06 2008 TualatriX <tualatrix@gmail.com> - 0.4.3-3
- build noarch package
- add some dependencies
- update package summary
- combine the binary package and the data package

* Fri Nov 28 2008 bbbush <bbbush.yuan@gmail.com> - 0.4.3-2
- update desktop file database

* Fri Nov 28 2008 bbbush <bbbush.yuan@gmail.com> - 0.4.3-1
- initial import
