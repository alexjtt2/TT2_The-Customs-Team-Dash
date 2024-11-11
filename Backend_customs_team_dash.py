from flask import Flask, jsonify
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration for SQL Server connection
ODBC_CONNECTION_STRING = (
    'DRIVER={SQL Server};'
    'SERVER=zm2-db01.core.core-business.com;'
    'DATABASE=DemoTT2MandSMasterTest;'
    'Trusted_Connection=yes;'
)

# SQL Query for the Donut Chart 
DONUT_CHART_QUERY = """
SELECT 
    ps.Description AS Status_Name,
    COUNT(*) AS Status_Count
FROM 
    [DemoTT2MandSMasterTest].[dbo].[Product] p
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON pis.ProductId = p.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
WHERE 
    ps.Description IN ('Pending Information', 'Approved and Classified', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
    AND COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE)) = '2024-09-05'
GROUP BY 
    ps.Description
ORDER BY 
    ps.Description;
"""

# SQL Query for the Stacked Column Chart
STACKED_COLUMN_CHART_QUERY_PERFORMANCE_BY_APPAREL_TYPE_TOP_10 = """
SELECT 
    at.Description AS ApparelType_Name,
    ps.Description AS Status_Name,
    COUNT(p.Id) AS Status_Count
FROM 
    [DemoTT2MandSMasterTest].[dbo].[Product] p
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ApparelType] at ON p.ApparelTypeId = at.Id
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON pis.ProductId = p.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
WHERE 
    ps.Description IN ('Pending Information', 'Approved and Classified', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
    AND COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE)) = '2024-09-05'
    AND at.Description != 'UNDEFINED'
GROUP BY 
    at.Description, 
    ps.Description
ORDER BY 
    at.Description, 
    ps.Description;
"""

# SQL Query for the Stacked Horizontal Bar Chart (Performance by Apparel Group)
STACKED_HORIZONTAL_BAR_CHART_QUERY_PERFORMANCE_BY_APPAREL_GROUP_TOP_10 = """
WITH ApparelGroupCounts AS (
    SELECT 
        pg.Description AS ApparelGroup_Name,
        ps.Description AS Status_Name,
        COUNT(*) AS Status_Count
    FROM 
        [DemoTT2MandSMasterTest].[dbo].[Product] p
    INNER JOIN 
        [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
    LEFT JOIN
        [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON pis.ProductId = p.Id
    LEFT JOIN
        [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
    LEFT JOIN
        [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
    WHERE 
        ps.Description IN ('Pending Information', 'Approved and Classified', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
        AND COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE)) = '2024-09-05'
    GROUP BY 
        pg.Description, 
        ps.Description
),
TotalCounts AS (
    SELECT 
        ApparelGroup_Name,
        SUM(Status_Count) AS Total_Count
    FROM 
        ApparelGroupCounts
    GROUP BY 
        ApparelGroup_Name
)
SELECT 
    agc.ApparelGroup_Name,
    agc.Status_Name,
    agc.Status_Count
FROM 
    ApparelGroupCounts agc
INNER JOIN 
    (SELECT TOP 10 ApparelGroup_Name, Total_Count FROM TotalCounts ORDER BY Total_Count DESC) tc 
    ON agc.ApparelGroup_Name = tc.ApparelGroup_Name
ORDER BY 
    tc.Total_Count DESC, 
    agc.ApparelGroup_Name, 
    agc.Status_Name;
"""

# SQL Query for the Cumulative Performance (Spline Line Chart)
CUMULATIVE_PERFORMANCE_QUERY_SPLINE_LINE_CHART = """
SELECT 
    CAST(p.DateSubmitted AS DATE) AS Submitted_Date,
    ps.Description AS Status_Name,
    COUNT(p.Id) AS Status_Count
FROM 
    [DemoTT2MandSMasterTest].[dbo].[Product] p
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON pis.ProductId = p.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
WHERE 
    ps.Description IN ('Pending Information','Under Vendor Review', 'Revision Required', 'Under Customs Review', 'Approved and Classified')  
    AND CAST(p.DateSubmitted AS DATE) BETWEEN DATEADD(DAY, -7, '2024-09-30') AND '2024-09-30'
GROUP BY 
    ps.Description,
    CAST(p.DateSubmitted AS DATE)
ORDER BY 
    Submitted_Date, 
    ps.Description;
"""

# SQL Query for Vendor Performance (Performance by Vendor - Stacked Horizontal Bar Chart)
VENDOR_PERFORMANCE_QUERY = """
SELECT 
	v.CompanyName AS Vendor_Name,	
    ps.Description AS Status_Name,
    COUNT(p.Id) AS Status_Count
FROM 
    [DemoTT2MandSMasterTest].[dbo].[Product] p
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ApparelType] at ON p.ApparelTypeId = at.Id
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[Vendor] v ON p.VendorId = v.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON pis.ProductId = p.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
LEFT JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
WHERE 
    ps.Description IN ('Revision Required', 'Under Customs Review', 'Approved and Classified')  
    AND CAST(p.DateSubmitted AS DATE) = '2024-09-30'
GROUP BY 
	v.CompanyName,
    ps.Description
ORDER BY
	v.CompanyName,
    ps.Description;
"""

