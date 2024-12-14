@echo off

setlocal

set py=python\python.exe
set md=py_pdf.booklet

call %py% -m %md% --make %*

pause
