import pandas as pd
import json
from datetime import datetime

def export_data_for_mockplus(stores_data, sales_data, store_data):
    # 数据预处理
    sales_data = sales_data.copy()
    store_data = store_data.copy()
    stores_data = stores_data.copy()
    
    # 日期转换
    sales_data['Date'] = pd.to_datetime(sales_data['Date'])
    store_data['Date'] = pd.to_datetime(store_data['Date'])
    
    # 合并数据
    merged_data = sales_data.merge(stores_data, on='Store')
    merged_data = merged_data.merge(store_data, on=['Store', 'Date'], how='left')
    
    # 计算基础指标
    total_sales = float(sales_data['Weekly_Sales'].sum())
    total_stores = int(len(stores_data))
    avg_store_size = float(stores_data['Size'].mean())
    total_depts = int(len(sales_data['Dept'].unique()))
    
    # 计算门店类型分析
    store_analysis = merged_data.groupby('Type').agg({
        'Weekly_Sales': ['sum', 'mean'],
        'Store': 'count'
    })
    store_analysis.columns = ['total_sales', 'avg_sales', 'store_count']
    store_analysis = store_analysis.reset_index()
    
    # 计算部门分析
    dept_analysis = merged_data.groupby('Dept').agg({
        'Weekly_Sales': ['sum', 'mean'],
        'Store': 'nunique'
    })
    dept_analysis.columns = ['total_sales', 'avg_sales', 'store_count']
    dept_analysis = dept_analysis.reset_index()
    
    # 计算环境因素相关性
    env_correlation = merged_data[['Weekly_Sales', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment']].corr()
    
    # 准备dashboard数据
    dashboard_data = {
        "overview": {
            "total_sales": total_sales,
            "total_stores": total_stores,
            "avg_store_size": avg_store_size,
            "total_depts": total_depts,
            "avg_sales_per_store": total_sales / total_stores if total_stores > 0 else 0,
            "avg_sales_per_dept": total_sales / total_depts if total_depts > 0 else 0
        },
        "sales_trend": {
            "dates": merged_data.groupby('Date')['Weekly_Sales'].sum().index.strftime('%Y-%m-%d').tolist(),
            "values": merged_data.groupby('Date')['Weekly_Sales'].sum().tolist(),
            "avg_daily_sales": float(merged_data.groupby('Date')['Weekly_Sales'].sum().mean())
        },
        "store_analysis": {
            "types": store_analysis['Type'].tolist(),
            "counts": store_analysis['store_count'].tolist(),
            "total_sales": store_analysis['total_sales'].tolist(),
            "avg_sales": store_analysis['avg_sales'].tolist()
        },
        "department_analysis": {
            "names": dept_analysis['Dept'].tolist(),
            "total_sales": dept_analysis['total_sales'].tolist(),
            "avg_sales": dept_analysis['avg_sales'].tolist(),
            "store_count": dept_analysis['store_count'].tolist()
        },
        "environment_analysis": {
            "dates": store_data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            "temperature": store_data['Temperature'].tolist(),
            "fuel_price": store_data['Fuel_Price'].tolist(),
            "cpi": store_data['CPI'].tolist(),
            "unemployment": store_data['Unemployment'].tolist(),
            "correlations": {
                "temperature": float(env_correlation.loc['Weekly_Sales', 'Temperature']),
                "fuel_price": float(env_correlation.loc['Weekly_Sales', 'Fuel_Price']),
                "cpi": float(env_correlation.loc['Weekly_Sales', 'CPI']),
                "unemployment": float(env_correlation.loc['Weekly_Sales', 'Unemployment'])
            }
        },
        "holiday_analysis": {
            "holiday_sales": float(merged_data[merged_data['IsHoliday'] == True]['Weekly_Sales'].mean()),
            "non_holiday_sales": float(merged_data[merged_data['IsHoliday'] == False]['Weekly_Sales'].mean()),
            "holiday_impact": float((
                merged_data[merged_data['IsHoliday'] == True]['Weekly_Sales'].mean() /
                merged_data[merged_data['IsHoliday'] == False]['Weekly_Sales'].mean() - 1
            ) * 100) if len(merged_data[merged_data['IsHoliday'] == False]) > 0 else 0
        }
    }
    
    # 导出为JSON文件
    with open('mockplus_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("数据已导出到 mockplus_data.json")

# 用于独立测试
if __name__ == "__main__":
    # 读取数据
    stores_data = pd.read_csv("stores data-set.csv")
    sales_data = pd.read_csv("sales data-set.csv")
    store_data = pd.read_csv("Features data set.csv")
    
    # 调用导出函数
    export_data_for_mockplus(stores_data, sales_data, store_data)