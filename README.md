# 鼠标操作录制系统

一个功能强大的鼠标操作录制和回放系统，可以录制您的鼠标操作并支持自动循环回放。

## 功能特点

- 🖱️ **鼠标操作录制**: 录制鼠标移动、点击、滚轮操作
- 📹 **实时录制**: 支持开始/停止录制控制
- ▶️ **操作回放**: 精确回放录制的鼠标操作
- 🔄 **循环回放**: 支持无限循环自动回放
- 💾 **文件保存**: 自动保存录制结果到JSON文件
- 📁 **文件管理**: 查看和加载已保存的录制文件
- 🌐 **Web界面**: 美观的网页操作界面
- 📊 **实时状态**: 显示录制和回放状态

## 系统要求

- Python 3.6+
- Linux/Windows/macOS
- 支持图形界面的系统

## 安装和使用

### 方法1: 使用启动脚本（推荐）

```bash
# 进入项目目录
cd /home/assus/EEG/JD

# 运行启动脚本
./start.sh
```

### 方法2: 手动安装

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务器**
   ```bash
   python app.py
   ```

3. **打开浏览器**
   
   在浏览器中访问: `http://localhost:5000`

## 使用说明

### 录制鼠标操作

1. 点击"开始录制"按钮
2. 执行您想要录制的鼠标操作
3. 点击"停止录制"按钮
4. 系统会自动保存录制结果

### 回放鼠标操作

1. **单次回放**: 点击"回放一次"按钮
2. **循环回放**: 点击"循环回放"按钮，系统将无限循环执行录制的操作
3. **停止回放**: 点击"停止回放"按钮

### 管理录制文件

- 在"保存的录制文件"部分可以看到所有已保存的录制
- 点击"加载"按钮可以加载特定的录制文件
- 每个录制文件显示录制时长、操作数量和创建时间

## 技术架构

- **后端**: Python Flask + pynput
- **前端**: HTML5 + CSS3 + JavaScript
- **数据存储**: JSON文件
- **鼠标控制**: pynput库

## 录制文件格式

录制文件以JSON格式保存在`recordings/`目录下，包含以下信息：

```json
{
  "actions": [
    {
      "type": "move",
      "x": 100,
      "y": 200,
      "timestamp": 1.23
    },
    {
      "type": "click",
      "x": 100,
      "y": 200,
      "button": "Button.left",
      "pressed": true,
      "timestamp": 2.45
    }
  ],
  "total_duration": 5.67,
  "created_at": "2024-01-01T12:00:00"
}
```

## 注意事项

1. **权限要求**: 在某些系统上，鼠标操作可能需要管理员权限
2. **屏幕分辨率**: 录制的坐标是绝对坐标，在不同分辨率下可能需要调整
3. **安全性**: 请谨慎使用循环回放功能，避免无限循环导致系统无法控制
4. **性能**: 录制大量操作时可能会影响系统性能

## 故障排除

### 常见问题

1. **pynput权限错误**
   - 在macOS上可能需要在"系统偏好设置 > 安全性与隐私 > 辅助功能"中授权
   - 在Linux上可能需要安装X11开发包

2. **Flask导入错误**
   ```bash
   pip install --upgrade Flask Flask-CORS
   ```

3. **端口占用**
   - 如果5000端口被占用，可以修改`app.py`中的端口号

## 开发说明

### 项目结构
```
/home/assus/EEG/JD/
├── app.py              # Flask后端应用
├── templates/
│   └── index.html      # 前端界面
├── recordings/         # 录制文件存储目录
├── requirements.txt    # Python依赖
├── start.sh           # 启动脚本
└── README.md          # 说明文档
```

### API接口

- `POST /api/start_recording` - 开始录制
- `POST /api/stop_recording` - 停止录制
- `POST /api/replay` - 开始回放
- `POST /api/stop_replay` - 停止回放
- `GET /api/status` - 获取状态
- `GET /api/recordings` - 获取录制文件列表
- `POST /api/load_recording` - 加载录制文件

## 许可证

MIT License

## 贡献

欢迎提交问题和功能建议！
