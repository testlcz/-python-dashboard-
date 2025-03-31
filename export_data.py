import pandas as pd
import json
from datetime import datetime

def export_data_for_mockplus():
    # 读取数据
    sales_data = pd.read_excel("销售数据.xlsx")
    customer_data = pd.read_excel("客户数据.xlsx")
    product_data = pd.read_excel("产品数据.xlsx")
    region_data = pd.read_excel("地区数据.xlsx")
    
    # 准备dashboard数据
    dashboard_data = {
        "overview": {
            "total_sales": float(sales_data['销售额'].sum()),
            "total_orders": len(sales_data),
            "avg_order_value": float(sales_data['销售额'].mean()),
            "total_customers": len(customer_data),
            "total_products": len(product_data)
        },
        "sales_trend": {
            "dates": sales_data.groupby('日期')['销售额'].sum().reset_index()['日期'].dt.strftime('%Y-%m-%d').tolist(),
            "values": sales_data.groupby('日期')['销售额'].sum().reset_index()['销售额'].tolist()
        },
        "customer_distribution": {
            "types": customer_data['客户类型'].value_counts().index.tolist(),
            "counts": customer_data['客户类型'].value_counts().values.tolist()
        },
        "top_products": {
            "names": sales_data.groupby('产品ID')['数量'].sum().reset_index()
                .merge(product_data, on='产品ID')
                .nlargest(10, '数量')['产品名称'].tolist(),
            "quantities": sales_data.groupby('产品ID')['数量'].sum().reset_index()
                .merge(product_data, on='产品ID')
                .nlargest(10, '数量')['数量'].tolist()
        },
        "region_sales": {
            "regions": sales_data.groupby('地区ID')['销售额'].sum().reset_index()
                .merge(region_data, on='地区ID')['地区名称'].tolist(),
            "sales": sales_data.groupby('地区ID')['销售额'].sum().reset_index()
                .merge(region_data, on='地区ID')['销售额'].tolist()
        }
    }
    
    # 导出为JSON文件
    with open('mockplus_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("数据已导出到 mockplus_data.json")

if __name__ == "__main__":
    export_data_for_mockplus() 