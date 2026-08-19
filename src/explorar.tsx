import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ExplorePage } from "./ExplorePage";
import "./styles.css";

createRoot(document.getElementById("root")!).render(<StrictMode><ExplorePage /></StrictMode>);
