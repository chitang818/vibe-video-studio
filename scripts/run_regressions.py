"""One agent-neutral regression entry with UTF-8 logs and isolated consumer build artifacts."""
import contextlib
import json
import os
from pathlib import Path
import sys
import time
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr,'reconfigure'):sys.stderr.reconfigure(encoding='utf-8')
    os.chdir(ROOT)
    output=ROOT/'artifacts/regressions'/uuid.uuid4().hex;output.mkdir(parents=True)
    os.environ['VIBE_TEST_ARTIFACTS']=str(output/'consumer-build')
    started=time.monotonic()
    with (output/'tests.log').open('w',encoding='utf-8') as log:
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
            result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    summary=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        skipped=len(result.skipped),passed=result.wasSuccessful(),elapsedSeconds=round(time.monotonic()-started,3),python=sys.version)
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True));print('Evidence: '+str(output))
    if not result.wasSuccessful():
        print((output/'tests.log').read_text(encoding='utf-8')[-8000:].encode('ascii','backslashreplace').decode('ascii'))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':sys.exit(main())
