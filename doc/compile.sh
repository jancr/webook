#!/usr/bin/env bash

# download python code styling
if [ ! -f pythonhighlight.sty ]; then
	wget https://raw.githubusercontent.com/olivierverdier/python-latex-highlighting/master/pythonhighlight.sty
fi

# compile 
pdflatex report.tex 
bibtex report.aux 
pdflatex report.tex 
pdflatex report.tex 
