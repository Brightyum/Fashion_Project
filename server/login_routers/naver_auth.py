from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
import os
import requests
import urllib.parse

from models.user_manager import UserManager
from models.token_manager import TokenManager

class NaverAuth():
    def __init__(self):
        self.blueprint = Blueprint("naver_auth", __name__)

        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.redirect_uri = os.getenv("NAVER_REDIRECT_URI")

        self.blueprint.add_url_rule("/auth/naver/login", view_func=self.login)
        self.blueprint.add_url_rule("/auth/naver/callback", view_func=self.callback)
        self.user_manager = UserManager
        self.token_manager = TokenManager
    
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
        
        checking_user = self.user_manager.get_user_by_email(email)
        if checking_user:
            print(f"기존 사용자 로그인: {email}")
            identity = {
                "userId": checking_user["userId"],
                "email": checking_user["email"],
                "name": checking_user["name"]
            }
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            self.token_manager.save_refresh_token(identity["userId"], refresh_token)

            return jsonify({
                "ok": True, 
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": identity 
            })
        else:
            print(f"신규 사용자, 회원가입: {email}")
            identity = {
                "provider": "naver",
                "email": email,
                "mobile": mobile,
                "name": name,
                "gender": gender
            }

            encoded_params = urllib.parse.urlencode(identity)
            return redirect(f"/signup?{encoded_params}")
        