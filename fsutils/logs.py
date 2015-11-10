# See file COPYING distributed with fsutils for copyright and license.

"""log file parsing"""

import os
import datetime
import dateutil.parser

class LogError(Exception):

    """base class for exceptions"""

    def __init__(self, msg):
        self.msg = msg
        return

    def __str__(self):
        return self.msg

class SubjectError(LogError):

    """error reading subject status"""

class NoRunError(LogError):

    """no run found"""

    def __init__(self):
        return

    def __str__(self):
        return 'no run found'

class LogError(LogError):

    """error in recon-all.log"""

class Subject:

    def __init__(self, spec, subjects_dir=None):
        self.subjects_dir = subjects_dir
        self.spec = spec
        if not self.subjects_dir or '/' in spec:
            self._init_from_path(self.spec)
        else:
            log = os.path.join(self.subjects_dir, 
                               spec, 
                               'scripts', 
                               'recon-all.log')
            self._init_from_path(log)
        return

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.runs[key]
        raise KeyError(key)

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        for run in self.runs:
            yield run
        return

    def _init_from_path(self, path):
        if os.path.isdir(path):
            log = os.path.join(path, 'scripts', 'recon-all.log')
            self._init_from_path(log)
            return
        self._read_log(path)
        return

    def _read_log(self, path):
        if not os.path.exists(path):
            raise SubjectError('%s does not exist' % path)
        self.runs = []
        with open(path) as fo:
            while True:
                try:
                    run = Run(self, len(self.runs)+1, fo)
                except NoRunError:
                    break
                except Exception:
                    raise LogError('error parsing log file')
                else:
                    self.runs.append(run)
        if not self.runs:
            raise SubjectError('no runs found')
        return

class Run:

    def __init__(self, subject, run_number, fo):
        self.subject = subject
        self.run_number = run_number
        self.t_end = None
        self.steps = []
        self.error = False
        end_state = self.read_log(fo)
        if end_state == 'start':
            raise NoRunError()
        return

    def read_log(self, fo):
        """read a recon-all.log

        states are:

            start
            header block
            post-header
            memory block
            post-memory
            verions block
            step
            end

        lines in the header block:

            date
            pwd
            $0
            args
            subjid
            SUBJECTS_DIR
            FREESURFER_HOME
            actual FREESURFER_HOME
            build stamp
            uname -a
        """
        state = 'start'
        headers = []
        for line in fo:
            line = line.strip()
            if line.startswith('To report a problem, see'):
                # this appears sometimes after a run (after we are done with 
                # this processing), so it will show up at the start of our 
                # processing of the next run
                continue
            if line.startswith('New invocation'):
                # appears between runs; ignore
                continue
            if line == r'\n\n':
                # sometimes appears between runs; ignore
                continue
            if state == 'start':
                if line:
                    state = 'header block'
                    headers.append(line)
                continue
            if state == 'header block':
                if line:
                    headers.append(line)
                else:
                    state = 'post-header'
                    self.t_start = dateutil.parser.parse(headers[0])
                    self.pwd = headers[1]
                    self.script_name = headers[2]
                    self.args = headers[3]
                    self.subjid = headers[4]
                    self.subjects_dir = headers[5]
                    self.freesurfer_home = headers[6]
                    self.actual_freesurfer_home = headers[7]
                    self.build_stamp = headers[8]
                    if self.build_stamp.startswith('build-stamp.txt: '):
                        self.build_stamp = self.build_stamp[17:]
                    self.uname = headers[9]
                continue
            if state == 'post-header':
                if line:
                    state = 'memory block'
                continue
            if state == 'memory block':
                if not line:
                    state = 'post-memory'
                continue
            if state == 'post-memory':
                if line:
                    state = 'versions block'
                continue
            if line.startswith('#@# '):
                if line.endswith(' --------------'):
                    if self.steps[-1]['name'].startswith('Qdec Cache'):
                        # this is a status line from mris_preproc, so we 
                        # skip it here
                        continue
                step = line[4:-28].strip()
                t = dateutil.parser.parse(line[-28:])
                self.steps.append({'name': step, 'tstart': t})
                state = 'step'
                continue
            # state == 'step'
            if 'exited with ERRORS' in line:
                self.error = True
                self.t_end = dateutil.parser.parse(line[-28:])
                state = 'end'
                break
            if 'finished without error' in line:
                self.error = False
                self.t_end = dateutil.parser.parse(line[-28:])
                state = 'end'
                break
        return state

    @property
    def is_running(self):
        if self.t_end:
            return False
        return True

    @property
    def t_run(self):
        if self.is_running:
            return now() - self.t_start
        return self.t_end - self.t_start

    @property
    def step_number(self):
        if not self.is_running or not self.steps:
            return None
        return len(self.steps)

    @property
    def step_name(self):
        if not self.is_running or not self.steps:
            return None
        return self.steps[-1]['name']

    @property
    def step_t_start(self):
        if not self.is_running or not self.steps:
            return None
        return self.steps[-1]['tstart']

    @property
    def step_t_run(self):
        if not self.is_running or not self.steps:
            return None
        return now() - self.step_t_start

def now():
    return datetime.datetime.now(dateutil.tz.tzlocal())

# eof
