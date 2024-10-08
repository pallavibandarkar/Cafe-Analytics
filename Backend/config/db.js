import mongoose from "mongoose";

export const connectDb=async function main() {
    await mongoose.connect("mongodb://localhost:27017/Login-Form")
    .then(()=>{
        console.log("Connected to db Successfully!")
    });
  }