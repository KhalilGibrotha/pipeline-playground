#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Keep development checks independent of a writable home directory. This is
# useful in Codex's WSL sandbox, CI runners, and locked-down containers.
export ANSIBLE_LOCAL_TEMP="${ANSIBLE_LOCAL_TEMP:-/tmp/pipeline-playground/ansible-local}"
export ANSIBLE_REMOTE_TEMP="${ANSIBLE_REMOTE_TEMP:-/tmp/pipeline-playground/ansible-remote}"
export ANSIBLE_HOME="${ANSIBLE_HOME:-/tmp/pipeline-playground/ansible-home}"
export ANSIBLE_CONFIG="${ANSIBLE_CONFIG:-$repo_root/ansible/ansible.cfg}"
export ANSIBLE_ROLES_PATH="${ANSIBLE_ROLES_PATH:-$repo_root/ansible/roles}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/pipeline-playground/cache}"
mkdir -p "$ANSIBLE_LOCAL_TEMP" "$ANSIBLE_REMOTE_TEMP" "$ANSIBLE_HOME" "$XDG_CACHE_HOME"

echo "==> Repository hygiene"
python3 scripts/check_repository_hygiene.py --all

echo "==> Repository hygiene regressions"
python3 -m unittest discover --start-directory scripts/tests --pattern 'test_*.py'

echo "==> YAML lint"
yamllint .

echo "==> Catalog and manifest fixtures"
python3 scripts/validate_manifest_fixtures.py

echo "==> Ansible lint"
(
  cd ansible
  ansible-lint .
)

echo "==> Manifest creation behavior"
(
  cd ansible
  ansible-playbook playbooks/test-manifest-creation.yml
)

echo "==> Readiness lifecycle behavior"
(
  cd ansible
  ansible-playbook playbooks/test-readiness-lifecycle.yml
)

if command -v molecule >/dev/null 2>&1; then
  echo "==> Molecule role scenarios"
  for role in ansible/roles/*; do
    (
      cd "$role"
      molecule reset
      molecule test
    )
  done
else
  echo "==> Molecule not installed; role scenarios skipped"
  echo "    Install the Dev Spaces/WSL development dependencies to run them."
fi
