import { useState } from 'react'
import './App.css'
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Output from "./pages/Output"
function App() {
  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/output" element={<Output />}></Route>
        
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App