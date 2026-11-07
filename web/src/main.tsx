import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { GameIntroPrototype } from "./GameIntroPrototype";
import "./styles.css";
import "./GameIntroPrototype.css";

const prototype = new URLSearchParams(window.location.search).get("prototype");

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {prototype === "game-intro" ? <GameIntroPrototype /> : <App />}
  </StrictMode>
);
