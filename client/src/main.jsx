// React 앱의 진입점 (main.jsx)
import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

// 페이지 컴포넌트 import
import MainPage from "./pages/MainPage.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import OutfitPage from "./pages/OutfitPage.jsx"; 

const router = createBrowserRouter([
  { path: "/", element: <MainPage /> },
  { path: "/login", element: <Login /> },
  { path: "/signup", element: <Signup /> },
  { path: "/recommend", element: <OutfitPage /> },
]);

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
