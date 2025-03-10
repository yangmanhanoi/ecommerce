from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define the URLs of your microservices (inside Docker or your network)
MICROSERVICES = {
    "customer": "http://customer_service:8000",
    "cart": "http://cart_service:8001",
    "order": "http://order_service:8002",
    "payment": "http://payment_service:8003",
    "shipping": "http://shipping_service:8004",
    "product": "http://product_service:8005"
}

def forward_request(service, endpoint):
    """Forward request to the respective microservice"""
    url = f"{MICROSERVICES[service]}{endpoint}"
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key != "Host"},
            json=request.get_json(),
            params=request.args
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Service {service} unavailable"}), 503


@app.route("/auth/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE"])
def auth_proxy(endpoint):
    return forward_request("auth", f"/{endpoint}")

@app.route("/product/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE"])
def product_proxy(endpoint):
    return forward_request("product", f"/{endpoint}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)