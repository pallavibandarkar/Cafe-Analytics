import React, { useState } from "react"
import "./App.css"
import { Route, Routes } from "react-router-dom"
import Navbar from "./components/Navbar/Navbar.jsx"
import Home from "./pages/Home/Home.jsx"
import Login from "./components/Login/Login.jsx"
function App() {
  let [currState,setCurrState] = useState("false")
  return (
    <>
      {currState?<Login setCurrState={setCurrState}/>:<></>}
      <Navbar setCurrState={setCurrState}/>
      <Routes>
        <Route path="/" element={<Home/>}/>
      </Routes>
    </>
  )
}

export default App
