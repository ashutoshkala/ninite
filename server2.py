from flask import Flask, request, render_template

app = Flask(__name__)
code = """

        #/bin/bash
clear && rm -rf ~/macapps && mkdir ~/macapps > /dev/null && cd ~/macapps

###############################
#    Print script header      #
###############################

echo $"
                                                                                                       
                  ,;         .             L.                                                        ,;
                f#i         ;W             EW:        ,ft                                          f#i 
 GEEEEEEEL    .E#t         f#E GEEEEEEEL   E##;       t#E            ..           ..       :     .E#t  
 ,;;L#K;;.   i#W,        .E#f  ,;;L#K;;.   E###t      t#E           ;W,          ,W,     .Et    i#W,   
    t#E     L#D.        iWW;      t#E      E#fE#f     t#E          j##,         t##,    ,W#t   L#D.    
    t#E   :K#Wfff;     L##Lffi    t#E      E#t D#G    t#E         G###,        L###,   j###t :K#Wfff;  
    t#E   i##WLLLLt   tLLG##L     t#E      E#t  f#E.  t#E       :E####,      .E#j##,  G#fE#t i##WLLLLt 
    t#E    .E#L         ,W#i      t#E      E#t   t#K: t#E      ;W#DG##,     ;WW; ##,:K#i E#t  .E#L     
    t#E      f#E:      j#E.       t#E      E#t    ;#W,t#E     j###DW##,    j#E.  ##f#W,  E#t    f#E:   
    t#E       ,WW;   .D#j         t#E      E#t     :K#D#E    G##i,,G##,  .D#L    ###K:   E#t     ,WW;  
    t#E        .D#; ,WK,          t#E      E#t      .E##E  :K#K:   L##, :K#t     ##D.    E#t      .D#; 
     fE          tt EG.            fE      ..         G#E ;##D.    L##, ...      #G      ..         tt 
      :             ,               :                  fE ,,,      .,,           j                     
                                                        ,                                              


"

###############################
#    Define worker functions  #
###############################
versionChecker() {
	local v1=$1; local v2=$2;
	while [ `echo $v1 | egrep -c [^0123456789.]` -gt 0 ]; do
		char=`echo $v1 | sed 's/.*\([^0123456789.]\).*/\1/'`; char_dec=`echo -n "$char" | od -b | head -1 | awk {'print $2'}`; v1=`echo $v1 | sed "s/$char/.$char_dec/g"`; done
	while [ `echo $v2 | egrep -c [^0123456789.]` -gt 0 ]; do
		char=`echo $v2 | sed 's/.*\([^0123456789.]\).*/\1/'`; char_dec=`echo -n "$char" | od -b | head -1 | awk {'print $2'}`; v2=`echo $v2 | sed "s/$char/.$char_dec/g"`; done
	v1=`echo $v1 | sed 's/\.\./.0/g'`; v2=`echo $v2 | sed 's/\.\./.0/g'`;
	checkVersion "$v1" "$v2"
} 
checkVersion() {
	[ "$1" == "$2" ] && return 1
	v1f=`echo $1 | cut -d "." -f -1`;v1b=`echo $1 | cut -d "." -f 2-`;v2f=`echo $2 | cut -d "." -f -1`;v2b=`echo $2 | cut -d "." -f 2-`;
	if [[ "$v1f" != "$1" ]] || [[ "$v2f" != "$2" ]]; then [[ "$v1f" -gt "$v2f" ]] && return 1; [[ "$v1f" -lt "$v2f" ]] && return 0;
		[[ "$v1f" == "$1" ]] || [[ -z "$v1b" ]] && v1b=0; [[ "$v2f" == "$2" ]] || [[ -z "$v2b" ]] && v2b=0; checkVersion "$v1b" "$v2b"; return $?
	else [ "$1" -gt "$2" ] && return 1 || return 0; fi
}

echo "hiii"

appStatus() {
  if [ ! -d "/Applications/$1" ]; then echo "uninstalled"; else
    if [[ $5 == "build" ]]; then BUNDLE="CFBundleVersion"; else BUNDLE="CFBundleShortVersionString"; fi
    INSTALLED=`/usr/libexec/plistbuddy -c Print:$BUNDLE: "/Applications/$1/Contents/Info.plist"`
      if [ $4 == "dmg" ]; then COMPARETO=`/usr/libexec/plistbuddy -c Print:$BUNDLE: "/Volumes/$2/$1/Contents/Info.plist"`;
      elif [[ $4 == "zip" || $4 == "tar" ]]; then COMPARETO=`/usr/libexec/plistbuddy -c Print:$BUNDLE: "$3$1/Contents/Info.plist"`; fi
    checkVersion "$INSTALLED" "$COMPARETO"; UPDATED=$?;
    if [[ $UPDATED == 1 ]]; then echo "updated"; else echo "outdated"; fi; fi
}
installApp() {
  echo $'\360\237\214\200  - ['$2'] Downloading app...'
  if [ $1 == "dmg" ]; then curl -s -L -o "$2.dmg" $4; yes | hdiutil mount -nobrowse "$2.dmg" -mountpoint "/Volumes/$2" > /dev/null;
    if [[ $(appStatus "$3" "$2" "" "dmg" "$7") == "updated" ]]; then echo $'\342\235\214  - ['$2'] Skipped because it was already up to date!\n';
    elif [[ $(appStatus "$3" "$2" "" "dmg" "$7") == "outdated" && $6 != "noupdate" ]]; then ditto "/Volumes/$2/$3" "/Applications/$3"; echo $'\360\237\214\216  - ['$2'] Successfully updated!\n'
    elif [[ $(appStatus "$3" "$2" "" "dmg" "$7") == "outdated" && $6 == "noupdate" ]]; then echo $'\342\235\214  - ['$2'] This app cant be updated!\n'
    elif [[ $(appStatus "$3" "$2" "" "dmg" "$7") == "uninstalled" ]]; then cp -R "/Volumes/$2/$3" /Applications; echo $'\360\237\221\215  - ['$2'] Succesfully installed!\n'; fi
    hdiutil unmount "/Volumes/$2" > /dev/null && rm "$2.dmg"
  elif [ $1 == "zip" ]; then curl -s -L -o "$2.zip" $4; unzip -qq "$2.zip";
    if [[ $(appStatus "$3" "" "$5" "zip" "$7") == "updated" ]]; then echo $'\342\235\214  - ['$2'] Skipped because it was already up to date!\n';
    elif [[ $(appStatus "$3" "" "$5" "zip" "$7") == "outdated" && $6 != "noupdate" ]]; then ditto "$5$3" "/Applications/$3"; echo $'\360\237\214\216  - ['$2'] Successfully updated!\n'
    elif [[ $(appStatus "$3" "" "$5" "zip" "$7") == "outdated" && $6 == "noupdate" ]]; then echo $'\342\235\214  - ['$2'] This app cant be updated!\n'
    elif [[ $(appStatus "$3" "" "$5" "zip" "$7") == "uninstalled" ]]; then mv "$5$3" /Applications; echo $'\360\237\221\215  - ['$2'] Succesfully installed!\n'; fi;
    rm -rf "$2.zip" && rm -rf "$5" && rm -rf "$3"
  elif [ $1 == "tar" ]; then curl -s -L -o "$2.tar.bz2" $4; tar -zxf "$2.tar.bz2" > /dev/null;
    if [[ $(appStatus "$3" "" "$5" "tar" "$7") == "updated" ]]; then echo $'\342\235\214  - ['$2'] Skipped because it was already up to date!\n';
    elif [[ $(appStatus "$3" "" "$5" "tar" "$7") == "outdated" && $6 != "noupdate" ]]; then ditto "$3" "/Applications/$3"; echo $'\360\237\214\216  - ['$2'] Successfully updated!\n';
    elif [[ $(appStatus "$3" "" "$5" "tar" "$7") == "outdated" && $6 == "noupdate" ]]; then echo $'\342\235\214  - ['$2'] This app cant be updated!\n'
    elif [[ $(appStatus "$3" "" "$5" "tar" "$7") == "uninstalled" ]]; then mv "$5$3" /Applications; echo $'\360\237\221\215  - ['$2'] Succesfully installed!\n'; fi
    rm -rf "$2.tar.bz2" && rm -rf "$3"; fi
}


"""

