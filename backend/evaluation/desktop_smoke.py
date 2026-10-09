"""Opt-in real macOS dispatch of temporary synthetic files; no Windows claim."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from app.desktop import act
from app.security import ApiError

def main():
    if sys.platform != 'darwin':
        raise SystemExit('This smoke test is macOS only; Windows remains untested.')
    import fcntl
    report={}
    with tempfile.TemporaryDirectory(prefix='sift-desktop-') as temp:
        base=Path(temp).resolve();root=base/'Root ü with spaces';root.mkdir()
        files=[]
        for sub in ['one','two']:
            (root/sub).mkdir();path=root/sub/'same ü $(literal).txt'
            path.write_text('Sift synthetic desktop smoke document: '+sub);files.append(path)
        before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
        for i,path in enumerate(files):
            for reveal in [False,True]:
                act(path,reveal,root=root);report[f'{i}:{"reveal" if reveal else "open"}']='OS dispatch succeeded'
        def rejected(label,path,active_root):
            try: act(path,root=active_root)
            except ApiError as exc: report[label]=exc.code
            else: raise AssertionError(label+' was accepted')
        with files[0].open('rb') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            rejected('exclusive_advisory_lock',files[0],root)
        files[0].chmod(0)
        try: rejected('unreadable_file',files[0],root)
        finally: files[0].chmod(0o600)
        report['source_hashes_unchanged']=before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
        rejected('unsupported_type',root/'file.exe',root)
        files[0].unlink();rejected('missing_file',files[0],root)
        outside=base/'outside.txt';outside.write_text('Synthetic outside document')
        files[0].symlink_to(outside);rejected('symlink_escape',files[0],root)
        moved=base/'moved';root.rename(moved);root.symlink_to(moved,target_is_directory=True)
        rejected('replaced_root',files[1],root)
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
