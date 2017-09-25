#!/usr/bin/env python
from __future__ import print_function

import sys
import math
import os
import glob
import platform
import subprocess
import tempfile
import shutil
import re
from lxml import etree


MAC = "Mac OS"
WINDOWS = "Windows"
PLATFORM = platform.system()

STANDALONE = False
LOG_LEVEL = 3


######################
# XML namespace definitions

SVG_NS = u"http://www.w3.org/2000/svg"
INKSCAPE_NS = u"http://www.inkscape.org/namespaces/inkscape"
XLINK_NS = u"http://www.w3.org/1999/xlink"
RENDLTX_NS = u"http://NOTSET"

NSS = {
    u'inkscape': INKSCAPE_NS,
    u'svg': SVG_NS,
    u'xlink': XLINK_NS,
    u'rendltx': RENDLTX_NS,
}

# uncocmment the following to register namespaces globally if newer LXML versions
# are shipped with Inkscape on Windows, then remove 'nsmap=NSS' syntax
# etree.register_namespace("rendltx", RENDLTX_NS)

######################
# logging functions

log_level_debug = 1
log_level_info = 2
log_level_error = 3


def log_info(*msg):
    log_message(log_level_info, *msg)


def log_debug(*msg):
    log_message(log_level_debug, *msg)


def log_error(*msg):
    log_message(log_level_error, *msg)


def log_message(msg_level, *msg):
    global LOG_LEVEL
    if LOG_LEVEL > msg_level:
        return

    global STANDALONE
    if STANDALONE:
        print(*msg)
    else:
        for m in msg:
            inkex.debug(m)


def set_log_level(l):
    global LOG_LEVEL
    LOG_LEVEL = l


######################
#  Check if we are in the inkscape extension folder
try:
    import inkex
    EXT_PATH = os.path.abspath(os.path.split(inkex.__file__)[0])
    STANDALONE = False
except ImportError:
    STANDALONE = True


