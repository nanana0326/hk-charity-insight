# 部署成可分享的网站链接（给老板查看）

用 **Vercel** 部署前端，几分钟内会得到一个类似 `https://你的项目名.vercel.app` 的链接，直接发给老板即可打开。

---

## 一、先把代码放到 GitHub

1. 若尚未安装 Git：到 https://git-scm.com 下载安装。
2. 在 https://github.com 注册/登录，点 **New repository** 新建仓库（例如 `hk-charity-insights`），不要勾选 “Add a README”。
3. 在本项目文件夹打开终端（PowerShell 或 CMD），执行：

```powershell
cd "c:\Users\Lenovo\Desktop\港大\cursor"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/hk-charity-insights.git
git push -u origin main
```

（把 `你的用户名/hk-charity-insights` 换成你的仓库地址。）

---

## 二、用 Vercel 部署并拿到链接

1. 打开 https://vercel.com ，用 GitHub 账号登录。
2. 点 **Add New…** → **Project**。
3. 在列表里选刚推送的仓库（如 `hk-charity-insights`），点 **Import**。
4. **重要**：在 “Root Directory” 旁点 **Edit**，填 `apps/web`，确认。
5. **Framework Preset** 保持 **Next.js** 即可。
6. 若老板**只查看页面**（首页、FAQ、导航等），无需填环境变量，直接点 **Deploy**。
7. 等一两分钟，部署完成后会显示 **Visit**，点进去就是你的网站链接，例如：  
   `https://hk-charity-insights-xxx.vercel.app`  
   把这个链接发给老板即可。

---

## 说明

- **只部署前端时**：首页、FAQ、文档上传页、Web impact 等页面都能打开和浏览；上传文档、生成报告等功能需要后端 API，此时会不可用或报错。
- **若以后需要“上传文档 / 分析”也能用**：需要把 `apps/api` 部署到一台服务器（如 Railway、Render 或云主机），并得到 API 地址（如 `https://你的-api.railway.app`）。然后在 Vercel 项目里：**Settings → Environment Variables**，新增 `NEXT_PUBLIC_API_BASE_URL`，值为 `https://你的-api.railway.app/api`，再重新部署一次前端即可。

完成“一 + 二”后，你就有一个可以直接发给老板查看的网站链接。
