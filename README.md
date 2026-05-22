# 中国行政区划数据集（xzqh）

[![build-app](https://github.com/Goo-git/xzqh/actions/workflows/build-app.yml/badge.svg)](https://github.com/Goo-git/xzqh/actions/workflows/build-app.yml)

一个**通用的、可被其他项目直接复用**的中国行政区划（省 / 地级 / 县级 / 乡级）数据集与建库工具，数据来自中华人民共和国民政部官网 <https://dmfw.mca.gov.cn>。

提供三种使用方式：
1. **桌面 GUI**（`app/`）—— PySide6 写的可执行窗口程序，覆盖抓取 / 生成 / 浏览，免命令行。
2. **CLI 脚本**（`tools/`）—— `fetch_xzqh.py`、`generate_sql.py`，适合自动化/CI 场景。
3. **现成产物**（`dist/<version>/`）—— SQL/CSV，可直接灌库无需 Python。

提供两层数据：
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
├── app/                             PySide6 桌面 GUI
│   ├── __main__.py                  入口（python -m app）
│   ├── main_window.py               主窗 + 三个 Tab
│   ├── paths.py                     兼容 PyInstaller 冻结后的路径解析
│   ├── tabs/                        FetchTab / GenerateTab / BrowseTab
│   ├── workers/                     QThread 包装 CLI 的 run(args, on_log)
│   └── widgets/log_view.py          日志 + 进度条组合
├── tools/
│   ├── fetch_xzqh.py                从民政部官网抓取最新数据（CLI + run() 库函数）
│   └── generate_sql.py              JSON → SQL/CSV 生成器（CLI + run() 库函数）
├── packaging/
│   └── xzqh-gui.spec                PyInstaller 配置
├── .github/workflows/
│   └── build-app.yml                push tag v* / release/** 触发，Windows 自动打包
└── requirements{,-dev}.txt
```

---

## 桌面 GUI

### 从源码运行
```bash
pip install -r requirements.txt
python -m app
```

三个 Tab：
- **抓取数据** — 表单设置 `--workers / --county-sleep / --no-townships / --reuse` 等参数，进度条显示当前省份，日志实时刷新；支持协作式取消（在省份完成后停止）。
- **生成 SQL/CSV** — 下拉选版本与方言，点「生成」即可，完成后可一键打开输出目录。
- **数据预览** — 树状浏览省 / 地 / 县 / 乡，展开县级时懒加载乡级，避免一次塞 38k+ 节点；支持按名称或 code 过滤。

### 编译与独立打包 (Compilation & Packaging)

项目提供了方便的本地打包脚本与 CI 自动化流水线，可将 Python 源码直接编译打包为**无 Python 运行环境依赖、双击即用**的单体客户端可执行文件。

#### 1. 准备工作 (Prerequisites)

首先，需要确保安装了开发与打包所需的全部依赖（包括 `pyinstaller` 与 `Pillow` 图标生成库）：
```bash
# 安装基础运行依赖
pip install -r requirements.txt

# 安装开发与打包专用依赖
pip install -r requirements-dev.txt
```

#### 2. 生成程序图标 (Icon Generation)
程序图标位于 `assets/` 目录中。在打包前，必须确保这些图标已被正确生成。您可以通过以下幂等命令随时重新生成程序图标（含 Windows 所需的多尺寸 ICO 和主窗口 PNG 图标）：
```bash
python tools/make_icons.py
```
> [!NOTE]
> - `make_icons.py` 依赖 `Pillow` 库，会自动读取配置的渐变色和几何结构并生成 `assets/icon.png` 与 `assets/icon.ico`。
> - macOS 所需的 `.icns` 格式图标，在本地无需额外关注。CI 端会在 macOS 环境下通过系统原生的 `iconutil` 命令从高清 PNG 现场转换产出。

#### 3. 本地编译打包 (Local Packaging)
使用 PyInstaller 配合项目已配置好的 `.spec` 描述文件进行一键封装：
```bash
pyinstaller packaging/xzqh-gui.spec --noconfirm
```

**编译配置说明 (`packaging/xzqh-gui.spec`):**
- **打包模式**: 单文件模式 (`onefile`)，将 Python 解析器、动态链接库和 `assets/icon.png` 资源包全部打入单体 EXE。
- **无命令行窗口**: 已设定 `console=False`，双击启动时纯窗口化运行，不会弹出黑色的 CMD 命令行窗口。
- **代码修剪**: 自动排除 `tkinter` 等无关依赖，缩减包体体积。

**编译产物路径:**
- **Windows**: `dist/xzqh-gui.exe` (单文件可执行程序，双击即用，约 46MB)
- **macOS**: `dist/xzqh-gui.app` (标准应用安装包，支持直接拖拽至「应用程序」文件夹)

#### 4. GitHub Actions CI 自动构建 (CI/CD Automated Build)
项目配置了完善的 GitHub Actions 流水线，可在 CI 云端全自动跨平台构建。
- **流水线配置文件**: `.github/workflows/build-app.yml`
- **触发条件**:
  - 推送形如 `v*` 的版本标签（例如 `git push origin v1.0`）
  - 推送或合并至 `release/**` 分支
  - 亦可在 GitHub Action 界面手动点击 `workflow_dispatch` 触发。
- **流水线逻辑**:
  - 分别启动 `windows-latest` 和 `macos-latest` 两路矩阵节点。
  - 在 macOS runner 上自动调用 `iconutil` 将高清 icon 转换为 `.icns`。
  - 生成 `xzqh-gui-windows.exe` 和 `xzqh-gui-macos.app.zip` 产物（云端保留 30天）。
  - 若为 `v*` 标签触发，则会自动创建相应的 **GitHub Release** 并挂载这两份打包产物，同时利用 commit logs 自动生成发布日志。

#### 5. 常见打包与运行问题 (Troubleshooting)

> [!WARNING]
> **Windows SmartScreen 阻止运行 (未签名误报)**
> 由于打包生成的 `.exe` 文件没有购买商业数字证书签名，Windows Defender 或 SmartScreen 可能会在初次运行时提示“未知的发布者”。这属于 PyInstaller 封装程序的正常现象。
> **解决方法**: 点击提示弹窗中的“更多信息”，然后点击“仍要运行”即可；或者手动将文件加入安全白名单。

> [!IMPORTANT]
> **macOS “无法打开，因为无法验证开发者” (Gatekeeper)**
> 在 macOS 首次双击打开 `.app` 时，系统可能会因为未签名拒绝打开。
> **解决方法**: 
> 1. 打开系统的“系统设置 -> 隐私与安全性”，找到底部提示并点击“仍要打开”；
> 2. 或者在终端运行以下命令，解除 Gatekeeper 对该应用的限制：
>    ```bash
>    xattr -d com.apple.quarantine /path/to/xzqh-gui.app
>    ```

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

- **台湾省**：上游官网仅以 `code='资料暂缺'`、`level=2` 的占位提供，生成器会**自动跳过** code 非数字的节点（含整棵子树），因此数据集中**不含台湾省**。若业务需要展示，请在应用层补一行 `(code='71', name='台湾省', level=1, parent_code=NULL)` 之类的桩数据。
- **新疆生产建设兵团**：部分团场 `type` 字段为「团」「农场」，并以 `65xxxx` 为父级挂在新疆维吾尔自治区下。
- **直辖市/特别行政区**：北京/天津/上海/重庆/香港/澳门没有 level=2 的地级，省下直接挂区/县。

## 数据来源与许可

数据来自中华人民共和国民政部公开发布页面（`https://dmfw.mca.gov.cn/XzqhVersionPublish.html`）。本仓库的脚本与衍生 SQL/CSV 仅做格式转换与索引化，请按原始页面公示的版权与使用规定自行评估合规性。
