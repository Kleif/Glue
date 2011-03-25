
Much like Github's [Jekyll][], Glue is a [Python][] script that generates websites  
based on templates, a content folder and a configuration file. However, Glue makes  
some interesting and different design decissions and it's much simpler. 

[Jekyll]: http://github.com/mojombo/jekyll
[Python]: http://www.python.org

Installation
------------

Glue has no 'setup.py' file and needs no installation. It's a tiny, single-file  
10kb program. To use it, just place 'glue.py' somewhere in your $PATH.

It also has no command-line arguments. To execute, 'cd' to the directory where  
your website is located and invoke it:

    $ ls
    content/ templates/ www/ setup.yaml

    $ glue.py
    Done: 4 generated files and 6 static files.
    Time: 0.0955 seconds.

If anything goes wrong, it will stop as soon as possible with a detailed  
message, hopefully before anything gets generated. It's no fun to overwrite  
your current website with a half-baked new one because there were errors so  
Glue won't write to disk until the very last moment.

Dependencies
------------

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

Differences with Jekyll
-----------------------

The first obvious difference is that Glue is written in Python. This isn't a big deal  
unless you are on a Windows system where installing Ruby gems can be a chore.

Jekyll works on a number of [special][] folders as a transformation engine. It takes  
some files, churns them through a [Liquid][] template and/or some filters like markdown  
and spits out pure HTML ready to be deployed to your web host.

[Liquid]: http://www.liquidmarkup.org/
[special]: http://github.com/mojombo/jekyll/wiki/Usage

Here is how a Jekyll site structure looks (left), compared to Glue (right):

    site/                              site/
       _layouts/                          templates/
          base.html                          base.html
          post.html                          post.html
       _posts/                            content/
          2010-02-11-title 1.markdown        posts/
          2010-03-11-title 2.markdown           title 1.post 
       _site/                                   title 2.post
       config.yml                            index.html
       index.html                         www/
                                          setup.yaml

They are very similar, but there is a main difference:

Jekyll categorizes all the files inside the \_posts/ subfolder that have  
a [YAML header][] making them available at compile-time for Liquid to use.  
Thus, in your posts you can use a variable that denotes them: 'post.\*' and in  
general templates you can access: 'site.posts.\*'

Instead, Glue categorizes files **by extension** and has no builtin notion of posts.

Each extension represents a collection of items, which may be posts, sidebar widgets,  
part of documentation for a project or whatever you want, and makes them all available  
as 'item.\*' in individual items and 'content.extension.\*' in templates.

[YAML header]: http://github.com/mojombo/jekyll/wiki/yaml-front-matter

The configuration file
----------------------

The bundled setup.yaml file contains:

/setup.yaml:

    date_input:  "%d/%m/%Y"
    date_output: "%A, %d. %B %Y"
    markdown_extensions: ['codehilite', 'extra']

Those three fields are required. 'date\_input' is the format you want to use  
to write dates in your items and 'date\_output' a convenience format that is  
generated and added to each entry (as 'item.date\_str') when rendering the website.

Syntax highlighting is enabled as well as other extensions. An overview of the  
extensions that are supported is in the [Python Markdown][] homepage.  
Those include tables, footnotes and even image galleries with thumbnails.

More definitions may be added to the file and they will be available at  
rendering time. For example:

    email: "my_email@mydomain.com"
    title: "Yet another blog on the earth"

During template generation, those are accessed as: 'setup.email' and 'setup.title'.  
If you aren't in the mood of customizing it, the defaults are fine.

[Python Markdown]: http://www.freewisdom.org/projects/python-markdown/Available_Extensions

Writing templates
-----------------

To be able to render items we need templates. In Glue, templates are written  
using the [Jinja2][] template system, which supports inheritance, macros,  
filters and a bunch of other niceties.

A minimal base template could look like this:

/templates/base.html:

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

      <head>
        <title> {{ setup.title }} </title>
      </head>

      <body>
        {% block content %} {% endblock %}
      </body>

    </html>

The important part is the content block. We can override it in each page to  
change what it's rendered in the final website. If we were to write a blog,  
a post template that defines how each entry looks may be defined as:

/templates/post.html:

    {% extends "base.html" %}
    {% block content %}

      <h2> {{ item.title }} </h2> written at: {{ item.date_str }}

      {{ item.content }}

      {% if item.prev %}
        <a href="{{ item.prev.url }}"> {{ item.prev.title }} </a>
      {% endif %}

      {% if item.next %}
        <a href="{{ item.next.url }}"> {{ item.next.title }} </a>
      {% endif %}

    {% endblock %}

When Glue categorizes all the files inside '/content/' it makes them available  
to templates with a few properties added. Then, we use those properties  
to build the website logic.