######################
# SVG transformer
#    Parse, modify and create SVG transform attributes
class SvgTransformer:

    # matrix multiplication helper function
    def _matmult(self, a, b):
        zip_b = zip(*b)
        # uncomment next line if python 3 :
        # zip_b = list(zip_b)
        return [[sum(ele_a * ele_b for ele_a, ele_b in zip(row_a, col_b))
                 for col_b in zip_b] for row_a in a]

    # init a neutral transform matrix
    def _init_matrix(self):
        matrix = [[0] * 3 for i in range(3)]
        matrix[0][0] = 1
        matrix[1][1] = 1
        matrix[2][2] = 1
        return matrix

    # parse an SVG transform command and extract its type and parameters
    def _parse_transform(self, attrStr):
        if "translate" in attrStr:
            coordStr = attrStr[10:-1]
            coordList = list([float(coord) for coord in coordStr.split(",") if coord])
            return coordList, "translate"
        elif "matrix" in attrStr:
            coordStr = attrStr[7:-1]
            coordList = list([float(coord) for coord in coordStr.split(",") if coord])
            return coordList, "matrix"
        elif "rotate" in attrStr:
            coordStr = attrStr[8:-1]
            coordList = list([float(coord) for coord in coordStr.split(",") if coord])
            return coordList, "rotate"
        elif "scale" in attrStr:
            coordStr = attrStr[6:-1]
            coordList = list([float(coord) for coord in coordStr.split(",") if coord])
            if len(coordList) == 1:
                coordList.append(coordList[0])
            return coordList, "scale"
        else:
            return None, None

    # constructor
    def __init__(self, attrStr=""):
        self.matrix = self._init_matrix()
        self.transform_type = ""
        if attrStr:
            self.apply_transform(attrStr)

    # apply a transform given in form of a SVG transform command
    def apply_transform(self, attrStr):
        coordList, transform_type = self._parse_transform(attrStr)
        if transform_type == "translate":
            new_matrix = self._init_matrix()
            new_matrix[0][2] = coordList[0]
            new_matrix[1][2] = coordList[1]
            self.matrix = self._matmult(new_matrix, self.matrix)
        elif transform_type == "matrix":
            log_debug(coordList)
            new_matrix = self._init_matrix()
            log_debug(new_matrix)
            new_matrix[0][0] = coordList[0]
            new_matrix[1][0] = coordList[1]
            new_matrix[0][1] = coordList[2]
            new_matrix[1][1] = coordList[3]
            new_matrix[0][2] = coordList[4]
            new_matrix[1][2] = coordList[5]
            self.matrix = self._matmult(new_matrix, self.matrix)
        elif transform_type == "rotate":
            log_debug(coordList)
            new_matrix = self._init_matrix()
            log_debug(new_matrix)
            new_matrix[0][0] = math.cos(math.radians(coordList[0]))
            new_matrix[1][0] = math.sin(-1.0 * math.radians(coordList[0]))
            new_matrix[0][1] = math.sin(math.radians(coordList[0]))
            new_matrix[1][1] = math.cos(math.radians(coordList[0]))
            self.matrix = self._matmult(new_matrix, self.matrix)
        elif transform_type == "scale":
            log_debug(coordList)
            new_matrix = self._init_matrix()
            log_debug(new_matrix)
            new_matrix[0][0] = coordList[0]
            new_matrix[1][1] = coordList[1]
            self.matrix = self._matmult(new_matrix, self.matrix)
        else:
            log_error("\nUnknown transform: " + attrStr)
            raise RuntimeError()

    # scaling
    def scale(self, factor):
        new_matrix = self._init_matrix()
        new_matrix[0][0] = factor
        new_matrix[1][1] = factor
        self.matrix = self._matmult(new_matrix, self.matrix)

    # translate
    def translate(self, x, y):
        new_matrix = self._init_matrix()
        new_matrix[0][2] = x
        new_matrix[1][2] = y
        self.matrix = self._matmult(new_matrix, self.matrix)

    # return current transformation as SVG transform matrix string
    def to_string(self):
        return "matrix(%f,%f,%f,%f,%f,%f)" % (self.matrix[0][0], self.matrix[1][0], self.matrix[0][1], self.matrix[1][1], self.matrix[0][2], self.matrix[1][2])


# https://gist.github.com/Leechael/8144525
class dict2obj(dict):
    def __init__(self, d, default=None):
        self.__d = d
        self.__default = default
        super(self.__class__, self).__init__(d)

    def __getattr__(self, k):
        if k in self.__d:
            v = self.__d[k]
            if isinstance(v, dict):
                v = self.__class__(v)
            setattr(self, k, v)
            return v
        return self.__default


