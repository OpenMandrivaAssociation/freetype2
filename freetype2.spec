%define build_subpixel 0
%define build_plf 0
%{?_with_plf: %global build_plf 1}
%{?_with_subpixel: %global build_subpixel 1}

%define release %mkrel 1
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

%define git_url git://git.sv.gnu.org/freetype/freetype2.git

Summary:	A free and portable TrueType font rendering engine
Name:		freetype2
Version:	2.4.9
Release:	%{release}%{?extrarelsuffix}
License:	FreeType License/GPL
Group:		System/Libraries
URL:		http://www.freetype.org/
Source0:	http://savannah.nongnu.org/download/freetype/freetype-%{version}.tar.gz
Source1:	http://savannah.nongnu.org/download/freetype/freetype-%{version}.tar.gz.sig
Source2:	http://savannah.nongnu.org/download/freetype/freetype-doc-%{version}.tar.gz
Source3:	http://savannah.nongnu.org/download/freetype/freetype-doc-%{version}.tar.gz.sig
Source4:	http://savannah.nongnu.org/download/freetype/ft2demos-%{version}.tar.gz
Source5:	http://savannah.nongnu.org/download/freetype/ft2demos-%{version}.tar.gz.sig
Patch0:		ft2demos-2.3.12-mathlib.diff
Patch1:		freetype-2.4.2-CVE-2010-3311.patch
BuildRequires:	zlib-devel
BuildRequires:	pkgconfig
BuildRequires:	libx11-devel

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
Requires:	%{libname} >= %{version}-%{release}
Requires:	zlib-devel
Obsoletes:	%{name}-devel
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
This package is only needed if you intend to develop or compile applications
which rely on the FreeType2 library. If you simply want to run existing
applications, you won't need this package.

%package demos
Summary:	A collection of FreeType demos
Group:		File tools

%description demos
The FreeType engine is a free and portable font rendering engine, developed to
provide advanced font support for a variety of platforms and environments. The
demos package includes a set of useful small utilities showing various
capabilities of the FreeType library.

%prep
%setup -q -n freetype-%{version} -a2 -a4

pushd ft2demos-%{version}
%patch0 -p0
popd

%patch1 -p1 -b .CVE-2010-3311

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
export CFLAGS="`echo %{optflags} |sed s/O2/O0/`"
%endif

%configure2_5x
%make

pushd ft2demos-%{version}
%make X11_PATH=%{_prefix} TOP_DIR=".."
popd

%install
rm -fr %{buildroot}
%makeinstall_std

%multiarch_binaries %{buildroot}%{_bindir}/freetype-config

%multiarch_includes %{buildroot}%{_includedir}/freetype2/freetype/config/ftconfig.h

install -d %{buildroot}%{_bindir}

for ftdemo in ftbench ftdiff ftdump ftgamma ftgrid ftlint ftmulti ftstring ftvalid ftview; do
    builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo %{buildroot}%{_bindir}
done

# cleanup
rm -fr %{buildroot}%{_libdir}/*.*a

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%doc docs/*
%{_bindir}/freetype-config
%{_libdir}/*.so
%dir %{_includedir}/freetype2
%{_includedir}/freetype2/*
%{_includedir}/ft2build.h
%{_datadir}/aclocal/*
%{_libdir}/pkgconfig/*
%{multiarch_bindir}/freetype-config
%dir %{multiarch_includedir}/freetype2
%{multiarch_includedir}/freetype2/*

%files demos
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
