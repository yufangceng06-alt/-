# 粉盔小桃 Windows 桌宠

以照片中的粉色头盔、墨镜、双马尾和波点裙为灵感制作的透明窗口桌宠。

## 功能

- 透明、无边框、可拖动窗口
- 8 帧循环动画，支持双击打开 AI 对话
- 右键菜单：AI 对话、设置、重置位置、退出
- OpenAI 兼容的聊天接口，可配置接口地址、API Key、模型和角色设定
- 自动保存窗口位置、大小、置顶选项和 AI 设置
- 一键打包为 Windows EXE

## 直接运行

1. 安装 Python 3.10 或更高版本，并在安装时勾选“Add Python to PATH”。
2. 双击 `start.bat`。
3. 右键桌宠 → `设置`，填写 API Key 和模型。

默认接口是 `https://api.openai.com/v1`。也可填写任何兼容 OpenAI `/chat/completions` 协议的服务地址。

## 打包 EXE

双击 `build_exe.bat`。完成后程序位于：

`dist\PinkHelmetPet\PinkHelmetPet.exe`

整个 `dist\PinkHelmetPet` 文件夹可复制到其他 Windows 电脑使用，不要求安装 Python。

## 不安装 Python：使用 GitHub 在线构建

GitHub 的 Windows 云端电脑会自动完成打包，你自己的电脑不需要安装 Python。

1. 登录 GitHub，点击右上角 `+` → `New repository`，创建一个仓库。
2. 解压本项目，把 `PinkHelmetPet` 文件夹内的全部内容上传到仓库根目录。注意必须包含隐藏目录 `.github`。
3. 打开仓库顶部的 `Actions` 页面。
4. 左侧选择 `Build Windows Desktop Pet`。
5. 点击右侧 `Run workflow`，再点击绿色的 `Run workflow`。
6. 等待约 3–8 分钟，任务出现绿色对勾后点开该次运行记录。
7. 在页面底部 `Artifacts` 区域下载 `PinkHelmetPet-Windows-x64`。
8. 解压下载文件，再解压其中的 `PinkHelmetPet-Windows-x64.zip`，双击 `PinkHelmetPet.exe`。

以后每次向 `main` 或 `master` 分支上传程序修改，GitHub 也会自动重新构建。生成的下载文件默认保留 30 天。

## 操作

- 左键拖动：移动桌宠
- 左键双击：打开 AI 对话
- 右键：打开功能菜单

## 隐私说明

API Key 和偏好设置仅由 Qt 的 `QSettings` 保存在当前 Windows 用户配置中，不写入项目源码。聊天内容只在当前窗口会话中保留，不落盘。

## 项目结构

```
PinkHelmetPet/
├─ assets/sprite_sheet.png
├─ pet_app/app.py
├─ run_pet.py
├─ start.bat
├─ build_exe.bat
├─ PinkHelmetPet.spec
├─ .github/workflows/build-windows.yml
├─ requirements.txt
└─ README.md
```