# SQL Query for Gantt Chart (Grouping in a Hierarchy)
GANTT_CHART_QUERY = """
SELECT 
    po.[OrderNumber] AS PO_No,
    CONCAT(
        '#', ol.LegacyLineID, ' / ',
        'ID: ', ol.Id, ' / ',
        'UPC: ', ol.UniqueProductCode, ' / ',
        pg.Description, ' / ',
        p.Description, ' / ',
        'Qty: ', ol.OrderQuantity, ' / ',
        'Size: ', ol.PrimarySize
    ) AS PO_Details,
    ps.Description AS Product_Status,
    FORMAT(lit.CreatedAt, 'dd-MM-yy') AS CreatedAt,
    FORMAT(p.DateSubmitted, 'dd-MM-yy') AS DateSubmitted,
    FORMAT(p.DateCompleted, 'dd-MM-yy') AS DateCompleted,
    FORMAT(po.DeliveryDate, 'dd-MM-yy') AS DeliveryDate,
    v.CompanyName AS Vendor
FROM 
    [DemoTT2MandSMasterTest].[dbo].[PurchaseOrder] po
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[Vendor] v ON po.VendorId = v.Id
INNER JOIN 
    [DemoTT2MandSMasterTest].[dbo].[OrderStatus] os ON po.OrderStatusId = os.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[OrderStatusType] ost ON po.OrderStatusTypeId = ost.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[OrderType] ot ON po.OrderTypeId = ot.Id 
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[PackType] pt ON po.PackTypeId = pt.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[Department] dp ON po.DepartmentId = dp.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[OrderLine] ol ON po.Id = ol.OrderId
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[Product] p ON ol.ProductId = p.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductStatus] ps ON p.ProductStatusId = ps.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductItemSet] pis ON ol.ProductId = pis.ProductId
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[LegacyItemType] lit ON pis.LegacyItemTypeId = lit.Id
INNER JOIN
    [DemoTT2MandSMasterTest].[dbo].[ProductGroup] pg ON lit.ProductGroupId = pg.Id
WHERE 
    CAST(p.DateSubmitted AS DATE) BETWEEN DATEADD(DAY, -1, '2024-09-30') AND '2024-09-30'
    AND po.OrderNumber IN ('2031074392', '2031073674')
ORDER BY 
    po.[OrderNumber] DESC;
"""

@app.route('/api/overall_performance_donut_chart', methods=['GET'])
def get_overall_performance_donut_chart():
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(DONUT_CHART_QUERY)
            rows = cursor.fetchall()

            # Process the fetched data into a format suitable for the donut chart
            data = []
            for row in rows:
                product_status = row.Status_Name
                count = row.Status_Count
                data.append({
                    'name': product_status,
                    'y': count
                })

            # Return the result as JSON
            response = {
                'data': data
            }

            return jsonify(response), 200

    except Exception as e:
        # Log the exception (you can enhance this for better logging)
        print(f"Error in /api/overall_performance_donut_chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the donut chart data.'}), 500

@app.route('/api/apparel_performance_top_5_stacked_column__chart', methods=['GET'])
def get_apparel_performance_top_5_stacked_column__chart():
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(STACKED_COLUMN_CHART_QUERY_PERFORMANCE_BY_APPAREL_TYPE_TOP_10)
            rows = cursor.fetchall()

            # Process the fetched data for the stacked column chart
            data = {}
            total_counts = {}
            status_names_set = set()  # Collect unique status names
            for row in rows:
                apparel_type = row.ApparelType_Name
                status_name = row.Status_Name
                count = row.Status_Count

                status_names_set.add(status_name)  # Add status name to the set

                if apparel_type not in data:
                    data[apparel_type] = {}
                    total_counts[apparel_type] = 0

                data[apparel_type][status_name] = count
                total_counts[apparel_type] += count

            # Sort categories based on total count in descending order
            sorted_categories = sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True)

            # Convert the set of status names to a sorted list
            status_names = sorted(status_names_set)

            # Build the series data using the dynamic list of status names
            series = []
            for status in status_names:
                series_data = []
                for category in sorted_categories:
                    series_data.append(data[category].get(status, 0))  # Default to 0 if no count
                series.append({
                    'name': status,
                    'data': series_data
                })

            # Structure the final JSON response
            response = {
                'categories': sorted_categories,
                'series': series
            }

            return jsonify(response), 200

    except Exception as e:
        # Log the exception (you can enhance this for better logging)
        print(f"Error in /api/apparel_performance_top_5_stacked_column__chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the apparel performance data.'}), 500

@app.route('/api/apparel_group_performance_top_5_horizontal_stacked_bar_chart', methods=['GET'])
def get_apparel_group_performance_top_5_horizontal_stacked_bar_chart():
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(STACKED_HORIZONTAL_BAR_CHART_QUERY_PERFORMANCE_BY_APPAREL_GROUP_TOP_10)
            rows = cursor.fetchall()

            # Process the fetched data for the stacked horizontal bar chart
            data = {}
            total_counts = {}
            status_names_set = set()  # Collect unique status names
            for row in rows:
                apparel_group = row.ApparelGroup_Name
                status_name = row.Status_Name
                count = row.Status_Count

                status_names_set.add(status_name)  # Add status name to the set

                if apparel_group not in data:
                    data[apparel_group] = {}
                    total_counts[apparel_group] = 0

                data[apparel_group][status_name] = count
                total_counts[apparel_group] += count

            # Sort categories based on total count in descending order
            categories = sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True)

            # Convert the set of status names to a sorted list
            status_names = sorted(status_names_set)

            # Build the series data using the dynamic list of status names
            series = []
            for status in status_names:
                series_data = []
                for category in categories:
                    count = data[category].get(status, None)  # Get count or None
                    if count not in [None, 0]:
                        series_data.append(count)
                    else:
                        series_data.append(None)  # Maintain alignment with categories
                if any(value is not None for value in series_data):  # Only add series if it has non-None data
                    series.append({
                        'name': status,
                        'data': series_data
                    })

            # Structure the final JSON response
            response = {
                'categories': categories,
                'series': series
            }

            return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/apparel_group_performance_top_5_horizontal_stacked_bar_chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the apparel group performance data.'}), 500


