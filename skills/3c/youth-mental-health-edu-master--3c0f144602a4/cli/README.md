# 青少年心理健康教育 CLI

把 青少年心理健康教育 master skill 的认知 OS 物化成 bash 工具。
不替代 SKILL.md（思维顾问），是它的「执行端」：交互问询 → 应用 playbook / protocol → 输出结构化报告。

## 用法

所有脚本支持 `--help` / `--explain` / `--dry-run` / `--json` 四个标准 flag。

```bash
# 拿到新问题时, 按 N 个研究维度做功课
./protocol/agentic.sh

# 决策树评估 (基于 playbook)
./decision/topic-1.sh
# SOP 走查 (workflow)
./workflow/universal-mental-health-screenin.sh

# 看背后的心智模型 / playbook (不交互)
./protocol/agentic.sh --explain
```

## 脚本清单

| 脚本 | 作用 |
|------|------|
| `protocol/agentic.sh` | Agentic Protocol (7 维度) — 拿到新问题时按这一行的研究维度做功课 |
| `decision/topic-1.sh` | 心理 决策树 (4 条规则) |
| `decision/general-playbook.sh` | 通用 Playbook 决策树 (6 条规则) |
| `workflow/universal-mental-health-screenin.sh` | Universal Mental Health Screening (全校心理健康普筛) SOP 走查 |
| `workflow/student-crisis-response.sh` | Student Crisis Response (个别学生危机干预) SOP 走查 |
| `workflow/sel-curriculum-implementation-se.sh` | SEL Curriculum Implementation (SEL 课程规划与实施) SOP 走查 |
| `workflow/classroom-mh-lesson-design.sh` | Classroom MH Lesson Design (班级心理主题课设计与教学) SOP 走查 |
| `workflow/individual-student-counseling.sh` | Individual Student Counseling (学生个案心理辅导) SOP 走查 |
| `workflow/parent-school-mh-communication.sh` | Parent-School MH Communication (家校联动心理健康沟通) SOP 走查 |
| `workflow/teacher-mh-literacy-training.sh` | Teacher MH Literacy Training (教师心理健康素养培训) SOP 走查 |
| `workflow/mtss-framework-setup-mtss.sh` | MTSS Framework Setup (MTSS/分层干预体系搭建) SOP 走查 |
| `workflow/digital-mh-tool-selection-deploy.sh` | Digital MH Tool Selection & Deployment (数字心理健康工具选型与部署) SOP 走查 |
| `workflow/mh-program-evaluation.sh` | MH Program Evaluation (心理健康教育项目评估) SOP 走查 |

## 设计与生成

CLI 子树由 `tools/cli_writer.py` 自动从 `references/synthesis.md` (Section 2 Playbook + Section 9 Agentic Protocol) 和 `references/research/03-workflows.md` 生成。

完整 spec 在 master-skill 仓库 `references/cli-spec.md`。

## 重新生成

如果 synthesis.md 或 03-workflows.md 更新了, 重跑:

```bash
python3 <master-skill>/tools/cli_writer.py emit \
  --skill-dir <this-skill-dir> \
  --synthesis references/synthesis.md \
  --workflows references/research/03-workflows.md \
  --industry-cn "青少年心理健康教育"
```
