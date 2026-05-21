# 行政区划数据 - `Xzqh20251231`

本目录由 `tools/generate_sql.py` 生成，包含可直接接入其他项目的行政区划资源。

## 数据概览
| 指标 | 数量 |
|------|------|
| 总记录数 | 42131 |
| 省级 (level=1) | 33 |
| 地级 (level=2) | 334 |
| 县级 (level=3) | 2845 |
| 乡级 (level=4) | 38919 |

## 目录结构
```
Xzqh20251231/
├── mysql/
│   ├── schema.sql        建表
│   ├── data_full.sql     全量替换（DELETE WHERE version=… 后 INSERT）
│   └── data_upsert.sql   幂等 UPSERT（按 (version, code) 冲突更新）
├── postgresql/
│   ├── schema.sql
│   ├── data_full.sql
│   └── data_upsert.sql
├── csv/
│   └── region.csv
└── README.md
```

## 表结构 `region`
| 列 | 类型 | 说明 |
|----|------|------|
| id | BIGINT | 自增主键 |
| version | VARCHAR(32) | 数据版本（如 `Xzqh20251231`），支持多版本共存 |
| code | VARCHAR(12) | 行政区划代码 |
| name | VARCHAR(64) | 行政区划名称 |
| level | TINYINT/SMALLINT | 1省 2地级 3县级 4乡级 |
| type | VARCHAR(32) | 省/直辖市/地级市/市辖区/街道 等 |
| parent_code | VARCHAR(12) | 父级代码（顶层为 NULL） |
| sort_order | INT | 同级内顺序 |

约束：
- `UNIQUE (version, code)`
- `FOREIGN KEY (version, parent_code) REFERENCES region(version, code) ON DELETE CASCADE ON UPDATE CASCADE`

## 接入方式

### MySQL / MariaDB
```bash
mysql -uroot -p mydb < mysql/schema.sql
mysql -uroot -p mydb < mysql/data_full.sql     # 或 mysql/data_upsert.sql
```

### PostgreSQL
```bash
psql -d mydb -f postgresql/schema.sql
psql -d mydb -f postgresql/data_full.sql       # 或 postgresql/data_upsert.sql
```

### 通过 CSV 加载（更快）
MySQL：
```sql
LOAD DATA LOCAL INFILE 'csv/region.csv' INTO TABLE region
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n' IGNORE 1 LINES
  (version, code, name, level, type, @parent, sort_order)
  SET parent_code = NULLIF(@parent, '');
```

PostgreSQL：
```sql
\copy region(version, code, name, level, type, parent_code, sort_order)
  FROM 'csv/region.csv' WITH (FORMAT csv, HEADER true, NULL '');
```

## 版本更新
1. 重新运行 `tools/fetch_xzqh.py` 抓取最新版本。
2. 运行 `python tools/generate_sql.py --version <新版本>` 生成对应 `dist/<新版本>/`。
3. 选择导入方式：
   - **替换当前版本**：`data_full.sql` 会先删本版本数据再插入。
   - **幂等同步**：`data_upsert.sql` 可重复执行而不丢历史。
   - **多版本并存**：`version` 列已就绪，应用查询时 `WHERE version = ?` 即可。

## 示例查询

最新版本：
```sql
SELECT MAX(version) FROM region;
```

某省下的地级市：
```sql
SELECT code, name FROM region
WHERE version = 'Xzqh20251231' AND parent_code = '43' AND level = 2
ORDER BY sort_order, code;
```

省 → 市 → 县 三级展开（湖南）：
```sql
SELECT p.name AS province, c.name AS city, d.name AS county
FROM region p
JOIN region c ON c.version = p.version AND c.parent_code = p.code
JOIN region d ON d.version = p.version AND d.parent_code = c.code
WHERE p.version = 'Xzqh20251231' AND p.code = '43'
ORDER BY c.code, d.code;
```

向上回溯（已知乡镇代码反查省/市/县/乡）：
```sql
WITH RECURSIVE chain AS (
  SELECT * FROM region WHERE version = 'Xzqh20251231' AND code = '430102001'
  UNION ALL
  SELECT r.* FROM region r
    JOIN chain c ON r.version = c.version AND r.code = c.parent_code
)
SELECT level, code, name FROM chain ORDER BY level;
```

> 数据源：中华人民共和国民政部 <https://dmfw.mca.gov.cn/XzqhVersionPublish.html>
