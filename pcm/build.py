
import os
from os import path
import shutil

src_path = path.join(path.dirname(__file__),'..','KiBuzzard')

metadata_template = path.join(path.dirname(__file__),'metadata_template.json')
resources_path = path.join(path.dirname(__file__),'resources')
#print(src_path)

build_path = path.join('build')

try:
    shutil.rmtree(build_path)
except FileNotFoundError:
    pass
os.mkdir(build_path)
os.mkdir(path.join(build_path,'plugin'))
os.chdir(build_path)

shutil.copytree(src_path, path.join('plugin','plugins'))

# clean out any __pycache__ or .pyc files (https://stackoverflow.com/a/41386937)
import pathlib
[p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]
[p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]


# copy metadata
shutil.copy(metadata_template, path.join('plugin','metadata.json'))
# copy icon
shutil.copytree(resources_path, path.join('plugin','resources'))


# zip all files
shutil.make_archive('KiBuzzard_pcm', 'zip', 'plugin')


zip_size = path.getsize('KiBuzzard_pcm.zip')

from pathlib import Path

uncompressed_size = sum(f.stat().st_size for f in Path('plugin').glob('**/*') if f.is_file())

import hashlib
with open('KiBuzzard_pcm.zip', 'rb') as f:
    zip_sha256 = hashlib.sha256(f.read()).hexdigest()

# load up json script
import json

with open(metadata_template) as f:
    md = json.load(f)
    md['versions'][0].update({
        'install_size': uncompressed_size,
        'download_size': zip_size,
        'download_sha256': zip_sha256,
        'download_url': 'https://github.com/gregdavill/KiBuzzard/releases/download/{0}/KiBuzzard-{0}-pcm.zip'.format(md['versions'][0]['version'])
    })
        
    with open('metadata.json', 'w') as of:
        json.dump(md, of, indent=2)
