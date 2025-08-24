import React, { useEffect, useMemo, useState } from "react";
import "./Signup.css";

export default function Signup() {
  const url = new URL(window.location.href);
  const provider = url.searchParams.get("provider");
  const socialEmail = url.searchParams.get("email") || "";
  const socialName = url.searchParams.get("name") || "";
  const isSocial = useMemo(() => Boolean(provider), [provider]);

  const [form, setForm] = useState({
    email: socialEmail,
    name: socialName,
    phone: "",
    gender: "",
    password: "",
    passwordConfirm: "",
  });

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (isSocial) {
      setForm((f) => ({ ...f, password: "", passwordConfirm: "" }));
    }
  }, [isSocial]);

  function onChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setMsg("");

    if (!isSocial) {
      if (form.password.length < 8) {
        alert("비밀번호는 8자 이상으로 설정해주세요.");
        return;
      }
      if (form.password !== form.passwordConfirm) {
        alert("비밀번호가 일치하지 않습니다.");
        return;
      }
    }

    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("email", form.email);
      fd.append("name", form.name);
      fd.append("phone", form.phone);
      fd.append("gender", form.gender);
      if (!isSocial) {
        fd.append("password", form.password);
      }

      const res = await fetch("/auth/register", {
        method: "POST",
        body: fd,
        credentials: "include",
      });
      const data = await res.json();

      if (!res.ok || data.ok === false) {
        setMsg(data.error || data.msg || "회원가입 실패");
        return;
      }

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
      }
      setMsg("회원가입 성공! 메인으로 이동합니다.");
      window.location.href = "/";
    } catch {
      setMsg("요청 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="signup-page">
      <div className="card">
        <div className="title">회원가입</div>
        <p className="desc">
          {isSocial
            ? "서비스 이용을 위해 추가 정보를 입력해주세요."
            : "서비스 이용을 위해 정보를 입력해주세요."}
        </p>

        {isSocial && (
          <div className="social-info">
            <strong>{provider}</strong> 계정으로 간편가입을 진행합니다.
          </div>
        )}

        <form onSubmit={onSubmit}>
          <label>이메일</label>
          <input
            type="email"
            name="email"
            placeholder="your-email@example.com"
            required
            disabled={isSocial}
            value={form.email}
            onChange={onChange}
          />

          <label>이름</label>
          <input
            type="text"
            name="name"
            placeholder="홍길동"
            required
            disabled={isSocial}
            value={form.name}
            onChange={onChange}
          />

          <label>휴대폰 번호</label>
          <input
            type="tel"
            name="phone"
            placeholder="010-1234-5678"
            required
            value={form.phone}
            onChange={onChange}
          />

          <label style={{ marginBottom: 8 }}>성별</label>
          <div className="radio-row">
            <label>
              <input
                type="radio"
                name="gender"
                value="male"
                required
                checked={form.gender === "male"}
                onChange={onChange}
              />
              <span>남성</span>
            </label>
            <label>
              <input
                type="radio"
                name="gender"
                value="female"
                checked={form.gender === "female"}
                onChange={onChange}
              />
              <span>여성</span>
            </label>
          </div>

          {!isSocial && (
            <>
              <label>비밀번호</label>
              <input
                type="password"
                name="password"
                placeholder="비밀번호를 입력하세요"
                required
                value={form.password}
                onChange={onChange}
              />

              <label>비밀번호 확인</label>
              <input
                type="password"
                name="passwordConfirm"
                placeholder="비밀번호를 다시 입력하세요"
                required
                value={form.passwordConfirm}
                onChange={onChange}
              />
            </>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "가입 중..." : "가입 완료"}
          </button>
        </form>

        {msg && <p className="muted" style={{ marginTop: 12 }}>{msg}</p>}

        <div className="footer">
          이미 계정이 있으신가요?{" "}
          <a href="/login" aria-label="로그인으로 이동">로그인</a>
        </div>
      </div>
    </div>
  );
}
