# python-reporter：一个可以保存Python脚本任何中间结果的工具。

在执行一个Python脚本时，如果需要的获取程序运行的一些中间结果，往往没有什么好的办法。例如，在xxx程序中以xxx计算中位数，
这个中位数只是一个中间变量。如果在其他地方需要这个中位数，一种常见的做法是把这个中位数打印出来。但是这种方法不适用于大量中间数据
的情况，`python-reporter`致力于解决这个问题。

## 安装

```
pip install python-reporter
```

## 使用

### 读取报告

```python
import reporter


report_id = 'xxx'
report = reporter.Report(report_id)
report.foo  # 第一种方法
report.get('foo')  # 第二种方法
report.pop('foo')  # 第三种方法
```

### 保存报告

```python
import reporter


report = reporter.Report()
report << ('foo', 'bar')  # 第一种方法
report + ('hello', 'world')  # 第二种方法
report.add('foobar', 'foobar')  # 第三种方法
report_id = report.save()
```

第一种、第二种方法，传入的必须是长度为2的元组或列表，第一个元素是变量名称、第二个元素是变量的值。
由于变量需要保存，所以变量必须是可序列化的。

### 保存方式

`reporter`支持两种种保存方式：

1. `DatabaseBackend`，即变量保存到数据库（默认）
2. `FileBackend`，即变量以json形式保存到文件中

#### DatabaseBackend

注意：需要先初始化数据库。例如：

```python
backend = reporter.DatabaseBackend('sqlite:////path/to/reporter.db')
backend.create_table()
```

1. 在程序内部指定数据库连接

```
report = reporter.Report(
    backend=reporter.DatabaseBackend('sqlite:////path/to/reporter.db')
)
```

2. 通过环境变量指定数据库连接

```shell
export REPORTER_DB_URL = 'sqlite:////path/to/reporter.db'
```

```python
report = reporter.Report()
```

3. 使用默认数据库连接（即保存SQLite文件到当前目录）

```python
report = reporter.Report()
```

#### FileBackend

1. 在程序内部指定保存地址

```python
report = reporter.Report(backend=reporter.FileBackend('/path/to/reporter'))
```

那么报告以文件保存到`/path/to/reporter/`文件夹下，文件名为`reporter-report-xxx.json`。

2. 通过环境变量指定保存地址

```shell
export REPORTER_DIR=/path/to/reporter
```

```python
report = reporter.Report(backend=reporter.FileBackend())
```

那么报告以文件保存到`/path/to/reporter/`文件夹下，文件名为`reporter-report-xxx.json`。

3. 使用默认目录（即当前目录）

```python
report = reporter.Report(backend=reporter.FileBackend())
```

那么报告以文件保存到当前目录下，文件名为`reporter-report-xxx.json`。

### 如何自定义保存方式

`reporter`默认支持`FileBackend`，如果需要以其他方式保存，可以自定义`Backend`，继承自`reporter.Backend`，且
实现`load(report_id)`、`save(report_id, data)`两个方法即可。

```python
class MyBackend(reporter.Backend):
    def load(self, report_id):
        pass

    def save(self, report_id, data):
        pass


report = reporter.Report(backend=MyBackend())
```
