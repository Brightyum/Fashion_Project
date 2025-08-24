import sys
import os
from flask_jwt_extended import decode_token
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# sys.path에 프로젝트 루트 폴더가 없으면 추가합니다.
if project_root not in sys.path:
    sys.path.append(project_root)

from flask import Flask, redirect, request, jsonify, render_template, make_response
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)
from dotenv import load_dotenv
from datetime import timedelta

from login_routers.google_auth import GoogleAuth
from login_routers.kakao_auth import KakaoAuth
from login_routers.naver_auth import NaverAuth
from models.token_manager import TokenManager 
from models.user_manager import UserManager

# csrf 사이트 확인

class Server:
    def __init__(self):
        load_dotenv()
        self.app = Flask(__name__, template_folder="../templates")

        # 서버 보안 키 설정
        self.app.secret_key = os.getenv("FLASK_SECRET_KEY")
        # 서버 JWT 설정
        self.app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
        # Access Token 만료 시간 설정
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
        # Refresh Token 만료 시간 설정
        self.app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

        self.jwt = JWTManager(self.app)
        # CORS(
        #     self.app,
        #     supports_credentials=True,
        #     resources={r"*": {"origins": os.getenv("CORS_ALLOW_ORIGINS")}},
        # )

        #개발에서는 HTTP라서 secure=True 쿠키가 전송되지 않음
        #로컬에서만 secure=False로 두고 배포 시 다시 True
        # CORS: React 개발 서버 허용
        CORS(
            self.app,
            supports_credentials=True,
            resources={r"*": {"origins": "http://localhost:5173"}},
        )

        self.token_manager = TokenManager()
        self.user_manager = UserManager()
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
        self.app.add_url_rule(
            "/auth/token/refresh",
            endpoint="token_refresh",
            view_func=self.refresh_token,
            methods=["POST"],
        )
        google_auth = GoogleAuth()
        self.app.register_blueprint(google_auth.blueprint)

        kakao_auth = KakaoAuth()
        self.app.register_blueprint(kakao_auth.blueprint)

        naver_auth = NaverAuth()
        self.app.register_blueprint(naver_auth.blueprint)

        self.app.add_url_rule("/signup", view_func=self.signup_page, methods=["GET"])
        self.app.add_url_rule("/auth/register", view_func=self.register_user, methods=["POST"])


    def login_page(self):
        return render_template("login_page.html")
    
    def signup_page(self):
        return render_template("signup.html")

    def login_func(self):
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

        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        # if self.token_manager.save_refresh_token(user["user_id"], refresh_token):
        #     return jsonify({"ok":False, "error": "토큰 저장 실패"}), 500
        
        # return jsonify({"ok": True, "access_token": access_token, "refresh_token": refresh_token, "user": identity}), 200

        # DB 저장 실패 시 True/False인지 구현에 따라 다를 수 있음 (여기선 False가 정상이라고 가정)
        if self.token_manager.save_refresh_token(user["user_id"], refresh_token):
            return jsonify({"ok": False, "error": "토큰 저장 실패"}), 500

        body = {"ok": True, "access_token": access_token, "user": identity}
        resp = make_response(jsonify(body), 200)

        # 개발환경(HTTP)에서는 secure=False
        resp.set_cookie(
                "refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,        # <---- 로컬에서 False
                samesite="Strict"
            )
        return resp

    # def refresh_token(self):
    #     token = request.headers.get("Authorization")
    #     if not token or not token.startswith("Bearer "):
    #         return jsonify({"msg": "토큰이 누락되었습니다."}), 401
        
    #     refresh_token = token.split(" ")[1]

    #     try:
    #         # 토큰 유효성 검사
    #         verify_jwt_in_request(refresh_token)
    #         # 토큰에서 사용자 정보 추출
    #         identity = get_jwt_identity()

    #         if not self.token_manager.verify_refresh_token(identity["user_id"], refresh_token):
    #             return jsonify({"msg": "유효하지 않은 토큰이므로, 다시 로그인하세요."}), 401
            
    #         new_access_token = create_access_token(identity=identity)
    #         return jsonify({"ok": True, "access_token": new_access_token}), 200
    #     except Exception as e:
    #         return jsonify({"msg": "유효하지 않은 토큰이므로, 다시 로그인하세요."}), 401
    
    
    def refresh_token(self):
        # 1) 쿠키에서 리프레시 토큰 꺼내기
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return jsonify({"ok": False, "msg": "리프레시 토큰 없음"}), 401

        try:
            # 2) 토큰 디코딩(유효성/서명/만료 검증 포함)
            decoded = decode_token(refresh_token)
            identity = decoded["sub"]  # create_*_token(identity=...)에 넣었던 객체

            # 3) DB 보관 토큰과 대조
            uid = identity.get("user_id") or identity.get("userId")
            if not uid or not self.token_manager.verify_refresh_token(uid, refresh_token):
                return jsonify({"ok": False, "msg": "유효하지 않은 토큰, 다시 로그인 필요"}), 401

            # 4) 새 access 토큰 발급
            new_access = create_access_token(identity=identity)
            return jsonify({"ok": True, "access_token": new_access}), 200

        except Exception:
            return jsonify({"ok": False, "msg": "리프레시 토큰 검증 실패"}), 401


    def register_user(self):
        form_data = request.form.to_dict()

        if self.user_manager.get_user_by_email(form_data.get("email")):
            return jsonify({"ok": False, "error": "이미 사용중인 이메일입니다."}), 409
        
        new_user = self.user_manager.create_user(form_data)
        if new_user:
            identity = {
                "userId": new_user["userId"],
                "email": new_user["email"],
                "name": new_user["name"]
            }

        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.token_manager.save_refresh_token(new_user["userId"], refresh_token)
        response_body = {
            "ok": True,
            "msg": "회원가입 및 로그인 성공",
            "access_token": access_token,
            "user": identity
        }
        response = make_response(jsonify(response_body), 201)

        response.set_cookie(
            'refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Strict'
        )
        return response
    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Server().run()