######################
# SVG processor
#    Retrieve all text elements, render them with Latex and add the result in
#    a new layer
class SvgProcessor:

    def __init__(self, infile, options):
        self.options = options
        self.svg_input = infile

        self.defaults = dict2obj({"scale": 1.0, "depth": 0.0, "fontsize": 10, "preamble": "",
                                  "math": False, "newline": False})

        # load from file or use existing document root
        if isinstance(infile, str):
            tree = etree.parse(self.svg_input)
            self.docroot = tree.getroot()
        else:
            self.docroot = infile.getroot()

        # check for render layer and try to read options
        render_layer = self.docroot.find("{%s}g[@id='ltx-render-layer']" % SVG_NS)
        if render_layer is not None:
            self.get_parameters(render_layer)

        # Determine unit conversion scale factor
        # here we have to find our document units and calculate a conversion
        # factor to get from pt to the respective document unit.
        match = re.match(r"^([0-9][0-9.]*)\s*(em|ex|px|pt|pc|cm|mm|in|)$", self.docroot.attrib["width"])
        user_unit = match.group(2)
        if not user_unit:
            user_unit = 'px'
        svg_width = float(match.group(1))
        # match = re.match(r"^([0-9][0-9.]*)\s*(em|ex|px|pt|pc|cm|mm|in|)$", self.docroot.attrib["height"])
        # svg_height = match.group(1)

        # default conversion factors from unit X to px at 90 dpi
        # Note: Latex output converted to SVG is always in pt
        units_px = {'px': 1, 'pt': 1.25, 'pc': 15, 'mm': 3.543307, 'cm': 35.43307, 'in': 90}

        if 'viewBox' in self.docroot.attrib:
            viewbox = self.docroot.attrib['viewBox'].split()
            self.unit_conversion_factor = units_px['pt'] * (float(viewbox[2]) / (svg_width * units_px[user_unit]))
        else:
            self.unit_conversion_factor = units_px['pt'] / units_px[user_unit]

        # set defaults if any required option is still None
        if self.options.scale is None:
            self.options.scale = self.defaults.scale
        if self.options.depth is None:
            self.options.depth = self.defaults.depth
        if self.options.fontsize is None:
            self.options.fontsize = self.defaults.fontsize
        if self.options.preamble is None:
            self.options.preamble = self.defaults.preamble
        if self.options.math is None:
            self.options.math = self.defaults.math
        if self.options.newline is None:
            self.options.newline = self.defaults.newline

    def add_id_prefix(self, node, prefix):
        for el in node.xpath('//*[attribute::id]', namespaces=NSS):
            el.attrib['id'] = prefix + "-" + el.attrib['id']
        for el in node.xpath('//*[attribute::xlink:href]', namespaces=NSS):
            old_href = el.attrib['{%s}href' % XLINK_NS]
            el.attrib['{%s}href' % XLINK_NS] = "#" + prefix + "-" + old_href[1:]
        node.attrib['id'] = prefix

    def insert_node(self, node, root, prefix):
        # check if node already exists
        old_node = None
        for el in root.getiterator():
            if 'id' in el.attrib and el.attrib['id'] == prefix:
                old_node = el
                root.remove(el)

        # transfer style and transforms etc.
        if old_node is not None:
            if 'transform' in old_node.attrib:
                node.attrib['transform'] = old_node.attrib['transform']
            if 'style' in old_node.attrib:
                self.apply_style(node, old_node.attrib['style'])

        root.append(node)

    def apply_style(self, node, style):
        # TODO: strip spaces from style string before splitting
        # properties = dict([item.split(":") for item in style.split(";") if item])
        # style_render = ""

        # if 'fill' in properties:
        #    style_render += "fill:" + properties['fill'] + ';'

        node.attrib['style'] = style
        for g in node.findall('.//{%s}g' % SVG_NS):
            if 'style' in g.attrib:
                g.attrib.pop('style')

        return node

    def align_placement(self, node, txt):
        if 'x' in txt.attrib and 'y' in txt.attrib:
            aligned_pos = (float(txt.attrib['x']), float(txt.attrib['y']))
        else:
            aligned_pos = (0, 0)

        # remove position offset, anchor is top/right most element
        pos_list = list()
        for el in node.getiterator():
            if 'x' in el.attrib and 'y' in el.attrib:
                el_pos = (float(el.attrib['x']), float(el.attrib['y']))
                pos_list.append(el_pos)

        if not pos_list:
            log_debug("Warning: Element has no x/y position assigned!")
            return node

        pos_list.sort()
        pos_offset = pos_list[0]

        for el in node.getiterator():
            if 'x' in el.attrib:
                el.attrib['x'] = str(float(el.attrib['x']) - pos_offset[0])
            if 'y' in el.attrib:
                el.attrib['y'] = str(float(el.attrib['y']) - pos_offset[1])

        transform = SvgTransformer()
        transform.scale(self.unit_conversion_factor)
        transform.translate(aligned_pos[0], aligned_pos[1])

        if 'transform' in txt.attrib:
            transform.apply_transform(txt.attrib['transform'])

        for el in txt.iterancestors():
            if 'transform' in el.attrib:
                transform.apply_transform(el.attrib['transform'])

        log_debug(transform.to_string())
        node.attrib['transform'] = transform.to_string()

        return node

    def get_parameters(self, render_layer):
        if render_layer is None:
            return

        preamble_path = render_layer.attrib.get('{%s}preamble' % RENDLTX_NS, None)
        if self.options.preamble is None and preamble_path:
            self.options.preamble = preamble_path

        scale = render_layer.attrib.get('{%s}scale' % RENDLTX_NS, None)
        if self.options.scale is None and scale is not None:
            self.options.scale = float(scale)

        depth = render_layer.attrib.get('{%s}depth' % RENDLTX_NS, None)
        if self.options.depth is None and scale is not None:
            self.options.depth = float(depth)

        fontsize = render_layer.attrib.get('{%s}fontsize' % RENDLTX_NS, None)
        if self.options.fontsize is None and fontsize is not None:
            self.options.fontsize = round(float(fontsize))

        newline = render_layer.attrib.get('{%s}newline' % RENDLTX_NS, None)
        if self.options.newline is None and newline is not None:
            self.options.newline = newline in ('True', 'true')

        math = render_layer.attrib.get('{%s}math' % RENDLTX_NS, None)
        if self.options.math is None and math is not None:
            self.options.math = math in ('True', 'true')

    def store_parameters(self, render_layer):
        if render_layer is None:
            return

        if self.options.preamble is not None:
            render_layer.attrib['{%s}preamble' % RENDLTX_NS] = self.options.preamble

        if self.options.scale is not None:
            render_layer.attrib['{%s}scale' % RENDLTX_NS] = str(self.options.scale)

        if self.options.depth is not None:
            render_layer.attrib['{%s}depth' % RENDLTX_NS] = str(self.options.depth)

        if self.options.fontsize is not None:
            render_layer.attrib['{%s}fontsize' % RENDLTX_NS] = str(self.options.fontsize)

        if self.options.newline is not None:
            render_layer.attrib['{%s}newline' % RENDLTX_NS] = str(self.options.newline)

        if self.options.math is not None:
            render_layer.attrib['{%s}math' % RENDLTX_NS] = str(self.options.math)

    def run(self):

        lat2svg = Latex2SvgRenderer()

        # check for existing render layer or add new one
        render_layer = self.docroot.find("{%s}g[@id='ltx-render-layer']" % SVG_NS)
        if render_layer is None:
            log_debug("Creating a new render layer...")
            render_layer = etree.Element('g', nsmap=NSS)
            render_layer.attrib['{%s}label' % INKSCAPE_NS] = 'Rendered Latex'
            render_layer.attrib['{%s}groupmode' % INKSCAPE_NS] = 'layer'
            render_layer.attrib['id'] = 'ltx-render-layer'
            self.docroot.append(render_layer)
        else:
            log_debug("Using a previous render layer...")

        if self.options.newline is True:
            #line_ending = '\\newline\n'
            line_ending = '\\\\\n'
        else:
            line_ending = '\n'

        for txt in self.docroot.findall('.//{%s}text' % SVG_NS):
            if self.options.depth > 0 and txt.xpath('count(ancestor::*)') > self.options.depth + 1:
                    continue

            log_debug("ID: " + txt.attrib.get('id', None))

            latex_string = ""
            txt_empty = True
            if txt.text:
                latex_string += txt.text + line_ending
                txt_empty = False
            tspans = txt.findall('{%s}tspan' % SVG_NS)
            for ts in tspans:
                if ts.text:
                    latex_string += ts.text + line_ending
                    txt_empty = False
                else:
                    latex_string += line_ending
            if txt_empty:
                log_debug("Empty text element, skipping...")
                continue
            if self.options.math and latex_string[0] is not '$':
                latex_string = '$' + latex_string + '$'
            log_debug(latex_string)
            rendergroup = lat2svg.render(latex_string, self.options.preamble, self.options.fontsize, self.options.scale)
            rendergroup = self.align_placement(rendergroup, txt)
            # rendergroup = self.apply_style(rendergroup, txt)
            self.add_id_prefix(rendergroup, 'lx-' + txt.attrib['id'])
            self.insert_node(rendergroup, render_layer, 'lx-' + txt.attrib['id'])

        self.store_parameters(render_layer)
        return self.docroot


