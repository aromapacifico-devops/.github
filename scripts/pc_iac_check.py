"""Checks the project rules for Terraform that TFLint does not cover.

usage: pc_iac_check.py module DIR
       pc_iac_check.py root DIR [DIR ...]

Module rules
  PC-IAC-001  root files and sample files exist
  PC-IAC-002  governance variables client, project, environment and additional_tags exist
  PC-IAC-005  versions.tf declares configuration_aliases = [aws.project], no provider block exists,
              and every AWS resource and data source sets provider = aws.project
Root rules
  PC-IAC-005  the main provider uses alias principal
  PC-IAC-015  every module source is a Git address of the organization pinned to vX.Y.Z

Exit status 0 when every rule holds and 1 otherwise. Each finding names the rule, file and line.
"""

import re
import sys
from pathlib import Path

MODULE_FILES = [".gitignore", "CHANGELOG.md", "README.md", "data.tf", "locals.tf", "main.tf", "outputs.tf",
                "providers.tf", "variables.tf", "versions.tf"]
SAMPLE_FILES = ["README.md", "data.tf", "main.tf", "outputs.tf", "providers.tf", "terraform.tfvars", "variables.tf"]
GOVERNANCE = ["client", "project", "environment", "additional_tags"]
SOURCE = re.compile(r'^git::https://github\.com/aromapacifico-devops/[A-Za-z0-9._-]+\.git\?ref=v\d+\.\d+\.\d+$')
BLOCK = re.compile(r'^[ \t]*(resource|data|provider|module|variable)\s+"([^"]+)"(?:\s+"([^"]+)")?\s*\{', re.M)


def strip_comments(text):
    """Blanks comments and keeps line numbers, leaving quoted strings intact."""
    out, i, n = [], 0, len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
        elif c == '"':
            in_string = True
            out.append(c)
            i += 1
        elif c == "#" or text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append("".join(ch for ch in text[i:end] if ch == "\n"))
            i = end
        else:
            out.append(c)
            i += 1
    return "".join(out)


def blocks(path):
    """Yields (kind, labels, body, line) for each top-level block of a file."""
    text = strip_comments(path.read_text(encoding="utf-8"))
    for match in BLOCK.finditer(text):
        depth, i = 0, match.end() - 1
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            elif text[i] == '"':
                i += 1
                while i < len(text) and text[i] != '"':
                    i += 2 if text[i] == "\\" else 1
            i += 1
        line = text.count("\n", 0, match.start()) + 1
        yield match.group(1), [g for g in match.groups()[1:] if g], text[match.end():i], line


def check_module(root):
    findings = []
    for name in MODULE_FILES:
        if not (root / name).is_file():
            findings.append(f"PC-IAC-001 {name} is missing")
    for name in SAMPLE_FILES:
        if not (root / "sample" / name).is_file():
            findings.append(f"PC-IAC-001 sample/{name} is missing")

    tf_files = sorted(root.glob("*.tf"))
    declared = {labels[0] for path in tf_files for kind, labels, _, _ in blocks(path) if kind == "variable"}
    for name in GOVERNANCE:
        if name not in declared:
            findings.append(f"PC-IAC-002 variable {name} is missing")

    versions = root / "versions.tf"
    if versions.is_file() and not re.search(r'configuration_aliases\s*=\s*\[\s*aws\.project\s*\]',
                                            strip_comments(versions.read_text(encoding="utf-8"))):
        findings.append("PC-IAC-005 versions.tf must declare configuration_aliases = [aws.project]")

    for path in tf_files:
        for kind, labels, body, line in blocks(path):
            where = f"{path.name}:{line}"
            if kind == "provider":
                findings.append(f"PC-IAC-005 {where} a module configures no provider")
            elif kind in ("resource", "data") and labels[0].startswith("aws_"):
                if not re.search(r'^\s*provider\s*=\s*aws\.project\s*$', body, re.M):
                    findings.append(f"PC-IAC-005 {where} {kind} {'.'.join(labels)} must set provider = aws.project")
    return findings


def check_root(root):
    findings = []
    tf_files = sorted(root.glob("*.tf"))
    providers = [labels for path in tf_files for kind, labels, body, _ in blocks(path)
                 if kind == "provider" and labels[0] == "aws" and re.search(r'alias\s*=\s*"principal"', body)]
    if not providers:
        findings.append(f"PC-IAC-005 {root} needs a provider aws with alias principal")
    for path in tf_files:
        for kind, labels, body, line in blocks(path):
            if kind != "module":
                continue
            source = re.search(r'^\s*source\s*=\s*"([^"]+)"', body, re.M)
            if not source or not SOURCE.match(source.group(1)):
                found = source.group(1) if source else "no source"
                findings.append(f"PC-IAC-015 {root.name}/{path.name}:{line} module {labels[0]} source {found} must be "
                                "git::https://github.com/aromapacifico-devops/<repo>.git?ref=vX.Y.Z")
    return findings


def main(argv):
    if len(argv) < 3 or argv[1] not in ("module", "root"):
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    check = check_module if argv[1] == "module" else check_root
    findings = [f for directory in argv[2:] for f in check(Path(directory))]
    for finding in findings:
        print(finding)
    print(f"{len(findings)} finding(s) in {', '.join(argv[2:])}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
