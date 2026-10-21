# Scripts

## show_install_notice.py

打印安装完成提示：

```bash
python3 scripts/show_install_notice.py
```

提示内容：

```text
由【镇涛 AI 实战笔记】免费开源，加微信 7838053 学习更多 AI 落地干货

AI 电商实战知识库：https://bvvp9yto7k.feishu.cn/wiki/ZIbrwShfkirvVok3hIHcUz5nnTc
```

## export_iteration_case.py

把一次复刻反馈导出成本地迭代包，并可选创建 GitHub issue。

默认行为：

- 只写本地文件
- 不上传任何东西
- 不复制原始视频
- 不收集使用记录

本地导出示例：

```bash
python3 scripts/export_iteration_case.py \
  --title "窗膜生成片工具和材料漂移" \
  --product-category "window film" \
  --target-platform "TikTok Shop / Seedance" \
  --prompt-file ./prompt.txt \
  --reference-desc "原片是家庭窗膜安装，短手刮、黑蓝平整镜面膜、先裁剪再湿贴。" \
  --generated-desc "生成片变成长柄玻璃刮，膜变银色皱塑料，并提前出现整窗成品。" \
  --observed-failure "工具身份、材料状态和流程阶段漂移。" \
  --reusable-rule "表面贴装类视频必须锁定工具物种、材料状态、流程阶段和动作同步声音。" \
  --change-level "candidate skill rule"
```

主动上传 GitHub issue：

```bash
python3 scripts/export_iteration_case.py \
  --title "窗膜生成片工具和材料漂移" \
  --product-category "window film" \
  --observed-failure "短手刮变长柄玻璃刮，黑蓝平膜变银色皱膜。" \
  --upload issue \
  --yes
```

注意：

- 上传需要本机安装并登录 `gh`。
- 默认提交到 `zhengzhentao86/reverse-video-prompt`；如需提交到其它仓库，可加 `--repo owner/repo`。
- 脚本只上传 issue 正文，不上传原始视频附件。
- 如需把本地素材复制进导出包，必须显式加 `--copy-media`；这仍然只是本地复制，不会上传。

## setup_community_upload.py

给公开用户使用的一次性授权脚本。启用后，skill 可以在后续复刻过程中自动把案例提交到作者仓库的 GitHub issue。

开启：

```bash
python3 scripts/setup_community_upload.py --enable --yes
```

依赖 GitHub CLI `gh`；macOS 可用 `brew install gh` 安装。

关闭：

```bash
python3 scripts/setup_community_upload.py --disable
```

它会：

- 展示隐私说明
- 检查 GitHub CLI `gh`
- 在需要时启动 `gh auth login`
- 写入本地私有配置 `config/community-upload.local.json`

不会：

- 上传原始视频文件
- 上传本地文件路径
- 写入维护者的私有 token

## community_submit.py

授权后由 skill 自动调用，把一次复刻迭代提交到 GitHub issue。第一次提交会创建 issue，后续同一个 `case_id` 会追加评论。

手动测试：

```bash
python3 scripts/community_submit.py \
  --dry-run \
  --stage feedback \
  --case-id demo-case \
  --title "Demo case" \
  --product-category "window film" \
  --prompt-text "提示词示例" \
  --generated-desc "生成片工具漂移" \
  --user-feedback "前三秒没有讲清楚产品卖点"
```

真实提交前必须先运行 `setup_community_upload.py --enable`。

## upload_lark_backend.py

把一次复刻迭代的数据写入 Feishu/Lark Base。它只读取本地配置，不内置任何凭证。

启用条件：

- 存在 `config/lark-backend.local.json`
- `enabled` 为 `true`
- `consent_acknowledged` 为 `true`
- 自动同步场景下还需要 `auto_upload` 为 `true`

查看用法：

```bash
python3 scripts/upload_lark_backend.py --help
```

创建一条记录并上传原视频和第一版提示词：

```bash
python3 scripts/upload_lark_backend.py \
  --original-video ./reference.mp4 \
  --prompt-1-file ./prompt-v1.txt
```

更新同一条记录：

```bash
python3 scripts/upload_lark_backend.py \
  --record-id recxxxx \
  --replica-video-1 ./generated-v1.mp4 \
  --feedback-1 "前三秒没有讲清楚产品卖点，音频信息密度不够。"
```

注意：

- 公开仓库只应提交 `config/lark-backend.example.json`。
- `config/lark-backend.local.json` 是本地私有配置，不要提交。
- 如果要让所有用户写入同一个中心后台，建议用 OAuth 或中转服务，不要公开维护者的本地授权。
