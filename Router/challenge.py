# wait for schemas.py
from flask import Flask, request, jsonify, make_response
from models import Challenge
from schemas import ChallengeSchema
import json

app = Flask(__name__)


@app.route('/challenges', methods=['POST'])
def create_challenge():
    data = request.json
    challenge_schema = ChallengeSchema()
    try:
        challenge_data = challenge_schema.load(data)
        # 假设我们有一个add_challenge函数负责处理新Challenge的逻辑
        challenge = add_challenge(challenge_data)
        return jsonify(challenge_schema.dump(challenge)), 201
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify(str(e)), 500
    


@app.route('/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    try:
        # 假设我们有一个get_challenge_by_id函数来检索挑战
        challenge = get_challenge_by_id(challenge_id)
        challenge_schema = ChallengeSchema()
        return jsonify(challenge_schema.dump(challenge))
    except ChallengeNotFoundError:
        return jsonify({"message": "Challenge not found"}), 404
    except Exception as e:
        return jsonify(str(e)), 500
    


@app.route('/challenges', methods=['GET'])
def get_challenges():
    try:
        # 假设我们有一个get_all_challenges函数来获取所有挑战
        challenges = get_all_challenges()
        challenge_schema = ChallengeSchema(many=True)
        return jsonify(challenge_schema.dump(challenges))
    except Exception as e:
        return jsonify(str(e)), 500
    


@app.route('/challenges/<int:challenge_id>', methods=['PUT'])
def update_challenge(challenge_id):
    data = request.json
    challenge_schema = ChallengeSchema()
    try:
        challenge_data = challenge_schema.load(data)
        # 假设我们有一个update_challenge_by_id函数来更新挑战
        challenge = update_challenge_by_id(challenge_id, challenge_data)
        return jsonify(challenge_schema.dump(challenge))
    except ValidationError as e:
        return jsonify(e.messages), 400
    except ChallengeNotFoundError:
        return jsonify({"message": "Challenge not found"}), 404
    except Exception as e:
        return jsonify(str(e)), 500

@app.route('/challenges/<int:challenge_id>', methods=['DELETE'])
def delete_challenge(challenge_id):
    try:
        # 假设我们有一个delete_challenge_by_id函数来删除挑战
        delete_challenge_by_id(challenge_id)
        return jsonify({}), 204
    except ChallengeNotFoundError:
        return jsonify({"message": "Challenge not found"}), 404
    except Exception as e:
        return jsonify(str(e)), 500
    
    

# 处理错误
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

if __name__ == '__main__':
    app.run(debug=True)
