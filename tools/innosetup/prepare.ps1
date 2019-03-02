
# Download ressources from MSYS2
$msys2_repo= "http://repo.msys2.org/mingw/x86_64/"

$client = new-object System.Net.WebClient
$zipExe = join-path ${env:ProgramFiles} '7-zip\7z.exe'
$pwd = Get-Location

function get_msys2_package($pkg){	
    If (-Not (Test-Path "$pkg")){
    	Write-Host "Downloading $pkg ..."
        $client.DownloadFile("$msys2_repo/$pkg", (Join-Path $pwd $pkg))
    }
    Write-Host "Extracting $pkg ..."
    &$zipExe x $pkg -y | Out-Null
    &$zipExe x $pkg.Substring(0,$pkg.Length-3) -y -opygobject | Out-Null
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
get_msys2_package("mingw-w64-x86_64-adwaita-icon-theme-3.24.0-1-any.pkg.tar.xz")

# Dependencies for glib-compile-schemas.exe
get_msys2_package("mingw-w64-x86_64-glib2-2.52.0-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-pcre-8.41-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-gettext-0.19.8.1-3-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-libwinpthread-git-5.0.0.4833.f057c525-1-any.pkg.tar.xz")
get_msys2_package("mingw-w64-x86_64-libiconv-1.15-1-any.pkg.tar.xz")


# Compile gschemas
Write-Host "Compiling glib schemas ..."
&"pygobject\mingw64\bin\glib-compile-schemas.exe" pygobject\mingw64\share\glib-2.0\schemas

# pdf2svg
If (-Not (Test-Path "pdf2svg.zip")){
	Write-Host "Downloading pdf2svg ..."
    $client.DownloadFile("https://github.com/jalios/pdf2svg-windows/archive/master.zip", "pdf2svg.zip")
}
Write-Host "Extracting pdf2svg ..."
Expand-Archive pdf2svg.zip -Force -dest .