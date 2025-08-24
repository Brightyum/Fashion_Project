// 메인 페이지 UI
// 지금은 날씨 API가 없으므로 makeMockWeather()에서 더미 데이터를 생성해서 보여주고 있음. 날씨 api 연결되면 로직 수정 할 것

import React, { useEffect, useMemo, useState } from "react";
import "./MainPage.css"; 

// 날씨 상태별 아이콘 
const ICON = { clear:"☀️", clouds:"☁️", rain:"🌧️", snow:"❄️", drizzle:"🌦️", thunder:"⛈️", mist:"🌫️" };

// 더미데이터(나중에 없앨거임)
function makeMockWeather(lat, lon){
  const city = "부산";  
  const now = new Date();
  const hours = [];
  const base = 26;

  // 더미 24시간 날씨 데이터
  for (let i=0;i<24;i++){
    const t = new Date(now.getFullYear(), now.getMonth(), now.getDate(), i, 0, 0);
    const wave = Math.sin((i-13)/3);
    const temp = Math.round(base + wave*4);
    const condition = wave>0.3 ? "clear" : "clouds"; // 단순히 맑음/구름으로 처리
    hours.push({ dt: t.toISOString(), temp, condition, windKmh: 10 });
  }

  const min = Math.min(...hours.map(h=>h.temp));
  const max = Math.max(...hours.map(h=>h.temp));
  const cur = hours[new Date().getHours()];

  return {
    location:{ city, lat, lon },
    now:{ temp:cur.temp, feels:cur.temp, condition:cur.condition, humidity:60, windKmh:cur.windKmh },
    today:{ min, max, hours }
  };
}

// 오늘 날씨 요약
function buildSummary(w){
  const {min, max} = w.today;
  return `최저 ${min}° / 최고 ${max}°로 ${max>=28?"더운": max<=18?"선선한":"온화한"} 하루 예상됩니다.`;
}


function fmtTime(iso){
  return new Date(iso).toLocaleTimeString("ko-KR",{hour:"2-digit",minute:"2-digit"});
}

// 메인 페이지 요소
export default function MainPage(){
  // 상태 정의
  const [coords, setCoords]   = useState(null);     // 위도/경도
  const [geoMsg, setGeoMsg]   = useState(null);     // 위치 권한 관련 메시지
  const [weather, setWeather] = useState(null);     // 날씨 데이터
  const [loading, setLoading] = useState(true);     // 로딩 상태

  // 위치 가져오기 (실패하면 부산 기본값)
  useEffect(()=>{
    if (!("geolocation" in navigator)){
      setGeoMsg("위치 권한을 사용할 수 없어 기본 위치(부산)를 사용합니다.");
      setCoords({ lat:35.1796, lon:129.0756 });
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos)=> setCoords({ lat:pos.coords.latitude, lon:pos.coords.longitude }),
      ()=> { setGeoMsg("위치 권한이 거부되어 기본 위치(부산)를 사용합니다."); setCoords({ lat:35.1796, lon:129.0756 }); },
      { enableHighAccuracy:true, maximumAge:60000, timeout:12000 }
    );
  },[]);

  // 날씨 데이터 (더미) 가져오기
  useEffect(()=>{
    if(!coords) return;
    setLoading(true);
    const t = setTimeout(()=>{
      setWeather(makeMockWeather(coords.lat, coords.lon));
      setLoading(false);
    }, 300);
    return ()=> clearTimeout(t);
  },[coords]);

  // 요약 문구 생성
  const summary = useMemo(()=> weather ? buildSummary(weather) : "", [weather]);

  // 화면에 나타나는 UI
  return (
    <div className="page">
      {/* 헤더 */}
      <header className="header">
        <div className="container header-row">
          <div className="brand">
            <span aria-hidden className="brand-emoji">🧭</span>
            <span className="brand-name">이름아직못정함티비</span>
            {weather?.location?.city && (
              <span className="brand-city">· {weather.location.city}</span>
            )}
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <a className="nav-link" href="/login">로그인</a>
            <a className="nav-link" href="/signup">회원가입</a>
          </div>
        </div>
      </header>


      {/* 본문 */}
      <main className="container grid">
        <section className="col-left">
          {/* 위치 권한 메시지 */}
          {geoMsg && <div className="banner">{geoMsg}</div>}

          {/* 현재 날씨 카드 */}
          <section className="card">
            {loading || !weather ? (
              <div className="skeleton h160"></div> // 로딩 상태
            ) : (
              <div className="row gap16">
                <div className="now-icon">{ICON[weather.now.condition]}</div>
                <div className="col">
                  <div className="title-sm">{weather.location.city}</div>
                  <div className="temp-line">
                    <span className="temp-big">{weather.now.temp}°C</span>
                    <span className="muted">체감 {weather.now.feels}°</span>
                  </div>
                  <div className="meta">
                    <span>습도 {weather.now.humidity}%</span>
                    <span>바람 {weather.now.windKmh} km/h</span>
                    <span>최저 {weather.today.min}° / 최고 {weather.today.max}°</span>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* 오늘 요약 카드 */}
          <section className="card">
            {loading || !weather ? (
              <div className="skeleton h96"></div>
            ) : (
              <>
                <h2 className="card-title">오늘 날씨 요약</h2>
                <p className="summary">{summary}</p>
              </>
            )}
          </section>

          {/* 추천 페이지 이동 버튼 */}
          <section className="card">
            <div className="cta">
              <div>
                <h3 className="card-title">오늘의 날씨를 바탕으로 코디 추천 받기</h3>
                <p className="muted">보유 옷/선호 스타일을 반영한 적절한 옷차림을 제안합니다.</p>
              </div>
              <a className="btn-primary" href="#">오늘 맞춤 코디 보러가기</a>
            </div>
          </section>
        </section>

        {/* 우측: 시간대별 미리보기 */}
        <section className="col-right">
          <section className="card">
            <h2 className="card-title">시간대별 미리보기</h2>
            {loading || !weather ? (
              <div className="skeleton h160"></div>
            ) : (
              <div className="hour-grid">
                {weather.today.hours.slice(6,22).map(h=>(
                  <div key={h.dt} className="hour-card">
                    <div className="muted">{fmtTime(h.dt)}</div>
                    <div className="hour-icon">{ICON[h.condition]}</div>
                    <div className="strong">{h.temp}°C</div>
                    <div className="muted xs">바람 {h.windKmh} km/h</div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}