@app.route('/api/cumulative_performance_spline_line_chart', methods=['GET'])
def get_cumulative_performance_spline_line_chart():
    try:
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(CUMULATIVE_PERFORMANCE_QUERY_SPLINE_LINE_CHART)
            rows = cursor.fetchall()

            # Organize data by date and status
            data = {}
            for row in rows:
                submitted_date = str(row.Submitted_Date) # Format the date
                status_name = row.Status_Name
                count = row.Status_Count
                if submitted_date not in data:
                    data[submitted_date] = {}
                data[submitted_date][status_name] = count

            # Prepare dates and series for the line chart
            dates = sorted(data.keys())
            status_names = ['Revision Required', 'Under Customs Review', 'Approved and Classified']
            series = []
            for status in status_names:
                series_data = [data[date].get(status, 0) for date in dates]
                series.append({'name': status, 'data': series_data})

            # Return the result in the format Highcharts expects
            response = {'categories': dates, 'series': series}
            return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/cumulative_performance_spline_line_chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the cumulative performance data.'}), 500

@app.route('/api/vendor_performance', methods=['GET'])
def get_vendor_performance():
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(VENDOR_PERFORMANCE_QUERY)
            rows = cursor.fetchall()

            # Process the fetched data for the chart
            data = {}
            total_counts = {}
            for row in rows:
                vendor_name = row.Vendor_Name
                status_name = row.Status_Name
                count = row.Status_Count

                if vendor_name not in data:
                    data[vendor_name] = {}
                    total_counts[vendor_name] = 0

                data[vendor_name][status_name] = count
                total_counts[vendor_name] += count

            # Sort vendors by total count in descending order
            sorted_vendors = sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True)

            # Prepare the categories and series for the chart
            categories = sorted_vendors
            status_names = ['Revision Required', 'Under Customs Review', 'Approved and Classified']
            series = []
            for status in status_names:
                series_data = []
                for category in categories:
                    count = data[category].get(status, 0)  # Use 0 instead of None
                    series_data.append(count)
                series.append({
                    'name': status,
                    'data': series_data
                })

            # Structure the final JSON response
            response = {
                'categories': categories,
                'series': series
            }

            return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/vendor_performance: {e}")
        return jsonify({'error': 'An error occurred while fetching the vendor performance data.'}), 500


@app.route('/api/gantt_chart', methods=['GET'])
def get_gantt_chart_data():
    try:
        # Connect to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(GANTT_CHART_QUERY)
            rows = cursor.fetchall()

            # Organize data in a parent-child structure
            data = {}
            for row in rows:
                po_number = row.PO_No
                po_details = row.PO_Details
                vendor = row.Vendor
                created_at = row.CreatedAt
                delivery_date = row.DeliveryDate

                if po_number not in data:
                    data[po_number] = {
                        'id': po_number,
                        #'name': po_number,
                        'start': created_at,
                        'end': delivery_date,
                        'vendor': vendor,
                        'collapsed': True,
                        'children': []
                    }

                # Append PO_Details as a child entry
                data[po_number]['children'].append({
                    'id': po_details,
                    #'name': po_details,
                    'start': created_at,
                    'end': delivery_date,
                    'parent': po_number
                })

            response = {'data': list(data.values())}
            return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/gantt_chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the Gantt chart data.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

