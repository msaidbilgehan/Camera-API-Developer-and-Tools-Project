import sys
from os.path import expanduser

library_path = "/".join(sys.path[0].replace("\\", "/").split("/")[:-1])
sys.path.append(library_path)

import global_libs