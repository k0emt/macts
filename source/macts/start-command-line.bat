@echo off
rem change the following line to set a new default dir:
cd C:\sumo-0.14.0\bin\

set default_dir=%windir%\..

cmd /K "set PATH=%CD%;%PATH%&& set SUMO_BINDIR=%CD%&& set SUMO_HOME=%CD%\..&& cd /d %default_dir% && echo info: added location of sumo executables to the search path && echo info: variables SUMO_HOME, SUMO_BINDIR are set && cd /d C:\macts\source\macts