from distutils.core import setup


setup(
    name="django-usertools",
    version="1.0.16",
    description="A fire-and-forget enhancement to the Django user admin.",
    author="Dave Hall",
    author_email="dave@etianen.com",
    url="http://github.com/etianen/django-usertools",
    zip_safe=False,
    packages=[
        "usertools",
        "usertools.management",
        "usertools.management.commands",
        "usertools.templatetags",
    ],
    install_requires=[
        "django>=1.8",
    ],
    package_dir={
        "": "src",
    },
    package_data={
        "usertools": [
            "locale/*/LC_MESSAGES/django.*",
            "templates/admin/auth/user/*.html",
            "templates/admin/auth/user/*.txt",
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
