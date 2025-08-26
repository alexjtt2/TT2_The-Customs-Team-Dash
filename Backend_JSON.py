from flask import Blueprint, jsonify
import logging
import os
import json
from flask_cors import CORS

json_api = Blueprint('json_api', __name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

#=================================================KPI CARDS======================================================

@json_api.route('/api/kpi_cards', methods=['GET'])
def get_kpi_cards():
    """Get KPI cards data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing KPI cards data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\kpi_cards.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if not isinstance(data, list):
            logging.error(f"Invalid JSON structure: Expected a list at the root.")
            return jsonify({'error': 'Invalid data format: Expected a list of KPI cards.'}), 500
        required_keys = {'status_name', 'earliest_count', 'latest_count', 'count_change', 'percentage_change'}
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                logging.error(f"Invalid KPI card format at index {idx}: Expected a dictionary.")
                return jsonify({'error': f'Invalid data format: KPI card at index {idx} is not a dictionary.'}), 500
            missing_keys = required_keys - item.keys()
            if missing_keys:
                logging.error(f"Missing keys in KPI card at index {idx}: {missing_keys}")
                return jsonify({'error': f'Invalid data format: KPI card at index {idx} is missing keys {missing_keys}.'}), 500
            if not isinstance(item['status_name'], str):
                logging.error(f"Invalid type for 'status_name' in KPI card at index {idx}: Expected string.")
                return jsonify({'error': f'Invalid data type: "status_name" in KPI card at index {idx} must be a string.'}), 500
            if not isinstance(item['earliest_count'], int):
                logging.error(f"Invalid type for 'earliest_count' in KPI card at index {idx}: Expected integer.")
                return jsonify({'error': f'Invalid data type: "earliest_count" in KPI card at index {idx} must be an integer.'}), 500
            if not isinstance(item['latest_count'], int):
                logging.error(f"Invalid type for 'latest_count' in KPI card at index {idx}: Expected integer.")
                return jsonify({'error': f'Invalid data type: "latest_count" in KPI card at index {idx} must be an integer.'}), 500
            if not isinstance(item['count_change'], int):
                logging.error(f"Invalid type for 'count_change' in KPI card at index {idx}: Expected integer.")
                return jsonify({'error': f'Invalid data type: "count_change" in KPI card at index {idx} must be an integer.'}), 500
            if not isinstance(item['percentage_change'], (int, float)):
                logging.error(f"Invalid type for 'percentage_change' in KPI card at index {idx}: Expected float.")
                return jsonify({'error': f'Invalid data type: "percentage_change" in KPI card at index {idx} must be a number.'}), 500
        return jsonify(data), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in KPI Cards endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in KPI Cards endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

#=========================================OVERALL PERFORMANCE DOUT CHART======================================================

@json_api.route('/api/overall_performance_donut_chart', methods=['GET'])
def get_overall_performance_donut_chart():
    """Get overall performance donut chart data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing donut chart data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\overall_performance_donut_chart.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if 'data' not in data or not isinstance(data['data'], list):
            logging.error(f"'data' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "data".'}), 500
        if 'total' not in data or not isinstance(data['total'], (int, float)):
            logging.error(f"'total' key missing or not a number in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "total".'}), 500
        for entry in data['data']:
            if 'name' not in entry or 'y' not in entry:
                logging.error(f"Invalid data entry format in JSON file: {entry}")
                return jsonify({'error': 'Invalid data format: each data entry must contain "name" and "y".'}), 500
            if not isinstance(entry['y'], (int, float)):
                logging.error(f"'y' field in data entry is not a number: {entry}")
                return jsonify({'error': 'Invalid data format: "y" field in data entries must be a number.'}), 500
        return jsonify(data), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in overall performance donut chart endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in overall performance donut chart endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500


#=========================================APPAREL PERFORMANCE TOP 10 STACKED COLUMN CHART======================================================

@json_api.route('/api/apparel_performance_top_10_stacked_column__chart', methods=['GET'])
def get_apparel_performance_top_10_stacked_column__chart():
    """Get apparel performance top 10 stacked column chart data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing stacked column chart data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\item_type_group.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if 'categories' not in data or not isinstance(data['categories'], list):
            logging.error(f"'categories' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "categories".'}), 500
        if 'series' not in data or not isinstance(data['series'], list):
            logging.error(f"'series' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "series".'}), 500
        for series_entry in data['series']:
            if 'name' not in series_entry or 'data' not in series_entry:
                logging.error(f"Invalid series entry format in JSON file: {series_entry}")
                return jsonify({'error': 'Invalid data format: series entries must contain "name" and "data".'}), 500
            if not isinstance(series_entry['data'], list):
                logging.error(f"'data' field in series entry is not a list: {series_entry}")
                return jsonify({'error': 'Invalid data format: "data" field in series must be a list.'}), 500
        num_categories = len(data['categories'])
        for series_entry in data['series']:
            if len(series_entry['data']) != num_categories:
                logging.error(f"Data length mismatch in series '{series_entry['name']}': expected {num_categories}, got {len(series_entry['data'])}")
                return jsonify({'error': f'Data length mismatch in series "{series_entry["name"]}".'}), 500
        return jsonify(data), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in apparel performance top 10 stacked column chart endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in apparel performance top 10 stacked column chart endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    
#=========================================APPAREL GROUP PERFORMANCE TOP 10 HORIZONTAL STACKED BAR CHART======================================================

@json_api.route('/api/apparel_group_performance_top_10_horizontal_stacked_bar_chart', methods=['GET'])
def get_apparel_group_performance_top_10_horizontal_stacked_bar_chart():
    """Get apparel group performance top 10 horizontal stacked bar chart data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing horizontal stacked bar chart data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\item_attribute_performance.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if 'categories' not in data or not isinstance(data['categories'], list):
            logging.error(f"'categories' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "categories".'}), 500
        if 'series' not in data or not isinstance(data['series'], list):
            logging.error(f"'series' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "series".'}), 500
        total_counts = {category: 0 for category in data['categories']}
        for series_entry in data['series']:
            for idx, value in enumerate(series_entry['data']):
                if value is not None:
                    total_counts[data['categories'][idx]] += value
        sorted_categories = sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True)
        sorted_series = []
        for series_entry in data['series']:
            sorted_data = [series_entry['data'][data['categories'].index(category)] for category in sorted_categories]
            sorted_series.append({'name': series_entry['name'], 'data': sorted_data})
        response = {
            'categories': sorted_categories,
            'series': sorted_series
        }
        return jsonify(response), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in apparel group performance top 10 horizontal stacked bar chart endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in apparel group performance top 10 horizontal stacked bar chart endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500


#=========================================ITEM TYPE PERFORMANCE TOP 10 HORIZONTAL STACKED BAR CHART======================================================

@json_api.route('/api/item_type_performance_top_10_horizontal_stacked_bar_chart', methods=['GET'])
def get_item_type_performance_top_10_stacked_horizontal_bar_chart():
    """Get item type performance top 10 horizontal stacked bar chart data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing item type stacked bar chart data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\item_types_performance.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if 'categories' not in data or not isinstance(data['categories'], list):
            logging.error(f"'categories' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "categories".'}), 500
        if 'series' not in data or not isinstance(data['series'], list):
            logging.error(f"'series' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "series".'}), 500
        total_counts = {category: 0 for category in data['categories']}
        for series_entry in data['series']:
            for idx, value in enumerate(series_entry['data']):
                if value is not None:
                    total_counts[data['categories'][idx]] += value
        sorted_categories = sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True)
        sorted_series = []
        for series_entry in data['series']:
            sorted_data = [
                series_entry['data'][data['categories'].index(category)] if series_entry['data'][data['categories'].index(category)] != 0 else None
                for category in sorted_categories
            ]
            sorted_series.append({'name': series_entry['name'], 'data': sorted_data})
        response = {
            'categories': sorted_categories,
            'series': sorted_series
        }
        return jsonify(response), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in item type performance endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in item type performance endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    

#=========================================CUMULATIVE PERFORMANCE STACKED AREA CHART======================================================
@json_api.route('/api/cumulative_performance_stacked_area_chart', methods=['GET'])
def get_cumulative_performance_stacked_area_chart():
    """Get cumulative performance stacked area chart data from JSON file.

    Returns
    -------
    flask.Response
        JSON response containing stacked area chart data or error message.
    """
    try:
        json_path = 'Brainstorm_dataset\\cumulative_performance_stacked_area_chart.json'
        if not os.path.exists(json_path):
            logging.error(f"JSON file not found at path: {json_path}")
            return jsonify({'error': 'Data file not found.'}), 500
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if 'categories' not in data or not isinstance(data['categories'], list):
            logging.error(f"'categories' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "categories".'}), 500
        if 'series' not in data or not isinstance(data['series'], list):
            logging.error(f"'series' key missing or not a list in JSON file: {json_path}")
            return jsonify({'error': 'Invalid data format: missing or incorrect "series".'}), 500
        for series_entry in data['series']:
            if 'name' not in series_entry or 'data' not in series_entry:
                logging.error(f"Invalid series entry format in JSON file: {series_entry}")
                return jsonify({'error': 'Invalid data format: series entries must contain "name" and "data".'}), 500
            if not isinstance(series_entry['data'], list):
                logging.error(f"'data' field in series entry is not a list: {series_entry}")
                return jsonify({'error': 'Invalid data format: "data" field in series must be a list.'}), 500
        num_categories = len(data['categories'])
        for series_entry in data['series']:
            if len(series_entry['data']) != num_categories:
                logging.error(f"Data length mismatch in series '{series_entry['name']}': expected {num_categories}, got {len(series_entry['data'])}")
                return jsonify({'error': f'Data length mismatch in series "{series_entry["name"]}".'}), 500
        return jsonify(data), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in cumulative performance stacked area chart endpoint: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 500
    except Exception as e:
        logging.error(f"Error in cumulative performance stacked area chart endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.register_blueprint(json_api)
    app.run(debug=True, host='0.0.0.0', port=5000)
