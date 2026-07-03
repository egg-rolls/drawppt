# PRD: DrawPPT MCP Server

## 1. 项目概述

### 1.1 项目名称
DrawPPT MCP Server

### 1.2 项目目标
构建一个 MCP 服务器，让 AI Agent（如 Claude、Cursor）能够通过"画笔"方式直接创建、编辑、预览和导出 PPTX 文件，无需 HTML 中间态，实现零损耗的幻灯片生成。

### 1.3 核心价值
- **零损耗**：直接操作 python-pptx 对象，像素级精确控制
- **语义清晰**：每个工具职责单一，AI Agent 易于理解和调用
- **可视化反馈**：支持 PNG 预览，非视觉模型也能校验布局效果
- **完整生命周期**：支持创建、编辑、预览、导出全流程

---

## 2. 目标用户

### 2.1 主要用户
- AI Agent（Claude、Cursor、GPT-4 等）
- 通过 MCP 协议调用工具的 AI 应用

### 2.2 典型使用场景
1. **自动生成 PPT**：用户提供内容大纲，AI 自动生成完整演示文稿
2. **图片排版**：结合 TakeApart 等工具，将解析出的元素重新排版到 PPT
3. **模板填充**：基于预设布局，动态填充文字和图片
4. **迭代优化**：AI 预览后发现问题，自动调整布局

---

## 3. 功能需求

### 3.1 会话管理（Session）

| 功能 | 描述 | 优先级 |
|------|------|--------|
| create_session | 创建新的 PPTX 会话 | P0 |
| delete_session | 删除会话及临时文件 | P1 |

**约束**：
- 一个 session 对应一个 PPTX 文件（可包含多页）
- 设计稿基准分辨率：1920×1080（16:9）
- 坐标单位：像素（px）

### 3.2 页面操作（Slide）

| 功能 | 描述 | 优先级 |
|------|------|--------|
| add_slide | 追加空白页 | P0 |
| insert_slide | 在指定位置插入页面 | P1 |
| delete_slide | 删除指定页面 | P1 |

### 3.3 元素操作（Element）

#### 3.3.1 文本框（Textbox）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| x, y | int | ✓ | 左上角坐标（px） |
| w, h | int | ✓ | 宽高（px） |
| text | string | ✓ | 文本内容（支持多段落，用 \n 分隔） |
| font_size | int | 否 | 字号（默认 18） |
| font_family | string | 否 | 字体（默认 "微软雅黑"） |
| color | string | 否 | 颜色，如 "#333333"（默认黑色） |
| bold | bool | 否 | 是否加粗（默认 false） |
| italic | bool | 否 | 是否斜体（默认 false） |
| align | string | 否 | 对齐：left/center/right（默认 left） |
| line_spacing | float | 否 | 行间距倍数（默认 1.0） |
| paragraph_spacing | int | 否 | 段间距（px，默认 0） |

**操作**：
- add_textbox：创建文本框
- update_textbox：修改文本框属性

#### 3.3.2 图片（Image）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| x, y | int | ✓ | 左上角坐标（px） |
| w, h | int | ✓ | 宽高（px） |
| image_path | string | ✓ | 图片文件路径（本地绝对路径） |

**操作**：
- add_image：插入图片
- update_image：修改图片位置/尺寸

#### 3.3.3 形状（Shape）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| x, y | int | ✓ | 左上角坐标（px） |
| w, h | int | ✓ | 宽高（px） |
| shape_type | string | ✓ | 形状类型 |
| fill_color | string | 否 | 填充颜色 |
| border_color | string | 否 | 边框颜色 |
| border_width | int | 否 | 边框宽度（px） |
| border_radius | int | 否 | 圆角半径（px，仅圆角矩形） |

**支持的形状类型**：
- `rectangle`：矩形
- `rounded_rectangle`：圆角矩形
- `oval`：椭圆/圆形
- `triangle`：三角形
- `arrow_right`：右箭头
- `arrow_up`：上箭头
- `star`：五角星
- `hexagon`：六边形

**操作**：
- add_shape：创建形状
- update_shape：修改形状属性

### 3.4 背景设置

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| slide_index | int | ✓ | 页面索引（从 0 开始） |
| bg_type | string | ✓ | 类型：solid/gradient/image |
| color | string | 条件 | 纯色背景时必填 |
| gradient_start | string | 条件 | 渐变起始色 |
| gradient_end | string | 条件 | 渐变结束色 |
| gradient_direction | string | 条件 | 渐变方向：horizontal/vertical |
| image_path | string | 条件 | 图片背景路径 |

### 3.5 元素层级

| 功能 | 描述 | 优先级 |
|------|------|--------|
| bring_to_front | 置于顶层 | P1 |
| send_to_back | 置于底层 | P1 |
| bring_forward | 上移一层 | P1 |
| send_backward | 下移一层 | P1 |

**默认行为**：按添加顺序自然叠放（后添加的在上层）

### 3.6 预览功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| preview_slides | 预览当前草稿 | P0 |

**预览模式**：
- `json`：返回元素列表、坐标、尺寸等结构化数据
- `png`：导出为图片文件，返回文件路径

**JSON 输出格式**：
```json
{
  "session_id": "xxx",
  "slide_count": 3,
  "slides": [
    {
      "index": 0,
      "background": { "type": "solid", "color": "#FFFFFF" },
      "elements": [
        {
          "id": "elem_001",
          "type": "textbox",
          "x": 100, "y": 100, "w": 300, "h": 50,
          "content": "标题",
          "font_size": 24,
          "bold": true
        }
      ]
    }
  ]
}
```

**PNG 输出**：
- 每页生成一张 PNG 图片
- 分辨率：1920×1080
- 返回文件路径列表

### 3.7 导出功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| export_pptx | 导出为 PPTX 文件 | P0 |

**参数**：
- `session_id`：会话 ID
- `output_path`：输出文件名（相对工作目录）

**行为**：
- 导出到当前工作目录
- 返回完整文件路径

---

## 4. 非功能需求

### 4.1 性能
- 单页元素数量：建议 ≤ 100
- 单个 PPT 页数：建议 ≤ 50 页
- PNG 预览生成时间：< 5 秒/页

### 4.2 兼容性
- Python 3.9+
- 依赖：python-pptx, Pillow, MCP Python SDK

### 4.3 可靠性
- 元素 ID 自动生成，保证唯一性
- 坐标越界时给出警告，不阻断执行
- 图片路径不存在时报错，不插入损坏元素

---

## 5. 版本规划

### v0.1（MVP）✅ 已完成
- [x] create_session / delete_session
- [x] add_slide
- [x] add_textbox / add_image / add_shape
- [x] set_background（纯色、渐变）
- [x] preview_slides（JSON 模式）
- [x] export_pptx

### v0.2 ✅ 已完成
- [x] update_textbox / update_image / update_shape
- [x] delete_element
- [x] insert_slide / delete_slide
- [x] 元素层级操作（bring_to_front / send_to_back / bring_forward / send_backward）
- [x] set_background（渐变、图片）
- [ ] preview_slides（PNG 模式）—— 暂不实现

### v0.3
- [ ] 撤销/重做
- [ ] 批量操作
- [ ] 模板支持
- [ ] 动画效果（探索）
