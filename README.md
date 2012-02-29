django-usertools
================

**django-usertools** is a fire-and-forget enhancement to the Django user admin.


Features
--------

* Send invitation emails to your fellow admin users, allowing them to choose their own password on first login.
* Search through user lists using integrated [django-watson](https://github.com/etianen/django-watson) search.
* Batch admin actions for managing users and groups.


Installation
------------

1.  Checkout the latest django-usertools release and copy or symlink the `src/usertools` directory into your `PYTHONPATH`.
2.  Add `'usertools'` to your `INSTALLED_APPS` setting.


Management commands
-------------------

*   **syncgroups:** Create or maintain the set of default administrations groups. Can be safely run multiple times.


Default administration groups
-----------------------------

The syncgroups command sets up two default administration groups:

*   **Administrators:** Users with the right to edit everything.
*   **Editors:** Users with the right to edit everything except Group and User models.


Documentation
-------------

django-usertools is a simple plugin, so all required documentation can be found in this readme file.

You can keep up to date with the latest announcements by joining the
[django-usertools discussion group][].

[django-usertools discussion group]: http://groups.google.com/group/django-usertools
    "django-usertools Google Group"

    
More information
----------------

The django-usertools project was developed by Dave Hall. You can get the code
from the [django-usertools project site][].

[django-usertools project site]: http://github.com/etianen/django-usertools
    "django-usertools on GitHub"
    
Dave Hall is a freelance web developer, based in Cambridge, UK. You can usually
find him on the Internet in a number of different places:

*   [Website](http://www.etianen.com/ "Dave Hall's homepage")
*   [Twitter](http://twitter.com/etianen "Dave Hall on Twitter")
*   [Google Profile](http://www.google.com/profiles/david.etianen "Dave Hall's Google profile")