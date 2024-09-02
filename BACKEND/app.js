import express from "express";
import {connectDb} from "./config/db.js"
import session from "express-session";
import { Cookie } from "express-session";
import User from "./models/user.js"
import passport from "passport";
import LocalStrategy from "passport-local";
import cors from 'cors'

const app = express();
connectDb();


const sessionOptions={
    secret:"mysupersecret@11222**&&&",
    resave:false,
    saveUninitialized:true,
    cookie:{
        expires:Date.now()+7*24*60*60*1000,
        maxAge: 7*24*60*60*1000,
        httpOnly:true,       
    }
}

app.use(express.json()); // to parse JSON bodies
app.use(express.urlencoded({ extended: true })); // to pars

app.use(session(sessionOptions));
passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

app.use(cors());


app.get("/",(req,res)=>{
    res.send("Hello root");
})

// app.get("/loign",async(req,res)=>{
//     let user= new User({
//         email:"abc@gmail.com",
//         username:"abc"
//     })

//     let registeredUser = await User.register(user,"helloworld");
//     res.send(registeredUser);
// })

app.post("/signup",async(req,res)=>{
    let {username,email,password} = req.body;
    try{
        let newUser = new User({
            username:username,
            email:email,
        })
        let registeredUser = await User.register(newUser,password);
        console.log(registeredUser);
    }catch(err){
        res.status(500).send(err.message);
    }
})

app.post("/login",passport.authenticate("local"),async(req,res)=>{
    console.log(req.body)
    res.send("Welcom");
})

app.listen(8080,()=>{
    console.log("App Listening on port 8080");
})