footer = """
      echo $'--------------------------------------------------------------------------------'
    echo $'\360\237\222\254  - Thank you for using our website name!! Liked it? Recommend us to your friends!'
    echo $'\360\237\222\260  - The time is gold. Have I saved you a lot? :) - donate
    echo $'--------------------------------------------------------------------------------\n'
    rm -rf ~/macapps
    """

list = [
    '"dmg" "Firefox" "Firefox.app" "http://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US" "" "" ""',
    '"zip" "Chromium" "Chromium.app" "https://download-chromium.appspot.com/dl/Mac" "chrome-mac/" "" ""',
    '"dmg" "Firefox Dev." "Firefox Developer Edition.app" "http://download.mozilla.org/?product=firefox-devedition-latest-ssl&os=osx&lang=en-US" "" "" ""',
    '"dmg" "Docker" "Docker.app" "https://desktop.docker.com/mac/main/amd64/Docker.dmg" "" "" ""',
    '"zip" "Visual Studio Code" "Visual Studio Code.app" "http://go.microsoft.com/fwlink/?LinkID=620882" "" "" ""',
    '"dmg" "Google Chrome Canary" "Google Chrome Canary.app" "https://dl.google.com/chrome/mac/universal/canary/googlechromecanary.dmg" "" "" ""',
    '"dmg" "Brave" "Brave Browser.app" "https://referrals.brave.com/latest/Brave-Browser.dmg" "" "" ""',
    '"dmg" "Vivaldi" "Vivaldi.app" "https://downloads.vivaldi.com/stable/Vivaldi.6.0.2979.18.universal.dmg" "" "" ""',
    '"dmg" "TorBrowser" "Tor Browser.app" "https://www.torproject.org/dist/torbrowser/11.0.3/TorBrowser-11.0.3-osx64_en-US.dmg" "" "" ""',
    '"dmg" "Sleipnir" "Sleipnir.app" "http://www.fenrir-inc.com/services/download.php?file=Sleipnir.dmg" "" "" ""',
    '"dmg" "Yandex" "Yandex.app" "https://cache-mskmar01.cdn.yandex.net/download.cdn.yandex.net/browser/yandex/ru/Yandex.dmg" "" "" ""',
    '"zip" "Unison 2" "Unison.app" "http://download.panic.com/unison/Unison%202.2.zip" "" "" ""',
    '"dmg" "Evernote" "Evernote.app" "http://evernote.com/download/get.php?file=EvernoteMac" "" "" ""',
    '"dmg" "aText" "aText.app" "http://www.trankynam.com/atext/downloads/aText.dmg" "" "" ""',
    '"zip" "BetterTouchTool" "BetterTouchTool.app" "http://bettertouchtool.net/BetterTouchTool.zip" "" "" ""',
    '"dmg" "OmniFocus" "OmniFocus.app" "http://www.omnigroup.com/download/latest/omnifocus" "" "" ""',
    '"dmg" "Dropbox" "Dropbox.app" "https://www.dropbox.com/download?plat=mac" "" "" ""',
    '"dmg" "Drive" "Backup and Sync.app" "https://dl-ssl.google.com/drive/installgoogledrive.dmg" "" "" ""',
    '"dmg" "Sync" "Resilio Sync.app" "https://download-cdn.resilio.com/stable/osx/Resilio-Sync.dmg" "" "" ""',
    ' "dmg" "MEGAsync" "MEGAsync.app" "https://mega.co.nz/MEGAsyncSetup.dmg" "" "" ""',
    '"dmg" "OpenOffice" "OpenOffice.app" "https://downloads.sourceforge.net/project/openofficeorg.mirror/4.1.11/binaries/en-US/Apache_OpenOffice_4.1.11_MacOS_x86-64_install_en-US.dmg" "" "" ""',
    '"dmg" "LibreOffice" "LibreOffice.app" "http://download.documentfoundation.org/libreoffice/stable/7.5.3/mac/x86_64/LibreOffice_7.5.3_MacOS_x86-64.dmg" "" "" ""',
    '"dmg" "Alfred 4" "Alfred 4.app" "https://cachefly.alfredapp.com/Alfred_5.1_2134.dmg" "" "" ""',
    '"dmg" "Quicksilver" "Quicksilver.app" "http://github.qsapp.com/downloads/Quicksilver.2.0.2.dmg" "" "" ""',
    '"zip" "CCC" "Carbon Copy Cloner.app" "http://bombich.com/software/download_ccc.php?v=latest" "" "" ""',
    '"dmg" "SuperDuper!" "SuperDuper!.app" "http://www.shirt-pocket.com/downloads/SuperDuper!.dmg" "" "" ""',
    '"dmg" "HyperSwitch" "HyperSwitch.app" "http://bahoom.com/hyperswitch/download" "" "" ""',
    '"zip" "Fantastical" "Fantastical.app" "http://flexibits.com/fantastical/download" "" "" ""',
    "ihisas",
]


# print(list(6))
# @app.route('/')
@app.route("/", methods=["GET", "POST"])
def main():
    def split(s):
        result = [int(s[i : i + 2]) for i in range(0, len(s), 2)]
        return result

    if request.method == "POST":
        # getting input with name = fname in HTML form
        selected = request.form.get("select")
        selected = str(selected)
        x = split(selected)
        s = code
        p = "installApp "
        for i in range(len(x)):
            o = ""
            o = p + list[i]
            s += o
        s += footer
        return s
    # return render_template("form.html")
    return render_template("index.html")
    # return "hi"


@app.route("/download")
def search():
    bar = request.args.getlist("id")
    print(bar)
    s = code
    # print(list[int(bar[0])])
    p = "installApp "
    for i in bar:
        o = ""
        o = p + list[int(i)]
        s += o
    s += footer
    return s


if __name__ == "__main__":
    app.run(debug=True)
