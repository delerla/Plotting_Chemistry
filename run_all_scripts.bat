@echo off
setlocal

title Run All Analytical Scripts
echo ==============================================================================
echo  Automated Pipeline - Running All 5 Analytical Modules
echo ==============================================================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo [Running FTIR...]
python scripts\01_ftir.py
echo.

echo [Running XRD...]
python scripts\02_xrd.py
echo.

echo [Running UV-Vis...]
python scripts\03_uv_vis_kinetics.py
echo.

echo [Running XPS...]
python scripts\04_xps.py
echo.

echo [Running SEM & EDX...]
python scripts\05_sem_edx.py
echo.

echo ==============================================================================
echo  [DONE] All analytical modules executed successfully!
echo  Check the output\ folder for 600 DPI figures and LabPlot matrices.
echo ==============================================================================
pause
