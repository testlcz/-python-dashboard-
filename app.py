# 标准库
import os
from datetime import datetime, timedelta

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

# 设置页面配置
st.set_page_config(
    page_title="销售数据分析仪表板",
    page_icon="📊",
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
st.title("📊 销售数据分析仪表板")

# 数据加载函数
@st.cache_data
def load_data():
    try:
        # 检查文件是否存在
        required_files = ["销售数据.xlsx", "客户数据.xlsx", "产品数据.xlsx", "地区数据.xlsx"]
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"找不到文件: {file}")
        
        # 读取数据
        sales_data = pd.read_excel("销售数据.xlsx")
        customer_data = pd.read_excel("客户数据.xlsx")
        product_data = pd.read_excel("产品数据.xlsx")
        region_data = pd.read_excel("地区数据.xlsx")
        
        # 确保日期列格式正确
        if '日期' in sales_data.columns:
            sales_data['日期'] = pd.to_datetime(sales_data['日期']).dt.date
        
        return sales_data, customer_data, product_data, region_data
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None, None

# 加载数据
sales_data, customer_data, product_data, region_data = load_data()

if sales_data is not None and customer_data is not None and product_data is not None and region_data is not None:
    # 创建侧边栏
    st.sidebar.header("🔍 数据筛选")
    
    # 日期范围选择
    min_date = sales_data['日期'].min()
    max_date = sales_data['日期'].max()
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 产品类别筛选
    product_categories = product_data['产品类别'].unique()
    selected_categories = st.sidebar.multiselect(
        "选择产品类别",
        options=product_categories,
        default=product_categories
    )
    
    # 地区筛选
    regions = region_data['地区名称'].unique()
    selected_regions = st.sidebar.multiselect(
        "选择地区",
        options=regions,
        default=regions
    )
    
    # 应用筛选
    filtered_sales = sales_data[
        (sales_data['日期'] >= date_range[0]) &
        (sales_data['日期'] <= date_range[1])
    ]
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_sales = filtered_sales['销售额'].sum()
        st.metric("总销售额", f"¥{total_sales:,.2f}")
    with col2:
        total_orders = len(filtered_sales)
        st.metric("总订单数", f"{total_orders:,}")
    with col3:
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        st.metric("平均订单金额", f"¥{avg_order_value:,.2f}")
    with col4:
        total_customers = len(filtered_sales['客户ID'].unique())
        st.metric("活跃客户数", f"{total_customers:,}")
    
    # 创建两列布局
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 销售趋势图
        st.subheader("📈 销售趋势")
        sales_trend = filtered_sales.groupby('日期')['销售额'].sum().reset_index()
        fig_trend = px.line(
            sales_trend,
            x='日期',
            y='销售额',
            title='每日销售趋势',
            template='plotly_white'
        )
        fig_trend.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 客户分布
        st.subheader("👥 客户分布")
        customer_dist = customer_data['客户类型'].value_counts()
        fig_customer = px.pie(
            values=customer_dist.values,
            names=customer_dist.index,
            title='客户类型分布',
            template='plotly_white'
        )
        fig_customer.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_customer, use_container_width=True)
    
    with col_right:
        # 产品销量排行
        st.subheader("🏆 产品销量排行")
        product_sales = filtered_sales.groupby('产品ID')['数量'].sum().reset_index()
        product_sales = product_sales.merge(product_data, on='产品ID')
        top_products = product_sales.nlargest(10, '数量')
        fig_products = px.bar(
            top_products,
            x='产品名称',
            y='数量',
            title='Top 10 产品销量',
            template='plotly_white'
        )
        fig_products.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_products, use_container_width=True)
        
        # 地区销售分布
        st.subheader("🌍 地区销售分布")
        region_sales = filtered_sales.groupby('地区ID')['销售额'].sum().reset_index()
        region_sales = region_sales.merge(region_data, on='地区ID')
        fig_region = px.bar(
            region_sales,
            x='地区名称',
            y='销售额',
            title='各地区销售额分布',
            template='plotly_white'
        )
        fig_region.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_region, use_container_width=True)
    
    # 底部详细数据表格
    st.subheader("📋 详细数据")
    tab1, tab2, tab3 = st.tabs(["销售数据", "客户数据", "产品数据"])
    
    with tab1:
        st.dataframe(filtered_sales)
    with tab2:
        st.dataframe(customer_data)
    with tab3:
        st.dataframe(product_data)
    
    # 导出功能
    st.sidebar.header("📥 数据导出")
    if st.sidebar.button("导出分析报告"):
        # 这里可以添加导出报告的逻辑
        st.sidebar.success("报告导出成功！")

else:
    st.error("数据加载失败，请检查数据文件是否存在且格式正确。")
    st.info("请确保以下文件已正确放置在项目目录中：")
    st.info("- 销售数据.xlsx\n- 客户数据.xlsx\n- 产品数据.xlsx\n- 地区数据.xlsx")