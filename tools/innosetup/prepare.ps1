
# download ressources
$client = new-object System.Net.WebClient

If (-Not (Test-Path "pygi.7z")){
    $client.DownloadFile("http://downloads.sourceforge.net/project/pygobjectwin32/pygi-aio-3.4.2_rev11.7z", "pygi.7z")
}

If (-Not (Test-Path "pdf2svg.zip")){
    $client.DownloadFile("https://github.com/jalios/pdf2svg-windows/archive/master.zip", "pdf2svg.zip")
}


# unpack
$zipExe = join-path ${env:ProgramFiles(x86)} '7-zip\7z.exe'
&$zipExe x pygi.7z -y "-opygi"
Expand-Archive pdf2svg.zip -dest .

# prepare python packages
mkdir site-packages
robocopy /e pygi/py26 site-packages
robocopy /e pygi/gtk site-packages/gtk /XD "locale" "poppler" "webkitgtk-3.0" "gstreamer-1.0" "babl-0.1" "gegl-0.2" "gtk-doc" "gedit" /XF "libpoppler-34.dll" "libtelepathy-glib-0.dll" "libwebkitgtk-3.0-0.dll" "libgexiv2-1.dll"