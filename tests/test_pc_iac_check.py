"""Seeded violations for pc_iac_check.py. Run with python3 -m unittest discover -s tests."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pc_iac_check  # noqa: E402

VERSIONS = """terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 6.0"
      configuration_aliases = [aws.project]
    }
  }
}
"""

VARIABLES = "".join(f'variable "{name}" {{\n  type = string\n}}\n\n' for name in pc_iac_check.GOVERNANCE)

MAIN = """# A comment with provider "aws" { and a brace
resource "aws_sqs_queue" "work" {
  provider = aws.project

  name = "q-{x}"
}

data "aws_region" "current" {
  provider = aws.project
}

data "archive_file" "zip" {
  type = "zip"
}
"""

ROOT_MAIN = """module "network" {
  source = "git::https://github.com/aromapacifico-devops/terraform-aws-network.git?ref=v1.1.0"
}
"""

ROOT_PROVIDERS = """provider "aws" {
  alias  = "principal"
  region = var.region
}
"""


def write(base, files):
    for name, content in files.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def good_module(base):
    files = {name: "" for name in pc_iac_check.MODULE_FILES}
    files.update({f"sample/{name}": "" for name in pc_iac_check.SAMPLE_FILES})
    files.update({"versions.tf": VERSIONS, "variables.tf": VARIABLES, "main.tf": MAIN})
    write(base, files)


class ModuleRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        good_module(self.base)

    def tearDown(self):
        self.tmp.cleanup()

    def findings(self):
        return pc_iac_check.check_module(self.base)

    def test_a_complete_module_passes(self):
        self.assertEqual(self.findings(), [])

    def test_missing_files(self):
        os.remove(self.base / "locals.tf")
        os.remove(self.base / "sample" / "terraform.tfvars")
        self.assertEqual(self.findings(), ["PC-IAC-001 locals.tf is missing", "PC-IAC-001 sample/terraform.tfvars is missing"])

    def test_missing_governance_variable(self):
        write(self.base, {"variables.tf": VARIABLES.replace('variable "additional_tags"', 'variable "tags"')})
        self.assertEqual(self.findings(), ["PC-IAC-002 variable additional_tags is missing"])

    def test_missing_provider_alias(self):
        write(self.base, {"versions.tf": VERSIONS.replace("configuration_aliases = [aws.project]", "")})
        self.assertIn("PC-IAC-005 versions.tf must declare configuration_aliases = [aws.project]", self.findings())

    def test_resource_without_provider(self):
        write(self.base, {"main.tf": MAIN + '\nresource "aws_s3_bucket" "objects" {\n  bucket = "b"\n}\n'})
        self.assertEqual(self.findings(), ["PC-IAC-005 main.tf:16 resource aws_s3_bucket.objects must set provider = aws.project"])

    def test_provider_block_in_module(self):
        write(self.base, {"providers.tf": 'provider "aws" {\n  region = "us-east-1"\n}\n'})
        self.assertEqual(self.findings(), ["PC-IAC-005 providers.tf:1 a module configures no provider"])

    def test_commented_provider_is_ignored(self):
        write(self.base, {"providers.tf": '# provider "aws" {\n/* provider "aws" { */\n'})
        self.assertEqual(self.findings(), [])


class RootRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        write(self.base, {"main.tf": ROOT_MAIN, "providers.tf": ROOT_PROVIDERS})

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_pinned_root_passes(self):
        self.assertEqual(pc_iac_check.check_root(self.base), [])

    def test_branch_or_local_sources_fail(self):
        for source in ["git::https://github.com/aromapacifico-devops/terraform-aws-network.git?ref=main",
                       "../terraform-aws-network",
                       "git::https://github.com/someone/terraform-aws-network.git?ref=v1.0.0",
                       "git::https://github.com/aromapacifico-devops/terraform-aws-network.git?ref=v1.0"]:
            write(self.base, {"main.tf": ROOT_MAIN.replace(
                "git::https://github.com/aromapacifico-devops/terraform-aws-network.git?ref=v1.1.0", source)})
            findings = pc_iac_check.check_root(self.base)
            self.assertEqual(len(findings), 1, source)
            self.assertTrue(findings[0].startswith("PC-IAC-015"), source)

    def test_root_without_principal_alias(self):
        write(self.base, {"providers.tf": ROOT_PROVIDERS.replace('alias  = "principal"', 'alias  = "main"')})
        self.assertEqual(len(pc_iac_check.check_root(self.base)), 1)

    def test_command_exit_status(self):
        self.assertEqual(pc_iac_check.main(["x", "root", str(self.base)]), 0)
        write(self.base, {"main.tf": ROOT_MAIN.replace("v1.1.0", "main")})
        self.assertEqual(pc_iac_check.main(["x", "root", str(self.base)]), 1)


if __name__ == "__main__":
    unittest.main()
