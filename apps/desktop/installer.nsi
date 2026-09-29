
; WebBuilder Installer Script
!include "MUI2.nsh"

; App info
!define APP_NAME "WebBuilder Desktop"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "WebBuilder"
!define APP_DIR "$PROGRAMFILES\WebBuilder"
!define APP_EXE "WebBuilder.exe"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "dist/WebBuilder-Setup.exe"
InstallDir "${APP_DIR}"
RequestExecutionLevel admin

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Sections
Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\WebBuilder.exe"
    
    ; Include ML Engine data directory
    SetOutPath "$INSTDIR\ml_engine"
    File /r "ml_engine\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\WebBuilder"
    CreateShortcut "$SMPROGRAMS\WebBuilder\WebBuilder.lnk" "$INSTDIR\WebBuilder.exe"
    CreateShortcut "$DESKTOP\WebBuilder.lnk" "$INSTDIR\WebBuilder.exe"
    
    ; Uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    CreateShortcut "$SMPROGRAMS\WebBuilder\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Registry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WebBuilder" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WebBuilder" "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\WebBuilder.exe"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR\ml_engine"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\WebBuilder\*.lnk"
    RMDir "$SMPROGRAMS\WebBuilder"
    Delete "$DESKTOP\WebBuilder.lnk"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WebBuilder"
SectionEnd
