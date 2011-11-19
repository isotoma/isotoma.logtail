from distutils.core import setup

setup(name="isotoma.logtail",
      version="1.0",
      description="Log tailer",
      author="Doug Winter",
      author_email="doug.winter@isotoma.com",
      packages=["isotoma", "isotoma.logtail"],
      entry_points = {
        "console_scripts": [
            "logtail=isotoma.logtail.scripts.logtail:run",
        ]},
      install_requires = [
        'nevow',
        'yay',
      ]
     )

