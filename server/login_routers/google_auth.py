from flask import Blueprint, redirect, request, jsonify, url_for
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv
import os
import requests


class GoogleAuth:
    def __init__(self):
        load_dotenv()
        self.blueprint = Blueprint("google_auth", __name__)

        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        self.blueprint.add_url_rule("/auth/google/login", view_func=self.login)
        self.blueprint.add_url_rule("/auth/google/callback", view_func=self.callback)

    def login(self):
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
        )
        return redirect(google_auth_url)

    def callback(self):
        # 1) Google이 보낸 인증 코드 받기
        code = request.args.get("code")
        if not code:
            return jsonify({"ok": False, "error": "구글 인증 코드가 없습니다."}), 400

        # 2) Google 토큰 엔드포인트로 요청 보내기
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        token_res = requests.post(token_url, data=data).json()
        id_token = token_res.get("id_token")
        access_token = token_res.get("access_token")

        if not id_token:
            return (
                jsonify(
                    {"ok": False, "error": "구글 토큰 발급 실패", "detail": token_res}
                ),
                400,
            )

        # 3) 구글 사용자 정보 조회
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo = requests.get(userinfo_url, headers=headers).json()

        email = userinfo.get("email")
        name = userinfo.get("name")

        # 4) JWT 발급
        identity = {"provider": "google", "email": email, "name": name}
        jwt_token = create_access_token(identity=identity)

        return jsonify({"ok": True, "token": jwt_token, "user": identity})
