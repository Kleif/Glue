
Much like Github's [Jekyll][], Glue is a [Python][] script that generates websites
based on templates, a content folder and a configuration file. However, Glue makes
some interesting and different design decissions and it's much simpler. 

In particular, Glue categorizes everything **by file extension** and is **not** blog-aware.

Each extension represents a collection of items, which may be posts, sidebar widgets,
part of documentation for a project or whatever you want, and makes them all available
at compile time. This makes it easier to create any kind of website, be it or not a blog.

[Jekyll]: http://github.com/mojombo/jekyll
[Python]: http://www.python.org

# Installation

Glue has no 'setup.py' file and needs no installation. It's a tiny, single-file
10kb program. To use it, just place 'glue.py' somewhere in your $PATH.

It also has no command-line arguments. To execute, 'cd' to the directory where
your website is located and invoke it:

    $ ls
    content/ templates/ www/ setup.yaml

    $ glue.py
    note: not sorting section 'code' (no date specified)
    Done: 14 generated files and 20 static files.
    Time: 0.54849728 seconds.

# Dependencies

Glue has few dependencies. It's a trade-off. There is no support for Textile, Asciidoc
or many other filters. This is by design. One library for each task and that's it.

Required:

  * [Jinja2][] as the template system.
  * [Yaml][] for headers and the configuration file.
  * [Markdown][] which is used to write the content.

Optional:

  * [Pygments][] is needed to have syntax highlighting.

It works both on Python 2.6+ and Python 3, although you will need to run it through
'2to3.py' for it to work on the later. All the libraries also run on Python 3.

[Jinja2]:   http://pypi.python.org/pypi/Jinja2
[Markdown]: http://pypi.python.org/pypi/Markdown
[Pygments]: http://pypi.python.org/pypi/Pygments
[Yaml]:     http://pypi.python.org/pypi/PyYAML

# Documentation

Additional documentation will be written and linked here soon with detailed usage
instructions and differences with Jekyll as well as example sites. (a blog, gallery, etc)

