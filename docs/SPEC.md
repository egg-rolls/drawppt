# SPEC: DrawPPT MCP Server - 技术规格文档

## 1. 系统架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Protocol Layer                     │
│  (JSON-RPC over stdio/SSE)                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Tool Router                             │
│  (dispatch to appropriate handler)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Session Manager                           │
│  (create/delete sessions, maintain state)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Slide Manager │ │Element Manager│ │  Renderer     │
│ (add/delete/  │ │ (CRUD for     │ │ (PNG preview) │
│  reorder)     │ │  elements)    │ │               │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                ┌───────────────────┐
                │   python-pptx     │
                │   (PPTX Model)    │
                └───────────────────┘
```

### 1.2 目录结构
```
drawppt/
├── src/
│   └── drawppt/
│       ├── __init__.py
│       ├── server.py           # MCP 服务器入口
│       ├── session.py          # Session 管理
│       ├── slide.py            # 页面操作
│       ├── elements/
│       │   ├── __init__.py
│       │   ├── base.py         # 元素基类
│       │   ├── textbox.py      # 文本框
│       │   ├── image.py        # 图片
│       │   └── shape.py        # 形状
│       ├── background.py       # 背景设置
│       ├── renderer.py         # PNG 预览渲染
│       └── utils/
│           ├── __init__.py
│           ├── coordinate.py   # 坐标转换
│           ├── color.py        # 颜色解析
│           └── validators.py   # 输入验证
├── tests/
│   ├── test_session.py
│   ├── test_elements.py
│   └── test_renderer.py
├── docs/
│   ├── PRD.md
│   ├── PBD.md
│   └── SPEC.md
├── pyproject.toml
└── README.md
```

---

## 2. 核心数据结构

### 2.1 Session
```python
@dataclass
class Session:
    session_id: str
    width: int = 1920
    height: int = 1080
    slides: List[Slide]
    created_at: datetime
```

### 2.2 Slide
```python
@dataclass
class Slide:
    index: int
    background: Background
    elements: List[Element]
```

### 2.3 Element 基类
```python
@dataclass
class Element:
    element_id: str
    element_type: str  # 'textbox' | 'image' | 'shape'
    x: int
    y: int
    w: int
    h: int
    z_order: int  # 层级，数值越大越靠前
```

### 2.4 Textbox
```python
@dataclass
class Textbox(Element):
    text: str
    font_size: int = 18
    font_family: str = "微软雅黑"
    color: str = "#000000"
    bold: bool = False
    italic: bool = False
    align: str = "left"  # 'left' | 'center' | 'right'
    line_spacing: float = 1.0
    paragraph_spacing: int = 0
```

### 2.5 Image
```python
@dataclass
class Image(Element):
    image_path: str
```

### 2.6 Shape
```python
@dataclass
class Shape(Element):
    shape_type: str  # 'rectangle' | 'rounded_rectangle' | 'oval' | ...
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: int = 0
    border_radius: int = 0  # 仅圆角矩形
```

### 2.7 Background
```python
@dataclass
class Background:
    bg_type: str  # 'solid' | 'gradient' | 'image' | 'none'
    color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    gradient_direction: str = 'vertical'
    image_path: Optional[str] = None
```

---

## 3. 坐标系统

### 3.1 设计稿坐标系
- 原点：左上角 (0, 0)
- X 轴：向右为正，范围 [0, 1920]
- Y 轴：向下为正，范围 [0, 1080]
- 单位：像素（px）

### 3.2 python-pptx 坐标系
- 原点：左上角
- 单位：EMU（English Metric Units）
- 1 inch = 914400 EMU
- 1 cm = 360000 EMU

### 3.3 转换公式
```python
# 设计稿像素 → EMU
# 假设 1 inch = 96 px（标准 DPI）
EMU_PER_INCH = 914400
PX_PER_INCH = 96

def px_to_emu(px: int) -> int:
    return int(px * EMU_PER_INCH / PX_PER_INCH)

# 幻灯片尺寸
SLIDE_WIDTH_EMU = px_to_emu(1920)   # = 18288000 EMU
SLIDE_HEIGHT_EMU = px_to_emu(1080)  # = 10287000 EMU
```

---

## 4. 形状映射

### 4.1 python-pptx 形状类型
```python
from pptx.enum.shapes import MSO_SHAPE

SHAPE_MAP = {
    'rectangle': MSO_SHAPE.RECTANGLE,
    'rounded_rectangle': MSO_SHAPE.ROUNDED_RECTANGLE,
    'oval': MSO_SHAPE.OVAL,
    'triangle': MSO_SHAPE.ISOSCELES_TRIANGLE,
    'arrow_right': MSO_SHAPE.RIGHT_ARROW,
    'arrow_up': MSO_SHAPE.UP_ARROW,
    'star': MSO_SHAPE.STAR_5_POINT,
    'hexagon': MSO_SHAPE.HEXAGON,
}
```

---

## 5. 颜色处理

### 5.1 颜色格式
- 输入：`#RRGGBB` 或 `#RRGGBBAA`
- 内部存储：`#RRGGBB`
- python-pptx 使用：`RGBColor(r, g, b)`

### 5.2 转换函数
```python
def hex_to_rgb(hex_color: str) -> RGBColor:
    """将 #RRGGBB 转换为 RGBColor"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return RGBColor(r, g, b)
```

---

## 6. 工具实现规格

### 6.1 create_session
```python
async def create_session() -> dict:
    """
    创建新的 PPTX 会话
    
    Returns:
        {
            "session_id": "sess_xxxxxxxx",
            "width": 1920,
            "height": 1080,
            "slide_count": 0
        }
    """
```

