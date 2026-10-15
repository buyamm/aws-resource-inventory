# Project skills

Third-party Claude Code skills vendored into this repo (Claude Code loads `.claude/skills/*/SKILL.md`
automatically). Each directory keeps the upstream LICENSE; files are copied unmodified.

| Skill | Upstream (path @ commit) | License | Use it when |
|---|---|---|---|
| `aws-architecture-diagram` | [vidanov/aws-architecture-diagram-skill](https://github.com/vidanov/aws-architecture-diagram-skill) `skills/aws-architecture-diagram`, `references/`, 3 `templates/` @ `d0f8550` | MIT | Changing `src/diagram_generator.py`: group nesting (Cloud → Region → VPC → AZ → Subnet), verified `mxgraph.aws4.*` stencil names and colors, edge/layout rules |
| `drawio` | [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp) `plugins/claude-code/skills/drawio` @ `7ed3cc2` | Apache-2.0 | mxGraph XML structure, containers, ELK `--layout`, PNG/SVG export with the draw.io desktop CLI |
| `terraform-style-guide` | [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) `plugins/terraform/skills/terraform-style-guide` @ `f706481` | MPL-2.0 | HCL emitted by `src/iac_generator.py`: file layout, naming, variables/outputs contracts |
| `refactor-module` | same repo, `plugins/terraform/skills/refactor-module` @ `f706481` | MPL-2.0 | Splitting generated resources into `modules/` with variable/output interfaces |
| `terraform-search-import` | same repo, `plugins/terraform/skills/terraform-search-import` @ `f706481` | MPL-2.0 | `import` blocks / bulk import of existing resources |
| `terraform-skill` | [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill) `skills/terraform-skill` @ `0a3a4a6` | Apache-2.0 | `modules/` + `environments/` layout, state/backends, trivy/checkov, `terraform test` |

To update: re-clone upstream, review the diff of every file (skills are instructions Claude follows),
copy over, and bump the commit in this table.
