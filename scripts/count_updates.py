import argparse
import subprocess
import re
import urllib.request
from pathlib import Path

multi_version_stems: dict[str, bool] = {
    'lua': True, 'python': True, 'ruby': True, 'php': True, 'perl': True,
    'postgresql': True, 'mariadb': True, 'node': True, 'tcl': True, 'tk': True,
    'llvm': True, 'autoconf': True, 'jdk': True, 'automake': True
}

class Dewey:
    deweys: list[str]
    suffix: str
    suffix_value: int

    def __init__(self, string: str) -> None:
        self.deweys = string.split('.')
        self.suffix = ''
        self.suffix_value = 0
        if self.deweys:
            last = self.deweys[-1]
            m = re.match(r'^(\d+)(rc|alpha|beta|pre|pl)(\d*)$', last)
            if m:
                self.deweys[-1] = m.group(1)
                self.suffix = m.group(2)
                self.suffix_value = int(m.group(3) or '0')

    def to_string(self) -> str:
        r = '.'.join(self.deweys)
        if self.suffix:
            r += self.suffix + (str(self.suffix_value) if self.suffix_value else '')
        return r

    def compare(self, other: 'Dewey') -> int:
        deweys1 = self.deweys
        deweys2 = other.deweys
        min_len = min(len(deweys1), len(deweys2))
        for i in range(min_len):
            r = self._dewey_part_compare(deweys1[i], deweys2[i])
            if r != 0:
                return r
        r = len(deweys1) - len(deweys2)
        if r != 0:
            return 1 if r > 0 else -1
        return self._suffix_compare(other)

    def _dewey_part_compare(self, a: str, b: str) -> int:
        if a.isdigit() and b.isdigit():
            ia = int(a)
            ib = int(b)
            return 1 if ia > ib else -1 if ia < ib else 0
        m = re.match(r'^(\d+)([a-zA-Z]?)\.(\d+)([a-zA-Z]?)$', a + '.' + b)
        if m:
            an, al, bn, bl = m.groups()
            ian = int(an)
            ibn = int(bn)
            r = 1 if ian > ibn else -1 if ian < ibn else 0
            if r != 0:
                return r
            if al and bl:
                return 1 if al > bl else -1 if al < bl else 0
            elif al:
                return 1
            elif bl:
                return -1
            else:
                return 0
        return 1 if a > b else -1 if a < b else 0

    def _suffix_compare(self, other: 'Dewey') -> int:
        a = self
        b = other
        if a.suffix == b.suffix:
            return 1 if a.suffix_value > b.suffix_value else -1 if a.suffix_value < b.suffix_value else 0
        if a.suffix == 'pl':
            return 1
        if b.suffix == 'pl':
            return -1
        if a.suffix > b.suffix:
            return -self._suffix_compare(other)
        if a.suffix == '':
            return 1
        if a.suffix == 'alpha':
            return -1
        if a.suffix == 'beta':
            return -1
        return 0

class Version:
    original_string: str
    v: int
    p: int
    dewey: Dewey

    def __init__(self, string: str) -> None:
        self.original_string = string
        self.v = 0
        m = re.match(r'(.*)v(\d+)$', string)
        if m:
            self.v = int(m.group(2))
            string = m.group(1)
        self.p = -1
        m = re.match(r'(.*)p(\d+)$', string)
        if m:
            self.p = int(m.group(2))
            string = m.group(1)
        self.dewey = Dewey(string)

    def compare(self, other: 'Version') -> int:
        if self.v != other.v:
            return 1 if self.v > other.v else -1
        if self.dewey.to_string() == other.dewey.to_string():
            return 1 if self.p > other.p else -1 if self.p < other.p else 0
        return self.dewey.compare(other.dewey)

def get_version_prefix(v: str) -> str:
    parts = v.split('.')
    numeric: list[str] = []
    for p in parts:
        m = re.match(r'^\d+', p)
        if not m:
            break
        numeric.append(m.group(0))
        if len(numeric) >= 2:
            break
    return '.'.join(numeric)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Count or list updateable packages.')
parser.add_argument('--list', action='store_true', help='List the available updates instead of counting them.')
args = parser.parse_args()

# Determine mirror
mirror: str = 'https://cdn.openbsd.org/pub/OpenBSD'
installurl_path = Path('/etc/installurl')
if installurl_path.exists():
    with installurl_path.open('r') as f:
        mirror = f.readline().strip()

# Determine if -current
is_current: bool = False
sysctl_output: str = subprocess.check_output(['sysctl', 'kern.version']).decode()
if '-current' in sysctl_output:
    is_current = True

# Determine release and arch
release: str = 'snapshots' if is_current else subprocess.check_output(['uname', '-r']).decode().strip()
arch: str = subprocess.check_output(['machine']).decode().strip()

# Construct URL
url: str = f"{mirror}/{release}/packages/{arch}/index.txt"

# Fetch index.txt
with urllib.request.urlopen(url) as response:
    index_data: str = response.read().decode()

# Load available packages
available: dict[str, str] = {}
for line in index_data.splitlines():
    fields: list[str] = line.split()
    if not fields:
        continue
    file: str = fields[-1]
    if not file.endswith('.tgz'):
        continue
    file = file[:-4]
    m = re.match(r'^(.*?)-(\d.*)$', file)
    if m:
        stem: str = m.group(1)
        rest: str = m.group(2)
        parts: list[str] = rest.split('-')
        version: str = parts[0]
        flavor: str = '-'.join(parts[1:]) if len(parts) > 1 else ''
    else:
        stem = file
        version = ''
        flavor = ''
    key: str = stem + ('-' + flavor if flavor else '')
    available[key] = file

# Get all installed packages
pkg_db: Path = Path('/var/db/pkg')
installed: list[str] = [entry.name for entry in pkg_db.iterdir() if (entry / '+CONTENTS').is_file()]

# Collect updates
updates: list[str] = []
for inst in installed:
    if inst.startswith('quirks-'):
        continue
    m = re.match(r'^(.*?)-(\d.*)$', inst)
    if m:
        stem = m.group(1)
        rest = m.group(2)
        parts = rest.split('-')
        version = parts[0]
        flavor = '-'.join(parts[1:]) if len(parts) > 1 else ''
    else:
        stem = inst
        version = ''
        flavor = ''
    key = stem + ('-' + flavor if flavor else '')
    if key not in available:
        continue
    cand: str = available[key]
    m = re.match(r'^(.*?)-(\d.*)$', cand)
    if m:
        rest_c: str = m.group(2)
        parts_c: list[str] = rest_c.split('-')
        version_c: str = parts_c[0]
    else:
        continue
    if stem in multi_version_stems:
        prefix: str = get_version_prefix(version)
        prefix_c: str = get_version_prefix(version_c)
        if prefix != prefix_c:
            continue
    v_inst: Version = Version(version)
    v_cand: Version = Version(version_c)
    if v_cand.compare(v_inst) > 0:
        updates.append(f"{inst} -> {cand}")

if args.list:
    for update in updates:
        print(update)
else:
    print(len(updates))
