# 🎨 拼豆识别系统

基于 PaddleOCR 的智能颜色识别与统计工具，可自动识别拼豆颜色编号并生成统计报表。

## ✨ 功能特点

- 🖼️ **图片识别**：自动识别图片中的颜色编号
- 📊 **智能统计**：按色盘分类统计颜色数量
- 📁 **导出结果**：支持 CSV 和 Excel 格式导出
- 🔍 **色盘查询**：快速查询颜色所属色盘
- 🌐 **Web 界面**：简洁直观的操作界面

## 🚀 快速开始

### Windows 用户

1. 下载并解压 `拼豆识别系统.zip`
2. 双击运行 `拼豆识别系统.exe`
3. 程序会自动打开浏览器（访问 http://127.0.0.1:8080）
4. 开始使用！

### 开发者

```bash
# 1. 克隆项目
git clone <项目地址>
cd 拼豆识别

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python launcher.py
```

## 📖 使用说明

### 1. 图片识别

1. 打开网页后，点击上传区域选择图片
2. 调整识别参数（可选）：
   - 重叠值：识别区域重叠大小
   - 高度值：分割高度
   - 置信度阈值：过滤低置信度结果
3. 点击"开始识别"
4. 等待处理完成，下载 CSV/Excel 报表

### 2. 色盘查询

1. 在查询框输入颜色编号（空格分隔多个编号）
2. 点击查询按钮
3. 查看各颜色所属色盘

## 📦 项目结构

```
拼豆识别/
├── launcher.py              # 程序启动入口
├── app.py                   # Flask 后端
├── main.py                  # 核心识别逻辑
├── query_color_plate.py     # 色盘查询模块
├── color.json               # 颜色映射表
├── requirements.txt         # Python 依赖
├── templates/
│   └── index.html           # 前端页面
├── uploads/                 # 上传文件目录
├── bead_recognizer.spec     # 打包配置
├── build_windows.bat        # Windows 打包脚本
└── README.md                # 说明文档
```

## 🔧 打包指南

详见 [打包说明.md](打包说明.md)

快速打包命令：
```bash
# Windows
build_windows.bat

# 或手动
pip install pyinstaller
pyinstaller bead_recognizer.spec --clean --noconfirm
```

## 🛠️ 技术栈

- **后端**：Python + Flask
- **OCR 引擎**：PaddleOCR
- **图像处理**：OpenCV + NumPy
- **前端**：HTML5 + JavaScript
- **导出**：CSV / Excel

## 📝 配置说明

### color.json 格式

```json
{
  "color_plates": {
    "A盘": [
      {"code": "A01", "name": "红色"},
      {"code": "A02", "name": "蓝色"}
    ],
    "B盘": [
      {"code": "B01", "name": "绿色"}
    ]
  }
}
```

## ⚠️ 注意事项

1. **首次启动**：OCR 模型首次加载需要 1-3 分钟，请耐心等待
2. **模型大小**：PaddleOCR 模型文件较大（约 100MB+）
3. **端口占用**：默认使用 8080 端口，如被占用会自动切换
4. **浏览器兼容**：推荐使用 Chrome、Edge、Firefox 等现代浏览器

## 📋 系统要求

| 项目 | 最低要求 |
|------|----------|
| 操作系统 | Windows 10 / Windows 11 |
| 内存 | 4GB+（推荐 8GB） |
| 磁盘空间 | 2GB+ 可用空间 |
| 浏览器 | 支持 ES6 的现代浏览器 |

## 🐛 常见问题

**Q: 程序无法启动？**
> A: 确保已安装 Visual C++ Redistributable，可在微软官网下载。

**Q: 识别速度慢？**
> A: 首次加载 OCR 模型较慢，后续使用会更快。建议保持程序运行。

**Q: 识别结果不准确？**
> A: 可尝试调整置信度阈值，或改善图片质量（提高清晰度、对比度）。

**Q: 端口被占用？**
> A: 程序会自动尝试其他端口，请查看控制台输出的实际访问地址。

## 📄 开源协议

本项目仅供学习交流使用。

---

** Made with ❤️ for 拼豆爱好者 **
