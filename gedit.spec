%define glib2_version 2.12.0
%define pango_version 1.19.0
%define gtk2_version 2.10.0
%define gnome_vfs2_version 2.16.0
%define libgnomeui_version 2.16.0
%define desktop_file_utils_version 0.9
%define gail_version 1.2.0
%define gtksourceview_version 2.0.0
%define pygtk_version 2.9.7
%define pygobject_version 2.11.5
%define pygtksourceview_version 2.2.0
%define gnome_python_desktop_version 2.15.90
%define gnome_doc_utils_version 0.3.2
%define gconf_version 2.14
%define enchant_version 1.2.0
%define isocodes_version 0.35

Summary:	Text editor for the GNOME desktop
Name:		gedit
Version: 	2.28.4
Release: 	3%{?dist}
Epoch:		1
License:	GPLv2+ and GFDL
Group:		Applications/Editors
Source0:	http://download.gnome.org/sources/gedit/2.28/gedit-%{version}.tar.bz2

URL:		http://projects.gnome.org/gedit/
BuildRoot:	 %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(post):         desktop-file-utils >= %{desktop_file_utils_version}
Requires(post):		scrollkeeper >= 0.1.4
Requires(post):		GConf2 >= %{gconf_version}
Requires(pre):		GConf2 >= %{gconf_version}
Requires(preun):	GConf2 >= %{gconf_version}
Requires(postun):	scrollkeeper >= 0.1.4
Requires(postun):       desktop-file-utils >= %{desktop_file_utils_version}

# Make the file selector remember last window size
# This patch needs to go upstream
#Patch0: gedit-2.13.2-filesel.patch
%ifarch ppc64,x86_64,ia64,s390x
Patch1: gedit-2.13.90-libdir.patch
%endif

# http://bugzilla.gnome.org/show_bug.cgi?id=569214
Patch2: gedit-2.25.5-fix-python-path.patch

# http://bugzilla.gnome.org/show_bug.cgi?id=587053
Patch3: print-to-file.patch

# update translations
# https://bugzilla.redhat.com/show_bug.cgi?id=575754
Patch4: gedit-translations.patch

