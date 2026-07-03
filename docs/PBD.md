# PBD: DrawPPT MCP Server - 边界文档

## 1. 系统边界

### 1.1 系统定位
DrawPPT MCP Server 是一个**纯服务端**应用，通过 MCP 协议对外提供工具接口，不包含任何 UI 界面。

```
┌─────────────────┐     MCP Protocol     ┌─────────────────┐
│   AI Agent      │ ◄──────────────────► │  DrawPPT MCP    │
│ (Claude/Cursor) │                      │    Server       │
└─────────────────┘                      └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  python-pptx    │
                                         │  (PPTX 文件)    │
                                         └─────────────────┘
```

### 1.2 核心边界

| 边界内（In Scope） | 边界外（Out of Scope） |
|-------------------|----------------------|
| PPTX 文件创建/编辑/导出 | PPT 文件解析/读取 |
| 单页/多页管理 | PPT 动画效果 |
| 基础形状支持 | 复杂图表（柱状图、饼图） |
| 文本/图片/形状元素 | 表格元素 |
| 纯色/渐变/图片背景 | 母版/模板系统 |
| JSON/PNG 预览 | 实时协作 |
| 元素层级管理 | 撤销/重做（v0.3） |

---

## 2. 数据边界

### 2.1 输入数据

| 数据类型 | 来源 | 格式 | 约束 |
|---------|------|------|------|
| 文本内容 | AI Agent | string | 支持 \n 多段落 |
| 图片文件 | 本地文件系统 | PNG/JPG/GIF | 必须是本地可访问路径 |
| 坐标参数 | AI Agent | int (px) | 0 ≤ x ≤ 1920, 0 ≤ y ≤ 1080 |
| 颜色值 | AI Agent | string | 格式：#RRGGBB 或 #RRGGBBAA |

### 2.2 输出数据

| 数据类型 | 格式 | 返回方式 |
|---------|------|---------|
| JSON 预览 | JSON 对象 | 直接返回到 Agent 上下文 |
| PNG 预览 | 文件路径 | 返回文件路径，Agent 可读取 |
| PPTX 文件 | 文件路径 | 返回文件路径 |

### 2.3 数据不持久化
- Session 数据仅存在于内存中
- 导出的 PPTX/PNG 文件持久化到磁盘
- 服务重启后 Session 丢失（可通过重新导出恢复）

---

## 3. 接口边界

### 3.1 MCP 工具清单

#### 会话管理
```
create_session() → session_id
delete_session(session_id)
```

#### 页面操作
```
add_slide(session_id, background?) → slide_index
insert_slide(session_id, index, background?)
delete_slide(session_id, index)
```

#### 元素操作
```
add_textbox(session_id, slide_index, x, y, w, h, text, options?) → element_id
add_image(session_id, slide_index, x, y, w, h, image_path) → element_id
add_shape(session_id, slide_index, x, y, w, h, shape_type, options?) → element_id

update_textbox(session_id, element_id, options?)
update_image(session_id, element_id, options?)
update_shape(session_id, element_id, options?)

delete_element(session_id, element_id)
```

#### 背景设置
```
set_background(session_id, slide_index, bg_type, options?)
```

#### 层级操作
```
bring_to_front(session_id, element_id)
send_to_back(session_id, element_id)
bring_forward(session_id, element_id)
send_backward(session_id, element_id)
```

#### 预览 & 导出
```
preview_slides(session_id, format?, slide_index?) → json | [file_path]
export_pptx(session_id, output_path) → file_path
```

### 3.2 错误处理边界

| 错误类型 | 处理方式 | 是否阻断 |
|---------|---------|---------|
| session_id 不存在 | 返回错误信息 | 是 |
| element_id 不存在 | 返回错误信息 | 是 |
| slide_index 越界 | 返回错误信息 | 是 |
| 图片路径不存在 | 返回错误信息，不插入元素 | 是 |
| 坐标越界（超出 1920×1080） | 警告，继续执行 | 否 |
| 字体不存在 | 使用默认字体，警告 | 否 |
| 导出路径无权限 | 返回错误信息 | 是 |

---

## 4. 依赖边界

### 4.1 外部依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| python-pptx | ≥ 0.6.21 | PPTX 文件操作 |
| Pillow | ≥ 9.0 | PNG 预览生成 |
| mcp | ≥ 1.0 | MCP 协议实现 |

### 4.2 系统依赖
- Python 3.9+
- 操作系统：Windows/Linux/macOS

### 4.3 无依赖
- 不依赖数据库
- 不依赖外部 API
- 不依赖网络（除了 MCP 通信）

---

## 5. 安全边界

### 5.1 文件访问
- **读取**：仅允许读取本地文件系统中的图片文件
- **写入**：仅允许写入到当前工作目录
- **禁止**：不允许访问网络资源、不允许读取 PPTX 文件

### 5.2 资源限制
- 单个 Session 内存占用：< 100MB
- 单个 PPT 文件大小：< 50MB
- 并发 Session 数：建议 ≤ 10

### 5.3 输入验证
- 所有字符串参数进行转义处理
- 文件路径进行规范化处理，防止路径遍历
- 坐标参数限制在合理范围内

---

## 6. 性能边界

### 6.1 响应时间

| 操作 | 预期响应时间 |
|------|------------|
| create_session | < 100ms |
| add_textbox/image/shape | < 50ms |
| preview_slides (JSON) | < 200ms |
| preview_slides (PNG) | < 5s/页 |
| export_pptx | < 2s |

### 6.2 容量限制

| 指标 | 建议上限 |
|------|---------|
| 单页元素数 | 100 |
| 单 PPT 页数 | 50 |
| 单元素文本长度 | 10,000 字符 |
| 图片文件大小 | 10MB |

---

## 7. 演进边界

### 7.1 可扩展点
- 新增形状类型：在形状工厂中注册即可
- 新增元素类型：实现新的 add_xxx/update_xxx 工具
- 新增预览格式：扩展 preview_slides 的 format 参数

### 7.2 不可变部分
- 坐标体系（1920×1080 像素）一旦确定不可更改
- Session 生命周期模型（创建→编辑→导出→销毁）
- MCP 协议接口规范

### 7.3 未来探索
- PPT 动画效果（需要深入研究 python-pptx 动画 API）
- 表格元素（需要新的数据结构）
- 母版/模板系统（需要架构调整）
