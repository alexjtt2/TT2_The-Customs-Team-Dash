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
    ps.Description IN ('Pending Information', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
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
    ps.Description IN ('Pending Information', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
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
        ps.Description IN ('Pending Information', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
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
    COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE)) AS Date_For_Status,
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
    ps.Description IN ('Pending Information', 'Under Vendor Review', 'Revision Required', 'Under Customs Review')
    AND (
        (CAST(p.DateSubmitted AS DATE) BETWEEN DATEADD(DAY, -7, '2024-09-05') AND '2024-09-05')
        OR 
        (CAST(p.CreatedAt AS DATE) BETWEEN DATEADD(DAY, -7, '2024-09-05') AND '2024-09-05')
    )
    AND ps.Description != 'CANCELLED'
GROUP BY 
    ps.Description,
    COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE))
HAVING 
    COALESCE(CAST(p.DateSubmitted AS DATE), CAST(p.CreatedAt AS DATE)) BETWEEN DATEADD(DAY, -7, '2024-09-05') AND '2024-09-05'
ORDER BY 
    Date_For_Status, 
    ps.Description;
"""

@app.route('/api/overall_performance_donut_chart', methods=['GET'])
def get_overall_performance_donut_chart():
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(ODBC_CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(DONUT_CHART_QUERY)
            rows = cursor.fetchall()

            # Compute the total count
            total_count = sum(row.Status_Count for row in rows)

            # Process the fetched data into a format suitable for the donut chart
            data = []
            for row in rows:
                product_status = row.Status_Name
                count = row.Status_Count
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                data.append({
                    'name': product_status,
                    'y': count,
                    'percentage': percentage
                })

            # Return the result as JSON
            response = {
                'data': data,
                'total': total_count
            }

            return jsonify(response), 200

    except Exception as e:
        # Log the exception
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
            status_names_set = set()  # Collect unique status names
            for row in rows:
                submitted_date = str(row.Date_For_Status)  # Format the date as a string
                status_name = row.Status_Name
                count = row.Status_Count

                status_names_set.add(status_name)  # Add status name to the set

                if submitted_date not in data:
                    data[submitted_date] = {}

                data[submitted_date][status_name] = count

            # Prepare dates and series for the line chart
            dates = sorted(data.keys())
            status_names = sorted(status_names_set)

            # Build the series data using the dynamic list of status names
            series = []
            for status in status_names:
                series_data = []
                for date in dates:
                    count = data[date].get(status, 0)  # Get count or 0
                    series_data.append(count)
                series.append({'name': status, 'data': series_data})

            # Log the response for debugging
            response = {'categories': dates, 'series': series}
            print("API Response:", response)
            return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/cumulative_performance_spline_line_chart: {e}")
        return jsonify({'error': 'An error occurred while fetching the cumulative performance data.'}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

