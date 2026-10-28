"""External reviewer entry point. Key custody belongs to an independently controlled process."""
import argparse
import json
from pathlib import Path
from scripts.quality_gate import run_gate,validate_review
from scripts.release import sign_approval


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True);p.add_argument('--private-key',type=Path,required=True)
    p.add_argument('--reviewer-id',required=True)
    args=p.parse_args();root=args.project.resolve()
    if args.private_key.resolve().is_relative_to(root):
        raise SystemExit('Reviewer private keys must never be placed inside authoring projects')
    report=run_gate(root)
    if report['status']!='needs_review' or validate_review(root,report):
        raise SystemExit('Current automatic checks and actual review records must pass before signing')
    envelope=sign_approval(root,report,args.private_key.read_bytes(),args.reviewer_id)
    path=root/'release.attestation.json'
    if path.exists():raise SystemExit('Do not overwrite an approval; use a new project version or archive the old approval explicitly')
    path.write_text(json.dumps(envelope,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Detached approval written; key material was not copied into the project')


if __name__=='__main__':main()
