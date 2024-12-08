# chatWithQing

chatWithQing 是一个基于大模型的二创桌宠项目。

本项目主要方向为大模型角色扮演，互动性方面会有所欠缺（如与随机移动、更多动作以及与其他窗口的交互等）。~~所以想要互动性更强的桌宠请等池池出手~~

- 由于本人技术能力、精力有限，项目开发进度可能会较缓慢，敬请谅解。

##### **当前整合包处于测试阶段，有可能会有许多bug，遇到bug欢迎向作者反应**

## 功能

1. 已经可以使用的功能:

   - [X] 基础对话功能(目前接入的是 deepseek 的 api 服务)
   - [X] 触摸功能 (目前支持的部位：头(头顶)、头发、脸、发卡)
   - [X] TTS 语音支持
   - [X] 设置面板
   - [X] 当天+多天历史对话总结
   - [X] 短时间待机时自唤醒判断
   - [X] 表情差分功能
2. TODOLIST:

   - 一定会做的功能

     - [ ] 调用历史对话("回忆")功能
     - [ ] 对其他大模型厂商 api 和本地 api (ollama)的支持
     - [ ] 提醒(闹钟)功能
     - [ ] 天气查询
     - [ ] 图片/屏幕理解 moondream2-1.8b、fuyu-8b
   - 可能会做的功能  ~~(饼)~~

     - 对代码、长文本的额外窗口展示？
     - 性能监控？
     - 网页提取？搜索？
     - 多端支持(使用gradio)？
     - ...

## 更新历史

> 完整更新历史请在 `UPDATE HISTORY.md` 中查看

#### [v1.0.0] - 2024-10-16

- 添加了自激活功能
- 添加了表情差分功能
- 添加了 LLM 修复错误格式的返回数据功能
- 修复了若干 bug

## 部署教程

### 整合包方式

1. 下载整合包并解压
2. 双击 `整合包_启动主程序.bat` 启动主程序

### 仓库克隆方式

> 本项目推荐在 python 3.9 环境下运行。

1. 克隆仓库

   ```
   git clone https://github.com/CodeCCsky/chatWithQing.git

   ```
2. 进入项目目录

   ```
   cd chatWithQing

   ```
3. 创建并激活环境

   推荐使用 `conda`、`venv` 等包管理器管理环境。以下是使用 `conda` 安装的一个示例。

   ```
   conda create -n chatWithQing python=3.9

   conda activate chatWithQing
   ```
4. 安装依赖项

   ```
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

   ```
5. 前往 deepseek 官网注册并获取 api key

   官网地址: https://www.deepseek.com/zh
6. 启动主程序

   ```
   python main.py
   ```

## 联系信息

如果你有任何问题或建议，请通过以下方式联系我：

- 邮箱: <public_codeccsky.rifling121@aleeas.com>
- GitHub Issues: [https://github.com/CodeCCsky/chatWithQing/issues](https://github.com/CodeCCsky/chatWithQing/issues)

## 贡献指南

欢迎大家对社区的贡献！

如果你有什么好点子，欢迎在 [Issues](https://github.com/CodeCCsky/chatWithQing/issues) 中提出

## 许可证

> 本条目由 Claude 辅助完成，如有不妥之处欢迎指出。

本项目包含多种类型的内容，每种内容都受其各自的许可条款约束：

1.**软件**：本项目中的所有软件（包括 Python 代码和 XML 文件）均采用 GNU Affero 通用公共许可证 v3.0（AGPL-3.0）授权。

- 许可证文件：`licenses/SOFTWARE_LICENSE`
- 完整文本：[https://www.gnu.org/licenses/agpl-3.0.en.html](https://www.gnu.org/licenses/agpl-3.0.en.html)

2.**图像和音频**：`app/GUI/image` 和 `app/sound` 目录中的所有图像（图标除外）和音频文件均采用知识共享署名-非商业性使用 4.0 国际许可证（CC BY-NC 4.0）授权。

- 许可证文件：`licenses/MEDIA_LICENSE`
- 完整文本：[https://creativecommons.org/licenses/by-nc/4.0/deed.zh](https://creativecommons.org/licenses/by-nc/4.0/deed.zh)
- 注意：这些内容不得用于任何商业用途。
- 特别说明：这些图片和音频的作者[莲花池池](https://space.bilibili.com/760048)要求不能将本项目内的这些资源用于商业目的。在使用这些资源时，请遵守作者的意愿和CC BY-NC 4.0许可证的条款。

3.**OFL 授权字体**：字体文件 `app/GUI/font/荆南波波黑.ttf` 采用 SIL 开放字体许可证（OFL）授权。

- 许可证文件：`licenses/FONT_LICENSE`
- 完整文本：[https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&amp;id=OFL](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL)

4.**图标**：本项目中的图标采用不同的许可条款：

- 部分图标采用 SIL 开放字体许可证（OFL）授权。
- 部分图标采用 Apache 许可证 2.0 版授权。
- 部分图标采用 CC BY-NC 4.0 许可证授权（与图像和音频相同）。
- 请参阅 `licenses/ICON_LICENSES` 文件以了解每个图标的具体许可信息。

有关完整的许可详情，请参阅本项目根目录中的 `LICENSE` 文件。

## 关于隐私

> 本条目由 Claude 辅助完成，如有不妥之处欢迎指出。

本项目在调用 DeepSeek API 时会使用一些用户输入的敏感信息，例如名字、住址、性别等。请**不要填写真实信息**，以保护个人隐私，防止信息泄露。

1.**信息收集和使用**：

- 收集的信息包括但不限于名字、住址等。
- 这些信息仅在调用 DeepSeek API 时作为大模型对用户的认知信息传递，不会用于任何其他目的。
- 除调用 Deepseek API 时使用外，本项目不会上传或分享这些信息到任何外部服务器。

2.**信息存储**：

- 用户提供的信息将以非加密形式存储在项目根目录下 `setting/private_setting.yaml` 中。
- 请不要填写真实信息，以避免潜在的隐私泄露风险。
- 用户应自行承担提供和存储信息的风险和责任。

3.**用户责任**：

- 用户应确保所提供的信息是虚假的，以保护个人隐私。
- 用户应采取适当的安全措施，如使用强密码保护其设备，以防止未经授权的访问。

## 鸣谢

- 特别感谢[莲花池池](https://space.bilibili.com/760048)对图片部分的授权