######################
#  Render some latex code and return it as a SVG XML group node
class Latex2SvgRenderer:

    def _exec_command(self, cmd, ok_return_value=0):
        """
        Run given command, check return value, and return
        concatenated stdout and stderr.
        :param cmd: Command to execute
        :param ok_return_value: The expected return value after successful completion
        """

        try:
            # hides the command window for cli tools that are run (in Windows)
            info = None
            if PLATFORM == WINDOWS:
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = subprocess.SW_HIDE

            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 startupinfo=info)
            out, err = p.communicate()
        except OSError as err:
            log_error("\nCommand \"%s\" > failed: %s" % (' '.join(cmd), err))
            raise RuntimeError()

        if ok_return_value is not None and p.returncode != ok_return_value:
            log_error("\nCommand \"%s\" failed (code %d): \n\n %s" % (' '.join(cmd), p.returncode, out + err))
            raise RuntimeError()
        return out + err

    # render given latex code and return the result as an SVG group element
    def render(self, latex_code, preamble_file=None, fontsize=10, scale=1):

        # Options pass to LaTeX-related commands
        latexOpts = ['-interaction=nonstopmode',
                     '-halt-on-error']

        preamble = ""
        if preamble_file:
            log_debug("Loading preamble from " + preamble_file)
            with open(preamble_file, 'r') as preamble_file:
                preamble = preamble_file.read()

        if fontsize in [10, 11, 12]:
            doc_class = "article"
        else:
            doc_class = "scrartcl"

        texwrapper = \
