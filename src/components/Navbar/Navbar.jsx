import "./Navbar.css"
import {assets} from "../../assets/assets.js"
export default function Navbar(){
    return(
        <>
        <div className="Navbar">
          <div className="Nav-left">
            <img className="logo" src={assets.Coffe_Logo}/>
            <img className="logow" src={assets.coffee_w}/>
          </div>

    
          <ul className="Nav-menu">
            <li><a>Home</a></li>
            <li><a>Features</a></li>
            <li><a>Contact Us</a></li>
            <li><a>Insights Dashboard</a></li>
            <li><a> About Us</a></li>
          </ul>
          
          <div className="Navbar-right">
              <button>Sign Up</button>
          </div>
        </div>
        
        </>
    )
}