### 6.2 add_slide
```python
async def add_slide(
    session_id: str,
    background: Optional[dict] = None
) -> dict:
    """
    追加新页面
    
    Args:
        background: 可选背景配置
            {
                "bg_type": "solid",
                "color": "#FFFFFF"
            }
    
    Returns:
        {
            "slide_index": 0,
            "total_slides": 1
        }
    """
```

### 6.3 add_textbox
```python
async def add_textbox(
    session_id: str,
    slide_index: int,
    x: int, y: int, w: int, h: int,
    text: str,
    font_size: int = 18,
    font_family: str = "微软雅黑",
    color: str = "#000000",
    bold: bool = False,
    italic: bool = False,
    align: str = "left",
    line_spacing: float = 1.0,
    paragraph_spacing: int = 0
) -> dict:
    """
    添加文本框
    
    Returns:
        {
            "element_id": "elem_xxxxxxxx",
            "slide_index": 0,
            "position": {"x": 100, "y": 100, "w": 300, "h": 50}
        }
    """
```

### 6.4 add_image
```python
async def add_image(
    session_id: str,
    slide_index: int,
    x: int, y: int, w: int, h: int,
    image_path: str
) -> dict:
    """
    插入图片
    
    Returns:
        {
            "element_id": "elem_xxxxxxxx",
            "slide_index": 0,
            "position": {"x": 100, "y": 100, "w": 300, "h": 200}
        }
    """
```

### 6.5 add_shape
```python
async def add_shape(
    session_id: str,
    slide_index: int,
    x: int, y: int, w: int, h: int,
    shape_type: str,
    fill_color: Optional[str] = None,
    border_color: Optional[str] = None,
    border_width: int = 0,
    border_radius: int = 0
) -> dict:
    """
    添加形状
    
    Returns:
        {
            "element_id": "elem_xxxxxxxx",
            "slide_index": 0,
            "shape_type": "rectangle",
            "position": {"x": 100, "y": 100, "w": 200, "h": 200}
        }
    """
```

### 6.6 preview_slides
```python
async def preview_slides(
    session_id: str,
    format: str = "json",  # 'json' | 'png'
    slide_index: Optional[int] = None
) -> dict:
    """
    预览幻灯片
    
    JSON 格式返回:
        {
            "session_id": "sess_xxx",
            "slide_count": 2,
            "slides": [...]
        }
    
    PNG 格式返回:
        {
            "session_id": "sess_xxx",
            "format": "png",
            "files": [
                "/path/to/slide_0.png",
                "/path/to/slide_1.png"
            ]
        }
    """
```

### 6.7 export_pptx
```python
async def export_pptx(
    session_id: str,
    output_path: str
) -> dict:
    """
    导出 PPTX 文件
    
    Returns:
        {
            "file_path": "/absolute/path/to/output.pptx",
            "slide_count": 3,
            "file_size": 12345
        }
    """
```

---

## 7. PNG 预览渲染

### 7.1 渲染方案
使用 python-pptx 的内置能力 + Pillow 进行渲染：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from PIL import Image
import io

def render_slide_to_png(pres: Presentation, slide_index: int, output_path: str):
    """
    方案一：使用 LibreOffice 命令行转换（推荐）
    方案二：使用第三方库如 unoconv
    方案三：使用 python-pptx 导出为 SVG 再转换
    """
    # 实际实现将在开发阶段确定
```

### 7.2 临时文件管理
- PNG 预览文件存储在系统临时目录
- 路径格式：`/tmp/drawppt/{session_id}/slide_{index}.png`
- Session 删除时清理临时文件

---

## 8. 错误处理

### 8.1 错误码定义
```python
class ErrorCode(Enum):
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    SLIDE_INDEX_OUT_OF_RANGE = "SLIDE_INDEX_OUT_OF_RANGE"
    INVALID_IMAGE_PATH = "INVALID_IMAGE_PATH"
    INVALID_COLOR_FORMAT = "INVALID_COLOR_FORMAT"
    INVALID_SHAPE_TYPE = "INVALID_SHAPE_TYPE"
    EXPORT_FAILED = "EXPORT_FAILED"
    RENDER_FAILED = "RENDER_FAILED"
```

### 8.2 错误响应格式
```python
{
    "success": False,
    "error": {
        "code": "SESSION_NOT_FOUND",
        "message": "Session sess_xxx not found",
        "details": {}
    }
}
```

### 8.3 成功响应格式
```python
{
    "success": True,
    "data": {
        // 具体数据
    }
}
```

---

## 9. 依赖清单

### 9.1 核心依赖
```toml
[project]
dependencies = [
    "python-pptx>=0.6.21",
    "Pillow>=9.0",
    "mcp>=1.0",
]
```

### 9.2 开发依赖
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.20",
]
```

---

## 10. 测试策略

### 10.1 单元测试
- Session 生命周期
- 元素 CRUD 操作
- 坐标转换
- 颜色解析

### 10.2 集成测试
- 完整工作流（创建→编辑→预览→导出）
- 多页操作
- 错误场景

### 10.3 视觉回归测试
- 导出 PNG 与预期截图对比（可选）

---

## 11. 部署规格

### 11.1 安装方式
```bash
pip install drawppt
# 或
pip install -e .  # 开发模式
```

### 11.2 启动方式
```bash
# 作为 MCP 服务器启动
drawppt

# 或
python -m drawppt
```

### 11.3 MCP 配置
```json
{
  "mcpServers": {
    "drawppt": {
      "command": "drawppt",
      "args": []
    }
  }
}
```
