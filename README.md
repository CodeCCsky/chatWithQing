# chatWithQing

chatWithQing 是一个基于大模型的二创桌宠项目。

本项目主要方向为大模型角色扮演，互动性方面会有所欠缺（如与随机移动、更多动作以及与其他窗口的交互等）。~~所以想要互动性更强的桌宠请等池池出手~~

- 由于本人技术能力、精力有限，项目开发进度可能会较缓慢，敬请谅解。

## 功能

1. 已经可以使用的功能:

   - [X] 基础对话功能(目前接入的是 deepseek 的 api 服务)
   - [X] 触摸功能 (目前支持的部位：头(头顶)、头发、脸、发卡)
   - [X] TTS 语音支持
   - [X] 设置面板 (注意：该功能可能还有未知的bug。若有问题请在 issue 中提出。(有时间的话)会修的)
   - [X] 当天+多天历史对话总结
2. TODOLIST:

   - 一定会做的功能

     - [ ] 调用历史对话("回忆")功能
     - [ ] 短时间待机时自唤醒判断
     - [ ] 提醒(闹钟)功能
     - [ ] 天气查询
   - 可能会做的功能~~(可能不会做的饼)~~

     - 对其他大模型厂商 api 和本地 api (ollama)的支持
     - 对代码、长文本的额外窗口展示？
     - 性能监控？
     - 网页提取？搜索？

## 更新历史

#### [v1.0.0] - 2024-08-25

- 基本思考 + 对话功能上线
- 添加了离线计算 token 功能

#### [v1.1.0] - 2024-08-27

- 更新摸摸功能，支持摸头(头顶)、脸、头发和发卡

#### [v1.2.0] - 2024-09-14

- 添加 LICENSE
- 添加基础的 TTS 语音支持
- 添加设置界面
- 添加初始化界面
- 添加当天+多天历史对话总结功能
- 添加对话框、输入框自动调整透明度功能
- 添加 log (暂未完善)
- 修改了对话框(气泡框)的外观
- 修改了模型默认参数，获得更好的输出
- 暂时删除了离线计算 token 功能(过于鸡肋)

#### [v1.2.0-fix1]

- 修改了 README 文件中的过时部分
- 更新 requirements.txt
## 部署教程

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
   python main_gui.py
   ```

## 许可证

本项目包含多种类型的内容，每种内容都受其各自的许可条款约束：

1. **软件**：本项目中的所有软件（包括 Python 代码和 XML 文件）均采用 GNU Affero 通用公共许可证 v3.0（AGPL-3.0）授权。

- 许可证文件：`licenses/SOFTWARE_LICENSE`
- 完整文本：https://www.gnu.org/licenses/agpl-3.0.en.html

2. **图像和音频**：`app/GUI/image` 和 `app/sound` 目录中的所有图像（图标除外）和音频文件均采用知识共享署名-非商业性使用 4.0 国际许可证（CC BY-NC 4.0）授权。

   - 许可证文件：`licenses/MEDIA_LICENSE`
   - 完整文本：https://creativecommons.org/licenses/by-nc/4.0/deed.zh
   - 注意：这些内容不得用于任何商业用途。
   - 特别说明：这些图片和音频的作者[莲花池池](https://space.bilibili.com/760048)要求不能将本项目内的这些资源用于商业目的。在使用这些资源时，请遵守作者的意愿和CC BY-NC 4.0许可证的条款。
3. **OFL 授权字体**：字体文件 `app/GUI/font/荆南波波黑.ttf` 采用 SIL 开放字体许可证（OFL）授权。

   - 许可证文件：`licenses/FONT_LICENSE`
   - 完整文本：https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL
4. **图标**：本项目中的图标采用不同的许可条款：

   - 部分图标采用 SIL 开放字体许可证（OFL）授权。
   - 部分图标采用 Apache 许可证 2.0 版授权。
   - 部分图标采用 CC BY-NC 4.0 许可证授权（与图像和音频相同）。
   - 请参阅 `licenses/ICON_LICENSES` 文件以了解每个图标的具体许可信息。

有关完整的许可详情，请参阅本项目根目录中的 `LICENSE` 文件。

## 隐私政策

本项目在调用 DeepSeek API 时可能会收集一些用户的敏感信息，例如名字、住址、性别等。由于本项目技术限制，无法对用户提供的数据进行保护，请**不要填写真实信息**，以保护个人隐私，防止信息泄露。

1. **信息收集和使用**：

   - 收集的信息包括但不限于名字、住址等。
   - 这些信息仅在调用 DeepSeek API 时作为大模型对用户的认知信息传递，不会用于任何其他目的。
   - 除调用 Deepseek API 时使用外，本项目不会上传或分享这些信息到任何外部服务器。
2. **信息存储**：

   - 用户提供的信息将以非加密形式存储在项目根目录下setting/private_setting.yaml中。
   - 请不要填写真实信息，以避免潜在的隐私泄露风险。
   - 用户应自行承担提供和存储信息的风险和责任。
3. **用户责任**：

   - 用户应确保所提供的信息是虚假的，以保护个人隐私。
   - 用户应采取适当的安全措施，如使用强密码保护其设备，以防止未经授权的访问。

## 贡献 & 感谢

- 特别感谢[莲花池池](https://space.bilibili.com/760048)对图片部分的授权