A good reference for the syntax and capabilities of Jinja templates is [here](http://jinja.pocoo.org/templates/).

**Note:**  You can of course mix JS, CSS and anything you want inside templates.

Adding items
------------

An item may represent anything, a blog post, a menu item, a project, it doesn't matter  
as long as it has a YAML header and is located somewhere inside '/content/'.

For a blog, a post could look like this:

/content/hello world.post:

    ---
    title: Hello world!
    date: 03/25/2011
    template: post
    ---
    This is the content written in Markdown!

None of the fields is mandatory:

When 'date' is present, Glue will also add 'date\_str' and 'date\_xml' to the current item.  
The first one is useful in general while the second one is for [RSS][] or [Atom][] feeds.  
Additionally if all items in a section do declare a date, Glue will also sort them from newer to older.

[RSS]:  http://en.wikipedia.org/wiki/RSS
[Atom]: http://en.wikipedia.org/wiki/Atom_%28standard%29

When 'template' is present, Glue will render this item individually to a file using the template.  
This is usually what you want for things like blog posts. Otherwise it will still run it through  
Markdown and make it available to all the templates, but it won't be rendered.

Some remarks:

  * the template name does not include the extension.
  * the separators **must be** triple dashes.
  * the default encoding for everything is UTF-8.

Like in 'setup.yaml', you can add whatever you want in the header. If you are defining a menu  
entry or a sidebar widget, having an 'order' property is handy while for a programming project,  
maybe a 'downloadlink' is appropiate.

Item properties reference
-------------------------

Considering the previous 'hello world.post' item, Glue would yield the following  
information from the YAML front matter to 'post.html' when rendering:

    item.title:    hello world!
    item.date:     11/02/2010
    item.template: post.html

It adds some more properties automatically:

    item.id:       unique identifier (across sections too)
    item.url:      a link to this item in the web server
    item.date_str: the date processed according to the settings in 'setup.yaml'
    item.date_xml: RFC 822 compliant-date for Atom feeds
    item.prev:     the previous item (by date if 'date' was provided)
    item.next:     the next item

Finally, all templates receive the following information:

    content.*  all the items in all sections (for example: content.post.*)
    setup.*    the configuration settings

**Note:** 'item.url' is only present when the post has a template. Otherwise  
it makes no sense since it won't be rendered. Likewise, 'item.prev' and 'item.next'  
are only available when there are previous/next items in the given section.

Single pages and static files
-----------------------------

A website would be pretty bland without some CSS, images and useful things like  
an 'index.html' besides the dynamic items presented until this section.

Fortunately this is easy to solve. It all depends on how Glue dispatches the reading  
of the files that live inside '/content/'. Here is the excerpt:

  1. Files with extensions: '.html' or '.xml' are rendered as single templates.
  2. Files with a YAML header are read as items and categorized by extension.
  3. Everything else is copied verbatim, considered a static file.

Note that Glue recurses into subdirectories and recreates the same hierarchy  
in the output folder so you can layout everything as you wish.

Here is a direct comparison between a sample '/content/' folder with some items,  
pages and static files and the '/www/' folder generated after Glue has been invoked:

    content/                 www/
       css/                     css/
          pygments.css             pygments.css
          style.css                style.css
       images/                  images/
          menu1.png                menu1.png
          menu2.png                menu2.png
       posts/                   posts/
          title1.post              title1.post.html
          title2.post              title2.post.html
       index.html               index.html
       archives.html            archives.html
       rss.xml                  rss.xml

Items get the '.html' extension added to the original filename.  
Static files and single '.html' or '.xml' pages have their name untouched.

Example archives page
---------------------

I've only put an example that highlights how to access the 'item.\*' variables  
inside individual items when rendering, so here is an example single page that uses  
'content.post.\*' to render a list of all the posts in a table:

/content/archives.html:

    {% extends "base.html" %}

    {% block content %}
       <h2> Archives: </h2>

       <table>
         {% for post in content.post %}
           <tr> 
             <td> <a href="{{ post.url }}">{{ post.title }}</a> </td>        
             <td> {{ post.date }} </td>
           </tr>
         {% endfor %}
       </table>

    {% endblock %}

Note that Glue will sort all sections by their item's date in descending order  
so the archives page will be displayed from newer to older by default. Jinja [filters][]  
like 'reverse()', 'groupby()' and 'sort()' may prove useful when working with all the  
items in a given section.

[filters]: http://jinja.pocoo.org/templates/#filters

Syntax highlighting
-------------------

Make sure [Pygments][] is installed and the 'setup.yaml' file for  
your site has the following property set (This is enabled by default):

    ::bash
    markdown_extensions: ['codehilite', other extensions...]

At '/content/css' in the bundled .zip package you will notice a bunch of 'css' files.  
Those are the styles available, ready to be used in your website.  
I've taken them from [here](https://github.com/richleland/pygments-css).

Then, in a given item use it like this:

/content/sample item.post:

    Here is some complex code:

        ::Java
        // A very complex program.
        public static void main(String[] args) {
            system.out.println("Hello world");
        }

Conclusion
----------

This readme is already twice the size of 'glue.py', which scares me.  
It's often interesting how much funcionality a small program can provide.

Now it's your turn, download Glue and build something amazing with it, add disqus comments,  
rss feeds, or fork the source code and modify it to suit your needs.

Don't forget to contact me, I'm always interested to see applications of my software.

