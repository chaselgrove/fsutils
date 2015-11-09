# See file COPYING distributed with fsutils for copyright and license.

"""log file parsing"""

import os
import datetime
import dateutil.parser

now = datetime.datetime.now(dateutil.tz.tzlocal())

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

    def __init__(self, spec, print_dash_flag, subjects_dir=None):
        self.subjects_dir = subjects_dir
        self.spec = spec
        self.print_dash_flag = print_dash_flag
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
                    run = Run(self, len(self.runs), fo, self.print_dash_flag)
                except NoRunError:
                    break
                except Exception:
                    import traceback
                    traceback.print_exc()
                    raise LogError('error parsing log file')
                else:
                    self.runs.append(run)
        if not self.runs:
            raise SubjectError('no runs found')
        for run in self.runs:
            run.order_vars['NR'] = len(self.runs)
            run.print_vars['NR'] = len(self.runs)
        return

class Run:

    def __init__(self, subject, run_number, fo, print_dash_flag):
        self.subject = subject
        self.run_number = run_number
        self.t_end = None
        self.steps = []
        end_state = self.read_log(fo)
        if end_state == 'start':
            raise NoRunError()
        self.print_vars = {}
        self.order_vars = {}
        self.print_vars['BUILD'] = self.build_stamp
        self.order_vars['BUILD'] = self.build_stamp
        self.print_vars['UNAME'] = self.uname
        self.order_vars['UNAME'] = self.uname
        self.print_vars['ARGS'] = self.args
        self.order_vars['ARGS'] = self.args
        # NR is set by the subject object
        # RN is printed as one-based while run_number is zero-based
        self.order_vars['RN'] = self.run_number
        self.print_vars['RN'] = self.run_number+1
        self.order_vars['TSTART'] = self.t_start
        self.print_vars['TSTART'] = format_time(self.t_start)
        if not self.t_end:
            self.order_vars['TFINISH'] = None
            if print_dash_flag:
                self.print_vars['TFINISH'] = '-          -'
            else:
                self.print_vars['TFINISH'] = ''
            self.order_vars['TRUN'] = now-self.t_start
            self.print_vars['TRUN'] = format_delta(now-self.t_start)
            self.order_vars['R'] = True
            self.print_vars['R'] = 'R'
            self.order_vars['E'] = None
            if print_dash_flag:
                self.print_vars['E'] = '-'
            else:
                self.print_vars['E'] = ''
            if self.steps:
                self.order_vars['SN'] = len(self.steps)
                self.print_vars['SN'] = str(len(self.steps))
                self.order_vars['STEPNAME'] = self.steps[-1]['name']
                self.print_vars['STEPNAME'] = self.steps[-1]['name']
                tstart = self.steps[-1]['tstart']
                self.order_vars['STEPTSTART'] = tstart
                self.print_vars['STEPTSTART'] = format_time(tstart)
                self.order_vars['STEPTRUN'] = now-tstart
                self.print_vars['STEPTRUN'] = format_delta(now-tstart)
            else:
                self.order_vars['SN'] = None
                self.order_vars['STEPNAME'] = None
                self.order_vars['STEPTSTART'] = None
                self.order_vars['STEPTRUN'] = None
                if print_dash_flag:
                    self.print_vars['SN'] = '-'
                    self.print_vars['STEPNAME'] = '-'
                    self.print_vars['STEPTSTART'] = '-'
                    self.print_vars['STEPTRUN'] = '-'
                else:
                    self.print_vars['SN'] = ''
                    self.print_vars['STEPNAME'] = ''
                    self.print_vars['STEPTSTART'] = ''
                    self.print_vars['STEPTRUN'] = ''
        else:
            self.order_vars['TFINISH'] = self.t_end
            self.print_vars['TFINISH'] = format_time(self.t_end)
            self.order_vars['TRUN'] = self.t_end-self.t_start
            self.print_vars['TRUN'] = format_delta(self.t_end-self.t_start)
            self.order_vars['R'] = False
            if print_dash_flag:
                self.print_vars['R'] = '-'
            else:
                self.print_vars['R'] = ''
            if self.error:
                self.order_vars['E'] = True
                self.print_vars['E'] = 'E'
            else:
                self.order_vars['E'] = False
                if print_dash_flag:
                    self.print_vars['E'] = '-'
                else:
                    self.print_vars['E'] = ''
            self.order_vars['SN'] = None
            self.order_vars['STEPNAME'] = None
            self.order_vars['STEPTSTART'] = None
            self.order_vars['STEPTRUN'] = None
            if print_dash_flag:
                self.print_vars['SN'] = '-'
                self.print_vars['STEPNAME'] = '-'
                self.print_vars['STEPTSTART'] = '-'
                self.print_vars['STEPTRUN'] = '-'
            else:
                self.print_vars['SN'] = ''
                self.print_vars['STEPNAME'] = ''
                self.print_vars['STEPTSTART'] = ''
                self.print_vars['STEPTRUN'] = ''
        self.order_vars['SPEC'] = self.subject.spec
        self.print_vars['SPEC'] = self.subject.spec
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

def format_time(t):
    return t.strftime('%Y-%m-%d %H:%M:%S')

def format_delta(d):
    s = d.seconds % 60
    minutes = d.seconds / 60
    m = minutes % 60
    hours = minutes / 60
    h = 24 * d.days + hours
    return '%02d:%02d:%02d' % (h, m, s)

# eof
