import React from "react";
import { Homepage } from "./pages/Homepage";
import "./App.css";
import relativeTime from "dayjs/plugin/relativeTime";
import dayjs from "dayjs";
import "dayjs/locale/vi";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";

// Need init only once
dayjs.locale("vi");
dayjs.extend(relativeTime);
dayjs.extend(timezone);
dayjs.extend(utc);

function App() {
  return <Homepage />;
}

export default App;
