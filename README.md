# 文件夹结构
Obs_env                        # 虚拟环境
Obs_project/                   # 项目根目录
├── .gitignore                 # 忽略文件（如venv/, *.pyc）
├── requirements.txt           # 依赖清单
├── docs/                      # 项目文档
│   ├── setup.md               # 安装指南
│   ├── api.md                 # API接口文档
│   ├── models.md              # 数据模型关系图
│   └── screenshots/           # 界面截图
├── config/                    # 主配置目录（原Django的project_manager文件夹重命名）
│   ├── __init__.py
│   ├── settings.py            # 拆分配置为多个文件（见下文）
│   ├── urls.py                # 全局路由
│   └── wsgi.py
├── apps/                      # 所有应用模块
│   ├── requirements/          # 需求管理
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── views.py
│   ├── tasks/                 # 任务管理（类似结构）
│   └── ...                    # 其他应用
└── manage.py