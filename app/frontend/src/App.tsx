import React from "react";
import { Homepage } from "./pages/Homepage";
import "./App.css";
import relativeTime from "dayjs/plugin/relativeTime";
import dayjs from "dayjs";
import "dayjs/locale/vi";

// Need init only once
dayjs.locale("vi");
dayjs.extend(relativeTime);

function App() {
  return <Homepage />;
}

export default App;
