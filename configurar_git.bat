@echo off
echo ================================================================
echo        CONFIGURACION DE GIT
echo ================================================================
echo.
echo Por favor ingresa tu informacion de GitHub:
echo.

set /p EMAIL="Tu email de GitHub: "
set /p NAME="Tu nombre: "

git config --global user.email "%EMAIL%"
git config --global user.name "%NAME%"

echo.
echo ================================================================
echo Configuracion completada!
echo ================================================================
echo Email: %EMAIL%
echo Nombre: %NAME%
echo ================================================================
echo.
echo Ahora puedes hacer commits.
echo.
pause

