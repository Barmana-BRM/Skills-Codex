---
name: testing-test-automation-engineer
description: |
  自动化测试助手 - 专业的测试自动化设计与实现专家。适用场景：
  (1) 自动化测试框架选型与搭建（Selenium/Cypress/Playwright/Appium）
  (2) 自动化测试脚本编写（Web/API/Mobile）
  (3) 测试数据管理与Mock设计
  (4) CI/CD测试集成（Jenkins/GitLab CI/GitHub Actions）
  (5) Page Object模式与测试架构设计
  (6) 测试报告生成与可视化
  (7) 自动化测试维护与优化
  (8) 并行测试与分布式执行
  触发关键词：自动化测试、测试框架、Selenium、Cypress、Playwright、CI/CD、测试脚本、Page Object、Mock、测试报告
---

# 自动化测试助手

专业的测试自动化设计与实现专家，帮助构建高效可维护的自动化测试体系。

## 核心工作流程

### 1. 自动化测试框架选型

**主流框架对比：**

| 框架 | 语言 | 适用场景 | 优势 | 劣势 |
|------|------|----------|------|------|
| Selenium | 多语言 | Web UI | 生态成熟、跨浏览器 | 速度较慢、不稳定 |
| Cypress | JavaScript | Web UI | 快速、稳定、调试友好 | 仅Chrome系、无跨域 |
| Playwright | 多语言 | Web UI | 快速、跨浏览器、自动等待 | 较新、生态在发展 |
| Appium | 多语言 | Mobile | 跨平台、原生/混合 | 配置复杂、速度慢 |
| pytest | Python | API/单元 | 灵活、插件丰富 | 仅Python |
| Jest | JavaScript | 单元/API | 零配置、快照测试 | 仅JavaScript |
| JUnit | Java | 单元/API | 标准、稳定 | 仅Java |
| TestNG | Java | 全类型 | 并行、数据驱动 | 学习曲线 |

**选型决策树：**
```
选择测试框架
├── 测试类型？
│   ├── Web UI测试
│   │   ├── 需要跨浏览器 → Playwright/Selenium
│   │   ├── 仅Chrome系 → Cypress
│   │   └── 企业级稳定性 → Selenium
│   ├── Mobile测试
│   │   ├── 原生应用 → Appium/XCUITest/Espresso
│   │   └── 混合应用 → Appium
│   ├── API测试
│   │   ├── Python → pytest + requests
│   │   ├── JavaScript → Jest + axios
│   │   └── Java → RestAssured
│   └── 单元测试
│       └── 使用语言原生框架
└── 团队技能？
    ├── Python熟练 → pytest体系
    ├── JavaScript熟练 → Cypress/Playwright
    └── Java熟练 → TestNG/JUnit
```

### 2. 测试架构设计

**分层架构：**
```
测试架构分层
├── 测试用例层（Test Layer）
│   ├── 测试类/测试方法
│   ├── 测试数据
│   └── 断言验证
├── 业务逻辑层（Business Layer）
│   ├── 页面操作封装
│   ├── 业务流程组合
│   └── 通用业务方法
├── 页面对象层（Page Object Layer）
│   ├── 元素定位
│   ├── 页面操作
│   └── 页面验证
├── 基础设施层（Infrastructure Layer）
│   ├── 驱动管理
│   ├── 日志记录
│   ├── 报告生成
│   └── 配置管理
└── 工具层（Utility Layer）
    ├── 数据工具
    ├── 文件工具
    └── 断言扩展
```

**Page Object模式：**
```python
# 示例：Python + Playwright
class LoginPage:
    def __init__(self, page):
        self.page = page
        # 元素定位器
        self.username_input = page.locator('#username')
        self.password_input = page.locator('#password')
        self.login_button = page.locator('#login-btn')
        self.error_message = page.locator('.error-msg')

    def navigate(self):
        self.page.goto('/login')
        return self

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return self

    def get_error_message(self):
        return self.error_message.text_content()
```

### 3. Web UI自动化

**元素定位策略优先级：**
```
定位策略（优先级从高到低）
├── data-testid：专用测试属性
│   └── [data-testid="login-button"]
├── ID：唯一标识
│   └── #login-button
├── Name：表单元素
│   └── [name="username"]
├── CSS Selector：灵活强大
│   └── .form-input.email
├── XPath：复杂场景
│   └── //div[@class='item'][1]
└── 文本内容：最后选择
    └── text="Login"
```

