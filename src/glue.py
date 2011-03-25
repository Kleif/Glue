#!/usr/bin/env python
import codecs, datetime, os, re, sys, time

## not shipped with python:
try:
    import yaml

    from jinja2   import Environment, FileSystemLoader, Template, TemplateError
    from markdown import markdown
    from yaml     import YAMLError

except ImportError:
    exit("error: this program requires Jinja2, Markdown and Yaml.")

## some utilities:
from email.utils import formatdate
from posixpath   import sep as posixsep
from os.path     import exists, isfile, join, relpath, split
from shutil      import copyfile, rmtree
from time        import mktime, strftime, strptime

## globals:
content = {}  # all section/items.
pages   = []  # all html/xml pages.
setup   = {}  # configuration.

output  = []  # generated content.
static  = []  # static content.

## notes:
## content is structured as a dict where each key is the section name
## and the value is a list of the items in that section:
## { section1: [item1, item2, item3...], section2: ..., ...}
##
## where each item is a dict that contains all the properties:
## { title: "", date: "", ... }

## template loader:
env = Environment(loader=FileSystemLoader('templates'))

def read():
    """
    read all the website content from the current folder:
    - .html and .xml files are considered templates.
    - 'setup.yaml' is read as the configuration file.

    other files are either read as content when
    a YAML header is present or as static content.
    """
    ## read item as content.
    def maybe_read_item(filepath, sect):
        try:
            # open first as binary and check header magic:
            with open(filepath, 'rb') as fd:
                test = fd.read(3)
                if test != b'---':
                    if test != codecs.BOM_UTF8 and fd.read(3) != b'---':
                        return
  
            with codecs.open(filepath, encoding='utf-8') as fd:
                fd.read(3)
                meta, raw = re.split('^---\s*', fd.read(), flags = re.M)

                # note: YAML header may be empty, thus the {}...
                item = dict(yaml.load(meta) or {}, src = filepath, raw = raw)

                content.setdefault(sect, [])
                content[sect].append(item)

                return True

        except (IOError, ValueError, TypeError, YAMLError) as err:
            exit("error reading: %s \n '%s'" % (filepath, str(err)))

    ## same as above for html pages.
    def read_page(filepath):
        try:
            with codecs.open(filepath, encoding='utf-8') as src:
                pages.append({'src'   : src.read(),
                              'target': relpath(filepath, 'content')})

        except IOError:
            exit("error: can't read page: %s" % filepath)

    ## read the setup file:
    try:
        with codecs.open('setup.yaml', encoding='utf-8') as file:
            setup.update(yaml.load(file.read()))

        # ensure those exist:
        setup['date_input']
        setup['date_output']
        setup['markdown_extensions']

    except KeyError as err:
        exit("error: the configuration file must contain: %s" % str(err))

    except (YAMLError, IOError):
        exit("error: can't load the configuration file: setup.yaml")

    ## read all the content:
    for root, dirs, files in os.walk('content'):
        for filename in files:
            filepath = join(root, filename)

            # extension as section: (nested extensions allowed)
            sect = ''.join(filename.split('.', 1)[1:]) or '.'

            # HTML, XML?: A standalone page/template.
            if sect in ['html', 'xml']:
                read_page(filepath)
                continue

            # either content or static file:
            maybe_read_item(filepath, sect) or static.append(filepath)

def preprocess():
    """
    add useful properties to the content items:
    - 'date_str' : a readable date
    - 'date_xml' : RFC 822 date for feeds
    - 'id'       : a numeric unique identifier for the item
    - 'next'     : is the next item to the current one
    - 'prev'     : is the previous item
    - 'url'      : absolute, represents the item in the web server
    """
    date_input  = setup['date_input']
    date_output = setup['date_output']

    ## add a 'datestr' property to items in the desired format
    ## specified in the configuration file and 'datexml' for rss.
    def add_date(item):
        try:
            if 'date' in item:
                stime = strptime(item['date'], date_input)

                item['date_str'] = strftime(date_output, stime)
                item['date_xml'] = formatdate(mktime(stime))

                return True

        except ValueError as err:
            exit("error: bad date format: %s in %s" % (str(err), item['src']))

    ## add dates, url/target, sort (if date), prev/next:
    for section, items in content.iteritems():
        total    = len(items)
        has_date = True

        for i in range(total):
            item = items[i]
            item['id'] = i

            has_date = has_date and add_date(item)

            # sample target: content/posts/01.post -> www/posts/01.post.html
            # where url: /posts/01.post.html
            if 'template' in item:
                item['target'] = relpath(item['src'], 'content') + '.html'
                item['url']    = join('/', item['target']).replace(os.sep, posixsep)

        # sort this section when all the items declare a date:
        if has_date:
            items = sorted(items, key = lambda it: strptime(it['date'], date_input), reverse = True)
            content[section] = items
        else:
            print(("note: not sorting section '%s' (no date)" % section))

        # prev & next:
        for i in range(total):
            if i < total - 1: items[i]['prev'] = items[i + 1]
            if i > 0:         items[i]['next'] = items[i - 1]

def generate_items_content():
    """
    use items content as templates to render themselves.
    (this allows one to embed code inside them)
    then run the content through Markdown.
    """
    for section, items in content.iteritems():
        for item in items:
            try:
                # this.* is available at compile-time so the posts
                # can refer to themselves:
                meta = env.from_string(item['raw'])
                item['content'] = meta.render(setup = setup, this = item)

                # markdown -> html:
                item['content'] = markdown(item['content'], setup['markdown_extensions'])

            except TemplateError as err:
                exit("error: can't use template: %s for: %s" % (str(err), item['src']))

def generate_output():
    """
    generate the final html pages in the site
    that will be rendered to files.
    """
    ## items:
    for section, items in content.iteritems():
        for item in [it for it in items if 'template' in it]:
            try:
                t = env.get_template(item['template'] + '.html')
                output.append({'file' : item['target'],
                               'html' : t.render(setup = setup, item = item, content = content)})

            except TemplateError as err:
                exit("error: can't use template: %s for: %s" % (str(err), item['src']))

    ## .html/.xml pages:
    for page in pages:
        try:
            t = env.from_string(page['src'])
            output.append({'file' : page['target'],
                           'html' : t.render(setup = setup, content = content)})

        except TemplateError as err:
            exit("error: in template page: %s" % str(err))

def write():
    """
    write all html content in both items and pages
    to the output folder and copy static files.
    """
    outdir = 'www'
    try:
        ## items and pages:
        for target in output:
            filename = join(outdir, target['file'])
            filepath = split(filename)[0]

            if not exists(filepath): os.makedirs(filepath)

            with codecs.open(filename, mode = 'w', encoding = 'utf-8') as file:
                file.write(target['html'])

        ## static content:
        for target in static:
            filename = join(outdir, relpath(target, 'content'))
            filepath = split(filename)[0]

            if not exists(filepath): os.makedirs(filepath)
            copyfile(target, filename)

    except IOError as err:
        exit("error when writing: %s" % filename)

start = time.clock()
read()
preprocess()
generate_items_content()
generate_output()
write()

print  "Done: %s generated files and %s static files. " % (len(output), len(static))
print  "Time: %s seconds." % (time.clock() - start)

