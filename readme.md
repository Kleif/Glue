
Much like Github's [Jekyll][], Glue is a [Python][] (2.6+ and 3) script that generates
websites based on templates, a content folder and a configuration file.  
However, Glue makes some interesting and different design decissions and it's much simpler. 

In particular, Glue categorizes everything **by file extension** and is **not** blog-aware.

Each extension represents a collection of items, which may be posts, sidebar widgets,
part of documentation for a project or whatever you want, and makes them all available
at compile time. This makes it easier to create any kind of website, be it or not a blog.

Unicode works, templates are written using [Jinja2][] which supports inheritance and macros,
entries (written in Markdown with extensions) can embed code themselves and [Pygments][] will
be used if available for syntax highlighting.

[Jekyll]:   http://github.com/mojombo/jekyll
[Python]:   http://www.python.org
[Jinja2]:   http://jinja.pocoo.org/docs/
[Pygments]: http://pygments.org

