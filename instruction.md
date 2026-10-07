# AWS Resource Inventory — Hướng dẫn sử dụng đầy đủ

> Dành cho người chưa biết gì về tool này. Đọc từ đầu đến cuối, làm theo từng bước là xong.

---

## Tool này làm gì?

Bạn tiếp nhận một hệ thống AWS mà **không có IaC, không có tài liệu, không có diagram**. Tool này giải quyết đúng bài toán đó:

1. **Tự động quét toàn bộ AWS account** — tìm tất cả EC2, S3, Lambda, RDS, VPC, IAM, DynamoDB, CloudWatch, Step Functions, Security Groups.
2. **Thu thập spec chi tiết** của từng resource (cấu hình đầy đủ như AWS trả về).
3. **Lưu ra file** JSON + Markdown có tổ chức, có checksum kiểm tra toàn vẹn dữ liệu.
4. **Tạo Terraform IaC** từ infrastructure đã có sẵn (kèm `terraform import` commands).
5. **Phân tích mối quan hệ** giữa các resource, phát hiện pattern (API GW → Lambda → DynamoDB, v.v.).
6. **Phát hiện rủi ro bảo mật**: S3 bucket public, IAM policy quá rộng, Security Group mở all.
7. **MCP Server**: cho AI Agent (Claude, v.v.) truy vấn infrastructure data an toàn — không cần expose AWS credentials.

**Output cuối cùng bạn nhận được:**
```
output/
├── json/                   # Spec chi tiết từng resource (JSON)
├── markdown/               # Tài liệu đọc được (Markdown)
├── raw/                    # Raw API response để audit
├── terraform/              # File .tf + import commands
├── diagrams/               # Architecture diagram (drawio)
├── analysis/               # Phân tích activity flow + security flags
└── summary_report.json     # Báo cáo tổng hợp + time savings
```

---

## Yêu cầu trước khi bắt đầu

| Yêu cầu | Kiểm tra |
|---|---|
| Python 3.11+ | `python3 --version` |
| AWS credentials đã config | `aws sts get-caller-identity` |
| Quyền read-only trên AWS account | Xem bên dưới |

### AWS permissions cần thiết (read-only)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:Describe*",
      "s3:GetBucket*", "s3:ListAllMyBuckets",
      "lambda:List*", "lambda:Get*",
      "rds:Describe*",
      "dynamodb:ListTables", "dynamodb:DescribeTable",
      "iam:List*", "iam:Get*",
      "logs:DescribeLogGroups",
      "states:ListStateMachines", "states:DescribeStateMachine",
      "sts:GetCallerIdentity",
      "ec2:DescribeRegions"
    ],
    "Resource": "*"
  }]
}
```

---

## Cài đặt (1 lần duy nhất)

```bash
# 1. Clone hoặc vào thư mục project
cd aws-resource-iventory

# 2. Tạo virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# 3. Cài dependencies
pip install -r requirements.txt
pip install -e .

# 4. Kiểm tra cài đặt thành công
python3 -c "import src.discovery; import src.collector; import src.mcp_server; print('OK')"
```

---

## Demo: Chạy từ đầu đến cuối

### Bước 1 — Cấu hình AWS credentials

```bash
# Cách 1: Dùng AWS CLI (khuyến nghị)
aws configure
# Nhập: Access Key ID, Secret Access Key, Region (vd: ap-southeast-1), output format: json

# Cách 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-southeast-1"

# Cách 3: Assume role (cross-account)
aws sts assume-role \
  --role-arn "arn:aws:iam::ACCOUNT_ID:role/ReadOnlyRole" \
  --role-session-name "inventory-session"
# Sau đó export 3 biến AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN từ output trên

# Kiểm tra credentials hoạt động
aws sts get-caller-identity
```

### Bước 2 — Chạy demo script (tất cả trong 1)

```bash
# Kích hoạt venv nếu chưa kích hoạt
source venv/bin/activate

