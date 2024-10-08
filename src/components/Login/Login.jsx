import React, { useState,useEffect } from "react";
import { assets } from "../../assets/assets.js";
import "./Login.css"
import axios from 'axios'
export default function login({setCurrState}){

    let [loginState,setLoginState] = useState("Sign Up");

    let [data,setData] = useState({
        username:"",
        password:"",
        email:""
    })

    const onChaneHandeler =(event)=>{
        setData((data)=>({...data,[event.target.name]:event.target.value}))
    }

    useEffect(()=>{
        console.log(data);
    },[data])

    const submitForm = async (event)=>{
        event.preventDefault();
        console.log(data);

        try {
            if (loginState === "Login") {
                const response = await axios.post("http://localhost:8080/login", data);
                console.log("Login successful:", response.data);
            } else {
                const response = await axios.post("http://localhost:8080/signup", data,{
                    headers: {
                        "Content-Type": "application/json"
                    }});
                console.log("Registration successful:", response.data);
            }
        } catch (error) {
            console.error("Error:", error);
        }


    }
    
    return(
    <>
    <div className="login">
        <form className="login-form" onSubmit={submitForm}>
            <div className="login-popup-title">
               <p>{loginState}</p>
               <img onClick={()=>setCurrState(false)} src={assets.cross_icon}/>
            </div>
            
            <div className="credentials">
            
            <div className="credentials">
               <label htmlFor="username"><b>Username:</b></label>
               <input placeholder="Enter Username" name="username" id="username" type="text" value={data.username} onChange={onChaneHandeler}/>
            </div>

            {loginState === "Login"?<></>:
            <div className="credentials">
                <label htmlFor="email"><b>E-mail:</b></label>
                <input placeholder="Enter E-mail" name="email" id="email" type="email" value={data.email} onChange={onChaneHandeler}/>
                
            </div>}

            <label htmlFor="username"><b>Password:</b></label>
            <input placeholder="Enter Password" name="password" id="password" type="password" value={data.password} onChange={onChaneHandeler}/>
            
            <button>{loginState==="Login"?"Login":"Create an account"}</button>
            </div>

            <div className="login-popup-condition">
                    <input type="checkbox"/>
                    <p>By continuing, I agree to the terms of use and privacy policy</p>
            </div>
            {loginState==="Login"
            ?<p>Create an account <span onClick={()=>setLoginState("Sign Up")}><b>Click here</b></span></p>
            :<p>Alredy have an account <span onClick={()=>setLoginState("Login")}><b>Click here</b></span></p> }
        </form>
    </div>
   </>
   )
}