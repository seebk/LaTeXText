
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

Required Software:

   * Inkscape (version >= 0.91)
   * MiKTeX 2.9
   * pdf2svg

Instructions:

  1. Navigate to the Inkscape extension folder in the Explorer.  If Inkscape is
  installed in C:/Program Files/Inkscape/ the extension directory is at
  C:/Program Files/Inkscape/share/extensions/.

  2. Copy the `render_latex.inx` and `render_latex.py` to the extension folder.

  3. Download the whole pdf2svg repository from
  https://github.com/jalios/pdf2svg-windows as a .zip file and copy the containing
  `dist-32bits` subfolder to the Inkscape extension folder. Rename it to
  `pdf2svg` afterwards.


### Mac OS X

Required Software:

   * Inkscape (version >= 0.91)
   * MacTex
   * pdf2svg (e.g. installed from Homebrew)
   * Python lxml package

Instructions:

  1. Open a command terminal and check if you can execute `pdflatex`. If it is not
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
