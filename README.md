# .github

Public profile of the organization, the contributing guide, default templates for issues and pull requests, and the workflows the repositories share. Any repository in the organization without its own template uses these.

## Shared checks

| Path | Purpose |
|---|---|
| `.github/workflows/terraform-module.yml` | Checks of a module repository |
| `.github/workflows/terraform-root.yml` | Checks of a repository of roots, with the root directories as input |
| `scripts/install-tool.sh` | Installs Terraform, TFLint, gitleaks, actionlint and zizmor at exact versions, after checking each SHA256 |
| `scripts/pc_iac_check.py` | Project rules TFLint does not cover, file layout, governance inputs, the `aws.project` alias and tag pinned module sources |
| `config/tflint.hcl`, `config/zizmor.yml` | Shared configuration of both tools |

A module repository calls the checks like this.

```yaml
jobs:
  checks:
    uses: aromapacifico-devops/.github/.github/workflows/terraform-module.yml@main
    permissions:
      contents: read
```

Third party actions are pinned to a full commit SHA, and Checkov runs from its image pinned by digest. Callers use `@main`, since this repository belongs to the organization and changes here go through review like any other.

```bash
python3 -m unittest discover -s tests
python3 scripts/pc_iac_check.py module ../terraform-aws-network
```

