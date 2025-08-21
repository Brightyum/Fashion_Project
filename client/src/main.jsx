// React 앱의 진입점
// index.html 안의 <div id="root"></div>에 MainPage 컴포넌트를 마운트

import React from "react";
import { createRoot } from "react-dom/client";

// 메인 페이지 컴포넌트 import
import MainPage from "./pages/MainPage.jsx";

// ReactDOM 18 버전 스타일의 렌더링 방식 사용
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* 메인 페이지를 root에 렌더링 */}
    <MainPage />
  </React.StrictMode>
);
