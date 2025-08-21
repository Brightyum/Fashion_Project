from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token
import os
import requests
import urllib.parse


class NaverAuth():
    def __init__(self):
        self.blueprint = Blueprint("naver_auth", __name__)

        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.redirect_uri = os.getenv("NAVER_REDIRECT_URI")

        self.blueprint.add_url_rule("/auth/naver/login", view_func=self.login)
        self.blueprint.add_url_rule("/auth/naver/callback", view_func=self.callback)
    
    def login(self):
        # 16바이트 길이의 예측 불가능한 랜던 데이터(hex함수는 16진수 문자열로 변환)
        state = os.urandom(16).hex()
        encoded_redirect_uri = urllib.parse.quote(self.redirect_uri, safe='')

        naver_auth_url = (
            "https://nid.naver.com/oauth2.0/authorize?response_type=code"
            f"&client_id={self.client_id}"
            f"&state={state}"
            f"&redirect_uri={encoded_redirect_uri}"
        )
        return redirect(naver_auth_url)
    
    def callback(self):
        code = request.args.get("code")
        state = request.args.get("state")

        if not code:
            return jsonify({"ok": False, "error": "네이버 인증 코드가 없습니다"}), 400
        
        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "state": state
        }
        token_res = requests.post(token_url, data=data).json()

        access_token = token_res.get("access_token")

        if not access_token:
            return jsonify({"ok": False, "error": "네이버 토큰 발급 실패"}), 400
        
        userinfo_url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo = requests.get(userinfo_url, headers=headers).json()

        email = userinfo.get("response", {}).get("email")
        mobile = userinfo.get("response", {}).get("mobile")
        name = userinfo.get("response", {}).get("name")
        gender = userinfo.get("response", {}).get("gender")
        
        identity = {
            "provider": "naver",
            "email": email,
            "mobile": mobile,
            "name": name,
            "gender": gender
        }
        jwt_token = create_access_token(identity=identity)
        return jsonify({"ok": True, "token": jwt_token, "user": identity})