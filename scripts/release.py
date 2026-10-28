"""Detached RSA-PSS approval. Trust is provisioned outside authoring projects."""
import base64
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from scripts.text_contract import strict_loads
from scripts.build_fast_project import digest

VERSION = 1


def approval_payload(root, report, reviewer):
    root=Path(root)
    return dict(version=VERSION,status='approved',reviewerId=reviewer,
        manifestSha256=digest(root/'vibe.project.json'),planSha256=digest(root/'quality-plan.json'),
        reviewSha256=digest(root/'quality-review.json'),inputFingerprint=report['inputFingerprint'],
        evidenceDigest=report['evidenceDigest'],profile=strict_loads((root/'quality-plan.json').read_text(encoding='utf-8'))['profile'])


def sign_approval(root, report, private_key_pem, reviewer):
    """Called only by a separately authorized reviewer; never generates a trusted key."""
    from scripts.quality_gate import input_fingerprint,validate_review
    if report.get('status')!='needs_review' or report.get('errors') or input_fingerprint(root)!=report.get('inputFingerprint') or validate_review(root,report):
        raise ValueError('Reviewer must approve the unchanged automatically checked and observed inputs')
    if strict_loads((Path(root)/'quality-review.json').read_text(encoding='utf-8'))['reviewer']!=reviewer:
        raise ValueError('Signing identity differs from the recorded reviewer')
    from cryptography.hazmat.primitives import serialization,hashes
    from cryptography.hazmat.primitives.asymmetric import padding,rsa
    key=serialization.load_pem_private_key(private_key_pem,password=None)
    if not isinstance(key,rsa.RSAPrivateKey) or key.key_size<3072:
        raise ValueError('Reviewer needs RSA >=3072 bits')
    public=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    payload=json.dumps(approval_payload(root,report,reviewer),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    signature=key.sign(payload,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),hashes.SHA256())
    if input_fingerprint(root)!=report['inputFingerprint']:
        raise ValueError('Inputs changed while signing')
    return dict(version=VERSION,keyId=hashlib.sha256(public).hexdigest(),
        payload=base64.b64encode(payload).decode(),signature=base64.b64encode(signature).decode())


def verify_approval(root, report, trust_store=None):
    from cryptography.hazmat.primitives import serialization,hashes
    from cryptography.hazmat.primitives.asymmetric import padding,rsa
    root=Path(root)
    configured=trust_store or os.environ.get('VIBE_TRUST_STORE')
    if not configured:
        raise ValueError('External reviewer trust store is not configured; self-reported passed is not release approval')
    trust_path=Path(configured).resolve()
    if trust_path.is_relative_to(root.resolve()):
        raise ValueError('Trust store must be managed outside the project')
    trust=strict_loads(trust_path.read_text(encoding='utf-8-sig'))
    envelope=strict_loads((root/'release.attestation.json').read_text(encoding='utf-8-sig'))
    if set(envelope)!={'version','keyId','payload','signature'} or envelope['version']!=VERSION or trust.get('version')!=VERSION:
        raise ValueError('Unsupported approval envelope')
    authority=trust['keys'][envelope['keyId']]
    key=serialization.load_pem_public_key(authority['publicKeyPem'].encode())
    if not isinstance(key,rsa.RSAPublicKey) or key.key_size<3072:
        raise ValueError('Invalid reviewer public key')
    der=key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    if hashlib.sha256(der).hexdigest()!=envelope['keyId']:
        raise ValueError('Reviewer key identity mismatch')
    payload=base64.b64decode(envelope['payload'],validate=True)
    key.verify(base64.b64decode(envelope['signature'],validate=True),payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),hashes.SHA256())
    actual=strict_loads(payload.decode('utf-8'))
    if actual!=approval_payload(root,report,authority['reviewerId']):
        raise ValueError('Approval is stale or does not match assets, policy, review and evidence')
    plan=strict_loads((root/'quality-plan.json').read_text(encoding='utf-8'))
    review=strict_loads((root/'quality-review.json').read_text(encoding='utf-8'))
    if plan['authorId']==authority['reviewerId'] or review['reviewer']!=authority['reviewerId']:
        raise ValueError('Author and trusted reviewer must differ and reviewer identity must match')
    return actual


def publish(root, report, target):
    """Fresh version directory, atomic promotion; failed/partial packages never appear as releases."""
    from scripts.quality_gate import input_fingerprint
    root,target=Path(root).resolve(),Path(target).resolve()
    if report.get('status')!='release_passed' or input_fingerprint(root)!=report['inputFingerprint']:
        raise ValueError('Only the unchanged approved project may be published')
    if target.exists() or target.is_relative_to(root):
        raise ValueError('Release target must be a new directory outside the source project')
    target.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.release-',dir=target.parent))
    try:
        manifest=strict_loads((root/'vibe.project.json').read_text(encoding='utf-8'))
        for name in set(manifest['assetHashes'])|{'vibe.project.json','quality-plan.json','quality-review.json','release.attestation.json'}:
            destination=staging/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,destination)
        evidence=Path(report['evidenceRoot'])
        shutil.copytree(evidence,staging/'quality-evidence')
        (staging/'quality-evidence/index.json').write_text(json.dumps(report['screenshots'],ensure_ascii=False,sort_keys=True,separators=(',',':')),encoding='utf-8')
        (staging/'quality-evidence/report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        if input_fingerprint(root)!=report['inputFingerprint']:
            raise ValueError('Source changed during publishing')
        for name, expected in manifest['assetHashes'].items():
            if digest(staging/name)!=expected:
                raise ValueError('Asset changed while copying the release: '+name)
        for item in report['screenshots']:
            if digest(staging/'quality-evidence'/item['file'])!=item['sha256']:
                raise ValueError('Screenshot changed while publishing: '+item['file'])
        verify_approval(staging,report)
        staging.rename(target)
    except BaseException:
        if staging.resolve().parent!=target.parent or not staging.name.startswith('.release-'):
            raise RuntimeError('Refusing to clean an unexpected release staging path')
        shutil.rmtree(staging)
        raise
    return target
