import "./Navbar.css"
import {assets} from "../../assets/assets.js"
import { useState } from "react";
export default function Navbar({setCurrState}){
    return(
        <>
        <div className="Navbar">
          <div className="Nav-left">
            <img className="logo" src={assets.Coffe_Logo}/>
            <img className="logow" src={assets.coffee_w}/>
          </div>

    
          <ul className="Nav-menu">
            <li><a href="#">Home</a></li>
            <li><a href="#features">Features</a></li>
            <li><a href="#contact">Contact Us</a></li>
            <li><a href="#">Insights Dashboard</a></li>
            <li><a href="#features"> About Us</a></li>
          </ul>
          
          <div className="Navbar-right">
              <button onClick={()=>setCurrState(true)}>Sign Up</button>
          </div>
        </div>
        
        </>
    )
}