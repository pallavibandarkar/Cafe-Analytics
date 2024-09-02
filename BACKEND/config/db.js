import mongoose from "mongoose";

export const connectDb=async function main() {
    await mongoose.connect("mongodb://127.0.0.1:27017/Login-Form")
    .then(()=>{
        console.log("Connected to db Successfully!")
    });
  }