**等待策略：**
```
等待类型
├── 隐式等待（不推荐）
│   └── 全局设置，影响所有元素
├── 显式等待（推荐）
│   ├── 等待元素可见
│   ├── 等待元素可点击
│   └── 自定义条件
├── 自动等待（现代框架）
│   └── Playwright/Cypress自动处理
└── 硬编码等待（避免）
    └── time.sleep() - 仅调试使用
```

**Playwright示例：**
```python
# conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

# test_login.py
def test_login_success(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("user@example.com", "password123")
    assert page.url == "/dashboard"

def test_login_invalid_password(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("user@example.com", "wrong")
    assert login_page.get_error_message() == "密码错误"
```

### 4. API自动化测试

**API测试框架：**
```python
# 基础请求封装
import requests
from dataclasses import dataclass

@dataclass
class APIResponse:
    status_code: int
    body: dict
    headers: dict
    elapsed: float

class APIClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self, endpoint, params=None):
        response = self.session.get(
            f"{self.base_url}{endpoint}",
            params=params
        )
        return self._parse_response(response)

    def post(self, endpoint, json=None, data=None):
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=json,
            data=data
        )
        return self._parse_response(response)

    def _parse_response(self, response):
        return APIResponse(
            status_code=response.status_code,
            body=response.json() if response.text else {},
            headers=dict(response.headers),
            elapsed=response.elapsed.total_seconds()
        )
```

**API测试用例：**
```python
import pytest

class TestUserAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"}
        )

    def test_get_user_success(self):
        response = self.client.get("/users/123")
        assert response.status_code == 200
        assert response.body["id"] == 123
        assert "name" in response.body

    def test_create_user_success(self):
        payload = {"name": "Test User", "email": "test@example.com"}
        response = self.client.post("/users", json=payload)
        assert response.status_code == 201
        assert response.body["name"] == "Test User"

    def test_get_user_not_found(self):
        response = self.client.get("/users/999999")
        assert response.status_code == 404
```

### 5. 测试数据管理

**数据管理策略：**
```
测试数据管理
├── 数据生成
│   ├── Faker库：随机真实数据
│   ├── 工厂模式：对象创建
│   └── Builder模式：复杂对象
├── 数据存储
│   ├── JSON/YAML文件：简单场景
│   ├── Excel：业务人员维护
│   └── 数据库：大规模数据
├── 数据隔离
│   ├── 测试前创建
│   ├── 测试后清理
│   └── 事务回滚
└── 数据驱动
    ├── pytest.mark.parametrize
    └── 外部数据源
```

**数据驱动示例：**
```python
import pytest

# 参数化测试
@pytest.mark.parametrize("username,password,expected", [
    ("valid_user", "valid_pass", 200),
    ("valid_user", "wrong_pass", 401),
    ("", "valid_pass", 400),
    ("valid_user", "", 400),
])
def test_login(username, password, expected):
    response = api_client.post("/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == expected

# 从文件加载数据
import json

def load_test_data(filename):
    with open(f"test_data/{filename}") as f:
        return json.load(f)

@pytest.mark.parametrize("data", load_test_data("login_cases.json"))
def test_login_from_file(data):
    response = api_client.post("/login", json=data["input"])
    assert response.status_code == data["expected_status"]
```

### 6. CI/CD集成

**GitHub Actions配置：**
```yaml
# .github/workflows/test.yml
name: Automated Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install

    - name: Run API tests
      run: pytest tests/api -v --tb=short

    - name: Run UI tests
      run: pytest tests/ui -v --tb=short

    - name: Upload test report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-report
        path: reports/
```

**Jenkins Pipeline：**
```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            parallel {
                stage('API Tests') {
                    steps {
                        sh 'pytest tests/api --junitxml=reports/api.xml'
                    }
                }
                stage('UI Tests') {
                    steps {
                        sh 'pytest tests/ui --junitxml=reports/ui.xml'
                    }
                }
            }
        }
    }

    post {
        always {
            junit 'reports/*.xml'
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Test Report'
            ])
        }
    }
}
```

### 7. 测试报告

