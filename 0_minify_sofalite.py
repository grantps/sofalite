"""
cd /home/g/projects && uv run --with jsmin "/home/g/projects/sofalite/0_minify_sofalite.py"
"""

import jsmin

with open("/home/g/projects/sofalite/src/sofalite/output/js/sofalite.js.uncompressed.js", "r") as f:
    oldjs = f.read()
newjs = jsmin.jsmin(oldjs)
with open("/home/g/projects/sofalite/src/sofalite/output/js/sofalitedojo_minified.js", "w") as f:
    f.write(newjs)
print("Finished")
