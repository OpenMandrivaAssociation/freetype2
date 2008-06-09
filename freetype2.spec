%define build_bytecode_interpreter 0
%define build_subpixel 0
%define build_plf 0
%{?_with_plf: %global build_plf 1}
%{?_with_bytecode_interpreter: %global build_bytecode_interpreter 1}
%{?_with_subpixel: %global build_subpixel 1}

%define name	freetype2
%define	version	2.3.5


%if %build_plf
%define distsuffix plf
%define build_subpixel 1
%define build_bytecode_interpreter 1
%endif

%define major	6
%define libname	%mklibname freetype %{major}
%define develname %mklibname -d freetype %{major}
%define staticdevelname %mklibname -d -s freetype %{major}

Name:		%name
Summary:	A free and portable TrueType font rendering engine
Version:	%version
Release:	%mkrel 2
License:	FreeType License/GPL
URL:		http://www.freetype.org/
Source0:	ftp://ftp.freetype.org/pub/freetype/freetype2/freetype-%{version}.tar.bz2
Source1:	ftp://ftp.freetype.org/pub/freetype/freetype2/freetype-doc-%{version}.tar.bz2

Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:	zlib-devel
BuildRequires:	pkgconfig
Group:		System/Libraries

%description
The FreeType2 engine is a free and portable TrueType font rendering engine.
It has been developed to provide TT support to a great variety of
platforms and environments. Note that FreeType2 is a library, not a
stand-alone application, though some utility applications are included
%if %{build_plf}

This package is in PLF because this build has bytecode interpreter and
subpixel hinting enabled which are covered by software patents.
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

This package is in PLF because this build has bytecode interpreter and
subpixel hinting enabled which are covered by software patents.
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

%prep
%setup -q -n freetype-%version -b 1

%if %{build_bytecode_interpreter}
perl -pi -e 's|/\* #define TT_CONFIG_OPTION_BYTECODE_INTERPRETER \*/|#define TT_CONFIG_OPTION_BYTECODE_INTERPRETER|' include/freetype/config/ftoption.h
%endif
%if %{build_subpixel}
perl -pi -e 's|^/\* #define FT_CONFIG_OPTION_SUBPIXEL_RENDERING \*/| #define FT_CONFIG_OPTION_SUBPIXEL_RENDERING|' include/freetype/config/ftoption.h
%endif


%build
%{?__cputoolize: %{__cputoolize} -c builds/unix}

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

%install
rm -fr %buildroot
%makeinstall

%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/freetype-config
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h

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
%multiarch %multiarch_bindir/freetype-config
%multiarch %dir %multiarch_includedir/freetype2
%multiarch %multiarch_includedir/freetype2/*

%files -n %{staticdevelname}
%defattr(-, root, root)
%{_libdir}/*.a
