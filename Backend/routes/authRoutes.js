import express from "express";
import passport from "passport";
import User from "../models/user.js";

const router = express.Router();

// Signup route
router.post("/signup", async (req, res) => {
  const { username, email, password } = req.body;
  try {
    const newUser = new User({
      username,
      email,
    });
    const registeredUser = await User.register(newUser, password);
    console.log(registeredUser);
    res.status(201).json({ success: true, message: "User registered successfully" });
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Login route
router.post("/login", passport.authenticate("local"), (req, res) => {
  if (req.isAuthenticated()) {
    res.status(200).json({ success: true, message: "Login successful" });
  } else {
    res.status(401).json({ success: false, message: "Invalid credentials" });
  }
});

export default router;
