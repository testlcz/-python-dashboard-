# 标准库
import os
from datetime import datetime, timedelta
import io
import base64
import pyperclip

# 数据处理和科学计算
import pandas as pd
import numpy as np

# 数据可视化
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Web应用框架
import streamlit as st

# 导入导出功能
from export_data import export_data_for_mockplus
from export import generate_excel_report

# 设置页面配置
st.set_page_config(
    page_title="零售数据分析仪表板",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric:hover {
        transform: translateY(-2px);
        transition: transform 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# 标题
st.title("🛍️ 零售数据分析仪表板")

# 数据加载函数
@st.cache_data
def load_data():
    try:
        # 检查文件是否存在
        required_files = ["stores data-set.csv", "sales data-set.csv", "Features data set.csv"]
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"找不到文件: {file}")
        
        # 读取数据
        stores_data = pd.read_csv("stores data-set.csv")
        sales_data = pd.read_csv("sales data-set.csv")
        store_data = pd.read_csv("Features data set.csv")
        
        # 确保日期列格式正确
        if 'Date' in sales_data.columns:
            sales_data['Date'] = pd.to_datetime(sales_data['Date']).dt.date
        if 'Date' in store_data.columns:
            store_data['Date'] = pd.to_datetime(store_data['Date']).dt.date
        
        return stores_data, sales_data, store_data
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None

# 复制数据函数
def copy_to_clipboard(df):
    # 将DataFrame转换为CSV格式的字符串
    csv_data = df.to_csv(index=False)
    # 复制到剪贴板
    pyperclip.copy(csv_data)
    return True

# 加载数据
stores_data, sales_data, store_data = load_data()

if stores_data is not None and sales_data is not None and store_data is not None:
    # 创建侧边栏
    st.sidebar.header("🔍 数据筛选")
    
    # 日期范围选择
    min_date = sales_data['Date'].min()
    max_date = sales_data['Date'].max()
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 门店类型筛选
    store_types = stores_data['Type'].unique()
    selected_types = st.sidebar.multiselect(
        "选择门店类型",
        options=store_types,
        default=store_types
    )
    
    # 部门筛选
    departments = sales_data['Dept'].unique()
    selected_depts = st.sidebar.multiselect(
        "选择部门",
        options=departments,
        default=departments
    )
    
    # 应用筛选
    filtered_sales = sales_data[
        (sales_data['Date'] >= date_range[0]) &
        (sales_data['Date'] <= date_range[1])
    ]
    
    # 合并数据
    filtered_sales = filtered_sales.merge(stores_data, on='Store')
    filtered_sales = filtered_sales.merge(store_data, on=['Store', 'Date'], how='left')
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_sales = filtered_sales['Weekly_sales'].sum()
        st.metric("总销售额", f"¥{total_sales:,.2f}")
    with col2:
        total_stores = len(filtered_sales['Store'].unique())
        st.metric("门店数量", f"{total_stores:,}")
    with col3:
        avg_store_size = filtered_sales['Size'].mean()
        st.metric("平均门店面积", f"{avg_store_size:,.0f}")
    with col4:
        total_depts = len(filtered_sales['Dept'].unique())
        st.metric("部门数量", f"{total_depts:,}")
    
    # 创建两列布局
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 销售趋势图
        st.subheader("📈 销售趋势")
        sales_trend = filtered_sales.groupby('Date')['Weekly_sales'].sum().reset_index()
        fig_trend = px.line(
            sales_trend,
            x='Date',
            y='Weekly_sales',
            title='每周销售趋势',
            template='plotly_white'
        )
        fig_trend.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 门店类型分布
        st.subheader("🏪 门店类型分布")
        type_sales = filtered_sales.groupby('Type')['Weekly_sales'].sum()
        fig_type = px.pie(
            values=type_sales.values,
            names=type_sales.index,
            title='各类型门店销售额分布',
            template='plotly_white'
        )
        fig_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col_right:
        # 部门销售排行
        st.subheader("🏆 部门销售排行")
        dept_sales = filtered_sales.groupby('Dept')['Weekly_sales'].sum().reset_index()
        top_depts = dept_sales.nlargest(10, 'Weekly_sales')
        fig_dept = px.bar(
            top_depts,
            x='Dept',
            y='Weekly_sales',
            title='Top 10 部门销售额',
            template='plotly_white'
        )
        fig_dept.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_dept, use_container_width=True)
        
        # 油价与销售关系
        st.subheader("⛽ 油价与销售关系")
        fig_fuel = px.scatter(
            filtered_sales,
            x='Fuel_price',
            y='Weekly_sales',
            title='油价与销售额关系',
            template='plotly_white'
        )
        st.plotly_chart(fig_fuel, use_container_width=True)
    
    # 底部详细数据表格
    st.subheader("📋 详细数据")
    tab1, tab2, tab3 = st.tabs(["门店数据", "销售数据", "环境数据"])
    
    with tab1:
        st.dataframe(stores_data)
        if st.button("复制门店数据", key="copy_stores"):
            if copy_to_clipboard(stores_data):
                st.success("门店数据已复制到剪贴板！")
    
    with tab2:
        st.dataframe(filtered_sales)
        if st.button("复制销售数据", key="copy_sales"):
            if copy_to_clipboard(filtered_sales):
                st.success("销售数据已复制到剪贴板！")
    
    with tab3:
        st.dataframe(store_data)
        if st.button("复制环境数据", key="copy_env"):
            if copy_to_clipboard(store_data):
                st.success("环境数据已复制到剪贴板！")
    
    # 导出功能
    st.sidebar.header("📥 数据导出")
    if st.sidebar.button("导出分析报告"):
        # 生成Excel报告
        excel_data = generate_excel_report(stores_data, sales_data, store_data)
        
        # 创建下载按钮
        st.sidebar.download_button(
            label="下载Excel报告",
            data=excel_data,
            file_name=f"零售数据分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # 生成Mockplus数据
        export_data_for_mockplus(stores_data, sales_data, store_data)
        
        st.sidebar.success("报告生成成功！")

else:
    st.error("数据加载失败，请检查数据文件是否存在且格式正确。")
    st.info("请确保以下文件已正确放置在项目目录中：")
    st.info("- stores data-set.csv\n- sales data-set.csv\n- Features data set.csv")
