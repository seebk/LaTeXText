#!/bin/bash

DEPENDENCIES=true
GTK3=false

echo -n "Check if Python LXML is available... "
python -c "import lxml" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "NOT FOUND"
    DEPENDENCIES=false
else
    echo "OK"
fi

if [ "$DEPENDENCIES" = false ]; then
    echo "ERROR: some required Python modules are missing."
    exit
fi

echo -n "Check if PyGObject is available... "
python -c "import gi" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "NOT FOUND, installing standard extension GUI"
    GTK3=false
else
    GTK3=true
    echo "OK"
fi

echo -n "Copying extension to ~/.config/inkscape/extensions/ ... "

cp extension/latextext.py ~/.config/inkscape/extensions/
    
if [ "$GTK3" = true ]; then
    cp extension/latextext_gtk3.py ~/.config/inkscape/extensions/
    cp extension/latextext_gtk3.inx ~/.config/inkscape/extensions/
else
    cp extension/latextext.inx ~/.config/inkscape/extensions/
fi

echo "done"