r"""\documentclass[%dpt]{%s}
\usepackage[a0paper]{geometry}
\newlength\tindent
\setlength{\tindent}{\parindent}
\setlength{\parindent}{0pt}
\renewcommand{\indent}{\hspace*{\tindent}}
%s
\pagestyle{empty}
\AtBeginDocument{\pdfliteral { %s 0 0 %s 0 0 cm }}
\begin{document}
    %s
\end{document}""" \
        % (fontsize, doc_class, preamble, scale, scale, latex_code)

        # Convert TeX to PDF

        tmp_path = tempfile.mkdtemp()
        texfile_path = os.path.join(tmp_path, 'tmp.tex')
        # Write tex
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        f_tex = open(texfile_path, 'w')
        try:
            f_tex.write(texwrapper)
        finally:
            f_tex.close()

        # Exec pdflatex: tex -> pdf
        if PLATFORM == MAC:
            LATEX_PATH = '/Library/TeX/texbin'
        else:
            LATEX_PATH = ''

        cmdlog = ""
        try:
            cmd = [os.path.join(LATEX_PATH, 'pdflatex'), texfile_path] + latexOpts
            cmdlog = self._exec_command(cmd)
        except RuntimeError as error:
            # TODO: cleanup excpetion handling and excception chains
            log_error(cmdlog)
            raise RuntimeError()

        if not os.path.exists(os.path.join(tmp_path, 'tmp.pdf')):
            log_error("pdflatex didn't produce output ", os.path.join(tmp_path, 'tmp.pdf'))
            # TODO: cleanup excpetion handling and excception chains
            raise RuntimeError()

        # Convert PDF to SVG
        if PLATFORM == WINDOWS:
            PDF2SVG_PATH = os.path.join(os.path.realpath(EXT_PATH), 'pdf2svg')
        else:
            PDF2SVG_PATH = ''
        self._exec_command([os.path.join(PDF2SVG_PATH, 'pdf2svg'), os.path.join(tmp_path, 'tmp.pdf'), os.path.join(tmp_path, 'tmp.svg'), '1'])

        tree = etree.parse(os.path.join(tmp_path, 'tmp.svg'))
        root = tree.getroot()

        rendergroup = etree.Element('g')
        for e in root.getchildren():
            rendergroup.append(e)

        os.chdir(old_cwd)
        shutil.rmtree(tmp_path)  # delete temp directory
        return rendergroup


