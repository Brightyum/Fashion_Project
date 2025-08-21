from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from dotenv import load_dotenv
from datetime import timedelta
import os

from login_routers.google_auth import GoogleAuth
from login_routers.kakao_auth import KakaoAuth
from login_routers.naver_auth import NaverAuth

# csrf 사이트 확인

class Server:
    def __init__(self):
        load_dotenv()
        self.app = Flask(__name__, template_folder="../templates")

        # 서버 보안 키 설정
        self.app.secret_key = os.getenv("FLASK_SECRET_KEY")
        # 서버 JWT 설정
        self.app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
        # 토큰 만료 시간
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

        self.jwt = JWTManager(self.app)
        CORS(
            self.app,
            supports_credentials=True,
            resources={r"*": {"origins": os.getenv("CORS_ALLOW_ORIGINS")}},
        )
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/", view_func=self.login_page)
        self.app.add_url_rule("/login", view_func=self.login_page)
        self.app.add_url_rule(
            "/auth/login-func",
            endpoint="login_func",
            view_func=Server.login_func,
            methods=["POST"],
        )
        google_auth = GoogleAuth()
        self.app.register_blueprint(google_auth.blueprint)

        kakao_auth = KakaoAuth()
        self.app.register_blueprint(kakao_auth.blueprint)

        naver_auth = NaverAuth()
        self.app.register_blueprint(naver_auth.blueprint)

    def login_page(self):
        return render_template("login_page.html")

    @staticmethod
    def login_func():
        # 이후 데이터베이스 연동
        prototype_user = {
            "test@gmail.com": {"name": "염승욱", "user_id": 1},
            "test2@gmail.com": {"name": "홍길동", "user_id": 2},
        }

        data = request.get_json()
        email = data.get("email").strip()
        name = data.get("name").strip()

        if not email or not name:
            return jsonify({"ok": False, "error": "email, name을 입력하세요."}), 400

        user = prototype_user.get(email)
        if not user:
            return jsonify({"ok": False, "error": "등록되지 않은 이메일입니다."}), 401

        if user["name"] != name:
            return jsonify({"ok": False, "error": "등록되지 않은 이름입니다."}), 401

        identity = {
            "user_id": user["user_id"],
            "provider": "proto",
            "email": email,
            "name": name,
        }
        token = create_access_token(identity=identity)
        return jsonify({"ok": True, "token": token, "user": identity}), 200

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Server().run()
