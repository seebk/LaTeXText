#define VERSION="0.1.1"
#define APP_ID="LaTexText"

[Setup]
AppName=LaTexText Inkscape extension
AppId={#APP_ID}
AppVerName=LaTexText Inkscape extension {#VERSION}
AppVersion={#VERSION}
VersionInfoVersion={#VERSION}
OutputBaseFilename={#APP_ID}-{#VERSION}

DefaultDirName={code:GetInkscapePath}
DirExistsWarning=no

PrivilegesRequired=admin

OutputDir=.

[Files]
Source: ..\..\extension\latextext.py; DestDir: "{app}\share\extensions"
Source: ..\..\extension\latextext.inx; DestDir: "{app}\share\extensions"
Source: ..\..\extension\latextext_gtk3.py; DestDir: "{app}\share\extensions"
Source: ..\..\extension\latextext_gtk3.inx; DestDir: "{app}\share\extensions"

Source: pdf2svg-windows-master\dist-32bits\*; DestDir: "{app}\share\extensions\pdf2svg"

Source: pygobject\mingw64\lib\python2.7\site-packages\*; DestDir: "{app}\lib\python2.7\site-packages"; Flags: recursesubdirs
Source: pygobject\mingw64\bin\*.dll; DestDir: "{app}";
Source: pygobject\mingw64\lib\girepository-1.0\*.typelib; DestDir: "{app}\lib\girepository-1.0"
Source: pygobject\mingw64\share\glib-2.0\schemas\gschemas.compiled; DestDir: "{app}\share\glib-2.0\schemas"
Source: pygobject\mingw64\share\icons\Adwaita\*; DestDir: "{app}\share\icons\Adwaita"; Flags: recursesubdirs
Source: pygobject\mingw64\share\licenses\adwaita-icon-theme\*; DestDir: "{app}\share\licenses\adwaita-icon-theme"

[Messages]
SelectDirLabel3=Please choose the folder where Inkscape was installed. Typically this is C:\Program Files\Inkscape.

[Code]

(* Try to find path to Inkscape from the Registry *)
function GetInkscapePath(S: String): String;
var
  sPath: String;
begin
  sPath := '';
  if DirExists(ExpandConstant('{pf}\Inkscape\')) then 
    sPath := ExpandConstant('{pf}\Inkscape\');
  if DirExists(ExpandConstant('{pf64}\Inkscape\')) then 
    sPath := ExpandConstant('{pf64}\Inkscape\');
  (* TODO: find path from registry... *)
  Result := ExtractFilePath(RemoveQuotes(sPath));
end;

(* Check for uninstaller executable name *)
function GetPathInstalled( AppID: String ): String;
var
  sPrevPath: String;
begin
  sPrevPath := '';
  if not RegQueryStringValue(HKLM,'Software\Microsoft\Windows\CurrentVersion\Uninstall\'+AppID+'_is1', 
                            'UninstallString', sPrevpath) then
    RegQueryStringValue(HKCU,'Software\Microsoft\Windows\CurrentVersion\Uninstall\'+AppID+'_is1',
                        'UninstallString', sPrevpath);
  Result := sPrevPath;
end;

(* Check if a old version is installed, and uninstall it if it is. *)
function checkForOldVersion(): Boolean;
var
  sPrevPath: String;
  sPrevID: String;
  msg: String;
  resultcode: Integer;
begin
    sPrevID := '{#APP_ID}';
    sPrevPath := GetPathInstalled( sprevID );
    msg := 'A previous version of ' + sPrevID + ' is already installed. ' +
           'It is recommended that you uninstall the existing version ' +
           'before running this setup. ' +
           'Click OK to uninstall the old version, or Cancel to abort.';
  
    if (Length(sPrevPath) > 0) then
    begin
      if MsgBox(msg, mbInformation, MB_okcancel) = idok then
        Result := ShellExec('open', sPrevPath, '', '', 0,
                            ewWaitUntilTerminated, resultcode)
      else
      begin
        Result := false;
      end;
    end
    else
    begin
      Result := true;
    end;
end;
 
function InitializeSetup(): Boolean;
begin
  Result := checkForOldVersion();
  Result := true;
end;