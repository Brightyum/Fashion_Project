
import React from "react";
import "./OutfitPage.css";

export default function OutfitPage() {
  return (
    <div className="page">
      <header className="header">
        <h2>오늘의 맞춤 코디 추천</h2>
      </header>
      <main className="container">
        <div className="outfit-grid">
          <div className="outfit-card">코디 1</div>
          <div className="outfit-card">코디 2</div>
          <div className="outfit-card">코디 3</div>
        </div>
      </main>
    </div>
  );
}
