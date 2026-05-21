# 中国行政区划数据集（xzqh）

一个**通用的、可被其他项目直接复用**的中国行政区划（省 / 地级 / 县级 / 乡级）数据集与建库工具，数据来自中华人民共和国民政部官网 <https://dmfw.mca.gov.cn>。

提供两层产物：
1. **原始 JSON 树**（`data/<version>/provinces/*.json`）—— 由抓取脚本生成。
2. **可落库 SQL / CSV**（`dist/<version>/`）—— 由生成脚本一键产出，覆盖 MySQL/MariaDB、PostgreSQL，以及通用 CSV。

---

## 快速接入（已有 `dist/Xzqh20251231/`）

如果只想用现成数据，无需运行任何抓取脚本：

### MySQL / MariaDB
```bash
mysql -u root -p mydb < dist/Xzqh20251231/mysql/schema.sql
mysql -u root -p mydb < dist/Xzqh20251231/mysql/data_full.sql
```

### PostgreSQL
```bash
psql -d mydb -f dist/Xzqh20251231/postgresql/schema.sql
psql -d mydb -f dist/Xzqh20251231/postgresql/data_full.sql
```

### CSV（更快，适合大批量加载）
- MySQL： `LOAD DATA LOCAL INFILE` 加载 `dist/Xzqh20251231/csv/region.csv`
- PostgreSQL： `\copy region FROM 'csv/region.csv' WITH (FORMAT csv, HEADER true, NULL '')`

详细命令与示例查询见 [`dist/Xzqh20251231/README.md`](dist/Xzqh20251231/README.md)。

---

## 表结构

单表 `region`，自引用 + 多版本共存：

| 列 | 类型 | 说明 |
|---|---|---|
| `id` | BIGINT | 自增主键 |
| `version` | VARCHAR(32) | 数据版本（如 `Xzqh20251231`） |
| `code` | VARCHAR(12) | 行政区划代码（2/4/6/9 位数字，台湾省占位为 `资料暂缺`） |
| `name` | VARCHAR(64) | 行政区划名称 |
| `level` | TINYINT/SMALLINT | 1=省 2=地级 3=县级 4=乡级 |
| `type` | VARCHAR(32) | 省 / 直辖市 / 地级市 / 市辖区 / 街道 等 |
| `parent_code` | VARCHAR(12) NULL | 父级代码，顶层为 NULL |
| `sort_order` | INT | 同级内顺序 |

约束：
- `UNIQUE (version, code)` —— 同一版本下 code 唯一，跨版本可重复
- `FOREIGN KEY (version, parent_code) REFERENCES region (version, code) ON DELETE CASCADE ON UPDATE CASCADE` —— 父级被删/改时自动级联

---

## 项目结构

```
xzqh/
├── data/                            原始 JSON 数据（按版本组织）
│   └── Xzqh20251231/
│       ├── province_index.json      省份索引
│       ├── provinces/*.json         34 省/直辖市的级联 JSON 树
│       └── Xzqh20251231_行政区划代码汇总.xlsx
├── dist/                            生成的可落库产物（按版本组织）
│   └── Xzqh20251231/
│       ├── mysql/{schema,data_full,data_upsert}.sql
│       ├── postgresql/{schema,data_full,data_upsert}.sql
│       ├── csv/region.csv
│       └── README.md
└── tools/
    ├── fetch_xzqh.py                从民政部官网抓取最新数据
    └── generate_sql.py              JSON → SQL/CSV 生成器
```

---

## 版本数据更新（后期升版本）

整个流程两步：抓取 → 生成。

### 1. 抓取最新版本
```bash
python tools/fetch_xzqh.py
```
脚本会自动从民政部 `XzqhVersionPublish.html` 解析最新发布版本号（例如 `Xzqh20260630`），并写入 `data/<新版本>/`。

常用参数：
- `--reuse`：复用已有省份 JSON，断点续跑
- `--no-townships`：跳过乡级抓取（更快，但只保留 1~3 级）
- `--workers N --county-sleep 0.3`：调节县级并发与节流

### 2. 生成 SQL / CSV
```bash
python tools/generate_sql.py
```
默认读取 `data/` 下**字典序最新**的版本目录，输出到 `dist/<版本>/`。可选：
- `--version Xzqh20260630`：指定版本
- `--dialect mysql` / `--dialect postgresql`：只产某一种方言（可重复）
- `--batch-size 1000`：调节 INSERT VALUES 单批行数
- `--no-csv`：跳过 CSV

### 3. 落库（三种策略任选）

| 策略 | 文件 | 适合场景 |
|---|---|---|
| **全量替换** | `data_full.sql` | 同一版本号需重导；先 `DELETE WHERE version=...` 再 `INSERT` |
| **幂等 UPSERT** | `data_upsert.sql` | 反复跑而不丢历史；按 `(version, code)` 冲突自动 UPDATE |
| **多版本共存** | 不需要额外脚本 | 直接把新版本数据 `data_full.sql` 灌进去，老版本仍在表里；应用 `WHERE version = ?` 切版本 |

> 在生产库切版本：先以新版本号 `data_full.sql` 灌入，应用切换 `version`，确认无误后 `DELETE FROM region WHERE version='<旧版本>'`，FK CASCADE 会带走旧版本所有子级。

---

## 示例查询

```sql
-- 最新版本号
SELECT MAX(version) FROM region;

-- 某省下的地级市
SELECT code, name FROM region
 WHERE version = 'Xzqh20251231' AND parent_code = '43' AND level = 2
 ORDER BY sort_order, code;

-- 省 → 市 → 县 三级展开（湖南）
SELECT p.name AS province, c.name AS city, d.name AS county
  FROM region p
  JOIN region c ON c.version = p.version AND c.parent_code = p.code
  JOIN region d ON d.version = p.version AND d.parent_code = c.code
 WHERE p.version = 'Xzqh20251231' AND p.code = '43'
 ORDER BY c.code, d.code;

-- 反查：从乡镇 code 一路回到省（递归 CTE）
WITH RECURSIVE chain AS (
  SELECT * FROM region WHERE version='Xzqh20251231' AND code='430102001'
  UNION ALL
  SELECT r.* FROM region r
    JOIN chain c ON r.version = c.version AND r.code = c.parent_code
)
SELECT level, code, name FROM chain ORDER BY level;
```

---

## 已知数据特性

- **台湾省**：上游官网未提供详细数据，本数据集保留为一行 `code='资料暂缺'`, `level=2`, `parent_code=NULL`，应用层按需过滤或单独处理。
- **新疆生产建设兵团**：部分团场 `type` 字段为「团」「农场」，并以 `65xxxx` 为父级挂在新疆维吾尔自治区下。
- **直辖市/特别行政区**：北京/天津/上海/重庆/香港/澳门没有 level=2 的地级，省下直接挂区/县。

## 数据来源与许可

数据来自中华人民共和国民政部公开发布页面（`https://dmfw.mca.gov.cn/XzqhVersionPublish.html`）。本仓库的脚本与衍生 SQL/CSV 仅做格式转换与索引化，请按原始页面公示的版权与使用规定自行评估合规性。
