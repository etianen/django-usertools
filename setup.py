from distutils.core import setup


setup(
    name = "django-usertools",
    version = "1.0.1",
    description = "A fire-and-forget enhancement to the Django user admin.",
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "http://github.com/etianen/django-usertools",
    download_url = "http://github.com/downloads/etianen/django-usertools/django-usertools-1.0.1.tar.gz",
    zip_safe = False,
    packages = [
        "usertools",
        "usertools.management",
        "usertools.management.commands",
        "usertools.templatetags",
        "usertools.migrations_auth",
    ],
    package_dir = {
        "": "src",
    },
    package_data = {
        "usertools": [
            "locale/*/LC_MESSAGES/django.*",
            "templates/admin/auth/user/*.html",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)