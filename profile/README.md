# Aroma Pacifico DevOps

Coffee platform modernization challenge, Universidad Icesi, 2026. The platform follows coffee from the farm to the buyer across Cauca, Huila and Tolima, on a serverless AWS design with a reusable infrastructure pattern.

This is an academic case study. Its figures, pilot and 2020 design are class material and do not describe an official project of the Federación Nacional de Cafeteros.

| Repository | Content |
|---|---|
| [`aromapacifico-devops-docs`](https://github.com/aromapacifico-devops/aromapacifico-devops-docs) | Architecture, decisions, diagrams and design documents |
| [`aromapacifico-devops-infra`](https://github.com/aromapacifico-devops/aromapacifico-devops-infra) | Terraform roots of each environment, bootstrap and deployment pipelines |
| [`terraform-aws-network`](https://github.com/aromapacifico-devops/terraform-aws-network) | VPC, subnets, routes, endpoints and the link to one collection center |
| [`terraform-aws-security`](https://github.com/aromapacifico-devops/terraform-aws-security) | Platform identities, encryption keys and permanent cloud firewall rules |
| [`terraform-aws-telemetry-ingestion`](https://github.com/aromapacifico-devops/terraform-aws-telemetry-ingestion) | Ingestion path from IoT Core to storage and alerts |
| [`terraform-aws-farm`](https://github.com/aromapacifico-devops/terraform-aws-farm) | Reusable identity of one farm |
| [`terraform-aws-inference-function`](https://github.com/aromapacifico-devops/terraform-aws-inference-function) | Event-driven inference function pattern |
| [`terraform-aws-module-template`](https://github.com/aromapacifico-devops/terraform-aws-module-template) | Template that starts a new module |

Each Terraform module has its own repository and version, and the infrastructure repository consumes them through exact tags.

Start with [`docs/architecture/README.md`](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/blob/main/docs/architecture/README.md).
