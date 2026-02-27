# GitHub 上传指南（中文）

这份指南是给你把当前 case study 用“论文风格”上传到 GitHub 用的。

## 1) 推荐仓库结构
```text
Simulated_CaseStudy_Project/
  README.md
  withme.md
  docs/
    PAPER_CASE_STUDY.md
    GITHUB_UPLOAD_GUIDE_CN.md
  src/
  data/
    processed/
  images/
```

## 2) 你应该上传哪些数据
建议上传：
- `data/processed/` 里的结果数据（可复现你的结论）
- `images/` 里的图
- `src/` 里的算法与绘图脚本

谨慎上传：
- 原始源数据（只上传确认可公开的数据）

## 3) 论文式写法（最稳结构）
在 `docs/PAPER_CASE_STUDY.md` 里按以下顺序写：
1. Abstract
2. Background
3. Objective
4. Data and Scope
5. Methodology (算法/模拟逻辑)
6. Results (表格 + 指标)
7. Discussion
8. Limitations
9. Conclusion
10. Reproducibility

你现在仓库里已经按这个结构写好了一版。

## 4) Git 命令上传步骤
在项目目录执行：

```bash
git status
git add README.md withme.md docs src data/processed images
git commit -m "Add paper-style case study, algorithms, and comparison visuals"
```

然后推送到远程：

```bash
git remote -v
# 如果还没绑定远程仓库，先执行：
# git remote add origin <your-github-repo-url>

git push -u origin main
```

如果你的默认分支不是 `main`，把命令里的 `main` 换成你的分支名（比如 `master`）。

## 5) GitHub 页面展示建议
- 把 `README.md` 作为项目首页（放结论和关键图）
- 把 `docs/PAPER_CASE_STUDY.md` 作为完整论文正文
- 在 README 顶部增加链接：
  - Full paper: `docs/PAPER_CASE_STUDY.md`

## 6) 投稿/投递时怎么讲
一句话版本：

> 我做了一个可复现的 workforce reallocation case simulation，对比 4x10 和 6x6-7；在考虑随机包装时间、fatigue、backlog 和 labor cost 后，6x6-7 在效率和成本上都更优。
