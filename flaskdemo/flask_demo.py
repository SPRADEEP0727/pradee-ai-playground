from flask import Flask, request, jsonify

app = Flask(__name__)

# GET API
@app.route('/add', methods=['GET'])
def add():
    num1 = int(request.args.get('num1'))
    num2 = int(request.args.get('num2'))

    result = num1 + num2

    return jsonify({
        "operation": "addition",
        "num1": num1,
        "num2": num2,
        "result": result
    })


# POST API
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json

    num1 = data.get("num1")
    num2 = data.get("num2")
    operation = data.get("operation")

    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        if num2 == 0:
            return jsonify({"error": "division by zero not allowed"})
        result = num1 / num2
    else:
        return jsonify({"error": "invalid operation"})

    return jsonify({
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": result
    })


if __name__ == "__main__":
    app.run(debug=True)