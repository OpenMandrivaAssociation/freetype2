%define build_subpixel 0
%define build_plf 0
%{?_with_plf: %global build_plf 1}
%{?_with_subpixel: %global build_subpixel 1}

%define name	freetype2
%define	version	2.4.4

%if %build_plf
%define distsuffix plf
%if %mdvver >= 201100
# make EVR of plf build higher than regular to allow update, needed with rpm5 mkrel
%define extrarelsuffix plf
%endif
%define build_subpixel 1
%endif

%define major	6
%define libname	%mklibname freetype %{major}
%define develname %mklibname -d freetype %{major}
%define staticdevelname %mklibname -d -s freetype %{major}

%define git_url git://git.sv.gnu.org/freetype/freetype2.git

Name:		%name
Summary:	A free and portable TrueType font rendering engine
Version:	%version
Release:	%mkrel 4%{?extrarelsuffix}
License:	FreeType License/GPL
URL:		http://www.freetype.org/
Source0:	http://savannah.nongnu.org/download/freetype/freetype-%{version}.tar.bz2
Source1:	http://savannah.nongnu.org/download/freetype/freetype-doc-%{version}.tar.bz2
Source2:	http://savannah.nongnu.org/download/freetype/ft2demos-%{version}.tar.bz2
Patch0:		ft2demos-2.3.12-mathlib.diff
Patch1:		freetype-2.4.2-CVE-2010-3311.patch
Patch2:		0001-Fall-back-to-autohinting-if-a-TTF-OTF-doesn-t-contai.patch
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:	zlib-devel
BuildRequires:	pkgconfig
BuildRequires:	libx11-devel
Group:		System/Libraries

%description
The FreeType2 engine is a free and portable TrueType font rendering engine.
It has been developed to provide TT support to a great variety of
platforms and environments. Note that FreeType2 is a library, not a
stand-alone application, though some utility applications are included
%if %{build_plf}

This package is in PLF because this build has subpixel hinting enabled which
is covered by software patents.
%endif

%package -n %{libname}
Summary:	Shared libraries for a free and portable TrueType font rendering engine
Group:		System/Libraries
Obsoletes:	%{name}
Provides:	%{name} = %{version}-%{release}

%description -n %{libname}
The FreeType2 engine is a free and portable TrueType font rendering
engine.  It has been developed to provide TT support to a great
variety of platforms and environments. Note that FreeType2 is a
library, not a stand-alone application, though some utility
applications are included
%if %{build_plf}

This package is in PLF because this build has subpixel hinting enabled which
is covered by software patents.
%endif

%package -n %{develname}
Summary:	Header files and static library for development with FreeType2
Group:		Development/C
Requires:	%{libname} = %{version}
Requires:	zlib-devel
Obsoletes:	%{name}-devel
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
This package is only needed if you intend to develop or compile applications
which rely on the FreeType2 library. If you simply want to run existing
applications, you won't need this package.

%package -n %{staticdevelname}
Summary:	Static libraries for programs which will use the FreeType2 library
Group:		Development/C
Requires:	%{libname}-devel = %{version}
Obsoletes:	%{name}-static-devel
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n %{staticdevelname}
This package includes the static libraries necessary for 
developing programs which will use the FreeType2 library.

If you are going to develop programs which use the FreeType2 library
you should install freetype2-devel.  You'll also need to have the 
freetype2 package installed.

%package demos
Summary:	A collection of FreeType demos
Group:		File tools

%description demos
The FreeType engine is a free and portable font rendering engine, developed to
provide advanced font support for a variety of platforms and environments. The
demos package includes a set of useful small utilities showing various
capabilities of the FreeType library.

%prep
%setup -q -n freetype-%version -b 1 -a2

pushd ft2demos-%{version}
%patch0 -p0
popd

%patch1 -p1 -b .CVE-2010-3311
%patch2 -p1

%if %{build_subpixel}
perl -pi -e 's|^/\* #define FT_CONFIG_OPTION_SUBPIXEL_RENDERING \*/| #define FT_CONFIG_OPTION_SUBPIXEL_RENDERING|' include/freetype/config/ftoption.h
%endif

%build

GCC_VERSION=`gcc --version | grep "^gcc" | awk '{ print $3 }' | sed 's+\([0-9]\)\.\([0-9]\)\..*+\1\2+'`
if [ $GCC_VERSION -lt 34 ]; then
#old gcc is generating wrong code with optimizations
export CFLAGS="-O"
fi

# some apps crash on ppc without this
%ifarch ppc
export CFLAGS="`echo %optflags |sed s/O2/O0/`"
%endif

%configure2_5x
%make

pushd ft2demos-%{version}
%make X11_PATH=%{_prefix} TOP_DIR=".."
popd

%install
rm -fr %buildroot
%makeinstall_std

%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/freetype-config

%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h

install -d $RPM_BUILD_ROOT/%{_bindir}

for ftdemo in ftbench ftdiff ftdump ftgamma ftgrid ftlint ftmulti ftstring ftvalid ftview; do
    builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo $RPM_BUILD_ROOT/%{_bindir}
done

%clean
rm -fr %buildroot

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files -n %{libname}
%defattr(-, root, root)
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-, root, root)
%doc docs/*
%{_bindir}/freetype-config
%{_libdir}/*.so
%{_libdir}/*.la
%dir %{_includedir}/freetype2
%{_includedir}/freetype2/*
%{_includedir}/ft2build.h
%{_datadir}/aclocal/*
%{_libdir}/pkgconfig/*
%multiarch_bindir/freetype-config
%dir %multiarch_includedir/freetype2
%multiarch_includedir/freetype2/*

%files -n %{staticdevelname}
%defattr(-, root, root)
%{_libdir}/*.a

%files demos
%defattr(-,root,root)
%{_bindir}/ftbench
%{_bindir}/ftdiff
%{_bindir}/ftdump
%{_bindir}/ftgamma
%{_bindir}/ftgrid
%{_bindir}/ftlint
%{_bindir}/ftmulti
%{_bindir}/ftstring
%{_bindir}/ftvalid
%{_bindir}/ftview
