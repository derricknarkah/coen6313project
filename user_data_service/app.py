
from flask import Flask, jsonify, request
from db_utils import secondary_container

app = Flask(__name__)

# Endpoint to fetch data from secondary DB
@app.route('/user_data', methods=['GET'])
def user_data():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    try:
        data = []
        for item in secondary_container.query_items(
                query="SELECT * FROM c WHERE c.user_id=@user_id",
                parameters=[{"name": "@user_id", "value": int(user_id)}],
                enable_cross_partition_query=True):
            data.append(item)

        return jsonify(data), 200

    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
