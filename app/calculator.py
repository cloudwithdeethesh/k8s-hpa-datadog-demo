from flask import Flask, request, jsonify, render_template
from ddtrace import patch_all, tracer
import time
import random
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable automatic instrumentation
patch_all()

app = Flask(__name__)

def trace_operation(operation_type):
    """Decorator to add tracing to calculator operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.trace(f'calculator.{operation_type}', service='calculator-app') as span:
                try:
                    logger.info(f"Processing {operation_type} operation")
                    data = request.get_json()
                    span.set_tag('operation.type', operation_type)
                    logger.info(f"Input values - x: {data.get('x')}, y: {data.get('y')}")
                    span.set_tag('input.x', data.get('x'))
                    span.set_tag('input.y', data.get('y'))

                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    span.set_metric('operation.duration', duration)
                    logger.info(f"Operation completed in {duration:.3f} seconds")
                    return result
                except Exception as e:
                    logger.error(f"Error in {operation_type}: {str(e)}")
                    span.error = 1
                    span.set_tag('error.type', type(e).__name__)
                    span.set_tag('error.msg', str(e))
                    raise
        # Preserve the original function's name and attributes
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator

def simulate_processing():
    """Simulate some processing time"""
    time.sleep(random.uniform(0.1, 0.5))

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/add', methods=['POST'])
@trace_operation('add')
def add():
    try:
        data = request.get_json()
        simulate_processing()
        result = data['x'] + data['y']
        return jsonify({"operation": "add", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/subtract', methods=['POST'])
@trace_operation('subtract')
def subtract():
    try:
        data = request.get_json()
        simulate_processing()
        result = data['x'] - data['y']
        return jsonify({"operation": "subtract", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/multiply', methods=['POST'])
@trace_operation('multiply')
def multiply():
    try:
        data = request.get_json()
        simulate_processing()
        result = data['x'] * data['y']
        return jsonify({"operation": "multiply", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/divide', methods=['POST'])
@trace_operation('divide')
def divide():
    try:
        data = request.get_json()
        simulate_processing()
        if data['y'] == 0:
            raise ValueError("Division by zero!")
        result = data['x'] / data['y']
        return jsonify({"operation": "divide", "result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/calculate', methods=['POST'])
@trace_operation('complex_calculation')
def calculate():
    """Complex calculation that calls multiple operations"""
    try:
        data = request.get_json()
        x = data['x']
        y = data['y']

        with tracer.trace('calculator.steps') as span:
            # Perform multiple operations
            add_result = x + y
            span.set_tag('step.add', add_result)
            simulate_processing()

            mult_result = add_result * 2
            span.set_tag('step.multiply', mult_result)
            simulate_processing()

            sub_result = mult_result - y
            span.set_tag('step.subtract', sub_result)
            simulate_processing()

            if y != 0:
                final_result = sub_result / y
            else:
                final_result = sub_result

            span.set_tag('step.final', final_result)

            return jsonify({
                "input": {"x": x, "y": y},
                "steps": {
                    "add": add_result,
                    "multiply": mult_result,
                    "subtract": sub_result,
                    "final": final_result
                }
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Allow overriding the port via environment variable; default to 8000
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)