from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title")
    content = data.get("content")

    missing_fields = []
    if not title:
        missing_fields.append("title")
    if not content:
        missing_fields.append("content")

    if missing_fields:
        return jsonify({
            "error": f"Missing field(s): {', '.join(missing_fields)}"
        }), 400

    new_id = max((post["id"] for post in POSTS), default=0) + 1

    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if post_to_delete is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]

    return jsonify({
        "message": f"Post with id {post_id} has been deleted successfully."
    }), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    # Update title and content optionally; otherwise, keep existing values.
    title = data.get("title", post["title"])
    content = data.get("content", post["content"])

    post["title"] = title
    post["content"] = content

    return jsonify(post), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    matching_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower() if title_query else True) and
           (content_query in post["content"].lower() if content_query else True)
    ]

    return jsonify(matching_posts), 200

@app.route('/api/posts/sorted', methods=['GET'])
def sort_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field:
        if sort_field not in valid_sort_fields:
            return jsonify({"error": f"Invalid sort field: '{sort_field}'"}), 400
        if direction not in valid_directions:
            return jsonify({"error": f"Invalid sort direction: '{direction}'"}), 400

        reverse = direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=reverse)
        return jsonify(sorted_posts), 200

    # Fallback: return unsorted if no sort param is given
    return jsonify(POSTS), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
