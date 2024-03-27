@echo off

cd %~dp0

python -m venv .venv

call %~dp0.venv\Scripts\activate

pip install -r requirements.txt

python Sinchronizer.py

pause