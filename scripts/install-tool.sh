#!/usr/bin/env bash
# Installs a check tool at an exact version and checks its SHA256 before use.
# usage: install-tool.sh terraform|tflint|gitleaks|actionlint|zizmor
set -euo pipefail

tool=$1
dest=${RUNNER_TEMP:-/tmp}/bin
mkdir -p "$dest"
work=$(mktemp -d)

fetch() {
  curl -fsSL -o "$work/pkg" "$1"
  echo "$2  $work/pkg" | sha256sum -c -
}

case "$tool" in
  terraform)
    fetch https://releases.hashicorp.com/terraform/1.17.1/terraform_1.17.1_linux_amd64.zip \
      4638628058e71a55212b1c563712eac03b902128f40740f3dc8174df12135061
    unzip -q -o "$work/pkg" terraform -d "$dest"
    ;;
  tflint)
    fetch https://github.com/terraform-linters/tflint/releases/download/v0.65.0/tflint_linux_amd64.zip \
      d4c545ed2e29d6338604b586f34f544f380f70f243aa72f7b484713835eaec61
    unzip -q -o "$work/pkg" tflint -d "$dest"
    ;;
  gitleaks)
    fetch https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
      551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
    tar -xzf "$work/pkg" -C "$dest" gitleaks
    ;;
  actionlint)
    fetch https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz \
      8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
    tar -xzf "$work/pkg" -C "$dest" actionlint
    ;;
  zizmor)
    name=zizmor-1.31.1-py3-none-manylinux_2_28_x86_64.whl
    printf 'zizmor @ https://files.pythonhosted.org/packages/py3/z/zizmor/%s --hash=sha256:%s\n' \
      "$name" 58e878eb2dbd2c6183c105e1ac28c14f7dd1eca44a783f1fe2a69647d012c410 > "$work/requirements.txt"
    python3 -m venv "$dest/zizmor-venv"
    "$dest/zizmor-venv/bin/pip" install --quiet --no-deps --require-hashes -r "$work/requirements.txt"
    ln -sf "$dest/zizmor-venv/bin/zizmor" "$dest/zizmor"
    ;;
  *)
    echo "unknown tool $tool" >&2
    exit 2
    ;;
esac

rm -rf "$work"
if [ -n "${GITHUB_PATH:-}" ]; then echo "$dest" >> "$GITHUB_PATH"; fi
"$dest/$tool" --version | head -1
