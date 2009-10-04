from common.systeminfo import module_check

SOURCES_LIST = '/etc/apt/sources.list'

AWN = ['Avant Window Navigator', 'avant-window-navigator', 'awn-project.org', 'awn.gpg']
AWN_TESTING = [_('Avant Window Navigator (Unstable Version)'), 'avant-window-navigator', 'awn-project.org', 'awn-testing.gpg']
Amarok = ['Amarok', 'amarok-nightly', 'amarok.kde.org', 'neon.gpg']
AmuleRelease = [_('aMule (Stable Version)'), 'amule', 'www.amule.org', 'amule-release.gpg']
Blueman = ['Blueman', 'blueman', 'blueman-project.org', 'blueman.gpg']
Backintime = ['Back In Time', 'backintime-gnome', 'backintime.le-web.org', 'backintime.gpg']
Breathe = [_('Breathe Icon Theme'), 'breathe-icon-theme', 'launchpad.net/breathe-icon-set', 'breathe-icon-theme.gpg']
Opera = ['Opera', 'opera', 'www.opera.com', 'opera.gpg']
Skype = ['Skype', 'skype', 'www.skype.com', '']
PlayOnLinux = ['PlayOnLinux', 'playonlinux', 'www.playonlinux.com', 'pol.gpg']
Ubuntu_cn = [_('Ubuntu Chinese Repository'), 'ubuntu-cn', 'www.ubuntu.org.cn', '']
Specto = ['Specto', 'specto', 'specto.sourceforge.net', 'specto.gpg']
OpenOffice = ['OpenOffice.org', 'openoffice', 'www.openoffice.org', 'ooo.gpg']
IBus = [_('IBus (Old Version)'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Intrepid = [_('IBus 1.2 for intrepid'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Jaunty = [_('IBus 1.2 for jaunty'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Karmic = [_('IBus 1.2 for karmic'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
Midori = ['Midori', 'midori', 'www.twotoasts.de', 'midori.gpg']
Empathy = ['Empathy', 'empathy', 'launchpad.net/~telepathy', 'empathy.gpg']
Exaile = ['Exaile', 'exaile', 'www.exaile.org', 'exaile.gpg']
WebKitGtk = ['WebKitGtk', 'webkitgtk', 'webkitgtk.org', 'webkitgtk.gpg']
Firefox = ['Firefox', 'firefox', 'www.mozilla.org', 'firefox.gpg']
MozillaSecurity = [_('Ubuntu Mozilla Security Team'), 'mozilla-security', 'launchpad.net/~ubuntu-mozilla-security', 'mozilla-security.gpg']
Compiz = ['Compiz', 'compiz', 'www.compiz.org', 'compiz.gpg']
Christine = [_('Christine Media Player'), 'christine', 'www.christine-project.org', 'christine.gpg']
ChromiumBrowser = ['Chromium Browser', 'chromium-browser', 'launchpad.net/chromium-project', 'chromium-browser.gpg']
CairoDock = ['Cairo Dock', 'cairo-dock',  'cairo-dock.org', 'cairo-dock.gpg']
Geany = ['Geany', 'geany', 'www.geany.org', 'geany.gpg']
Gnote = ['Gnote', 'gnote', 'live.gnome.org/Gnote', 'gnote.gpg']
GnomeDo = ['GNOME Do', 'gnome-do', 'do.davebsd.com', 'do.gpg']
GnomeGames = [_('Experimental Gnome Games'), 'gnome-games', 'launchpad.net/~gnome-games-experimental', 'gnome-games.gpg']
GnomeColors = ['Gnome Colors', 'gnome-colors', 'launchpad.net/~gnome-colors-packagers', 'gnome-colors.gpg']
Gmchess = [_('Chinese Chess'), 'gmchess', 'lerosua.org', 'gmchess.gpg']
GlobalMenu = [_('Gnome Global Menu'), 'gnome-globalmenu', 'code.google.com/p/gnome2-globalmenu', 'globalmenu.gpg']
GettingThingsGnome = ['Getting Things Gnome!', 'gtg', 'gtg.fritalk.com', 'gtg.gpg']
GetDeb = [_('GetDeb.net (Mirror)'), 'getdeb', 'www.getdeb.net', '']
Gwibber = ['Gwibber', 'gwibber', 'launchpad.net/gwibber', 'gwibber.gpg']
Gwibber_Daily = [_('Gwibber (Daily Version)'), 'gwibber', 'launchpad.net/gwibber', 'gwibber-daily.gpg']
Gimp_Testing = [_('GIMP (Testing Version)'), 'gimp', 'www.gimp.org', 'gimp-testing.gpg']
Banshee_Stable = [_('Banshee (Stable Version)'), 'banshee', 'banshee-project.org', 'banshee-stable.gpg']
Banshee_Unstable = [_('Banshee (Unstable Version)'), 'banshee', 'banshee-project.org', 'banshee-unstable.gpg']
Google = [_('Google Repository'), 'google', 'www.google.com/linuxrepositories/index.html', 'google.gpg']
Google_Testing = [_('Google Testing Repository'), 'google', 'www.google.com/linuxrepositories/testrepo.html', 'google.gpg']
GoogleGadgets = ['Google gadgets', 'google-gadgets', 'desktop.google.com/plugins/', 'gadgets.gpg']
ChmSee = ['Chmsee', 'chmsee', 'chmsee.gro.clinux.org', 'chmsee.gpg']
KDE4 = ['KDE 4', 'kde-4', 'www.kde.org', 'kde4.gpg']
UbuntuTweak = ['Ubuntu Tweak', 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak.gpg']
UbuntuTweakTesting = [_('Ubuntu Tweak (Unstable Version)'), 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak-unstable.gpg']
UbuDSL = ['UbuDSL', 'ubudsl', 'www.ubudsl.com', 'ubndsl.gpg']
NautilusDropbox = ['Nautilus DropBox', 'nautilus-dropbox', 'www.getdropbox.com', '']
Screenlets = ['Screenlets', 'screenlets', 'www.screenlets.org', 'screenlets.gpg']
Spicebird = ['Spicebird', 'spicebird', 'www.spicebird.com', 'spicebird.gpg']
Spicebird_Testing = [_('Spicebird (Testing Version)'), 'spicebird', 'www.spicebird.com', 'spicebird.gpg']
Synapse = ['Synapse', 'synapse', 'synapse.im', 'synapse.gpg']
Smplayer = ['SMPlayer', 'smplayer', 'smplayer.sourceforge.net', 'smplayer.gpg']
Mplayer = ['Mplayer', 'mplayer', 'www.mplayerhq.hu', 'mplayer.gpg']
Smplayer_Testing = [_('SMPlayer (Unstable Version)'), 'smplayer', 'smplayer.sourceforge.net', 'smplayer-testing.gpg']
Wine = ['Wine', 'wine', 'www.winehq.org', 'wine.gpg']
LXDE = ['LXDE', 'lxde', 'lxde.org', 'lxde.gpg']
Mono = ['Mono', 'mono', 'www.mono-project.com', 'mono.gpg']
Liferea = ['Liferea', 'liferea', 'liferea.sourceforge.net', 'liferea.gpg']
Terminator = ['Terminator', 'terminator', 'www.tenshu.net/terminator/', 'terminator.gpg']
Transmission_Stable = ['Transmission (Stable Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_stable.gpg']
Transmission_Beta = ['Transmission (Beta Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_beta.gpg']
Transmission_Nightly = ['Transmission (Nightly Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_nightly.gpg']
VirtualBox = ['VirtualBox', 'virtualbox', 'www.virtualbox.org', 'virtualbox.gpg']
VirtualBoxOse = [_('VirtualBox (Open Source Edition)'), 'virtualbox-ose', 'www.virtualbox.org', 'virtualboxose.gpg']
Vlc = [_('VLC media player'), 'vlc', 'www.videolan.org/vlc/', 'vlc.gpg']
Shutter = ['Shutter', 'shutter', 'launchpad.net/shutter', 'shutter.gpg']
Qt = ['Qt', 'qt', 'qt.nokia.com', 'qt.gpg']
Rednotebook = ['RedNoteBook', 'rednotebook', 'rednotebook.sourceforge.net', 'rednotebook.gpg']
Pidgin = ['Pidgin', 'pidgin', 'pidgin.im', 'pidgin.gpg']
Moovida = ['Moovida', 'moovida', 'www.moovida.com', 'moovida.gpg']
Moblin_Jaunty = [_('Moblin Desktop for Ubuntu 9.04 Jaunty'), 'moblin', 'launchpad.net/~sudbury-team', 'moblin-jaunty.gpg']
Moblin_Karmic = [_('Moblin Desktop for Ubuntu 9.10 Karmic'), 'moblin', 'launchpad.net/~moblin', 'moblin-karmic.gpg']
Galaxium = ['Galaxium', 'galaxium', 'code.google.com/p/galaxium/', 'galaxium.gpg']
Swiftweasel = ['Swiftweasel', 'swiftweasel', 'swiftweasel.tuxfamily.org', '']
Medibuntu = ['Medibuntu', 'medibuntu', 'www.medibuntu.org', 'medibuntu.gpg']
WineDoors = ['Wine Doors', 'wine-doors', 'www.wine-doors.org', 'wine-doors.gpg']
XBMC = ['XBMC', 'xbmc', 'xbmc.org', 'xbmc.gpg']
UbuntuX = ['Ubuntu X', 'ubuntu-x', 'launchpad.net/~ubuntu-x-swat', 'ubuntu-x.gpg']
UbuntuX_Unstable = ['Ubuntu X (Unstable)', 'ubuntu-x', 'launchpad.net/~xorg-edgers', 'ubuntu-x-unstable.gpg']
Clutter = ['Clutter', 'clutter', 'www.clutter-project.org', 'clutter.gpg']
Gloobus = ['Gloobus', 'gloobus', 'gloobus.wordpress.com', 'tweak.gpg']
Bisigi = [_('Bisigi Theme Project'), 'bisigi', 'www.bisigi-project.org', 'bisigi.gpg']
Pitivi = [_('PiTiVi video editor'), 'pitivi', 'www.pitivi.org', 'pitivi.gpg']
Kubuntu_update = [_('Kubuntu Update'), 'kubuntu-update', 'www.kubuntu.org', 'kubuntu.gpg']
Kubuntu_backports = [_('Kubuntu Backports'), 'kubuntu-backports', 'www.kubuntu.org', 'kubuntu.gpg']
Lyx = ['Lyx', 'lyx', 'www.lyx.org', 'lyx.gpg']
Tomboy_Stable = [_('Tomboy (Stable Version)'), 'tomboy', 'projects.gnome.org/tomboy/', 'tomboy.gpg']
Tomboy_Unstable = [_('Tomboy (Unstable Version)'), 'tomboy', 'projects.gnome.org/tomboy/', 'tomboy.gpg']
Inkscape_nightly = [_('Inkscape (Nightly Version)'), 'inkscape', 'www.inkscape.org', 'inkscape-nightly.gpg']
Pdfmod = ['PDF Mod', 'pdfmod', 'live.gnome.org/PdfMod', 'pdfmod.gpg']
Osdlyrics = [_('OSD Lyrics'), 'osdlyrics', 'code.google.com/p/osd-lyrics/', 'osdlyrics.gpg']
OpenShot = [_('OpenShot Video Editor'), 'openshot', 'www.openshotvideo.com', 'openshot.gpg']

SOURCES_DATA = [
    ['http://ppa.launchpad.net/reacocard-awn/ppa/ubuntu/', ['hardy','intrepid'], 'main', AWN],
    ['http://ppa.launchpad.net/awn-testing/ppa/ubuntu', ['hardy','intrepid', 'jaunty', 'karmic'], 'main', AWN_TESTING],
    ['http://ppa.launchpad.net/project-neon/ppa/ubuntu/', ['hardy', 'intrepid'], 'main', Amarok],
    ['http://ppa.launchpad.net/amule-releases/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', AmuleRelease],
    ['http://ppa.launchpad.net/blueman/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Blueman],
    ['http://le-web.org/repository', 'stable', 'main', Backintime],
    ['http://ppa.launchpad.net/breathe-dev/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Breathe],
    ['http://archive.ubuntu.org.cn/ubuntu-cn/', ['hardy', 'intrepid'], 'main restricted universe multiverse', Ubuntu_cn],
    ['http://ppa.launchpad.net/openoffice-pkgs/ppa/ubuntu', 'jaunty', 'main', OpenOffice],
    ['http://ppa.launchpad.net/globalmenu-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GlobalMenu],
    ['http://ppa.launchpad.net/markuz/ppa/ubuntu', ['jaunty'], 'main', Christine],
    ['http://ppa.launchpad.net/chromium-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', ChromiumBrowser],
    ['http://ppa.launchpad.net/specto/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Specto],
#    ['http://getdeb.masio.com.mx/', ['hardy', 'intrepid', 'jaunty'], '', GetDeb],
    ['http://ppa.launchpad.net/gnome-colors-packagers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GnomeColors],
    ['http://ppa.launchpad.net/gtg/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', GettingThingsGnome],
    ['http://ppa.launchpad.net/geany-dev/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Geany],
    ['http://ppa.launchpad.net/gnote/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gnote],
    ['http://ppa.launchpad.net/telepathy/ppa/ubuntu', ['jaunty', 'karmic'], 'main', Empathy],
    ['http://ppa.launchpad.net/exaile-devel/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Exaile],
    ['http://deb.opera.com/opera/', 'lenny', 'non-free', Opera],
    ['http://ppa.launchpad.net/firerabbit/ppa/ubuntu', ['intrepid','jaunty'], 'main', Synapse],
    ['http://download.skype.com/linux/repos/debian', 'stable', 'non-free', Skype],
    ['http://ppa.launchpad.net/rvm/smplayer/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Smplayer],
    ['http://ppa.launchpad.net/rvm/testing/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Smplayer_Testing],
    ['http://ppa.launchpad.net/rvm/mplayer/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Mplayer],
    ['http://ppa.launchpad.net/gwibber-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Gwibber],
    ['http://ppa.launchpad.net/matthaeus123/mrw-gimp-svn/ubuntu', ['jaunty', 'karmic'], 'main', Gimp_Testing], 
    ['http://ppa.launchpad.net/gwibber-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gwibber_Daily],
    ['http://ppa.launchpad.net/gmchess/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gmchess],
    ['http://deb.playonlinux.com/', ['hardy', 'intrepid', 'jaunty'], 'main', PlayOnLinux],
    ['http://ppa.launchpad.net/webkit-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', WebKitGtk],
    ['http://ppa.launchpad.net/midori/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Midori],
    ['http://ppa.launchpad.net/liferea/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Liferea],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-intrepid/ubuntu', 'intrepid', 'main', IBus_Intrepid],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-jaunty/ubuntu', 'jaunty', 'main', IBus_Jaunty],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-karmic/ubuntu', 'karmic', 'main', IBus_Karmic],
    ['http://ppa.launchpad.net/ibus-dev/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', IBus],
    ['http://ppa.launchpad.net/mono-edge/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', Mono],
    ['http://ppa.launchpad.net/ubuntu-mozilla-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Firefox],
    ['http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', MozillaSecurity],
    ['http://ppa.launchpad.net/compiz/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Compiz],
    ['http://ppa.launchpad.net/pidgin-developers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Pidgin],
    ['http://ppa.launchpad.net/moovida-packagers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Moovida],
    ['http://ppa.launchpad.net/sudbury-team/ppa/ubuntu', 'jaunty', 'main', Moblin_Jaunty],
    ['http://ppa.launchpad.net/moblin/ppa/ubuntu', ['jaunty', 'karmic'], 'main', Moblin_Karmic],
    ['http://repository.cairo-dock.org/ubuntu', ['hardy', 'intrepid'], 'cairo-dock', CairoDock],
    ['http://ppa.launchpad.net/do-core/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', GnomeDo],
    ['http://ppa.launchpad.net/banshee-team/ppa/ubuntu', ['hardy', 'intrepid'], 'main', Banshee_Stable],
    ['http://ppa.launchpad.net/banshee-unstable-team/ppa/ubuntu', ['hardy', 'intrepid', 'karmic'], 'main', Banshee_Unstable],
    ['http://dl.google.com/linux/deb/', 'stable', 'main non-free', Google],
    ['http://dl.google.com/linux/deb/', 'testing', 'non-free', Google_Testing],
    ['http://ppa.launchpad.net/googlegadgets/ppa/ubuntu', 'hardy', 'main', GoogleGadgets],
    ['http://ppa.launchpad.net/chmsee/hardy/ubuntu', 'hardy', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/intrepid/ubuntu', 'intrepid', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/jaunty/ubuntu', 'jaunty', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/karmic/ubuntu', 'karmic', 'main', ChmSee],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ppa/ubuntu', ['hardy', 'intrepid'], 'main', KDE4],
    ['http://linux.getdropbox.com/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', NautilusDropbox],
    ['http://ppa.launchpad.net/tualatrix/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', UbuntuTweak],
    ['http://ppa.launchpad.net/ubuntu-tweak-testing/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', UbuntuTweakTesting],
    ['http://ppa.launchpad.net/adrian5632/ppa/ubuntu', ['hardy', 'intrepid'], 'main', UbuDSL],
    ['http://ppa.launchpad.net/gilir/ppa/ubuntu', ['hardy', 'intrepid'], 'main', Screenlets],
    ['http://ppa.launchpad.net/spicebird/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', Spicebird],
    ['http://ppa.launchpad.net/spicebird/test-build/ubuntu', ['jaunty', 'karmic'], 'main', Spicebird_Testing],
    ['http://wine.budgetdedicated.com/apt', ['hardy', 'intrepid', 'jaunty'], 'main', Wine],
    ['http://ppa.launchpad.net/lxde/ppa/ubuntu', 'hardy', 'main', LXDE],
    ['http://ppa.launchpad.net/gnome-terminator/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Terminator],
    ['http://ppa.launchpad.net/transmissionbt/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Stable],
    ['http://ppa.launchpad.net/transmissionbt-beta/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Beta],
    ['http://ppa.launchpad.net/transmissionbt-nightly/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Nightly],
    ['http://download.virtualbox.org/virtualbox/debian', ['hardy', 'intrepid', 'jaunty'], 'non-free', VirtualBox],
    ['http://ppa.launchpad.net/debfx/virtualbox/ubuntu', ['intrepid', 'jaunty'], 'main', VirtualBoxOse],
    ['http://ppa.launchpad.net/c-korn/vlc/ubuntu', ['jaunty'], 'main', Vlc],
    ['http://ppa.launchpad.net/shutter/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Shutter],
    ['http://ppa.launchpad.net/debfx/qt/ubuntu', 'jaunty', 'main', Qt],
    ['http://robin.powdarrmonkey.net/ubuntu', 'jaunty', '', Rednotebook],
    ['http://ppa.launchpad.net/galaxium/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', Galaxium],
    ['http://download.tuxfamily.org/swiftweasel', ['hardy', 'intrepid'], 'multiverse', Swiftweasel],
    ['http://packages.medibuntu.org/', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'free non-free', Medibuntu],
    ['http://ppa.launchpad.net/wine-doors-dev-team/ppa/ubuntu', 'intrepid', 'main', WineDoors],
    ['http://ppa.launchpad.net/team-xbmc/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', XBMC],
    ['http://ppa.launchpad.net/gnome-games-experimental/ppa/ubuntu', ['jaunty', 'karmic'], 'main', GnomeGames],
    ['http://ppa.launchpad.net/ubuntu-x-swat/x-updates/ubuntu', ['jaunty', 'karmic'], 'main', UbuntuX],
    ['http://ppa.launchpad.net/xorg-edgers/ppa/ubuntu', ['jaunty', 'karmic'], 'main', UbuntuX_Unstable],
    ['http://ppa.launchpad.net/njpatel/clutter-edgers/ubuntu', 'jaunty', 'main', Clutter],
    ['http://ppa.launchpad.net/tualatrix/gloobus/ubuntu', 'jaunty', 'main', Gloobus],
    ['http://ppa.launchpad.net/bisigi/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Bisigi],
    ['http://ppa.launchpad.net/gstreamer-developers/ppa/ubuntu', 'jaunty', 'main', Pitivi],
    ['http://ppa.launchpad.net/kubuntu-ppa/ppa/ubuntu', 'jaunty', 'main', Kubuntu_update],
    ['http://ppa.launchpad.net/kubuntu-ppa/backports/ubuntu', 'jaunty', 'main', Kubuntu_backports],
    ['http://ppa.launchpad.net/lyx/ppa/ubuntu', 'jaunty', 'main', Lyx],
    ['http://ppa.launchpad.net/tomboy-packagers/stable/ubuntu', ['jaunty', 'karmic'], 'main', Tomboy_Stable],
    ['http://ppa.launchpad.net/tomboy-packagers/development/ubuntu', ['jaunty', 'karmic'], 'main', Tomboy_Unstable],
    ['http://ppa.launchpad.net/inkscape-nightly/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Inkscape_nightly],
    ['http://ppa.launchpad.net/pdfmod-team/ppa/ubuntu', ['karmic'], 'main', Pdfmod],
    ['http://ppa.launchpad.net/osd-lyrics/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Osdlyrics],
    ['http://ppa.launchpad.net/openshot.developers/ppa/ubuntu', ['jaunty', 'karmic'], 'main', OpenShot],
]

SOURCES_DEPENDENCIES = {
    Midori[0]: WebKitGtk[0],
    Liferea[0]: WebKitGtk[0],
    Smplayer[0]: Mplayer[0],
    Smplayer_Testing[0]: Mplayer[0],
    Moblin_Jaunty[0]: Moblin_Karmic[0],
}

SOURCES_CONFLICTS = {
    Skype[0]: Medibuntu[0],
}

def is_ubuntu(distro):
    if type(distro) == list:
        for dis in distro:
            if dis in module_check.get_supported_ubuntu():
                return True
            return False
    else:
        if distro in module_check.get_supported_ubuntu():
            return True
        return False

def filter_sources():
    newsource = []
    for item in SOURCES_DATA:
        distro = item[1]
        if is_ubuntu(distro):
            if module_check.get_codename() in distro:
                newsource.append([item[0], module_check.get_codename(), item[2], item[3]])
        else:
            newsource.append(item)

    return newsource

SOURCES_DATA = filter_sources()
