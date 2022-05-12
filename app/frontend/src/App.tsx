import React from "react";
import { useState } from "react";
import { TrendPage } from "./pages/TrendPage";
import "./App.css";
import relativeTime from "dayjs/plugin/relativeTime";
import dayjs from "dayjs";
import "dayjs/locale/vi";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { TopicDetail } from "./pages/TopicDetail";
import Trend from "./models/Trend";

// Need init only once
dayjs.locale("vi");
dayjs.extend(relativeTime);
dayjs.extend(timezone);
dayjs.extend(utc);

function RedirectToHomepage() {
  window.location.replace("/moi-nhat");
  return null;
}

function App() {
  const [trend, setTrend] = useState<Trend>();
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RedirectToHomepage />} />
        <Route
          path="/:trendCategory"
          element={<TrendPage trend={trend} setTrend={setTrend} />}
        />
        <Route path="/topic/:id/:index" element={<TopicDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
