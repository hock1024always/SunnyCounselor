# Counselor项目测试文档

## 📋 概述

本目录包含Counselor项目的完整测试套件，包括CounselorApp（咨询师端）和CounselorAdmin（管理端）的API测试。

## 🏗️ 测试结构

```
tests/
├── counselorapp/           # CounselorApp测试
│   └── test_api.py        # API接口测试
├── counseloradmin/         # CounselorAdmin测试  
│   └── test_api.py        # API接口测试
├── conftest.py            # 测试配置和fixture
├── run_tests.py           # 测试运行脚本
├── pytest.ini             # pytest配置文件
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
pip install pytest pytest-django pytest-cov requests
```

### 2. 运行测试

#### 运行所有测试
```bash
python tests/run_tests.py
```

#### 运行特定应用测试
```bash
# 只运行CounselorApp测试
python tests/run_tests.py --app counselorapp

# 只运行CounselorAdmin测试
python tests/run_tests.py --app counseloradmin
```

#### 带详细输出和覆盖率
```bash
python tests/run_tests.py --verbose --coverage
```

#### 生成HTML测试报告
```bash
python tests/run_tests.py --report
```

### 3. 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/counselorapp/test_api.py -v

# 运行特定测试类
pytest tests/counselorapp/test_api.py::TestCounselorAppAPI -v

# 运行特定测试方法
pytest tests/counselorapp/test_api.py::TestCounselorAppAPI::test_dashboard_stats -v
```

## 📊 测试覆盖范围

### CounselorApp测试覆盖

| 功能模块 | 测试用例数量 | 测试覆盖率 |
|---------|-------------|-----------|
| 数据看板统计 | 3个测试用例 | ✅ 完整覆盖 |
| 咨询列表管理 | 4个测试用例 | ✅ 完整覆盖 |
| 排班管理 | 2个测试用例 | ✅ 完整覆盖 |
| 评论管理 | 2个测试用例 | ✅ 完整覆盖 |
| 个人资料管理 | 2个测试用例 | ✅ 完整覆盖 |
| 集成测试 | 2个测试用例 | ✅ 完整覆盖 |

### CounselorAdmin测试覆盖

| 功能模块 | 测试用例数量 | 测试覆盖率 |
|---------|-------------|-----------|
| 学生信息管理 | 3个测试用例 | ✅ 完整覆盖 |
| 访谈记录管理 | 2个测试用例 | ✅ 完整覆盖 |
| 负面事件管理 | 2个测试用例 | ✅ 完整覆盖 |
| 转介管理 | 2个测试用例 | ✅ 完整覆盖 |
| 宣教内容管理 | 3个测试用例 | ✅ 完整覆盖 |
| 通知管理 | 2个测试用例 | ✅ 完整覆盖 |
| 轮播图管理 | 1个测试用例 | ✅ 完整覆盖 |
| 集成测试 | 3个测试用例 | ✅ 完整覆盖 |

## 🔧 测试配置

### 测试数据库
- 使用SQLite内存数据库进行测试
- 自动创建和销毁测试数据库
- 每个测试用例独立的数据环境

### 测试认证
- 模拟管理员用户和咨询师用户
- 自动处理JWT Token认证
- 权限控制测试

### 测试数据
- 使用pytest fixture创建测试数据
- 支持动态数据生成
- 测试数据自动清理

## 🧪 测试用例示例

### CounselorApp测试示例

```python
def test_dashboard_stats(self, api_client, test_counselor, test_consultations):
    """测试数据看板统计接口"""
    api_client.force_authenticate(user=test_counselor.user)
    
    url = reverse('dashboard-stats')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # 验证响应结构
    assert 'today_stats' in data
    assert 'yearly_stats' in data
    assert 'time_distribution' in data
```

### CounselorAdmin测试示例

```python
def test_student_create(self, api_client, admin_user):
    """测试创建学生接口"""
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('student-list')
    student_data = {
        'name': '新测试学生',
        'gender': 'male',
        'age': 17,
        'student_id': '20230099',
        # ... 其他字段
    }
    
    response = api_client.post(url, data=json.dumps(student_data))
    assert response.status_code == status.HTTP_201_CREATED
```

## 🔍 测试类型

### 1. 单元测试
- 测试单个API端点
- 验证请求/响应格式
- 测试错误处理

### 2. 集成测试
- 测试完整业务流程
- 验证数据一致性
- 测试工作流完整性

### 3. 权限测试
- 测试未授权访问
- 测试角色权限控制
- 测试数据访问权限

## 📈 测试报告

### 生成测试报告
```bash
# 生成HTML报告
pytest tests/ --html=test_reports/report.html --self-contained-html

# 生成覆盖率报告
pytest tests/ --cov=CounselorApp,CounselorAdmin --cov-report=html
```

### 报告位置
- HTML测试报告: `test_reports/report.html`
- 覆盖率报告: `htmlcov/index.html`

## 🐛 常见问题

### 1. 数据库连接失败
**问题**: `django.db.utils.OperationalError: no such table`
**解决**: 确保Django设置正确，测试数据库已创建

### 2. 认证失败
**问题**: `HTTP 401 Unauthorized`
**解决**: 检查测试用户是否正确创建和认证

### 3. 导入错误
**问题**: `ImportError: No module named 'CounselorApp'`
**解决**: 确保项目根目录在Python路径中

### 4. 测试数据冲突
**问题**: 测试数据重复或冲突
**解决**: 使用独立的测试数据库，确保测试隔离

## 🔄 持续集成

### GitHub Actions示例
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-django
    - name: Run tests
      run: python tests/run_tests.py --verbose --coverage
```

## 📞 技术支持

如果遇到测试相关问题，请检查：

1. 依赖包是否安装完整
2. Django设置是否正确配置
3. 测试数据库是否可访问
4. 测试数据是否准备正确

## 🎯 最佳实践

1. **测试命名**: 使用描述性的测试方法名
2. **测试隔离**: 每个测试用例独立运行
3. **数据清理**: 测试后自动清理测试数据
4. **错误处理**: 测试各种边界情况和错误场景
5. **性能考虑**: 避免在测试中创建过多数据

## 📝 版本历史

- v1.0.0: 初始版本，包含完整测试套件
- 支持CounselorApp和CounselorAdmin所有API接口测试
- 提供完整的测试运行和报告生成功能