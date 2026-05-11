# GitHub Project Submission Guide

这份文档用于以后把本地项目提交到 GitHub。默认示例用户名为 `lstdgasr`，命令适用于 PowerShell。

## 1. 第一次提交一个新项目

先进入项目目录：

```powershell
cd D:\your_project_folder
```

初始化 Git 仓库：

```powershell
git init -b main
```

检查当前文件：

```powershell
git status
```

如果项目里有虚拟环境、缓存、临时文件，先创建或检查 `.gitignore`。常见 Python 项目可以包含：

```gitignore
.venv/
__pycache__/
.pytest_cache/
data/live/
*.log
*.pyc
```

添加文件并提交：

```powershell
git add .
git commit -m "feat: initial project"
```

## 2. 在 GitHub 创建空仓库

在 GitHub 页面新建 repository：

- Owner 选择 `lstdgasr`
- Repository name 填项目名，例如 `my-data-analysis-project`
- 选择 Public 或 Private
- 不要勾选自动创建 README、`.gitignore`、License

创建完成后，GitHub 会显示一个空仓库页面。

## 3. 连接远程仓库并推送

推荐使用 SSH 地址：

```powershell
git remote add origin git@github.com:lstdgasr/my-data-analysis-project.git
git push -u origin main
```

如果你使用 HTTPS 地址：

```powershell
git remote add origin https://github.com/lstdgasr/my-data-analysis-project.git
git push -u origin main
```

推送成功后，刷新 GitHub 仓库页面，就能看到 README 和项目文件。

## 4. 已有仓库后续更新

每次修改完代码或文档后，按下面流程提交：

```powershell
git status
git add .
git commit -m "docs: update project documentation"
git push
```

提交信息可以按修改类型写：

```text
feat: add new feature
fix: fix a bug
docs: update documentation
test: add or update tests
refactor: reorganize code without changing behavior
chore: update config or maintenance files
```

## 5. 当前项目示例

这个项目的远程仓库是：

```text
git@github.com:lstdgasr/global-market-analytics-dashboard.git
```

后续更新这个项目时，在 `D:\Data_Analyse` 目录运行：

```powershell
git status
git add .
git commit -m "docs: update guide"
git push
```

## 6. 常见问题

### remote origin already exists

说明已经设置过远程仓库。先查看：

```powershell
git remote -v
```

如果地址错了，改成新的：

```powershell
git remote set-url origin git@github.com:lstdgasr/my-data-analysis-project.git
```

### src refspec main does not match any

通常是还没有提交，先执行：

```powershell
git add .
git commit -m "feat: initial project"
git push -u origin main
```

### Permission denied (publickey)

说明 SSH key 没有配置好。可以临时改用 HTTPS：

```powershell
git remote set-url origin https://github.com/lstdgasr/my-data-analysis-project.git
git push
```

### 文件太大无法推送

不要把大型原始数据、虚拟环境、模型文件、缓存文件提交到 GitHub。把它们加入 `.gitignore`，例如：

```gitignore
.venv/
data/raw/
data/live/
*.zip
*.parquet
*.pkl
```

如果大文件已经被提交进历史记录，需要单独清理 Git 历史，不要直接反复 `git add .`。

## 7. 推荐提交前检查

提交前尽量运行项目测试或启动检查：

```powershell
git status
uv run pytest
uv run streamlit run app.py
```

确认页面能打开、测试通过后再提交，GitHub 上的项目会显得更专业。

