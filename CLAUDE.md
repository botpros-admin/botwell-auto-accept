# CLAUDE.md — Secret handling (PLEASE READ FIRST)

Hey Claude (or any agent) — quick reminder before you touch secrets in this repo.

This repo is in the **internal-infra** secret tier. All secrets are managed via SOPS + GCP KMS, following the botpros-admin org policy. Full spec: https://github.com/botpros-admin/org-policy-workflows

## Where secrets live

Encrypted under `secrets/` in this repo, wrapped with this GCP KMS key:

```
projects/botpros-secrets/locations/global/keyRings/internal-infra/cryptoKeys/sops-key
```

A `.sops.yaml` at the repo root is already configured for this tier.

## To READ a secret (local, for debugging)

```bash
# One-time: ensure you're authenticated
gcloud auth application-default login --update-adc

# Decrypt a single secret file to stdout
sops -d secrets/internal-infra/<filename>.enc.json

# Or decrypt all secrets for this tier into shell env:
set -a; eval "$(sops -d secrets/internal-infra/<filename>.enc.json | jq -r 'to_entries | .[] | "\(.key)=\(.value|tojson)"')"; set +a
```

## To ADD or EDIT a secret

```bash
# Edit existing encrypted file (opens $EDITOR, decrypts on open, re-encrypts on save)
sops secrets/internal-infra/<filename>.enc.json

# Or encrypt a new plaintext file
sops -e plain.json > secrets/internal-infra/new.enc.json
rm plain.json  # always delete the plaintext
```

Then `git add secrets/internal-infra/...` and commit. The encrypted file is safe to push.

## To CONSUME secrets in this repo's CI (GitHub Actions)

Copy this block into any job that needs decrypted secrets:

```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: actions/checkout@v4
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/1047430058155/locations/global/workloadIdentityPools/github-actions/providers/github
      service_account: sops-decrypt-internal-infra@botpros-secrets.iam.gserviceaccount.com
  - uses: getsops/sops-installer-action@v1
  - run: sops -d secrets/internal-infra/<filename>.enc.json > /tmp/decrypted.json
```

Workload Identity Federation is already bound for this repo — no SA JSON key needed.

## HARD RULES (do not violate)

- ❌ Never commit a plaintext `.env`, `secrets.json`, `config.yaml`, or `*.pem` to this repo
- ❌ Never hardcode an API key, token, password, or credential into source code
- ❌ Never log or print decrypted secret values (even in debug output)
- ❌ Never copy a secret from another tier (e.g., Hartzell secret into a Botpros repo) — tier boundary = tenant firewall
- ✅ If you find an existing plaintext secret in source, flag it to the user before touching it
- ✅ If you need a new secret, ask the user for the value — never invent or guess

## Enforcement

Every push runs `.github/workflows/secret-policy.yml` which calls the reusable policy from `botpros-admin/org-policy-workflows`. It does three checks:
1. GitHub native secret-scanning — BLOCKS push if known token formats detected (AWS, CF, Stripe, GitHub PATs, etc.)
2. gitleaks scan — WARNS on broader plaintext patterns
3. SOPS-required check — WARNS if any new `*.env` or `secrets/**` file lacks SOPS metadata

Currently warn-only for Layers 2-3 (historical plaintext still being cleaned up); will flip to blocking once history is clean.

## Questions

If any of this is unclear or seems wrong for your use case, **ask the user before acting** — don't guess at secret handling.
