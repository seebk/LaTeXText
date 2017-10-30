
# download ressources
$msys2_repo= "http://repo.msys2.org/mingw/x86_64/"

$client = new-object System.Net.WebClient
$zipExe = join-path ${env:ProgramFiles(x86)} '7-zip\7z.exe'

function get_msys2_package($pkg){

    If (-Not (Test-Path "$pkg")){
        $client.DownloadFile("$msys2_repo/$pkg", $pkg)
    }
    &$zipExe x $pkg -y
    &$zipExe x $pkg.Substring(0,$pkg.Length-3) -y -opygobject
    Remove-Item $pkg.Substring(0,$pkg.Length-3)
}

get_msys2_package("mingw-w64-x86_64-atk-2.24.0-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-cairo-1.15.4-4-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-gdk-pixbuf2-2.36.6-2-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-gobject-introspection-runtime-1.52.0-0-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-gtk3-3.22.15-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-libepoxy-1.4.2-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-pango-1.40.6-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-python2-cairo-1.13.3-2-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-python2-gobject-3.24.1-1-any.pkg.tar.xz")

# pdf2svg
If (-Not (Test-Path "pdf2svg.zip")){
    $client.DownloadFile("https://github.com/jalios/pdf2svg-windows/archive/master.zip", "pdf2svg.zip")
}
Expand-Archive pdf2svg.zip -dest .