######################
# Init for standalone or Inkscape extension run mode

# commandline options shared by standalone application and inkscape extension
def add_options(parser):
    parser.add_option("-o", "--outfile", dest="outfile",
                      help="write to output file or directory", metavar="FILE")
    parser.add_option("-p", "--preamble", dest="preamble",
                      help="latex preamble file", metavar="FILE")
    parser.add_option("-f", "--fontsize", dest="fontsize", type="int",
                      help="latex base font size")
    parser.add_option("-s", "--scale", dest="scale", type="float",
                      help="apply additional scaling")
    parser.add_option("-d", "--depth", dest="depth", type="int",
                      help="maximum search depth for grouped text elements")
    parser.add_option("-n", "--newline", dest="newline",
                      action="store_true",
                      help="insert \\\\ at every line break")
    parser.add_option("-m", "--math", dest="math",
                      action="store_true",
                      help="encapsulate all text in math mode")
    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean",
                      help="remove all renderings")


if STANDALONE is False:
    # Create an Inkscape extension
    class RenderLatexEffect(inkex.Effect):
        def __init__(self):
            inkex.Effect.__init__(self)
            add_options(self.OptionParser)
            self.OptionParser.set_conflict_handler("resolve")
            self.OptionParser.add_option("-l", "--log", type='inkbool',
                                         action="store", dest="debug", default=False,
                                         help="show log messages in inkscape")
            self.OptionParser.add_option("-n", "--newline", dest="newline",
                                         action="store", type='inkbool',
                                         help="insert \newline at every line break")
            self.OptionParser.add_option("-m", "--math", type='inkbool',
                                         action="store", dest="math",
                                         help="encapsulate all text in math mode")

        def effect(self):
            if self.options.debug is True:
                set_log_level(log_level_debug)
            svgprocessor = SvgProcessor(self.document, self.options)
            svgprocessor.run()
else:
    # Create a standalone commandline application
    def main_standalone():
        # parse commandline arguments
        from optparse import OptionParser
        parser = OptionParser(usage="usage: %prog [options] SVGfile(s)")
        add_options(parser)
        parser.add_option("-v", "--verbose", default=False,
                          action="store_true", dest="verbose")
        (options, args) = parser.parse_args()

        if options.verbose is True:
            set_log_level(log_level_debug)

        # expand wildcards
        args = [glob.glob(arg) if '*' in arg else arg for arg in args]

        if len(args) < 1:
            log_error('No input file specified! Call with -h argument for usage instructions.')
            sys.exit(1)
        elif len(args) > 2 and options.outfile and not os.path.isdir(options.outfile):
            log_error('If more than one input file is specified -o/--outfile has to point to a directory.')
            sys.exit(1)

        # main loop, run the SVG processor for each input file
        for infile in args:
            if options.outfile:
                if os.path.isdir(options.outfile):
                    outfile = os.path.join(options.outfile, os.path.basename(infile))
                else:
                    outfile = options.outfile
            else:
                outfile = infile

            log_info("Rendering " + infile + " -> " + outfile)

            svgprocessor = SvgProcessor(infile, options)

            try:
                result = svgprocessor.run()
            except RuntimeError:
                log_error("ERROR while rendering " + infile)
                sys.exit(1)

            # write processed XML to a file
            xmlstr = etree.tostring(result, pretty_print=True, xml_declaration=True)
            f = open(outfile, 'w')
            f.write(xmlstr.decode('utf-8'))
            f.close()


if __name__ == "__main__":
    if STANDALONE is False:
        # run the extension
        effect = RenderLatexEffect()
        effect.affect()
    else:
        main_standalone()
