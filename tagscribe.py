# namcap tag descriptions
# Abhishek Dasgupta <abhidg@gmail.com>

tagscribe = {}

tagscribe["missing-maintainer"] = \
"""
<p>Missing Maintainer tag</p>
<p>The <code>Maintainer:</code> tag is missing in the
PKGBUILD.</p>
"""

tagscribe["missing-contributor"] = \
"""
<p>Missing Contributor tag</p>
<p>The <code>Maintainer:</code> tag is missing in the
PKGBUILD.</p>
"""

tagscribe["variable-not-array"] = \
"""
<p>Variable is not an array.</p>
<p>Some variable in the PKGBUILD should be a bash array
but is actually declared as a string, for example: using
<code>license="GPL"</code> instead of <code>license=('GPL')</code>
"""
