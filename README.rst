Namcap Reports
==============

namcap-reports is a automated report generator for the Arch Linux
source distribution (PKGBUILDs). It uses the output of namcap and the
power of python to churn out HTML.

**Dependencies** python>=2.5, make, bash, abs, namcap

Here's how the thing works:

* namcap is run against the entire ABS tree (would be better to make
  this run against a latest svn/cvs checkout) and a namcap.log is created.

* gen-pkglist-by-repository churns out three files: core, extra and community
  containing a list of packages in the respective repositories. On an Arch
  system, this can be easily done using pacman -Slq core >\| core etc. This
  script however works even without pacman installed.

* namcap-report.py takes the namcap.log plus these three repository listings
  and generates the output.

The maintainer-report generation is probably broken right now.

The maintainer report generation works as follows:

* First a maintainers.txt file is created in the same directory as the
  code; this is basically the output of parsing the PKGBUILDs and
  printing out the "# Maintainer: " lines along with the $pkgname.

* Then maintainer-report.py runs and generates the output, by
  default in the "maintainer/" directory.

Configuration
-------------

There's a configuration file for namcap-report now; either
/etc/namcap-reports.conf or $HOME/.namcap-reports.conf which has the
format as given in namcap-reports.conf.example::

   [namcap-reports]
   url: http://abhidg.mine.nu/arch/namcap-reports
   output_dir: /arch/namcap-reports
   template_dir: /arch/namcap-reports
   repo_files: /arch/namcap-reports

``output_dir`` is the most important one, that's where namcap-report and
maintainer-report place the generated files (maintainer-report actually
puts everything in a maintainer/ subdirectory of the ``output_dir`` directory).

``url`` is the base url for the RSS feeds and ``template_dir`` is the directory
where the index.html.tmpl and tags.html.tmpl files are stored (These are
the files which namcap-report uses to prepare the output). ``repo_files`` is
the directory where the package listings core, extra and community are
present. maintainer-report also looks for 'maintainers.txt' in the
repo_files directory.

A sample Makefile is also there. Currently a copy of ``namcap.log`` has to
present in ``output_dir``, but it is easy to fix that.

Logs
------

namcap-report and maintainer-report store the error logs in
``namcap-report-error.log`` and ``maintainer-report-error.log`` respectively.
At the start of each run, these error logs are *deleted*, so be sure to
keep a copy if you need to reference the logs at a later time. If you
give the verbose (-v) switch to them on the command line, the errors are
also printed to screen.

namcap-report generates another log: ``namcap-report-progress.log``, which
has the total number of errors and warnings over time. This can be useful
later, for example for drawing nice graphs :)

