# AWS Resource Inventory — Hướng dẫn sử dụng

> Dành cho người mới dùng tool. Làm theo từng bước từ trên xuống là chạy được.
> Tài liệu kỹ thuật bằng tiếng Anh: [README.md](README.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/ACCURACY_AND_SECURITY.md](docs/ACCURACY_AND_SECURITY.md), [docs/TESTING.md](docs/TESTING.md).

---

## 1. Tool này làm gì?

Bạn tiếp nhận một AWS account **không có IaC, không có tài liệu, không có diagram**. `aws-inventory` giúp bạn:

1. **Quét account** (chỉ dùng API đọc `Describe*`/`List*`/`Get*`) và thu thập cấu hình đầy đủ của 33 loại resource: EC2 instance, VPC, Security Group, Lambda, RDS instance, CloudWatch log group, Step Functions state machine, DynamoDB table, S3 bucket, IAM role, subnet, route table, internet gateway, NAT gateway, VPC endpoint, CloudFront distribution, load balancer (ALB/NLB), listener, target group, Route 53 hosted zone, ACM certificate, WAFv2 web ACL, ECS cluster, ECS service, ECS task definition (chỉ revision đang được service chạy), ECR repository, Auto Scaling group, launch template, ElastiCache replication group, SQS queue, SNS topic, EventBridge rule, EventBridge Scheduler schedule.
2. **Lưu ra thư mục output** (gọi là Output_Dir) dạng JSON + Markdown, có checksum SHA-256 để kiểm tra toàn vẹn.
3. **Phân tích** quan hệ giữa các resource (Lambda → DynamoDB, EC2 → VPC, ...), nhận diện pattern kiến trúc và phát hiện rủi ro bảo mật. **Mỗi kết luận đều có trích dẫn (citation)** trỏ tới đúng file và đúng thuộc tính đã thu thập.
4. **Vẽ diagram** draw.io với icon AWS chính thức.
5. **Sinh Terraform** kèm script `import.sh` và `verify_state.sh`.
6. **Kiểm chứng** toàn bộ output bằng lệnh `verify` (checksum + mọi citation).
7. **MCP server** cho AI Agent (Claude Desktop, Claude Code, ...) đọc dữ liệu đã thu thập, **không có quyền truy cập AWS**.

Chỉ `discover` và `collect` gọi AWS. Các lệnh còn lại chạy **offline** trên Output_Dir.

---

## 2. Chuẩn bị

| Yêu cầu | Cách kiểm tra |
|---|---|
| Python 3.11 trở lên | `python3.11 --version` |
| AWS credentials (chỉ cần cho `discover`/`collect`) | `aws sts get-caller-identity` |
| Quyền đọc trên account | xem mục 2.1 |
| (Tuỳ chọn) Terraform ≥ 1.5 | `terraform version` |
| (Tuỳ chọn) CLI `drawio-ai` để validate diagram | `drawio-ai --help` |

### 2.1. Quyền IAM tối thiểu

Policy đầy đủ nằm ở [docs/iam-policy.json](docs/iam-policy.json): chỉ gồm các action đọc cụ thể, không có wildcard. Gắn policy này (hoặc managed policy `ReadOnlyAccess` của AWS) cho user/role dùng để quét. Statement `sts:AssumeRole` chỉ cần khi bạn dùng `--role-arn`; nên giới hạn `Resource` của nó về đúng role cần assume.

### 2.2. Credentials

Tool **chỉ** lấy credentials qua chuỗi mặc định của boto3, theo thứ tự: biến môi trường, `~/.aws/credentials` / `~/.aws/config`, AWS SSO, role của container/EC2. Không có option nào để truyền access key trên dòng lệnh.

```bash
aws configure                      # hoặc
aws sso login --profile audit      # rồi dùng --profile audit
```

---

## 3. Cài đặt

```bash
git clone <repo> aws-resource-inventory
cd aws-resource-inventory
python3.11 -m venv venv
venv/bin/pip install -r requirements-dev.txt && venv/bin/pip install -e .
source venv/bin/activate
aws-inventory --version
```

Chỉ cần chạy tool (không chạy test/demo): `venv/bin/pip install -e .` là đủ.

---

## 4. Chạy thử với demo (không cần AWS account)

Demo tạo một account giả lập bằng moto (mỗi loại resource một cái, cố ý có vài cấu hình không an toàn) rồi chạy toàn bộ quy trình:

```bash
python scripts/demo.py                    # ghi vào ./demo-output
```

Kết quả mong đợi (rút gọn):