BuildRequires: gnome-common
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: pango-devel >= %{pango_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: GConf2-devel
BuildRequires: libSM-devel
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: enchant-devel >= %{enchant_version}
BuildRequires: iso-codes-devel >= %{isocodes_version}
BuildRequires: libattr-devel
BuildRequires: gail-devel >= %{gail_version}
BuildRequires: gtksourceview2-devel >= %{gtksourceview_version}
BuildRequires: scrollkeeper gettext
BuildRequires: pygtk2-devel >= %{pygtk_version}
BuildRequires: pygobject2-devel >= %{pygobject_version}
BuildRequires: pygtksourceview-devel >= %{pygtksourceview_version}
BuildRequires: python-devel
BuildRequires: gnome-doc-utils >= %{gnome_doc_utils_version}
BuildRequires: which
BuildRequires: autoconf, automake, libtool
BuildRequires: intltool

Requires: pygtk2 >= %{pygtk_version}
Requires: pygobject2 >= %{pygtk_version}
Requires: pygtksourceview >= %{pygtksourceview_version}
Requires: gnome-python2-desktop >= %{gnome_python_desktop_version}
# the run-command plugin uses zenity
Requires: zenity

%description
gedit is a small, but powerful text editor designed specifically for
the GNOME desktop. It has most standard text editor functions and fully
supports international text in Unicode. Advanced features include syntax
highlighting and automatic indentation of source code, printing and editing
of multiple documents in one window.

gedit is extensible through a plugin system, which currently includes
support for spell checking, comparing files, viewing CVS ChangeLogs, and
adjusting indentation levels. Further plugins can be found in the
gedit-plugins package.

%package devel
Summary: Support for developing plugins for the gedit text editor
Group: Development/Libraries
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: gtksourceview2-devel >= %{gtksourceview_version}
Requires: pygtk2-devel >= %{pygtk_version}
Requires: pkgconfig
Requires: gtk-doc

%description devel
gedit is a small, but powerful text editor for the GNOME desktop.
This package allows you to develop plugins that add new functionality
to gedit.

Install gedit-devel if you want to write plugins for gedit.

%prep
%setup -n gedit-%{version} -q

%ifarch ppc64,x86_64,ia64,s390x
%patch1 -p1 -b .libdir
%endif

%patch2 -p1 -b .fix-python-path
%patch3 -p1 -b .print-to-file
%patch4 -p1 -b .translations

autoreconf -f -i

%build
%configure \
	--disable-scrollkeeper \
	--disable-gtk-doc \
	--enable-python
make

# strip unneeded translations from .mo files
# ideally intltool (ha!) would do that for us
# http://bugzilla.gnome.org/show_bug.cgi?id=474987
cd po
grep -v ".*[.]desktop[.]in.*\|.*[.]server[.]in[.]in$" POTFILES.in > POTFILES.keep
mv POTFILES.keep POTFILES.in
intltool-update --pot
for p in *.po; do
  msgmerge $p %{name}.pot > $p.out
  msgfmt -o `basename $p .po`.gmo $p.out
done
cd ..

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --delete-original       	\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

## clean up all the static libs for plugins (workaround for no -module)
/bin/rm -f `find $RPM_BUILD_ROOT%{_libdir}/gedit-2/plugins -name "*.a"`
/bin/rm -f `find $RPM_BUILD_ROOT%{_libdir}/gedit-2/plugins -name "*.la"`

/bin/rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done

%find_lang %{name} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-desktop-database -q
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/gedit.schemas > /dev/null || :

# update icon themes
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gedit.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gedit.schemas > /dev/null || :
fi

%postun
update-desktop-database -q
scrollkeeper-update -q
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi


%files -f %{name}.lang
%defattr(-, root, root)
%doc README COPYING AUTHORS
%{_datadir}/gedit-2
%{_datadir}/applications/gedit.desktop
%{_mandir}/man1/*
%{_libdir}/gedit-2
%{_libexecdir}/gedit-2
%{_bindir}/*
%{_sysconfdir}/gconf/schemas/*


%files devel
%defattr(-, root, root)
%{_includedir}/gedit-2.20
%{_libdir}/pkgconfig/gedit-2.20.pc
%{_datadir}/gtk-doc/html/gedit/


%changelog
* Thu Aug 05 2010 Ray Strode <rstrode@redhat.com> 2.28.4-3
- Update translations again
  Resolves: #575754

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 1:2.28.4-2
- Update translations
Resolves: #575754

* Tue Mar 23 2010 Ray Strode <rstrode@redhat.com> - 1:2.28.4-1
Resolves: #575986
- Update to 2.28.4

* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> - 1:2.28.3-2
Resolves: #575935
- Allow .gnome2 to be relocated

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> - 1:2.28.3-1
- Update to 2.28.3

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.6-1
- Update to 2.27.6

* Mon Aug 24 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.5-1
- Update to 2.27.5

* Sat Aug 22 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.4-2
- Respect button-images setting

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.4-1
- Update to 2.27.4

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.3-1
- Update to 2.27.3

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.27.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.2-2
- Make some stubborn buttons behave

* Tue Jun 30 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.2-1
- Update to 2.27.2

* Fri Jun 26 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.1-2
- Improve print-to-file

* Sun May 31 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.27.1-1
- Update to 2.27.1

* Wed May 20 2009 Ray Strode <rstrode@redhat.com> 2.26.2-1
- Update to 2.26.2

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.1-2
- Don't drop schemas translations from po files

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gedit/2.26/gedit-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.8-1
- Update to 2.25.8

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.25.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.7-1
- Update to 2.25.7

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.6-1
- Update to 2.25.6

* Mon Jan 26 2009 Ray Strode <rstrode@redhat.com> - 1:2.25.5-3
- Different, more functional fix for bug 481556.

* Mon Jan 26 2009 Ray Strode <rstrode@redhat.com> - 1:2.25.5-2
- Fix up python plugin path to close up a security attack
  vectors (bug 481556).

* Tue Jan 20 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.5-1
- Update to 2.25.5

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.4-2
- Update to 2.25.4

* Mon Jan 05 2009 - Bastien Nocera <bnocera@redhat.com> - 1:2.25.2-3
- Remove some unneeded dependencies

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com>
- Rebuild for Python 2.6 

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com>
- Update to 2.25.2

* Sun Nov 30 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1:2.24.1-4
- Rebuild for Python 2.6

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.1-3
- Better URL

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.1-2
- Improve %%summmary and %%description

* Tue Nov  4 2008 Ray Strode <rstrode@redhat.com> - 1:2.24.1-1
- Update to 2.24.1 (bug 469934)

* Wed Oct 15 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.0-4
- Save some more space

* Thu Sep 25 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.0-3
- Save some space

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.0-2
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.90-1
- Update to 2.23.90

* Wed Aug 13 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.3-2
- Finally drop the vendor prefix, since it broke things again

* Wed Aug 13 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.3-1
- Update to 2.23.3

* Sat Aug  9 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.1-3
- One more icon name fix

* Wed Jul  9 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.1-2
- Use standard icon names

* Tue May 13 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.1-1
- Update to 2.23.1

* Tue Apr 08 2008 - Bastien Nocera <bnocera@redhat.com> - 1:2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.22.0-1
- Update to 2.22.0

* Thu Mar  6 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.2-2
- Don't OnlyShowIn=GNOME

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.2-1
- Update to 2.21.2

* Fri Feb 15 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.1-3
- Drop libgnomeprint22 BR

* Sat Feb  2 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.1-2
- Require zenity (#253815)

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.1-1
- Update to 2.21.1

* Tue Nov 27 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.4-1
- Update to 2.20.4

* Sun Nov 18 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.2-3
- Fix the license field

* Tue Nov 13 2007 Florian La Roche <laroche@redhat.com> - 1:2.20.2-2
- define pango_version

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.2-1
- Update to 2.20.2 (bug fixes and translation updates)

* Wed Sep 26 2007 Ray Strode <rstrode@redhat.com> - 1:2.20.1-1
- Update to 2.20.1 at the request of upstream

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.0-1
- Update to 2.20.0

* Fri Sep 14 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.92-1
- Update to 2.19.92

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.91-1
- Update to 2.19.91

* Wed Aug 15 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.90-1
- Update to 2.19.90
- %%find_lang also finds omf files now

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.3-3
- Remove a stale comment

* Mon Aug  6 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.3-2
- Update license field
- Use %%find_lang for help files

* Wed Aug  1 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.3-1
- Update to 2.19.3

* Thu Jul 19 2007 Jeremy Katz <katzj@redhat.com> - 1:2.19.2-2
- fix requires to be on pygtksoureview

* Tue Jul 10 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.2-1
- Update to 2.19.2
- Require gtksourceview2

* Mon Jun 25 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.1-1
- Update to 2.19.1

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.1-1
- Update to 2.18.1

* Sat May  5 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-3
- Add enchant-devel and iso-codes-devel BRs to build
  with spell-checking support (#227477)

* Tue Mar 27 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-2
- Reduce the size of the tags files

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.6-1
- Update to 2.17.6

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.5-1
- Update to 2.17.5

* Tue Jan 23 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.4-1
- Update to 2.17.4

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.3-1
- Update to 2.17.3

* Wed Dec 20 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.2-1
- Update to 2.17.2

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 1:2.17.1-2
- rebuild for python 2.5

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.1-1
- Update to 2.17.1

* Mon Dec  4 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.2-3
- Add BuildRequires for libattr-devel

* Thu Nov 30 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.2-2
- Small accessibility improvements

* Sat Nov  4 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.2-1
- Update to 2.16.2

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.0-4
- Fix scripts according to packaging guidelines

* Fri Sep  8 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.0-3
- Fix directory ownership issues (#205675)

* Tue Sep  5 2006 Ray Strode <rstrode@redhat.com> - 1:2.16.0-2.fc6
- Fix up dependencies a bit

* Tue Sep  5 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.0-1.fc6
- Update to 2.16.0
- Require pkgconfig for the -devel package

* Sun Aug 27 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.9-1.fc6
- Update to 2.15.9
- Add BR for perl-XML-Parser

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.8-1.fc6
- Update to 2.15.8

* Mon Aug 14 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.7-1.fc6
- Update to 2.15.7

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.6-2.fc6
- Bump gtksourceview requirement

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.6-1.fc6
- Update to 2.15.6

* Thu Aug 10 2006 Ray Strode <rstrode@redhat.com> - 1:2.15.5-2.fc6
- Apply patch from James Antill to copy extended attributes over
  when saving files (bug 202099)

* Thu Aug  3 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.5-1.fc6
- Update to 2.15.5

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.4-1
- Update to 2.15.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:2.15.3-1.1
- rebuild

* Tue Jun 13 2006 Matthias Clasen <mclasen@redhat.com> 2.15.3-1
- Update to 2.15.3

* Wed May 17 2006 Matthias Clasen <mclasen@redhat.com> 2.15.2-1
- Update to 2.15.2

* Sat May 13 2006 Dan Williams <dcbw@redhat.com> - 2.15.1-2
- Work around gnome.org #341055 (gedit doesn't remember previous open/save dir)

* Tue May  9 2006 Matthias Clasen <mclasen@redhat.com> 2.15.1-1
- Update to 2.15.1

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> 2.14.2-2
- Update to 2.14.2

* Thu Mar 16 2006 Matthias Clasen <mclasen@redhat.com> 2.14.1-1
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> 2.14.0-1
- Update to 2.14.0

* Tue Feb 28 2006 Karsten Hopp <karsten@redhat.de> 2.13.92-2	
- BuildRequire: gnome-doc-utils

* Sun Feb 26 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.92-1
- Update to 2.13.92

* Wed Feb 15 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:2.13.90-3.1
- bump again for double-long bug on ppc(64)

* Mon Feb  6 2006 John (J5) Palmieri <johnp@redhat.com> - 1:2.13.90-3
- Add dependancy on gnome-python2-desktop

* Mon Feb  6 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.90-2
- Enable python again
- Fix multiarch problem

* Mon Jan 30 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.90-1
- Update to 2.13.90

* Thu Jan 26 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.4-1
- Update to 2.13.4

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.3-1
- Update to 2.13.3

* Sun Jan 13 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.2-1
- Update to 2.13.2
- Update the persistent file selector size patch (again!)

* Sun Jan  8 2006 Dan Williams <dcbw@redhat.com > - 1:2.13.1-2
- Fix up and re-enable persistent file selector size patch

* Tue Jan  3 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.13.1-1
- Update to 2.13.1
- Disable scrollkeeper

* Wed Dec 21 2005 Jeremy Katz <katzj@redhat.com> - 1:2.13.0-3
- fix gedit-devel requirement to include epoch

* Tue Dec 20 2005 Matthias Clasen <mclasen@redhat.com> - 2.13.0-2
- Update requirements

* Wed Dec 14 2005 Matthias Clasen <mclasen@redhat.com> - 2.13.0-1
- Update to 2.13.0
- Comment out the fileselector patches for now, these
  will need updating for the new-mdi branch

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Oct  6 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.1-1
- Update to 2.12.1

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Tue Aug 16 2005 Matthias Clasen <mclasen@redhat.com> 
- New upstream version

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> - 2.10.4-1
- New upstream version

* Wed Aug 03 2005 Ray Strode <rstrode@redhat.com> - 2.10.3-1
- Update to upstream version 2.10.3

* Mon Jun 13 2005 Ray Strode <rstrode@redhat.com> 1:2.10.2-6
- Remove some patches that are already upstream 

* Tue Jun 07 2005 Ray Strode <rstrode@redhat.com> 1:2.10.2-5
- Dont pass user input as format specifiers to
  gtk_message_dialog_new (bug 159657).

* Thu Apr 14 2005 John (J5) Palmieri <johnp@redhat.com> - 2.10.2-3
- Revert the addition of the gedit icon to the hicolor theme as
  the new gnome-icon-theme package does the right thing

* Tue Apr 12 2005 Matthias Clasen <mclasen@redhat.com> - 2.10.2-2
- Add the icon to the hicolor theme, and rename it to what
  the .desktop file says.

* Fri Apr  8 2005 Ray Strode <rstrode@redhat.com> - 2.10.2-1
- Update to upstream version 2.10.2

* Tue Mar 29 2005 Warren Togami <wtogami@redhat.com> - 2.10.0-2
- devel req libgnomeprintui22-devel for pkgconfig (#152487)

* Thu Mar 17 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-1
- Update to upstream version 2.10.0

* Thu Mar  3 2005 Marco Pesenti Gritti <mpg@redhat.com> 1:2.9.7-1
- Update to 2.9.7

* Wed Feb  9 2005 Matthias Clasen <mclasen@redhat.com> 1:2.9.6-1
- Update to 2.9.6

* Sun Jan 30 2005 Matthias Clasen <mclasen@redhat.com> 1:2.9.5-1
- Update to 2.9.5

* Thu Nov  4 2004 Marco Pesenti Gritti <mpg@redhat.com> 1:2.8.1-2
- Update the desktop files database. (RH Bug: 135571)

* Mon Oct 11 2004 Dan Williams <dcbw@redhat.com> 1:2.8.1-1
- Update to 2.8.1

* Wed Sep 22 2004 Dan Williams <dcbw@redhat.com> 1:2.8.0-1
- Update to 2.8.0

* Wed Sep 15 2004 John (J5) Palmieri <johnp@redhat.com> 1:2.7.92-2
- Added the spelling plugin to the default gconf schema so that the
  tools menu is not empty (RH Bug: 31607)

* Tue Aug 31 2004 Alex Larsson <alexl@redhat.com> 1:2.7.92-1
- update to 2.7.92

* Wed Aug 18 2004 Dan Williams <dcbw@redhat.com> 1:2.7.91-1
- Update to 2.7.91

* Tue Aug  3 2004 Owen Taylor <otaylor@redhat.com> - 1:2.7.90-1
- Upgrade to 2.7.90
- Add patch to use Pango font names, not gnome-print font names

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat May 15 2004 Dan Williams <dcbw@redhat.com> 1:2.6.1-1
- Upgrade to 2.6.1

* Fri Apr 16 2004 Dan Williams <dcbw@redhat.com> 1:2.6.0-4
- Gnome.org #137825 Gedit crash on Find/Replace dialog close
    when hitting escape

* Tue Apr 13 2004 Warren Togami <wtogami@redhat.com> 1:2.6.0-3
- #111156 BR intltool scrollkeeper gettext
- #111157 -devel R eel2-devel gtksourceview-devel
- rm bogus BR esound

* Thu Apr 08 2004 Dan Williams <dcbw@redhat.com> 1:2.6.0-2
- Fix dumb bug in ~/.recently-used patch where lockf() could
    never succeed

* Wed Mar 31 2004 Dan Williams <dcbw@redhat.com> 1:2.6.0-1
- Update to gedit-2.6.0 sources

* Thu Mar 18 2004 Dan Williams <dcbw@redhat.com> 1:2.5.92-1
- Update to gedit-2.5.92 sources

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 25 2004 Dan Williams <dcbw@redhat.com> 1:2.5.90-1
- fix dumbness in the egg-recent file locking patch
- Remove the autotools-1.8 patch because it is no longer
    needed
- Require gtksourceview-devel >= 0.9 due to update to 2.5.90
- Update to gedit-2.5.90

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 11 2004 Dan Williams <dcbw@redhat.com> 1:2.5.3-3
- Correctly convert last path from open/save into a directory
   for storing in gconf, not a file

* Fri Feb 06 2004 Dan Williams <dcbw@redhat.com> 1:2.5.3-2
- Bring file selector size/last path patch up to 2.5.3
- Fix up the recent-files locking algorithm to have finer
   resolution timeouts

* Wed Jan 28 2004 Alexander Larsson <alexl@redhat.com> 1:2.5.3-1
- update to 2.5.3

* Mon Jan 19 2004 Dan Williams <dcbw@redhat.com> 1:2.4.0-5
- Work around recent files locking contention when using NFS
    home directories (gnome.org #131930)
- Make Find and Replace dialogs use a cancel button, so that
    pressing escape makes them close (gnome.org #131927)

* Thu Jan  8 2004 Dan Williams <dcbw@redhat.com> 1:2.4.0-4
- Remeber file selector size and last directory on open/save
   (gnome.org #123787)
- Small hack to work around switch from autotools 1.7 - 1.8

* Tue Oct 21 2003 Matt Wilson <msw@redhat.com> 1:2.4.0-3 
- eel_read_entire_file takes a pointer to an int, not to a gsize
  (#103933)

* Tue Oct  7 2003 Owen Taylor <otaylor@redhat.com> 1:2.4.0-2
- Fix bug with multibyte chars in shell-output plugin (#104027, Jens Petersen)
- Add missing BuildRequires on eel2, aspell-devel (#87746, Alan Cox)
- Add versioned Requires on eel2, libgnomeui (#103363, Jens Petersen)

* Fri Oct  3 2003 Alexander Larsson <alexl@redhat.com> 1:2.4.0-1
- 2.4.0

* Mon Sep 22 2003 Bill Nottingham <notting@redhat.com> 1:2.3.5-2
- fix defattr (#103333)

* Tue Aug 26 2003 Jonathan Blandford <jrb@redhat.com>
- require the new gtksourceview

* Fri Aug 15 2003 Jonathan Blandford <jrb@redhat.com> 1:2.3.3-1
- update for GNOME 2.4

* Tue Jul 29 2003 Havoc Pennington <hp@redhat.com> 1:2.2.2-2
- rebuild

* Mon Jul  7 2003 Havoc Pennington <hp@redhat.com> 1:2.2.2-1
- 2.2.2
- fix name of gettext domain
- remove recent-monitor patch now upstream

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May  1 2003 Havoc Pennington <hp@redhat.com> 1:2.2.0-3
- patch configure.in for new aspell

* Mon Apr 28 2003 Tim Powers <timp@redhat.com> 1:2.2.0-2
- rebuild to fix broken libpspell deps

* Tue Feb  4 2003 Alexander Larsson <alexl@redhat.com> 1:2.2.0-1
- Update to 2.2.0
- Add patch to disable recent files monitoring
- Bump libgnomeprint requirements

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Dec 13 2002 Tim Powers <timp@redhat.com> 1:2.1.4-1
- update to 2.1.4

* Mon Dec  9 2002 Havoc Pennington <hp@redhat.com>
- 2.1.3
- fix unpackaged files

* Thu Aug 15 2002 Owen Taylor <otaylor@redhat.com>
- Add missing bonobo server files (#71261, Taco Witte)
- Remove empty NEWS, FAQ files from %%doc (#66079)

* Thu Aug  1 2002 Havoc Pennington <hp@redhat.com>
- fix desktop file really

* Thu Aug  1 2002 Havoc Pennington <hp@redhat.com>
- fix desktop file

* Mon Jul 29 2002 Havoc Pennington <hp@redhat.com>
- 2.0.2
- build with new gail

* Tue Jul 23 2002 Havoc Pennington <hp@redhat.com>
- 2.0.1

* Tue Jun 25 2002 Owen Taylor <otaylor@redhat.com>
- 2.0.0, fix missing locale files

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 1.199.0
- use desktop-file-install
- remove static libs from plugins dir

* Sat Jun 08 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.121.1

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.120.0

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 1.118.0

* Fri Apr 19 2002 Havoc Pennington <hp@redhat.com>
- move to gnome 2 version

* Thu Apr 18 2002 Havoc Pennington <hp@redhat.com>
- fix ko.po

* Thu Apr 18 2002 Havoc Pennington <hp@redhat.com>
- get correct po files from elvis 

* Thu Apr 18 2002 Havoc Pennington <hp@redhat.com>
- gedit-pofiles.tar.gz, not gedit-po.tar.gz

* Mon Apr 15 2002 Havoc Pennington <hp@redhat.com>
- merge translations

* Fri Mar 29 2002 Havoc Pennington <hp@redhat.com>
- gettextize default font

* Thu Mar 28 2002 Havoc Pennington <hp@redhat.com>
- more multibyte fixes #61948

* Wed Mar 27 2002 Havoc Pennington <hp@redhat.com>
- 0.9.7 for multibyte support

* Tue Mar 26 2002 Akira TAGOH <tagoh@redhat.com> 0.9.4-11
- gedit-0.9.4-printprefs.patch: I forgot to add to POTFILES.in...
- gedit-po.tar.gz: added. it's on CVS now.

* Sun Mar 24 2002 Akira TAGOH <tagoh@redhat.com> 0.9.4-10
- gedit-0.9.4-printprefs.patch: fix typo and sanity check.

* Mon Mar 04 2002 Akira TAGOH <tagoh@redhat.com> 0.9.4-9
- Applied a font selector patch for the printing
- fix BuildRequires for automake-1.4

* Mon Jan 28 2002 Havoc Pennington <hp@redhat.com>
- rebuild in rawhide
- fix up cflags for moved gnome headers

* Thu Jul 19 2001 Havoc Pennington <hp@redhat.com>
- add some more build requires

* Tue Jul 17 2001 Havoc Pennington <hp@redhat.com>
- require libglade-devel to build

* Fri Jun 15 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Fri Feb 23 2001 Akira TAGOH <tagoh@redhat.com>
- Fixed preview for !ja locale.

* Wed Feb 07 2001 Akira TAGOH <tagoh@redhat.com>
- Fixed handling fontset. (Bug#24998)
- Added print out for multibyte patch.

* Fri Dec 29 2000 Matt Wilson <msw@redhat.com>
- 0.9.4

* Fri Aug 11 2000 Jonathan Blandford <jrb@redhat.com>
- Up Epoch and release

* Wed Aug 09 2000 Jonathan Blandford <jrb@redhat.com>
- include glade files so that it will actually work.

* Tue Aug 01 2000 Jonathan Blandford <jrb@redhat.com>
- upgrade package to newer version at request of author.

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 19 2000 Preston Brown <pbrown@redhat.com>
- FHS paths

* Sun Jun 11 2000 Jonathan Blandford <jrb@redhat.com>
- update to 0.7.9.  Somewhat untested.

* Fri Feb 11 2000 Jonathan Blandford <jrb@redhat.com>
- removed "reverse search function as it doesn't work.

* Thu Feb 03 2000 Preston Brown <pbrown@redhat.com>
- rebuild to gzip man pages

* Mon Jan 17 2000 Elliot Lee <sopwith@redhat.com>
- If I don't put in a log entry here, people will be very upset about not
  being able to find out that I am to blame for the 0.6.1 upgrade

* Mon Aug 16 1999 Michael Fulbright <drmike@redhat.com>
- version 0.5.4

* Sat Feb 06 1999 Michael Johnson <johnsonm@redhat.com>
- Cleaned up a bit for Red Hat use

* Thu Oct 22 1998 Alex Roberts <bse@dial.pipex.com>
- First try at an RPM