# Chạy toàn bộ pipeline
python3 scripts/demo.py --output-dir ./output --region ap-southeast-1
```

Nếu muốn quét nhiều region:
```bash
python3 scripts/demo.py --output-dir ./output --region ap-southeast-1 --region us-east-1
```

Nếu muốn quét ALL regions (chậm hơn, ~3-5 phút):
```bash
python3 scripts/demo.py --output-dir ./output --all-regions
```

### Bước 3 — Chạy từng bước thủ công (nếu muốn kiểm soát từng phần)

#### 3a. Discovery — tìm tất cả resources

```python
# demo_step1_discovery.py
import boto3
from src.discovery import ResourceDiscovery

session = boto3.Session(region_name="ap-southeast-1")
discovery = ResourceDiscovery(
    aws_session=session,
    regions=["ap-southeast-1"],          # bỏ dòng này để quét all regions
    max_workers=10,
    progress_callback=lambda region, done, total: print(f"  [{done}/{total}] {region}")
)

print("Đang quét AWS resources...")
resources = discovery.discover_all_resources()
print(f"\nTìm thấy {len(resources)} resources")

# In ra danh sách
for r in resources[:10]:  # xem 10 cái đầu
    print(f"  {r.resource_type:30s} {r.arn}")

errors = discovery.get_errors()
if errors:
    print(f"\n⚠ {len(errors)} lỗi (region không accessible hoặc không có quyền):")
    for e in errors:
        print(f"  {e.region} / {e.resource_type}: {e.message}")
```

```bash
python3 demo_step1_discovery.py
```

**Output mẫu:**
```
Đang quét AWS resources...
  [1/3] ap-southeast-1
  [2/3] us-east-1
  [3/3] global

Tìm thấy 47 resources
  aws_instance                   arn:aws:ec2:ap-southeast-1:123456789012:instance/i-0abc123
  aws_s3_bucket                  arn:aws:s3:::my-app-bucket
  aws_lambda_function            arn:aws:lambda:ap-southeast-1:123456789012:function:my-api
  ...
```

#### 3b. Thu thập Spec chi tiết

```python
# demo_step2_collect.py
import boto3
import json
from src.collector import SpecCollector
from src.discovery import ResourceDiscovery

session = boto3.Session(region_name="ap-southeast-1")
discovery = ResourceDiscovery(aws_session=session, regions=["ap-southeast-1"])
resources = discovery.discover_all_resources()

collector = SpecCollector(aws_session=session)

specs = []
for resource in resources:
    print(f"Thu thập spec: {resource.arn[:60]}...")
    result = collector.collect(resource)
    if result.is_ok():
        specs.append(result.unwrap())
    else:
        print(f"  ⚠ Bỏ qua: {result.unwrap_err().message}")

print(f"\nThu thập được {len(specs)} specs")
```

```bash
python3 demo_step2_collect.py
```

#### 3c. Lưu output ra file

```python
# demo_step3_output.py
import os
from src.output_generator import OutputGenerator

output_dir = "./output"
generator = OutputGenerator(output_dir=output_dir)

# specs = [...] từ bước 3b
result = generator.generate_all(
    specs=specs,
    account_id="123456789012",
    collection_metadata={"collected_at": "2024-01-15T10:00:00Z"}
)

print(f"✓ JSON files:     {output_dir}/json/")
print(f"✓ Markdown files: {output_dir}/markdown/")
print(f"✓ Raw responses:  {output_dir}/raw/")
print(f"✓ Summary report: {output_dir}/summary_report.json")
```

```bash
python3 demo_step3_output.py
```

#### 3d. Tạo Terraform IaC

```python
# demo_step4_terraform.py
from src.iac_generator import IaCGenerator

gen = IaCGenerator(output_dir="./output/terraform", spec_base_path="./output")
tf_result = gen.generate_terraform(specs=specs)

