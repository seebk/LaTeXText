
# Installation

### Linux

Required packages on Debian-based distributions:

  * inkscape (version >= 0.91)
  * texlive-base (pdflatex, ...)
  * pdf2svg
  * python and python-lxml (Python version < 3.0)


Run the `install.sh` script to copy all required files into the Inkscape
extension folder in your home directory.

### Windows

TODO

### Mac OS X

Required Software:

   * Inkscape (version >= 0.91)
   * MacTex
   * pdf2svg (e.g. installed from Homebrew)
   * Python lxml package

Instructions:

  1. Open a command terminal and check if you can execute pdflatex. If it is not
  found verify if MacTex is up-to-date and properly installed.

  2. Install pdf2svg from Homebrew. In a terminal type `brew install pdf2svg`.
  If `brew` is not found you have to install Homebrew first (see  http://brew.sh).

  3. Install python-lxml, for example with `pip`

        $ sudo easy_install pip  
        $ sudo pip install lxml

  4. Run the install script with `./install.sh`.



# Usage

### Inkscape extension

General instructions:

  * Put all text elements on a separate layer.

  * Run 'Extensions -> Render -> Render Latex Layer'. It will create a new layer
  with all text elements being rendered by `pdflatex`.

  * Switch visibility of the layers to either see the Latex code or to see the
  rendered result.

  * If you changed your Latex code or added new text elements, simply re-run
  the extension and it will update the render layer.

See the `demo/demo.svg` file to get a full example.

### Commandline mode

TODO


# Credits

Based on the great `Tex Text` extension...