**Allure报告配置：**
```python
# pytest配置
# pytest.ini
[pytest]
addopts = --alluredir=allure-results

# 测试用例添加装饰器
import allure

@allure.feature("用户管理")
@allure.story("用户登录")
@allure.severity(allure.severity_level.CRITICAL)
def test_login():
    with allure.step("打开登录页面"):
        page.goto("/login")

    with allure.step("输入用户名和密码"):
        page.fill("#username", "user")
        page.fill("#password", "pass")

    with allure.step("点击登录"):
        page.click("#login-btn")

    with allure.step("验证登录成功"):
        assert page.url == "/dashboard"
```

**HTML报告：**
```python
# conftest.py
import pytest
from datetime import datetime

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config._metadata['项目名称'] = 'My Project'
    config._metadata['测试环境'] = 'Staging'
    config._metadata['测试时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# pytest.ini
[pytest]
addopts = --html=reports/report.html --self-contained-html
```

## 输出模板

### 自动化测试方案
```markdown
# 自动化测试方案

## 项目信息
| 项目 | 内容 |
|------|------|
| 项目名称 | |
| 编写人 | |
| 版本 | V1.0 |
| 日期 | |

## 1. 自动化范围
### 1.1 自动化测试类型
| 类型 | 范围 | 工具 |
|------|------|------|
| API测试 | 核心接口 | pytest + requests |
| UI测试 | 主流程 | Playwright |
| 单元测试 | 核心模块 | pytest |

### 1.2 自动化覆盖率目标
| 测试类型 | 当前 | 目标 |
|----------|------|------|
| API测试 | 30% | 80% |
| UI测试 | 10% | 50% |
| 代码覆盖 | 40% | 70% |

## 2. 技术架构
### 2.1 框架选型
- 测试框架：pytest
- Web UI：Playwright
- API测试：requests
- 报告工具：Allure

### 2.2 项目结构
```
automation/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── pages/           # Page Objects
├── tests/
│   ├── api/         # API测试
│   └── ui/          # UI测试
├── utils/           # 工具类
├── data/            # 测试数据
└── reports/         # 测试报告
```

## 3. 执行策略
### 3.1 触发条件
| 场景 | 测试范围 | 触发方式 |
|------|----------|----------|
| 代码提交 | 冒烟测试 | 自动 |
| PR合并 | 回归测试 | 自动 |
| 每日构建 | 全量测试 | 定时 |
| 发布前 | 全量测试 | 手动 |

### 3.2 并行策略
- API测试：4个并行进程
- UI测试：2个并行进程

## 4. 维护计划
| 活动 | 频率 | 责任人 |
|------|------|--------|
| 用例维护 | 每Sprint | |
| 框架升级 | 每季度 | |
| 报告审查 | 每周 | |
```

### 自动化测试脚本模板
```python
"""
模块名称：用户登录测试
作者：
创建日期：
描述：测试用户登录功能的各种场景
"""

import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@allure.feature("用户认证")
@allure.story("用户登录")
class TestLogin:
    """登录功能测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, page):
        """测试前置：初始化页面对象"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.login_page.navigate()

    @allure.title("正常登录 - 有效凭证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, test_user):
        """
        测试目的：验证有效用户可以成功登录
        前置条件：用户已注册
        """
        self.login_page.login(
            username=test_user["username"],
            password=test_user["password"]
        )

        assert self.dashboard_page.is_displayed(), "登录后应显示仪表盘"
        assert self.dashboard_page.get_welcome_text() == f"欢迎, {test_user['name']}"

    @allure.title("登录失败 - 密码错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("password", ["wrong", "123456", ""])
    def test_login_invalid_password(self, test_user, password):
        """测试目的：验证错误密码无法登录"""
        self.login_page.login(
            username=test_user["username"],
            password=password
        )

        assert self.login_page.get_error_message() == "用户名或密码错误"
        assert self.login_page.is_displayed(), "应停留在登录页"
```

## 最佳实践

- **稳定性优先**：使用可靠的定位策略，避免脆弱测试
- **独立性**：每个测试独立运行，不依赖执行顺序
- **可维护性**：使用Page Object模式，分离定位与逻辑
- **快速反馈**：优化执行速度，及时发现问题
- **清晰报告**：使用Allure等工具生成可读报告
- **版本控制**：测试代码与产品代码同等对待