print(f"✓ Terraform files: ./output/terraform/")
print(f"  Tạo {tf_result['resource_count']} resource blocks")
print(f"  Import script:  ./output/terraform/import.sh")
print(f"  Verify script:  ./output/terraform/verify.sh")
print()
print("Để import vào Terraform state:")
print("  cd ./output/terraform && terraform init && bash import.sh")
print()
print("Để verify (0 changes = chính xác 100%):")
print("  terraform plan  # phải ra: 'No changes. Infrastructure is up-to-date.'")
```

```bash
python3 demo_step4_terraform.py
```

#### 3e. Phân tích activity flow + phát hiện rủi ro

```python
# demo_step5_analysis.py
from src.analysis_engine import AnalysisEngine

engine = AnalysisEngine()

# Phân tích toàn bộ
analysis = engine.analyze(specs=specs)

# Mối quan hệ giữa resources
print("=== RESOURCE RELATIONSHIPS ===")
for rel in analysis.relationships:
    print(f"  {rel.source} → {rel.target}  [{rel.relationship_type}]")

# Pattern phát hiện được
print("\n=== DETECTED PATTERNS ===")
for pattern in analysis.patterns:
    print(f"  {pattern.name}: {', '.join(pattern.resources)}")

# Cảnh báo bảo mật
print("\n=== SECURITY FLAGS ===")
for flag in analysis.security_flags:
    print(f"  ⚠ [{flag.severity}] {flag.resource_arn}")
    print(f"    {flag.description}")
    print(f"    Evidence: {flag.citation}")
```

```bash
python3 demo_step5_analysis.py
```

**Output mẫu:**
```
=== RESOURCE RELATIONSHIPS ===
  arn:aws:apigateway:...:api/abc  → arn:aws:lambda:...:function:my-api  [triggers]
  arn:aws:lambda:...:function:my-api  → arn:aws:dynamodb:...:table/Users  [reads/writes]

=== DETECTED PATTERNS ===
  API Gateway + Lambda + DynamoDB: my-api-gw, my-api, Users
  EC2 + Load Balancer: web-server-1, web-server-2, prod-alb

=== SECURITY FLAGS ===
  ⚠ [HIGH] arn:aws:s3:::my-old-bucket
    Bucket is publicly accessible
    Evidence: output/json/s3/my-old-bucket.json#PublicAccessBlockConfiguration

  ⚠ [MEDIUM] arn:aws:ec2:...:security-group/sg-0abc
    Security group allows unrestricted inbound (0.0.0.0/0) on port 22
    Evidence: output/json/ec2/security-groups/sg-0abc.json#IpPermissions
```

#### 3f. Dùng MCP Server cho AI Agent

```python
# demo_step6_mcp.py
from src.mcp_server import MCPServer

# MCPServer chỉ đọc từ cache local — KHÔNG gọi AWS API
mcp = MCPServer(cache_dir="./output/json")

# List resources
response = mcp.handle_request(
    operation="list-resources",
    params={"region": "ap-southeast-1", "resource_type": "lambda_function"}
)
print(f"Status: {response['status']}")
print(f"Lambda functions: {len(response['data'])} found")

# Lấy spec của 1 resource
spec_response = mcp.handle_request(
    operation="get-resource-spec",
    params={"arn": "arn:aws:lambda:ap-southeast-1:123456789012:function:my-api"}
)
import json
print(json.dumps(spec_response['data'], indent=2)[:500])
```

```bash
python3 demo_step6_mcp.py
```

---

## Xem kết quả output

Sau khi chạy xong, cấu trúc thư mục output:

```
output/
├── json/
│   ├── ap-southeast-1/
│   │   ├── ec2/
│   │   │   ├── i-0abc123.json          ← Spec đầy đủ của EC2 instance
│   │   │   └── i-0def456.json
│   │   ├── lambda/
│   │   │   └── my-api.json             ← Function config, env vars, layers, VPC
│   │   └── s3/
│   │       └── my-app-bucket.json      ← ACL, policy, encryption, versioning...
├── markdown/
│   ├── ap-southeast-1/
│   │   ├── ec2/
│   │   │   └── i-0abc123.md            ← Bảng đọc được, human-friendly
│   │   └── lambda/
│   │       └── my-api.md
├── raw/                                ← Raw AWS API responses (để audit)
├── terraform/
│   ├── ap-southeast-1/
│   │   ├── ec2.tf                      ← Terraform resource blocks
│   │   ├── lambda.tf
│   │   └── s3.tf
│   ├── import.sh                       ← Script import vào Terraform state
│   └── verify.sh                       ← Script verify 0 changes
├── analysis/
│   ├── relationships.json              ← Resource relationships
│   ├── patterns.json                   ← Detected patterns
│   └── security_flags.json            ← Security warnings với citations
└── summary_report.json                 ← Tổng kết: X resources, Y specs, Z giờ tiết kiệm
```

### Mở Markdown report

```bash
# Đọc report của một Lambda function
cat output/markdown/ap-southeast-1/lambda/my-api.md

