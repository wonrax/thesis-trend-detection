import React from "react";
import { Homepage } from "./pages/Homepage";
import "./App.css";
import relativeTime from "dayjs/plugin/relativeTime";
import dayjs from "dayjs";
import "dayjs/locale/vi";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { TopicDetail } from "./pages/TopicDetail";

// Need init only once
dayjs.locale("vi");
dayjs.extend(relativeTime);
dayjs.extend(timezone);
dayjs.extend(utc);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/topic/:id/:index" element={<TopicDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
