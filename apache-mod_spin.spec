#Module-Specific definitions
%define mod_name mod_spin
%define mod_conf A65_%{mod_name}.conf
%define mod_so %{mod_name}.so

%define	major 0
%define libname %mklibname rxv_spin %{major}
%define develname %mklibname rxv_spin -d

Summary:	Simple template language with data replacement capabilities for Apache
Name:		apache-%{mod_name}
Version:	1.1.7
Release:	%mkrel 4
Group:		System/Servers
License:	GPL
URL:		http://www.rexursive.com/software/modspin/
Source0:	ftp://ftp.rexursive.com/pub/mod-spin/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		mod_spin-no_strip.diff
Patch1:		mod_spin-borked_docs.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_unique_id >= 2.2.0
BuildRequires:  apache-devel >= 2.2.0
BuildRequires:	autoconf2.5
BuildRequires:	bison
BuildRequires:	doxygen
BuildRequires:	file
BuildRequires:	flex >= 2.5.33
BuildRequires:	libapreq-devel >= 2.07
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	tetex-latex
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_spin is an Apache module that provides (in conjunction with some other
modules) a simple template language with data replacement capabilities only,
persistent application and session data tracking, dynamic linking of
applications into Apache 2 as shared libraries, parameters, cookies and
multipart/form data parsing via libapreq2, simple API for (kind of) MVC
controller functionality and simple API for pooled (or not) access to SQL
databases.

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:          System/Libraries

%description -n	%{libname}
Shared libraries for %{name}

%package -n	%{develname}
Summary:	Development library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}
Provides:	librxv_spin-devel = %{version}
Provides:	%{mklibname rxv_spin 0 -d} = %{version}-%{release}
Obsoletes:	%{mklibname rxv_spin 0 -d}

%description -n	%{develname}
This package contains the static %{libname} library and its header
files.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0
%patch1 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

cp %{SOURCE1} %{mod_conf}

%build
rm -rf configure autom4te.cache
libtoolize --copy --force --automake; aclocal -I m4; autoheader; automake --add-missing --copy; autoconf

export STRIP="/bin/false"

%configure2_5x --localstatedir=/var/lib \
    --enable-packager \
    --with-pgsql \
    --with-mysql \
    --with-flex-reentrant=%{_prefix} \
    --libexecdir="`%{_sbindir}/apxs -q LIBEXECDIR`-extramodules"

make -C src

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

%makeinstall_std

# fix apache dir
mv %{buildroot}%{_libdir}/apache %{buildroot}%{_libdir}/apache-extramodules

# apache config
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# fix docs
rm -rf html_docs
cp -rp docs/html html_docs
chmod 644 html_docs/*
rm -f html_docs/installdox

# cleanup
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.*a
rm -rf %{buildroot}%{_docdir}/%{mod_name}-%{version}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc html_docs/* docs/mod_spin.pdf create-store-mysql.sql create-store.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/rxv_spin-config
%attr(0755,root,root) %{_libdir}/*.a
%attr(0644,root,root) %{_libdir}/*.la
%attr(0755,root,root) %{_libdir}/*.so
%{_includedir}/*
%{_datadir}/aclocal/*.m4
%{_libdir}/pkgconfig/mod_spin.pc
%{_mandir}/man3/*
