import React, { useEffect, useState } from "react";
import "./Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [msg, setMsg] = useState("");
  const [ok, setOk] = useState(false);
  const [apiRes, setApiRes] = useState("{}");
  const [token, setToken] = useState(localStorage.getItem("access_token") || "");

  useEffect(() => {
    setToken(localStorage.getItem("access_token") || "");
  }, []);

  const setMessage = (text, isOk = false) => {
    setMsg(text);
    setOk(isOk);
  };

  async function onSubmit(e) {
    e.preventDefault();
    setMessage("", true);
    setApiRes("{}");

    try {
      const res = await fetch("/auth/login-func", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: email.trim(), name: name.trim() }),
      });
      const data = await res.json();
      setApiRes(JSON.stringify(data, null, 2));

      if (!res.ok || data.ok === false) {
        setMessage(data.error || "로그인 실패", false);
        localStorage.removeItem("access_token");
        setToken("");
      } else {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("name", data.user.name);
        setToken(data.access_token);
        setMessage("로그인 성공! 토큰이 저장되었습니다.", true);
        window.location.href = "/";
      }
    } catch {
      setMessage("요청 중 오류가 발생했습니다.", false);
    }
  }

  async function callProfile() {
    setMessage("", true);
    setApiRes("{}");
    const t = localStorage.getItem("access_token");
    if (!t) {
      setMessage("토큰이 없습니다. 먼저 로그인하세요.", false);
      return;
    }
    try {
      const res = await fetch("/profile", {
        method: "GET",
        headers: { Authorization: "Bearer " + t },
        credentials: "include",
      });
      const data = await res.json();
      setApiRes(JSON.stringify(data, null, 2));
      if (!res.ok || data.ok === false)
        setMessage("프로필 호출 실패(토큰 오류 가능).", false);
      else setMessage("프로필 호출 성공.", true);
    } catch {
      setMessage("요청 중 오류가 발생했습니다.", false);
    }
  }

  return (
    <div className="login-page">
      <div className="container">
        <h1>로그인</h1>
        <p className="muted">로그인 후 JWT를 발급받아 서비스를 이용해보세요.</p>

        <section className="card">
          <form onSubmit={onSubmit}>
            <label htmlFor="email">이메일</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="test@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <label htmlFor="name">이름</label>
            <input
              id="name"
              name="name"
              type="text"
              placeholder="홍길동"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />

            <button type="submit" className="btn btn-primary">
              로그인
            </button>
          </form>

          {/* 회원가입 버튼 */}
          <a href="/signup" className="btn btn-outline">
            회원가입
          </a>

          <div className="divider"></div>

          {/* 소셜 로그인 버튼 */}
          <a href="/auth/google/login" className="btn btn-google">
            Google 계정으로 로그인
          </a>
          <a href="/auth/kakao/login" className="btn btn-kakao">
            Kakao 계정으로 로그인
          </a>
          <a href="/auth/naver/login" className="btn btn-naver">
            Naver 계정으로 로그인
          </a>

          <div style={{ minHeight: 20, marginTop: 16 }} className={ok ? "ok" : "err"}>
            {msg}
          </div>
        </section>

        <section className="card" style={{ marginTop: 20 }}>
          <h3>API 테스트</h3>
          <button onClick={callProfile} className="btn btn-outline" style={{ marginTop: 8 }}>
            /profile 호출 (토큰 필요)
          </button>
          <h4>응답</h4>
          <pre>{apiRes}</pre>
          <h4>저장된 토큰 (localStorage)</h4>
          <pre>{token || "(없음)"}</pre>
        </section>
      </div>
    </div>
  );
}