```
$ aws-inventory collect --output-dir demo-output --region us-east-1
Collected 14/14 resources in 0.32s (44 API calls) -> demo-output
Time saved: 1.17 hours (100.0%)
$ aws-inventory analyze --output-dir demo-output
Analyzed 14 resources: 11 relationships, 2 patterns, 3 security findings
$ aws-inventory generate-iac --output-dir demo-output
$ aws-inventory generate-docs --output-dir demo-output
$ aws-inventory verify --output-dir demo-output
OK: 68 files, 23 citations verified
```

Kết quả mẫu đã được commit sẵn ở [examples/output/](examples/output/). Các option khác:

```bash
python scripts/demo.py --output-dir examples/output       # tạo lại ví dụ mẫu
python scripts/demo.py --live --profile audit --region ap-southeast-1   # chạy trên account thật (chỉ đọc)
```

Demo xoá thư mục output trước khi chạy, nhưng **chỉ** khi thư mục rỗng hoặc là Output_Dir cũ (có `manifest.json`). Thư mục khác sẽ được giữ nguyên và demo thoát với mã 2.

Đo hiệu năng: `python scripts/benchmark.py` chạy `collect` trên account moto gồm 1000 tài nguyên ở 17 region, mỗi API call trễ thêm 100 ms. Kết quả đo nằm trong [docs/ACCURACY_AND_SECURITY.md](docs/ACCURACY_AND_SECURITY.md#performance-benchmark).

---

## 5. Quy trình trên account thật

### Bước 1 — (tuỳ chọn) `discover`: xem trước có gì

```bash
aws-inventory discover --region ap-southeast-1 --profile audit
```

Ghi `output/discovery.json` (danh sách resource + lỗi nếu có). Hữu ích để kiểm tra quyền và phạm vi trước khi thu thập.

### Bước 2 — `collect`: thu thập

```bash
aws-inventory collect --region ap-southeast-1 --region us-east-1 --output-dir ./output
```

- `--region` lặp lại được; bỏ trống = quét mọi region đang bật của account.
- `--profile` chọn profile AWS; `--role-arn` (+ `--external-id`) để assume role trước khi quét (session name `aws-resource-inventory`).
- `--max-workers` (mặc định 10) = số region/resource xử lý song song. Giảm xuống nếu bị throttling.
- `--project-tag KEY=VALUE` (lặp lại được, resource phải có **tất cả** các tag) = chỉ lấy resource của một project. Tool tìm resource có tag qua `tag:GetResources` (IAM role qua `iam:ListRoleTags`); nếu không truyền `--region` thì tìm ở mọi region đang bật và chỉ giữ các region có resource được tag. Ví dụ: `aws-inventory collect --project-tag service=shop --project-tag environment=prod`.
- Dù có `--project-tag` hay không, tool luôn đi theo các tham chiếu trong spec đã thu thập (VPC, security group, IAM role, log group, ...) để lấy thêm resource phụ thuộc chưa được tag.
- Mặc định bỏ qua default VPC, security group `default` của default VPC và service-linked role (`/aws-service-role/`), trừ khi có resource khác tham chiếu tới. `--include-defaults` để giữ lại tất cả.
- Phạm vi thực tế (tag, region, resource bị loại, resource nào được thêm vì spec nào tham chiếu) được ghi vào khối `scope` trong `manifest.json` và `collection_report.json`.

Cuối lệnh, tool in thời gian tiết kiệm được so với làm tay (ước tính 5 phút/resource). Ví dụ:

```
Collected 120/120 resources in 18.40s (391 API calls) -> ./output
Time saved: 9.99 hours (99.9%)
Reports: summary_report.md, collection_report.json
```

Khi gặp lỗi API, tool tự retry tối đa 3 lần (chờ 1 s rồi 2 s, hoặc theo header `Retry-After`), ghi lỗi vào `collection_report.json` và **tiếp tục** với resource khác.

### Bước 3 — `analyze`: phân tích + diagram

```bash
aws-inventory analyze --output-dir ./output
aws-inventory analyze --output-dir ./output --validate-diagram   # thêm bước drawio-ai validate nếu đã cài
```

Ghi:
- `analysis/analysis.json`, `analysis/analysis.md`: quan hệ (`vpc_connection`, `iam_role_usage`, `security_group`, `dynamodb_access`, `log_group`, `subnet_placement`, `route_table_association`, `route_target`, `lb_listener`, `forwards_to`, `certificate`, `cdn_origin`, `waf_protection`, `dns_alias`, `ecs_cluster`, `task_definition`, `container_image`, `lb_target`, `launch_template`, `subscription`, `event_target`), pattern ("Serverless Application", "Compute in VPC", "Static site: S3 + CloudFront", "Web app: CloudFront + ALB + ECS") và phát hiện bảo mật (`OVERLY_PERMISSIVE_IAM_POLICY`, `PUBLIC_S3_BUCKET`, `UNRESTRICTED_SECURITY_GROUP_ACCESS`), mỗi mục có điểm tin cậy và citation.
- `diagrams/architecture.drawio`: mở bằng <https://app.diagrams.net> hoặc draw.io desktop.

Các pattern chưa có luật nhận diện (API Gateway + Lambda + DynamoDB, EC2 + Load Balancer khi instance được đăng ký trực tiếp vào target group) được liệt kê trong `undetectable_patterns` kèm lý do, tool không đoán.

### Bước 4 — `generate-iac`: sinh Terraform

```bash
aws-inventory generate-iac --output-dir ./output                      # ghi vào ./output/terraform
aws-inventory generate-iac --output-dir ./output --terraform-dir ./infra
```

Cấu trúc: `main.tf` + `providers.tf` ở gốc, mỗi region là một module (`us-east-1/`, `global/` cho S3 và IAM), mỗi loại resource một file `<type>.tf`. Phía trên mỗi block có comment ghi file spec nguồn, ARN, region, các key đã map (`# mapped:`) và chưa map (`# unmapped:`).

Đưa resource có sẵn vào Terraform state:

```bash
cd output/terraform
terraform init
./import.sh          # terraform import từng resource (bỏ qua nếu đã có trong state)
./verify_state.sh    # terraform plan -detailed-exitcode: 0 = không thay đổi, 2 = có thay đổi, 1 = lỗi
```

Giá trị bị che (ví dụ biến môi trường chứa mật khẩu) xuất hiện kèm comment `# REDACTED: set manually` và được đưa vào `lifecycle.ignore_changes`; bạn cần tự điền nếu muốn Terraform quản lý chúng.

### Bước 5 — `generate-docs`: tài liệu hạ tầng

```bash
aws-inventory generate-docs --output-dir ./output
```

Ghi `docs/infrastructure.md`: thống kê resource, từng pattern, từng quan hệ và các phát hiện bảo mật. Mỗi câu kết thúc bằng citation dạng `[cite: <spec_file>#<property_path> sha256:<12 ký tự đầu>]`.

### Bước 6 — `verify`: kiểm chứng

```bash
aws-inventory verify --output-dir ./output
```

Lệnh này tính lại hash của mọi file trong `checksums.sha256` và kiểm tra **từng** citation trong `analysis/analysis.json`: file spec tồn tại, checksum khớp, đường dẫn thuộc tính tồn tại và giá trị đúng như đã trích dẫn.

- Thành công: `OK: <n> files, <m> citations verified`, mã thoát 0.
- Có sai lệch: mỗi dòng `đường_dẫn:số_dòng: lý do`, mã thoát 1. Ví dụ ai đó sửa tay file spec sau khi `analyze` → `verify` chỉ ra đúng file và dòng bị sửa.

---

## 6. Kết nối AI Agent qua MCP

```bash
aws-inventory mcp-serve --cache-dir /duong/dan/tuyet/doi/output
```

Bạn thường không chạy lệnh này bằng tay mà khai báo trong cấu hình MCP của client, ví dụ `.mcp.json` (Claude Code) hoặc `claude_desktop_config.json` (Claude Desktop):

```json
{
  "mcpServers": {
    "aws-inventory": {
      "command": "/duong/dan/aws-resource-inventory/venv/bin/aws-inventory",
      "args": ["mcp-serve", "--cache-dir", "/duong/dan/tuyet/doi/output"]
    }
  }
}
```

Hoặc với Claude Code:

```bash
claude mcp add aws-inventory -- /duong/dan/venv/bin/aws-inventory mcp-serve --cache-dir /duong/dan/output
```

Các tool AI Agent được dùng:

| Tool | Tham số | Trả về |
|---|---|---|
| `list-resources` | `region?`, `resource_type?` (tên chuẩn hoặc alias như `lambda`, `s3`) | danh sách resource + đường dẫn file spec + checksum |
| `get-resource-spec` | `arn` | toàn bộ spec (đã sanitize) |
| `analyze-activity-flow` | `arn?` | quan hệ, pattern, phát hiện bảo mật (lọc theo ARN nếu có) |
| `generate-documentation` | – | nội dung `infrastructure.md` + danh sách citation |

Cơ chế an toàn: server xoá mọi biến `AWS_*` và trỏ file config/credentials AWS tới đường dẫn không tồn tại trước khi chạy; code server không import boto3; chỉ chấp nhận 4 tool trên với đúng tham số (yêu cầu khác bị từ chối và ghi security log); tối đa 10 request/giây; mọi response đều qua sanitizer. ARN không có trong dữ liệu đã thu thập → lỗi kèm hướng dẫn chạy `aws-inventory collect`.

Ví dụ câu hỏi: "Liệt kê các Lambda function, cho biết chúng ghi vào bảng DynamoDB nào, trích dẫn file spec."

---

## 7. Cấu trúc Output_Dir

```
output/
├── manifest.json                         account, region, thời gian, phiên bản tool, số lượng
├── resources.json  resources.md          tổng hợp mọi resource
├── <type>/<region>/<id>.json|.md         mỗi resource một file (S3, IAM dùng region "global")
├── raw_responses/<type>/<region>/<id>_raw.json   response gốc của API (đã sanitize)
├── discovery.json                        kết quả discover + lỗi
├── collection_report.json                mọi API operation, lỗi, thời gian từng phase, số liệu
├── summary_report.md                     so sánh làm tay vs tự động
├── analysis/analysis.json  analysis.md   (analyze)
├── diagrams/architecture.drawio          (analyze)
├── docs/infrastructure.md                (generate-docs)
├── terraform/                            (generate-iac)
└── checksums.sha256  checksums.json      cập nhật sau mỗi lệnh có ghi file
```

`<type>` là tên loại resource theo Terraform: `aws_instance`, `aws_vpc`, `aws_security_group`, `aws_lambda_function`, `aws_db_instance`, `aws_cloudwatch_log_group`, `aws_sfn_state_machine`, `aws_dynamodb_table`, `aws_s3_bucket`, `aws_iam_role`, `aws_subnet`, `aws_route_table`, `aws_internet_gateway`, `aws_nat_gateway`, `aws_vpc_endpoint`, `aws_cloudfront_distribution`, `aws_lb`, `aws_lb_listener`, `aws_lb_target_group`, `aws_route53_zone`, `aws_acm_certificate`, `aws_wafv2_web_acl`, `aws_ecs_cluster`, `aws_ecs_service`, `aws_ecs_task_definition`, `aws_ecr_repository`, `aws_autoscaling_group`, `aws_launch_template`, `aws_elasticache_replication_group`, `aws_sqs_queue`, `aws_sns_topic`, `aws_cloudwatch_event_rule`, `aws_scheduler_schedule`. CloudFront, Route 53 và WAF web ACL scope CLOUDFRONT dùng region `global`.

---

## 8. Tham chiếu lệnh

Option chung (đặt **trước** tên lệnh): `--log-level DEBUG|INFO|WARNING|ERROR` (mặc định INFO, log ra stderr), `--no-color`, `--version`, `-h/--help`. Ví dụ: `aws-inventory --log-level DEBUG collect --region us-east-1`.

| Lệnh | Option | Gọi AWS? |
|---|---|---|
| `aws-inventory discover` | `--region`…, `--project-tag`…, `--include-defaults`, `--profile`, `--role-arn`, `--external-id`, `--output-dir` | có |
| `aws-inventory collect` | như `discover` + `--max-workers` | có |
| `aws-inventory analyze` | `--output-dir`, `--validate-diagram` | không |
| `aws-inventory generate-iac` | `--output-dir`, `--terraform-dir` | không |
| `aws-inventory generate-docs` | `--output-dir` | không |
| `aws-inventory verify` | `--output-dir` | không |
| `aws-inventory mcp-serve` | `--cache-dir` (bắt buộc) | không |

`--output-dir` mặc định là `./output`. `aws-inventory <lệnh> --help` in ví dụ cụ thể cho từng lệnh.

**Mã thoát:**

| Mã | Ý nghĩa |
|---|---|
| 0 | Thành công |
| 1 | Chạy xong nhưng có lỗi: lỗi discover/collect, file spec hỏng, `verify` thấy sai lệch, validate diagram thất bại |
| 2 | Không khởi động được: sai tham số, không có credentials, assume role thất bại, Output_Dir không có spec |

---

## 9. Bảo mật — những gì tool đảm bảo

- Chỉ gọi API đọc (`Describe*`, `List*`, `Get*`) cùng `sts:GetCallerIdentity` và `sts:AssumeRole`. Có test ghi lại mọi API call để kiểm tra điều này.
- Không ghi credentials ra file hay log. Mọi log và output trên terminal đều qua bộ lọc sanitize, bộ lọc này còn xoá đúng access key/secret/session token của phiên hiện tại nếu chúng xuất hiện.
- Dữ liệu ghi ra đĩa và trả qua MCP đều được sanitize: access key ID (`AKIA…`/`ASIA…`), private key PEM, và giá trị của các key có tên chứa `password`, `secret`, `token`, `api_key`, `credential`, ... được thay bằng `[REDACTED…]`. Cấu trúc JSON (key, độ dài list) giữ nguyên.

Chi tiết: [docs/ACCURACY_AND_SECURITY.md](docs/ACCURACY_AND_SECURITY.md).

---

## 10. Xử lý sự cố

| Hiện tượng | Nguyên nhân / cách xử lý |
|---|---|
| `Unable to call sts:GetCallerIdentity (NoCredentialsError)`, mã 2 | Chưa có credentials. Chạy `aws configure` / `aws sso login`, hoặc `export AWS_PROFILE=...`; kiểm tra bằng `aws sts get-caller-identity`. |
| `AssumeRole failed for <role>`, mã 2 | Caller không có quyền `sts:AssumeRole`, trust policy của role không tin caller, hoặc sai `--external-id`. |
| Log có `Missing <service>:<Action> permission`, mã 1 | Thiếu quyền đọc. Bổ sung từ `docs/iam-policy.json`. Thiếu quyền ở call phụ (tags, policy) chỉ làm thiếu key đó; thiếu quyền ở call chính thì resource bị bỏ qua. Xem chi tiết trong `collection_report.json`. |
| Lỗi discover ở một số region | Region chưa bật hoặc bị SCP chặn. Giới hạn bằng `--region`. |
| Bị throttling, chạy chậm | Giảm `--max-workers`. |
| `no resource specifications found in <dir>`, mã 2 | Lệnh offline trỏ vào thư mục chưa có dữ liệu. Chạy `collect` trước hoặc sửa `--output-dir`. |
| `verify` báo `checksum mismatch` | File bị sửa sau khi tạo. Chạy lại lệnh đã tạo ra file đó (`analyze`, `generate-iac`, `generate-docs` đều cập nhật checksum) hoặc `collect` lại. |
| `verify` báo sai lệch citation tại `file:dòng` | File spec bị sửa sau `analyze`. Chạy lại `analyze` (và `generate-docs`). |
| AI client không thấy tool / server tắt ngay | Dùng đường dẫn tuyệt đối cho cả lệnh và `--cache-dir`, thư mục phải tồn tại. Chạy thử lệnh trong terminal để xem lỗi trên stderr. |
| `terraform plan` vẫn có thay đổi sau `import.sh` | Xem phần giới hạn bên dưới; điền tay các giá trị `# REDACTED: set manually`. |
| `--validate-diagram` báo bỏ qua | Chưa cài CLI `drawio-ai`. XML vẫn được kiểm tra hợp lệ. |

---

## 11. Giới hạn đã biết

- Chỉ hỗ trợ các loại resource ở trên. CloudFront chỉ thu thập distribution (không thu thập edge location hay dải IP).
- ECS: chỉ thu thập các revision task definition mà service đang chạy; service phải dùng định dạng ARN dài (`service/<cluster>/<service>`). ElastiCache: chỉ replication group (không gồm cluster Memcached đứng riêng); subnet group, security group và engine version lấy từ member cluster đầu tiên.
- Biến môi trường ECS có `name` nhạy cảm (chứa `secret`, `password`, `token`, ...) và `UserData` của launch template luôn bị thay bằng `[REDACTED]`.
- Origin là load balancer được nối với load balancer đã thu thập theo DNS name khi phân tích, nhưng dependency closure không lần theo được (DNS name không xác định ARN); hãy gắn tag cho load balancer hoặc thu thập không dùng `--project-tag`.
- Terraform: rule của WAF web ACL, certificate phụ (không phải default) của listener, SNS subscription, mixed-instances policy của Auto Scaling và capacity provider của ECS cluster chưa được map; rule WAF được giữ ngoài plan bằng `ignore_changes = [rule]`. ACM certificate dạng IMPORTED cần tự điền `certificate_body`/`private_key`.
- Phân tích dựa trên luật cố định, không dùng LLM bên trong. Phần giải thích tự do do AI Agent kết nối qua MCP đảm nhận.
- Sanitizer che theo tên key, nên một số trường vô hại có tên chứa `token`, `secret`, ... (ví dụ `ClientToken` của EC2) cũng hiện là `[REDACTED]`.
- Terraform: code Lambda là file placeholder `lambda_<name>.zip`; không lấy được mật khẩu master của RDS; S3 lifecycle/CORS/website/ACL và DynamoDB TTL/PITR chưa được map; rule security group có mô tả khác nhau theo từng dải IP được sinh ra không kèm mô tả.
- Chưa hỗ trợ thu thập lại từng resource; muốn cập nhật thì chạy lại `collect`.
