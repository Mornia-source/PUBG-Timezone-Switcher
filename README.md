# PUBG-TimeZone-Switcher ⏰🌍

一款适用于 **PUBG 玩家** 的 Windows 小工具，能够 **一键切换系统时区**，免去在系统设置里反复查找的麻烦。  

PUBG 的登录机制会基于 **电脑系统时间 + IP 地址** 双重验证，  
本工具通过快速切换系统时区，帮助玩家更方便地适配不同的游戏服务器。  

---

## ✨ 功能特点

- 🚀 **一键切换时区**：快速切换到常用的目标时区（如韩国、日本、东南亚等）。  
- 🖱️ **简洁界面**：点击按钮即可完成操作。  
- 🌐 **自动映射国旗 Emoji**：在按钮上显示对应国家的国旗，直观明了。  
- 🛡️ **免系统繁琐设置**：无需进入 Windows 设置 → 时间 → 区域，就能完成时区切换。  

---

## 🖼️ 界面预览

（这里可以放一张运行界面的截图）

---

## ⚙️ 使用方法

1. 下载本项目并运行 `timezone_setter.exe`（或 `python timezone_setter.py`）。  
2. 在界面中点击目标国家的按钮。  
3. 系统时区将会立即切换，无需额外操作。  

---

## 📦 环境依赖

- Python 3.10+  
- 依赖库：  
  - [pywebview](https://pywebview.flowrl.com/)  
  - [pywin32](https://pypi.org/project/pywin32/)  

安装方式：  
```bash
pip install pywebview pywin32
