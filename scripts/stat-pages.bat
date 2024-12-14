@echo off

setlocal

set py=python\python.exe
set md=py_pdf.stat_pages

call %py% -m %md% %*

pause
