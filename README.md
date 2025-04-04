# 销售数据分析报表项目

这是一个基于Python的销售数据分析报表项目，使用Streamlit构建交互式Web界面，提供多维度的数据分析功能。

## 功能特点

- 销售概览：展示关键销售指标和趋势
- 客户分析：分析客户分布和特征
- 产品分析：产品销量排行和表现分析
- 地区分析：各地区销售分布情况

## 安装说明

1. 确保已安装Python 3.8或更高版本
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用说明

1. 准备数据文件：
   - 销售数据.xlsx
   - 客户数据.xlsx
   - 产品数据.xlsx
   - 地区数据.xlsx

2. 运行应用：
```bash
streamlit run app.py
```

3. 在浏览器中访问显示的地址（默认为 http://localhost:8501）

## 数据文件格式要求

### 销售数据.xlsx
- 日期：销售日期
- 客户ID：客户唯一标识
- 产品ID：产品唯一标识
- 地区ID：地区唯一标识
- 数量：销售数量
- 销售额：销售金额

### 客户数据.xlsx
- 客户ID：客户唯一标识
- 客户名称：客户名称
- 客户类型：客户类型

### 产品数据.xlsx
- 产品ID：产品唯一标识
- 产品名称：产品名称
- 产品类别：产品类别

### 地区数据.xlsx
- 地区ID：地区唯一标识
- 地区名称：地区名称
- 地区类型：地区类型 
