from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token
import os
import requests


class KakaoAuth():
    def __init__(self):
        self.blueprint = Blueprint("kakao_auth", __name__)

        self.client_id = os.getenv("KAKAO_CLIENT_ID")
        self.client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("KAKAO_REDIRECT_URI")

        self.blueprint.add_url_rule("/auth/kakao/login", view_func=self.login)
        self.blueprint.add_url_rule("/auth/kakao/callback", view_func=self.callback)

    def login(self):
        kakao_auth_url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
        )
        return redirect(kakao_auth_url)
    
    def callback(self):
        code = request.args.get("code")
        if not code:
            return jsonify({"ok": False, "error": "카카오 인증 코드가 없습니다."}), 400
        
        token_url = "https://kauth.kakao.com/oauth/token" 
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        token_res = requests.post(token_url, data=data).json()

        access_token = token_res.get("access_token")

        if not access_token:
            return (
                jsonify({
                    "ok":False,
                    "error": "카카오 토큰 발급 실패",
                    "detail": token_res
                }), 400
            )
        
        userinfo_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo = requests.get(userinfo_url, headers=headers).json()

        name = userinfo.get("properties", {}).get("nickname")
        identity = {
            "provider": "kakao",
            "name": name
        }
        jwt_token = create_access_token(identity=identity)
        
        return jsonify({"ok": True, "token": jwt_token, "user": identity})