#!/bin/bash

DEPENDENCIES=true

echo -n "Check if PyGObject is available... "
python -c "import gi" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "NOT FOUND"
    DEPENDENCIES=false
else
    echo "OK"
fi

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

echo -n "Copying extension to ~/.config/inkscape/extensions/ ... "

cp render_latex.py ~/.config/inkscape/extensions/
cp render_latex_gtk3.py ~/.config/inkscape/extensions/
cp render_latex.inx ~/.config/inkscape/extensions/
cp render_latex_gtk3.inx ~/.config/inkscape/extensions/

echo "done"
