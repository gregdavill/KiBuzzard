
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
paths = [
    os.path.join(dir_path, '..', 'deps'), 
    os.path.join(dir_path, '..', 'deps', 'fonttools', 'Lib'), 
    os.path.join(dir_path, '..', 'deps', 'svg2mod')
]

for path in paths:
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
