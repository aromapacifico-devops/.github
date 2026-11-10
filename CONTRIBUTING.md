# Contributing

This guide explains how changes reach the documentation, the infrastructure roots and the Terraform modules of the organization. It applies to every repository that does not carry its own `CONTRIBUTING.md`.

## Contents

- [How work flows](#how-work-flows)
- [Branches](#branches)
- [Commits](#commits)
- [Pull requests](#pull-requests)
- [Checks before review](#checks-before-review)
- [Module releases](#module-releases)
- [What the repositories enforce](#what-the-repositories-enforce)
- [Secrets](#secrets)

| Term | Meaning |
|---|---|
| Trunk | The `main` branch of each repository. It is the only long-lived branch |
| Story | An issue that describes one piece of work, with its acceptance criteria |
| Squash merge | A merge that turns every commit of a pull request into a single commit on `main` |
| Release tag | A `vX.Y.Z` tag that marks a published version of a module |

## How work flows

The team works on a single trunk. Every change starts from an up-to-date `main`, lives in a short branch and returns to `main` through a reviewed pull request. A branch should last a day or two. When a story is too large for that, split it into smaller stories that each leave `main` in a working state.

1. Take a story from the Ready column of the project board and assign it to yourself.
2. Create a branch from `main` and move the story to In progress.
3. Commit in small steps, each one checked before the next.
4. Open a pull request that closes the story and move the story to In review.
5. A teammate reviews it. After the approval, the author merges it and the board moves the story to Done.

Work on one story at a time, with one pull request per story. There are no release, develop or long-lived feature branches.

## Branches

Branch names follow `<type>/<issue>-<topic>`, in lowercase with hyphens, where the type matches the main commit type.

| Type | Use | Example |
|---|---|---|
| `feat` | New capability, document or module feature | `feat/4-security-identities` |
| `fix` | Correction of something already on `main` | `fix/3-changelog-1.0.0` |
| `docs` | Documentation only | `docs/76-contributing` |
| `chore` | Maintenance with no effect on behavior | `chore/<issue>-pin-tool-versions` |
| `refactor` | Code change that keeps behavior | `refactor/<issue>-split-locals` |

When a branch falls behind `main`, merge `main` into it. Once someone has started reviewing, avoid rebasing or force pushing, since it hides what changed since the last review.

## Commits

Commit messages follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and are written in English.

```text
<type>(<optional scope>): <summary in the imperative mood>

<optional body that explains why>

<optional footers>
```

- Allowed types are `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `perf` and `revert`.
- The first line has at most 72 characters, starts in lowercase and has no final period.
- The summary describes the change, for example `feat: add the telemetry key and its alias`.
- A change that breaks the interface of a module adds `!` after the type, as in `feat!: rename the role inputs`, and a `BREAKING CHANGE:` footer that tells consumers what to do.
- Each commit leaves the branch in a state that passes its checks.

## Pull requests

Every change reaches `main` through a pull request, including changes by administrators.

- The title follows the commit format. Pull requests are squash merged, and the title becomes the commit on `main`, so it feeds the changelog and the release notes.
- The description follows the template. It says what changed, links the story with `Closes <owner>/<repository>#<number>` and pastes the lines of output that prove each acceptance criterion.
- Keep pull requests small enough to review in one sitting. A pull request that grows past one story should be split.
- One approval from a teammate other than the author is required, except for the team leads, who should still ask for one whenever a reviewer is available. A new push dismisses earlier approvals, and every review conversation must be resolved before merging.
- The reviewer checks the change against the acceptance criteria of the story, reads the evidence and tries the change when it is cheap to do so.
- After the merge, GitHub deletes the remote branch. Delete your local branch by name.

## Checks before review

Run the checks of the repository before asking for a review, and paste their result in the pull request.

| Repository | Checks |
|---|---|
| Terraform modules | `terraform fmt -check -recursive`, `terraform test`, `terraform validate` in `sample/`, TFLint, Checkov and gitleaks |
| Infrastructure roots | `terraform fmt -check -recursive`, `terraform validate` in each environment, and the `terraform plan` of the environment the change targets |
| Documentation | Links resolve, and diagrams are exported again when their source changes |

Modules declare provider aliases with `configuration_aliases`, and `terraform validate` fails on such a module when it runs on its own. That is why modules are validated through `terraform test` and the `sample/` folder.

Terraform and provider versions come from `.terraform-version` and `versions.tf`. A story does not raise them as a side effect. A version change gets its own pull request.

Nobody runs `terraform apply` or `terraform destroy` from a laptop against a shared environment. Changes reach an environment through the pipeline after the merge.

## Module releases

Modules are published with [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) and consumed by exact tag, for example `?ref=v1.0.0`.

| Change | Version |
|---|---|
| Removes or renames an input or output, or changes a default in a way that alters existing resources | Major |
| Adds an optional input, an output or a resource that existing callers do not get by default | Minor |
| Fixes behavior without changing the interface | Patch |

1. Merge the changes to `main`.
2. Open a `chore: release X.Y.Z` pull request that moves the entries of `CHANGELOG.md` under the new version.
3. After it merges, tag that commit as `vX.Y.Z` and push the tag.

Release tags cannot be moved or deleted. A mistake in a release is fixed by publishing a new patch version.

## What the repositories enforce

The public repositories enforce these rules. The two team leads can merge a pull request without the approval, which keeps work moving when no reviewer is free. Their changes still go through a pull request, and GitHub records every bypass in the audit log.

| Target | Rule |
|---|---|
| `main` | Changes only through a pull request with one approval |
| `main` | New pushes dismiss earlier approvals, and review conversations must be resolved |
| `main` | Squash is the only merge method, and the commit takes the pull request title |
| `main` | It cannot be deleted or force pushed |
| `v*` tags in module repositories | They cannot be moved or deleted |

The team handbook is a private repository, and the GitHub plan of the organization cannot protect private repositories. Its pull requests follow the same flow by agreement.

## Secrets

Credentials, keys, tokens, Terraform state and plan files never go into a repository, an issue or a pull request. Pull requests show plan output with account numbers masked. If a secret is committed by mistake, rotate it first and then remove it from the history, since anyone may have copied it already.