# Đọc summary
cat output/summary_report.json | python3 -m json.tool
```

### Verify data accuracy

```bash
# Kiểm tra tất cả citations trong analysis đều có file gốc
python3 -c "
from src.output_generator import OutputGenerator
gen = OutputGenerator('./output')
result = gen.verify_citations('./output/analysis/')
if result['all_valid']:
    print('✓ Tất cả citations hợp lệ')
else:
    for mismatch in result['mismatches']:
        print(f'✗ {mismatch}')
"
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|---|---|---|
| `botocore.exceptions.NoCredentialsError` | Chưa config AWS credentials | Chạy `aws configure` |
| `botocore.exceptions.ClientError: AccessDenied` | IAM không đủ quyền | Thêm policy read-only ở phần trên |
| `ModuleNotFoundError: No module named 'src'` | Chưa cài package | Chạy `pip install -e .` |
| `ResourceDiscovery` trả về 0 resources | Region sai hoặc account rỗng | Kiểm tra `--region` và `aws ec2 describe-instances` |
| MCP Server trả về `"Run collection first"` | Chưa chạy bước thu thập | Chạy bước 3b và 3c trước |
| Terraform `plan` có changes | Spec thu thập không đầy đủ | Xem `collection_report.json` tìm failed specs |

---

## Tích hợp với AI Agent (Claude Desktop / Cursor)

Tool này có MCP Server để AI Agent đọc infrastructure data **không cần AWS credentials**:

```json
// Thêm vào Claude Desktop config (~/.claude/claude_desktop_config.json)
{
  "mcpServers": {
    "aws-inventory": {
      "command": "python3",
      "args": [
        "/path/to/aws-resource-iventory/scripts/mcp_server_run.py",
        "--cache-dir", "/path/to/output/json"
      ]
    }
  }
}
```

Sau đó trong Claude, bạn có thể hỏi:
- *"List tất cả Lambda functions trong ap-southeast-1"*
- *"Phân tích activity flow của my-api Lambda function"*
- *"Có security issue nào không?"*

---

## Chạy tests để verify

```bash
source venv/bin/activate

# Chạy toàn bộ test suite
pytest

# Chạy với coverage report
pytest --cov=src --cov-report=term-missing

# Chạy chỉ unit tests (nhanh, không cần AWS)
pytest tests/unit/ -v

# Chạy integration tests (cần AWS credentials)
pytest tests/integration/ -v
```

---

## Tóm tắt nhanh (TL;DR)

```bash
# Cài đặt
source venv/bin/activate && pip install -e .

# Config AWS
aws configure

# Chạy toàn bộ
python3 scripts/demo.py --output-dir ./output --region ap-southeast-1

# Xem kết quả
ls output/
cat output/summary_report.json
```

**Trong 5 phút bạn sẽ có:**
- Danh sách đầy đủ tất cả AWS resources
- Spec chi tiết dạng JSON + Markdown
- Terraform code để manage bằng IaC
- Phân tích mối quan hệ + cảnh báo security
- Báo cáo so sánh thời gian tự động vs thủ công
