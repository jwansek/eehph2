import shutil
import os

try:
    shutil.rmtree(os.path.join(os.environ["ALLUSERSPROFILE"], "EEHPH2"))
except:
    pass