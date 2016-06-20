
# Installation

### Linux

Required packages on Debian-based distributions

  * inkscape (version > 0.91)
  * texlive-base (pdflatex, ...)
  * pdf2svg
  * python and python-lxml (Python version < 3.0)


Run the `install.sh` script to copy all required files into the Inkscape
extension folder in your home directory.

### Windows

TODO

### Mac OS X

TODO


# Usage


### Inkscape extension

See the `demo/demo.svg` file to get a full example.

General instructions:

  * Put all text elements on a separate layer.

  * Run 'Extensions -> Render -> Render Latex Layer'. It will create a new layer
  with all text elements being rendered by `pdflatex`.

  * Switch visibility of the layers to either see the Latex code or to see the
  rendered result.

  * If you changed your Latex code or added new text elements, simply re-run
  the extension and it will update the render layer.


### Commandline mode

TODO


# Credits

Based on the great `Tex Text` extension...
